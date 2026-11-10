# 高因子、免费、切合：现实选项与提升方案

## 先说结论

“**高因子 + 免费 + 好过 + 切合**”四者不可能同时成立。高因子期刊一定更挑；当前工作（无硬件、TIR/EM 合成、负结果）的**现实上限约 IF 5**，对应 **IEEE JSTARS**。  
IF 7–8 的 **IEEE TGRS** 可以冲，但必须补一个真正的理论贡献；IF >10 的 ISPRS/RSE 与本文 scope 不符，不建议。

## 免费（无强制 APC）的高因子候选

| 期刊 | IF 约 | APC | 切合度 | 难度 | 现实性 |
|---|---:|---|---|---|---|
| IEEE TGRS | 7–8 | 无（订阅制，可选 OA） | 高：遥感理论/方法 | 很高 | 需新增理论或真实多模态数据 |
| IEEE JSTARS | 4.5–5.5 | 无（订阅制，可选 OA） | 很高：应用遥感/方法/数据集 | 高 | **当前工作可冲** |
| Computers & Geosciences | 3.5–4.5 | 无 | 很高：方法/软件/benchmark | 中高 | 稳 |
| ISPRS J. Photogramm. | 10–12 | 无 | 中：摄影测量/遥感 | 极高 | 不建议 |
| Remote Sensing of Environment | 12–13 | 无 | 低：环境遥感 | 极高 | 不建议 |
| GIScience & Remote Sensing | 5–6 | 可能 APC | 中 | 高 | 需确认 APC |

## 推荐路线

**主投：IEEE JSTARS**（IF 约 5，免费，遥感应用/方法/数据集，和“USGS 真实数据 + 多模态融合 benchmark”最匹配）。

**保底：Computers & Geosciences**（IF 约 4，免费，方法/软件，审稿人更接受 benchmark/负结果）。

**冲刺：IEEE TGRS**（IF 约 7–8，免费，但需要理论创新；当前版本不够）。

## 如何把当前论文提升到 JSTARS 水平

当前版本是“负结果 + 审计”，JSTARS 审稿人会问“so what”。需要加一个**正面方法贡献**，不需要硬件：

### 1. 可辨识性/条件数分析（核心加分项）

对线性混合模型 `z = H a + v`，推导 clay 估计方差与 `H` 条件数、通道权重 `W`、噪声 `σ` 的关系：

```
Var(a_clay) ∝ [(H^T W H + λI)^-1 H^T W Σ W H (H^T W H + λI)^-1]_clay,clay
```

给出：
- 什么条件下多模态融合**必然**降低 clay 方差；
- 为什么当前 EM 行（clay 低电阻率、其他矿物高电阻率）会导致**负增益**；
- 一个可直接计算的 “fusion gain index”，用于判断某模态是否值得加入。

这把“负结果”升级为“**可解释的融合增益理论**”。

### 2. 不确定度校准（第二个加分项）

当前 `P` 是前向滤波方差，未校准。补：
- 经验覆盖率（68%/95%）；
- reliability diagram；
- 温度/退化下的校准误差；
- 一个简单的方差重标定（temperature scaling / isotonic），并报告校准前后。

这是遥感/地学方法论文的常见高分点。

### 3. 真实数据-only 验证

至少加一组**只用真实伽马**的实验：
- gamma-only 反演 + Kalman；
- 多尺度/分区；
- 与 USGS 地质/蚀变资料对比（不声称发现，只谈一致性）。

避免审稿人认为“全靠合成数据”。

### 4. Benchmark 协议与代码

- 固定 H、固定 mask、固定指标；
- 一键复现；
- 负结果与修正建议；
- 作为“可复用协议”而不是“失败报告”。

## 建议的 JSTARS 版标题/摘要角度

**Title**: *When does multi-modal fusion improve airborne mineral exploration? An identifiability analysis and reproducible benchmark*

**Abstract 逻辑**：
1. 多模态融合被广泛提倡，但增益不可比；
2. 提出可辨识性指标与统一 benchmark；
3. 在真实 USGS 伽马 + 物理合成 TIR/EM 上系统实验；
4. 发现 EM 误配导致负增益、温度是主退化轴、CORAL 对逐通道缩放无效；
5. 给出融合增益判据与修正建议；
6. 代码/数据公开。

这比“我们提出一个卡尔曼框架”更有新意，也更适合 JSTARS。

## 6 周提升计划（不需要硬件）

| 周 | 任务 |
|---|---|
| 1 | 推导 clay 方差/条件数/fusion gain index；写成 1 页 theory |
| 2 | 在现有数据上计算 gain index，验证与实验一致 |
| 3 | 不确定度校准：覆盖率、reliability、重标定 |
| 4 | 补 gamma-only 真实数据实验；重画 7 图 |
| 5 | 英文初稿（JSTARS 模板）；补 30–40 篇文献 |
| 6 | 代码打包、cover letter、投稿 |

## 风险

- JSTARS 仍可能认为“应用太窄/负结果为主”；因此**理论 + 校准**是必需，不是可选。
- 若 6 周内做不出可辨识性分析，退回 **C&G**，不要硬投 TGRS。
- TGRS 需要更强的理论或真实多模态数据；当前不建议首投。

## 需要你确认

1. 目标 IF 是 **>5** 还是 **>8**？>5 选 JSTARS；>8 需补理论且仍有风险。
2. 是否接受“理论推导 + 不确定度校准”这部分新增工作（不需要硬件）？
3. 截止时间？JSTARS 审稿 3–5 个月，C&G 2–4 个月。
