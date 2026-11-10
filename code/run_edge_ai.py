"""Edge-AI module: MCU-style 1-D CNN residual learner with INT8 and latency.

This implements (in software, no MCU hardware) the proposal's "physics-
constrained AI residual learning, 1-D CNN, INT8, <300 KB, <200 ms" module:

1. a 1-D convolutional network over the 10-channel observation plus the physics
   clay estimate, implemented in pure NumPy (no torch/tf);
2. residual learning: prediction = physics_clay + CNN(features);
3. post-training INT8 quantization with size and accuracy measurements;
4. CPU latency benchmarks for tile inference (float and INT8-simulated).

Honest scope: CPU only, no Jetson/MCU device; INT8 is simulated (quantized
weights, float arithmetic). The training target is the gamma-derived clay
proxy, so CNN gains measure proxy agreement, not geological accuracy.
"""
from __future__ import annotations

import csv
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

SEED = 2026


# ----------------------------- tiny NumPy CNN ------------------------------
class Conv1D:
    def __init__(self, rng, cin, cout, k):
        self.w = (rng.standard_normal((cout, cin, k)) * np.sqrt(2.0 / (cin * k))).astype(np.float32)
        self.b = np.zeros(cout, dtype=np.float32)
        self.k, self.cin, self.cout = k, cin, cout

    def fwd(self, x, w=None, b=None):
        w = self.w if w is None else w
        b = self.b if b is None else b
        n, cin, L = x.shape
        Lout = L - self.k + 1
        cols = np.stack([x[:, :, i:i + Lout] for i in range(self.k)], axis=3)
        # (n, cin, Lout, k) -> (n, Lout, cin*k)
        cols = cols.transpose(0, 2, 1, 3).reshape(n, Lout, cin * self.k)
        wm = w.reshape(self.cout, cin * self.k)
        out = np.einsum("nlc,oc->nlo", cols, wm).transpose(0, 2, 1)  # (n, cout, Lout)
        return (out + b[None, :, None]).astype(np.float32), cols

    def bwd(self, cols, dout):
        # cols: (n, Lout, cin*k); dout: (n, cout, Lout)
        n, Lout, _ = cols.shape
        doutm = dout.transpose(0, 2, 1).reshape(-1, self.cout)   # (n*Lout, cout)
        colsm = cols.reshape(-1, cols.shape[-1])                 # (n*Lout, cin*k)
        dw = (doutm.T @ colsm).reshape(self.w.shape)
        db = dout.sum(axis=(0, 2))
        wm = self.w.reshape(self.cout, -1)
        dcols = (doutm @ wm).reshape(n, Lout, self.cin, self.k)  # (n, Lout, cin, k)
        dx = np.zeros((n, self.cin, Lout + self.k - 1), dtype=np.float32)
        for i in range(self.k):
            dx[:, :, i:i + Lout] += dcols[:, :, :, i].transpose(0, 2, 1)
        return dw.astype(np.float32), db.astype(np.float32), dx


class Dense:
    def __init__(self, rng, nin, nout):
        self.w = (rng.standard_normal((nin, nout)) * np.sqrt(2.0 / nin)).astype(np.float32)
        self.b = np.zeros(nout, dtype=np.float32)

    def fwd(self, x, w=None, b=None):
        return x @ (self.w if w is None else w) + (self.b if b is None else b)


def relu(x):
    return np.maximum(x, 0.0)


# ------------------------------- training ----------------------------------
def main():
    rng = np.random.default_rng(SEED)
    z, H, lay, _ = C.load_main("real", emfix=True)
    mask = C.load_analysis_mask()
    prior = C.load_clay_prior()

    x_phys = C.fuse(z, H)["x"]
    phys_clay = x_phys[C.TARGET]

    # features: main-line channels + physics clay, per pixel
    zn = np.stack([(z[i] - np.nanmean(z[i][mask])) / (np.nanstd(z[i][mask]) + 1e-6)
                   for i in range(z.shape[0])])
    feats = np.concatenate([zn, phys_clay[None]], axis=0)  # (n_ch, H, W)
    n_ch = feats.shape[0]

    # spatial block split (64 px blocks, checkerboard) to limit leakage
    h, w = mask.shape
    bid = (np.arange(h)[:, None] // 64) + (np.arange(w)[None, :] // 64)
    train_sel = mask & (bid % 2 == 0)
    test_sel = mask & (bid % 2 == 1)

    def pack(sel, cap=120_000, seed=1):
        r = np.random.default_rng(seed)
        idx = np.argwhere(sel)
        if len(idx) > cap:
            idx = idx[r.choice(len(idx), cap, replace=False)]
        X = feats[:, idx[:, 0], idx[:, 1]].T[:, None, :]  # (n, 1 channel, length 11)
        y = prior[idx[:, 0], idx[:, 1]]
        p = phys_clay[idx[:, 0], idx[:, 1]]
        return X.astype(np.float32), y.astype(np.float32), p.astype(np.float32)

    Xtr, ytr, ptr = pack(train_sel, seed=101)
    Xte, yte, pte = pack(test_sel, cap=200_000, seed=202)
    print(f"train {Xtr.shape}  test {Xte.shape}")

    # network: Conv1D(16,k=3) -> Conv1D(12,k=3) -> flatten((n_ch-4)*12) -> Dense(24) -> Dense(1)
    c1 = Conv1D(rng, 1, 16, 3)
    c2 = Conv1D(rng, 16, 12, 3)
    flat = (n_ch - 4) * 12          # two valid convs with k=3
    d1 = Dense(rng, flat, 24)
    d2 = Dense(rng, 24, 1)
    params = c1.w.size + c1.b.size + c2.w.size + c2.b.size + d1.w.size + d1.b.size + d2.w.size + d2.b.size
    print(f"params {params}")

    def forward(X, ws=None):
        ws = ws or {}
        a1, cols1 = c1.fwd(X, ws.get("c1w"), ws.get("c1b"))
        h1 = relu(a1)
        a2, cols2 = c2.fwd(h1, ws.get("c2w"), ws.get("c2b"))
        h2 = relu(a2)
        f = h2.reshape(len(X), -1)
        a3 = d1.fwd(f, ws.get("d1w"), ws.get("d1b"))
        h3 = relu(a3)
        out = d2.fwd(h3, ws.get("d2w"), ws.get("d2b"))[:, 0]
        cache = (cols1, cols2, f, a1, a2, a3, h3)
        return out, cache

    def train_step(Xb, yb, pb, lr):
        out, (cols1, cols2, f, a1, a2, a3, h3) = forward(Xb)
        # loss = mean((pb + out - yb)^2); d/dout
        dout = (2.0 * (pb + out - yb) / len(yb))[:, None]
        gd2w = h3.T @ dout
        gd2b = dout.sum(0)
        dh3 = dout @ d2.w.T
        da3 = dh3 * (a3 > 0)
        gd1w = f.T @ da3
        gd1b = da3.sum(0)
        df = da3 @ d1.w.T
        dh2 = df.reshape(len(Xb), 12, n_ch - 4)
        da2 = dh2 * (a2 > 0)
        dc2w, dc2b, dh1 = c2.bwd(cols2, da2)
        da1 = dh1 * (a1 > 0)
        dc1w, dc1b, _ = c1.bwd(cols1, da1)
        for p, g in ((d2.w, gd2w), (d2.b, gd2b), (d1.w, gd1w), (d1.b, gd1b),
                     (c2.w, dc2w), (c2.b, dc2b), (c1.w, dc1w), (c1.b, dc1b)):
            p -= lr * g.astype(np.float32)

    t0 = time.time()
    n_epoch, bs = 20, 512
    n = len(Xtr)
    for ep in range(n_epoch):
        perm = rng.permutation(n)
        lr = 3e-3 * (0.85 ** ep)
        for i in range(0, n, bs):
            sel = perm[i:i + bs]
            train_step(Xtr[sel], ytr[sel], ptr[sel], lr=lr)
        out_tr, _ = forward(Xtr)
        rmse = float(np.sqrt(np.mean((ptr + out_tr - ytr) ** 2)))
        if (ep + 1) % 4 == 0 or ep == 0:
            print(f"epoch {ep+1}/{n_epoch} train RMSE {rmse:.4f}")
    train_s = time.time() - t0

    # ---------------- evaluation -------------------------------------------
    out_te, _ = forward(Xte)
    pred_phys = pte
    pred_cnn = pte + out_te
    gt_te = yte > 0.55
    prev = float(gt_te.mean())

    def metrics_of(pred):
        pr = np.clip(pred, 0, 1)
        # matched-prevalence threshold: both estimators flag the same fraction
        thr = float(np.quantile(pr, 1.0 - prev))
        pos = pr >= thr
        tp = np.sum(pos & gt_te)
        prec = tp / max(pos.sum(), 1)
        rec = tp / max(gt_te.sum(), 1)
        f1m = 2 * prec * rec / max(prec + rec, 1e-9)
        # average precision (threshold-free)
        order = np.argsort(-pr)
        yy = gt_te[order]
        tpc = np.cumsum(yy)
        fpc = np.cumsum(~yy)
        precision = tpc / np.maximum(tpc + fpc, 1)
        recall = tpc / max(yy.sum(), 1)
        ap = float(np.sum(np.diff(np.concatenate([[0.0], recall])) * precision))
        rmse = float(np.sqrt(np.mean((pr - yte) ** 2)))
        return {"f1_matched": float(f1m), "ap": ap, "rmse": rmse}

    m_phys = metrics_of(pred_phys)
    m_cnn = metrics_of(pred_cnn)
    print("test physics:", m_phys)
    print("test CNN    :", m_cnn)

    # ---------------- INT8 quantization ------------------------------------
    def quant(t):
        s = np.abs(t).max() / 127.0
        return np.clip(np.round(t / max(s, 1e-12)), -127, 127).astype(np.int8), float(s)

    q = {k: quant(v) for k, v in (("c1w", c1.w), ("c1b", c1.b), ("c2w", c2.w),
                                  ("c2b", c2.b), ("d1w", d1.w), ("d1b", d1.b),
                                  ("d2w", d2.w), ("d2b", d2.b))}
    ws_q = {k: v[0].astype(np.float32) * v[1] for k, v in q.items()}
    size_int8 = sum(v[0].nbytes for v in q.values()) + 8 * 4
    out_q, _ = forward(Xte, ws_q)
    pred_q = pte + out_q
    m_q = metrics_of(pred_q)
    print("test INT8   :", m_q)

    # ---------------- latency ----------------------------------------------
    tile = Xte[:10000]
    t0 = time.time(); forward(tile); t_float = (time.time() - t0) * 1000
    t0 = time.time(); forward(tile, ws_q); t_q = (time.time() - t0) * 1000
    per_sample_us = t_q * 1000 / len(tile)
    print(f"latency 10k samples: float {t_float:.1f} ms, INT8-sim {t_q:.1f} ms "
          f"({per_sample_us:.1f} us/sample)")

    res = {
        "architecture": "Conv1D(16,k3)-Conv1D(12,k3)-Dense(24)-Dense(1), pure NumPy",
        "params": int(params),
        "int8_size_kb": size_int8 / 1024,
        "budget_300kb": size_int8 / 1024 < 300,
        "physics": m_phys,
        "cnn_float": m_cnn,
        "cnn_int8": m_q,
        "latency_ms_10k": {"float": t_float, "int8_sim": t_q},
        "latency_us_per_sample": per_sample_us,
        "budget_200ms": t_q < 200,
        "train_seconds": train_s,
        "train_n": int(len(Xtr)), "test_n": int(len(Xte)),
        "hardware": "CPU only; no Jetson/MCU; INT8 simulated (quantized weights)",
        "target_caveat": "target is the gamma-derived clay proxy",
    }
    C.save_json(C.PROC / "edge_ai.json", res)
    with open(C.PROC / "edge_ai.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["model", "f1_matched", "ap", "rmse"])
        wr.writerow(["physics", m_phys["f1_matched"], m_phys["ap"], m_phys["rmse"]])
        wr.writerow(["cnn_float", m_cnn["f1_matched"], m_cnn["ap"], m_cnn["rmse"]])
        wr.writerow(["cnn_int8", m_q["f1_matched"], m_q["ap"], m_q["rmse"]])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    names = ["physics", "CNN float", "CNN INT8"]
    axes[0].bar(names, [m_phys["ap"], m_cnn["ap"], m_q["ap"]],
                color=["#7f7f7f", "#1f77b4", "#2ca02c"])
    axes[0].set_ylabel("Average precision (test blocks)")
    axes[0].set_title("(a) Residual learner accuracy")
    axes[0].grid(axis="y", alpha=0.3)
    axes[1].bar(["float", "INT8-sim"], [t_float, t_q], color=["#1f77b4", "#2ca02c"])
    axes[1].axhline(200, color="red", ls="--", label="200 ms budget")
    axes[1].set_ylabel("ms / 10k samples")
    axes[1].set_title(f"(b) CPU latency (size {size_int8/1024:.1f} KB)")
    axes[1].legend(); axes[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "edge_ai.png", dpi=300)
    plt.close()
    print("saved edge_ai.json/csv/png")


if __name__ == "__main__":
    main()

