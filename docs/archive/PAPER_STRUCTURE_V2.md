# 论文结构重写（v2）

> 目标：把原稿从“我们提出一个统一卡尔曼框架，效果很好”改写成“**多模态融合何时真正有用：可辨识性分析 + 可复现基准 + 方法审计**”。
> 主投：IEEE JSTARS；备投：Computers & Geosciences。两刊结构通用，换模板即可。

---

## 0. 一句话论证

> 多模态融合的增益不是“加一个模态就更好”，而是由**响应矩阵的可辨识性、模态误差结构与评价目标**共同决定；我们用真实 USGS 伽马数据 + 文档化合成 TIR/EM 建立统一基准，给出可计算的 fusion gain index，并证明常被引用的 +104% 增益来自 H 矩阵混用而非模态贡献。

**不是找矿发现，不是硬件系统，是一篇“方法 + 基准 + 审计”论文。**

---

## 1. 标题、摘要、Highlights

### 标题（三选一）

1. **When does multi-modal fusion improve airborne mineral exploration? An identifiability analysis and reproducible benchmark**
2. **Fusion gain or matrix artefact? A reproducible benchmark for gamma–TIR–EM mineral exploration**
3. **Beyond a single modality: identifiability, uncertainty calibration and a reproducible benchmark for airborne mineral exploration**

首选 1：问题明确，JSTARS/C&G 都吃这一套。

### Abstract（约 220 词，英文草案）

> Multi-modal fusion is widely proposed to improve airborne mineral exploration, yet reported gains are rarely comparable because studies use different response matrices, synthetic augmentation recipes and metric definitions. We present a reproducible benchmark built on the real USGS airborne radiometric survey of the Ivanpah–Clark Mountain area (Nevada–California, 2019–2020), with physically informed synthetic thermal-infrared and electromagnetic modalities generated from documented endmembers and AEM statistics. The benchmark fixes one response matrix, one valid-pixel mask and one contingency-table metric, and then varies modality set, sensor degradation, temperature, domain shift, response-matrix perturbation, resolution and random seed. We derive a fusion gain index from the clay-estimate variance and show that it predicts when adding a modality helps. Legacy tri-modal fusion fails because the EM row uses raw resistivity with five mineral responses; replacing it with log10 resistivity and a clay-only response raises proxy F1 from 0.267 to 0.498 and average precision from 0.126 to 0.513, significantly above the independent and GLS baselines. The widely quoted +104 % fusion gain remains a matrix artefact. We release the code, data recipe and audit scripts, and recommend reporting recall, precision and F1 together with an explicit statement of the evaluation target.

### Highlights（5 条，≤85 字符）

1. One response matrix, one mask, one metric across all fusion experiments.
2. A fusion gain index predicts when adding a modality improves clay estimability.
3. Legacy EM mis-specification masks the fusion gain; correcting it unlocks it.
4. Log10 clay-only EM raises F1 from 0.267 to 0.498; the +104 % claim is an artefact.
5. Code, synthetic recipes and audit scripts are released for reuse.

---

## 2. 全文结构总表

| 节 | 标题 | 内容 | 词数 | 图/表 |
|---|---|---|---:|---|
| 1 | Introduction | 问题、三个失效模式、RQ、贡献 | 1300 | — |
| 2 | Related work | 单模态、融合、评价/可复现、gap | 1000 | — |
| 3 | Data and benchmark design | 真实伽马、合成 TIR/EM、两个真值、协议、指标 | 1600 | 表 1–2；图 1–2 |
| 4 | Methods | 观测/H、WLS、Kalman、深度、质量权重、基线、校准 | 1600 | 图 3 |
| 5 | Identifiability and fusion gain | 方差分解、条件数、gain index、预测 vs 观测 | 1200 | 图 4 |
| 6 | Experiments | 7 组实验矩阵 | 900 | 表 3 |
| 7 | Results | 主结果、消融、退化、温度、跨域、稳健性、校准 | 2200 | 图 5–9；表 4–7 |
| 8 | Discussion | 何时有用、EM 误配、指标含义、局限、建议 | 1300 | — |
| 9 | Conclusion | 4 条结论 | 300 | — |
| — | Reproducibility / Data availability | 代码、数据、环境、运行时间 | 250 | — |
| — | References | 35–45 篇 | — | — |

总计约 9000–10000 词，8–9 图，6–7 表。

---

## 3. 逐节写作提纲

### 1 Introduction（6 段，1300 词）

- **P1 场景**：航空伽马/EM/TIR 是矿产勘探的常规手段；单模态物理局限（伽马 30 cm、EM 多解、TIR 受水汽/粉尘影响）。引用 3–5 篇。
- **P2 承诺**：多模态融合被广泛报道能提升反演/填图；但“提升”从 10% 到 100% 不等，实验设置不可比。
- **P3 三个失效模式**：
  1. **响应矩阵不一致**：同一篇论文的消融与验证用不同 H；
  2. **合成循环**：TIR/EM 由伽马派生场生成，评价目标又由伽马派生；
  3. **指标口径混用**：coverage 与 recall 都叫“detection rate”。
- **P4 研究问题**：
  - RQ1：在什么条件下，加入一个模态会降低 clay 估计方差？
  - RQ2：为什么文献中的融合增益难以复现？
  - RQ3：怎样的基准协议能让结论可复现、可比较？
- **P5 贡献**（4 条，动词开头）：
  1. 建立统一基准（真实伽马 + 文档化合成 TIR/EM + 固定 H/掩膜/指标）；
  2. 推导 fusion gain index，给出“何时融合有用”的判据；
  3. 量化三个失效模式，证明 +104% 是 H 混用伪迹；
  4. 给出修正建议与开源实现。
- **P6 组织**：章节路线图。

**写作要求**：不要在 Introduction 里写“我们的框架全面优于基线”；只写“我们回答什么问题、发现什么”。

### 2 Related work（4 小节，1000 词）

- **2.1 单模态矿产勘探**：伽马能谱（K/eU/eTh、蚀变指数）、EM（电导率/多解）、TIR（Reststrahlen 带）。各 3–5 篇。
- **2.2 多模态融合**：贝叶斯、WLS、Kalman、PCA、深度学习；指出多数工作只报告“融合后更好”，缺可辨识性分析。
- **2.3 评价与可复现**：遥感/地学中的 benchmark、指标定义、合成数据循环、负结果。
- **2.4 Gap**：没有统一 H/掩膜/指标的基准；没有“何时融合有用”的判据；没有对合成循环的量化。

**不要**把 Related work 写成文献堆砌；每段结尾落到“因此本文……”。

### 3 Data and benchmark design（1600 词）

- **3.1 真实伽马**：USGS Ivanpah/Clark Mtn，2019-12–2020-03，295,943 样本、631 线、50 m 网格、1772×1075、66.4% 有效；K/eU/eTh 中位数；CSV 与网格一致性。表 1。
- **3.2 合成 TIR**：8–14 µm、200 点、splib07 端元、`TIR=Σa_m(1−R_m)`；说明这是合成，不是实测。
- **3.3 合成 EM**：40 层、0–600 m、Wisconsin AEM 层统计、受控相关场、seed。
- **3.4 两个 clay 真值**：TIR truth（0.3K+0.3Th，mean 0.30）与 EM truth（clay_prior，mean 0.46，valid 0.49），相关 0.57；说明这是原数据的结构性问题，本文把它作为审计对象。
- **3.5 Benchmark 协议**：固定 H、固定 valid mask、固定指标、固定 seeds；训练/测试不适用（无监督反演），用 leave-channel-out 与 modality ablation 代替。
- **3.6 指标定义**：positive = clay>0.25 & top-2；target = clay_prior>0.55；valid pixels；recall/precision/F1/IoU；明确“不是 detection rate”。表 2。

### 4 Methods（1600 词）

- **4.1 观测模型与 H**：10×5，逐行解释；明确 H 是相对 signature，不是绝对浓度。
- **4.2 WLS + 非负/闭合**：公式、λ=0.1、列归一化的说明与局限。
- **4.3 空间 Kalman**：F=I、Q、R_obs、前向滤波；P 不是校准区间。
- **4.4 深度 Kalman**：40 层、F=0.85I+0.15/N、Q=0.03、深度相关 H/R；说明地表模态在每层重复的结构性局限。
- **4.5 质量权重**：q(T,RH,fault)、W=diag(q)；主结果 uniform，场景实验用 q；明确方向。
- **4.6 基线**：independent、simple average、fixed weight、PCA、GLS/Bayesian、ours。
- **4.7 不确定度校准**：覆盖率、reliability、重标定；放到 Results 7.7 报告。

### 5 Identifiability and fusion gain（1200 词，核心加分项）

- **5.1 clay 方差分解**：从 `x̂=(HᵀWH+λI)⁻¹HᵀWz` 出发，给出 `Var(x̂_clay)` 的表达式（含 H、W、Σ）。
- **5.2 条件数与权重敏感度**：定义 `κ(H)`、`gain index`；解释为什么 EM 行 clay 低、其他矿物高会导致负增益。
- **5.3 Fusion gain index**：
  ```
  G_{S→S∪m} = 1 - Var_clay(S∪m) / Var_clay(S)
  ```
  G>0 表示加入模态 m 有用；G<0 表示有害。
- **5.4 预测 vs 观测**：用现有实验的 clay 方差/误差验证 G 的符号与排序；图 4。
- **写作要求**：这是“理论贡献”，不要只给公式；要给出可操作判据（例如 κ 超过多少、EM 权重低于多少时不要加）。

### 6 Experiments（900 词，表 3）

- 6.1 消融：γ、γ+TIR、γ+EM、all。
- 6.2 退化：EMI×5/×20、TIR×5、γ×5、EMI+TIR。
- 6.3 温度：−60…+80 °C。
- 6.4 跨域：Wyoming-like 变换、direct vs CORAL。
- 6.5 H 扰动：±5…30%。
- 6.6 分辨率/种子：50…800 m、20 seeds。
- 6.7 基线：6 种方法。
- 表 3：实验矩阵（目的、变量、指标、重复数）。

### 7 Results（2200 词）

每个小节统一四步：**问题 → 设置 → 数字 → 解释/局限**。

- **7.1 主融合**：Clay 0.458、R 0.693、P 0.165、F1 0.267、P_mean 0.008；图 5 地图+不确定度。
- **7.2 消融与 gain**：γ 0.342/0.325、γ+TIR 0.392/0.339、γ+EM 0.351/0.191、all 0.458/0.267；表 4；图 6。
- **7.3 退化**：正常 0.693、EMI 失效 0.976、TIR 0.433、γ 0.602；解释“EM 负增益”而不是“优雅退化”；表 5。
- **7.4 温度**：−60 0.352、25 0.690、80 0.348；图 7。
- **7.5 跨域**：direct 0.692、CORAL 0.689；gap 0.08%→0.17%；说明 CORAL 对逐通道缩放无效。
- **7.6 H 稳健性/基线**：±30% 0.659±0.228；baselines 表 6；ours 最高 clay/最平滑，但 F1 不是最高。
- **7.7 不确定度校准**：覆盖率、reliability、重标定前后；表 7/图 8。
- **7.8 分辨率/种子**：50→800 m R 0.693→0.759；20 seeds 0.6933±0.0001；图 9。

### 8 Discussion（1300 词）

- **8.1 何时融合有用**：G>0 的条件；H 条件数、模态误差、目标定义。
- **8.2 为什么 EM 误配**：原始 Ω·m 线性混合 + 五矿物响应 → clay 被错误归因；建议 log10(ρ)+clay-only。
- **8.3 指标含义**：proxy recall 不是地质精度；precision/F1 必须一起报；coverage 不是 detection rate。
- **8.4 局限**：TIR/EM 合成、两个 clay 真值、无独立 GT、无硬件、深度模型重复地表模态。
- **8.5 对后续研究的建议**：单一真值场、log-EM、不确定度校准、真实多模态数据。

### 9 Conclusion（300 词）

4 条：
1. 统一基准下，三模态不优于 γ+TIR；
2. +104% 是 H 混用伪迹；
3. fusion gain index 可预测模态是否有用；
4. 呼吁报告完整指标与明确目标。

### Reproducibility / Data availability（250 词）

- 代码：`code/`，24 个脚本，`run_all.py`；
- 数据：真实伽马来源/DOI（待补）、合成配方、seed；
- 环境：Python 3.10、GDAL、scipy；
- 运行时间：主融合 ~10 s（CPU），深度 ~?；
- 限制：原始 CSV 受 USGS 许可约束，提供派生网格与脚本。

---

## 4. 旧稿 → 新稿映射

| 旧稿 | 新稿 | 处理 |
|---|---|---|
| Abstract / Highlights | 新 Abstract / Highlights | 重写，删 +104%、65.26%、AI、edge |
| 1.1–1.2 | 1 P1–P2；2.1 | 保留背景，压缩 |
| 1.3 | 1 P3；2.4 | 改写成“三个失效模式” |
| 1.4 | 1 P5 | 四条贡献重写 |
| 2.1 | 3.1；4.1 | 保留传感器描述，删“已实现”语气 |
| 2.2 三级退化 | 删 | 未实现 |
| 2.3 Jetson | 删 | 未实现 |
| 3.1 | 4.1–4.2 | 保留公式，补可辨识性 |
| 3.2 | 4.5 | 改成质量权重，明确方向 |
| 3.3 | 4.4 | 保留，补局限 |
| 4 AI 残差 | 删 / Future work | 无代码 |
| 5.1 | 3.1–3.4 | 改数据出处，补两个真值 |
| 5.2 | 3.6 | 统一指标 |
| 5.3 | 4.6 | 基线重写 |
| 6.1 | 7.2 | 用统一 H 重算 |
| 6.2 | 7.3 | 加“EM 负增益”解释 |
| 6.3 | 7.1/4.4 | 保留深度，补局限 |
| 6.4 | 7.5 | 重算 CORAL |
| 6.5 | 7.4 | 删 edge，保留温度 |
| 6.6 | 7.6 | 重算基线 |
| 6.7 | 7.7/9 | 改成 mean proxy recall + F1 |
| 7.1 | 8.1 | 保留 |
| 7.2 | 8.4 | 扩展 limitations |
| 8 | 9 | 重写 |

---

## 5. 图表清单

| 编号 | 内容 | 来源 |
|---|---|---|
| 图 1 | 真实伽马 + 合成 TIR/EM + proxy | `fig_data.png` |
| 图 2 | Benchmark 协议（固定 H/掩膜/指标） | 新画 |
| 图 3 | 方法流程（WLS→Kalman→depth） | `fig_method.png` |
| 图 4 | Fusion gain index 预测 vs 观测 | 新画 |
| 图 5 | 主结果：5 矿物 + 不确定度 | `fig_results.png` / `kf_fusion_final.png` |
| 图 6 | 消融：Clay/F1/gain | `ablation.png` |
| 图 7 | 退化 + 温度 | `validation.png` + 新画 |
| 图 8 | 不确定度校准 | 新画 |
| 图 9 | 分辨率/种子/H 稳健性 | `sensitivity.png` + 新画 |
| 表 1 | 数据与有效像元 | 新表 |
| 表 2 | 指标定义 | 新表 |
| 表 3 | 实验矩阵 | 新表 |
| 表 4 | 消融 | `ablation.csv` |
| 表 5 | 退化/温度 | `validation.csv` |
| 表 6 | 基线 | `baselines.csv` |
| 表 7 | 不确定度校准 | 新表 |

---

## 6. 8 周写作顺序

| 周 | 任务 |
|---|---|
| 1 | 冻结标题/摘要/贡献；把 `RESULTS.md` 变成表 4–6 |
| 2 | 写 3 Data & Benchmark；表 1–2 |
| 3 | 写 4 Methods；图 3 |
| 4 | 写 5 Identifiability；图 4；补推导 |
| 5 | 写 7 Results；图 5–9；表 7 校准 |
| 6 | 写 2 Related Work；补 35–45 篇文献 |
| 7 | 写 1 Intro/8 Discussion/9 Conclusion；删旧节 |
| 8 | 英文润色、Cover letter、Code/Data statement、投稿 |

---

## 7. 必须删掉 / 必须补上

### 删掉

- Section 4（AI 残差、1D-CNN、INT8、<300 KB）
- 2.2 三级退化、2.3 Jetson、<200 ms
- 状态向量里的 drift/env（代码没有）
- +104%、65.26% 作为 detection rate、CORAL 5.22%→0.27%
- “Colorado Mineral Belt”
- “13 experiments”除非逐条映射

### 补上

- Related Work（35–45 篇）
- fusion gain index 推导
- 不确定度校准
- gamma-only 真实数据实验
- 统计检验/CI
- 图表、参考文献、Code/Data availability
- Limitations（合成、proxy、无硬件、深度模型）

---

## 8. 审稿人问题预演

1. **“Why is this not just a negative result?”** → 因为给了可计算的 gain index + 可复用协议 + 修正建议。
2. **“Synthetic TIR/EM?”** → 明确声明；主结论不依赖“合成数据代表真实”，而依赖“协议可复现 + 负结果可解释”。
3. **“Why two clay truths?”** → 这是原数据的结构性问题，本文把它作为审计对象；建议后续用单一真值场。
4. **“Metric definition?”** → 表 2 固定；同时报 recall/precision/F1/IoU。
5. **“Novelty vs Kalman fusion?”** → 不是新滤波，而是可辨识性判据 + 基准 + 审计。
6. **“Why JSTARS/C&G?”** → 遥感方法/地学计算与可复现性。

---

## 9. 下一步

1. 确认主投 **JSTARS** 还是 **C&G**（决定模板与图数）。
2. 确认是否补 **fusion gain 推导 + 不确定度校准**（不需要硬件，约 2 周）。
3. 我把本提纲落成 **Word 骨架**（标题/小节/图表占位/TODO），你直接在 Word 里填正文。


