# 发表策略：无硬件、无团队、无预算、仅 USGS 数据

## 结论

**IJEM（International Journal of Extreme Manufacturing）在当前条件下不可行，建议立即换刊。**

这不是“再补一点实验”能解决的问题。IJEM 的 *Measurements and systems* 分支要求的是**测量系统/装备本身**的贡献：硬件、计量标定、环境试验、不确定度预算。没有硬件，就没有 E1–E12 的任何一项；没有团队和预算，6 个月内也搭不起来。用纯 USGS 数据 + 合成 TIR/EM 投 IJEM，desk reject 的概率接近确定。

## 为什么不可行（硬门槛）

| IJEM 要求 | 当前条件 | 结论 |
|---|---|---|
| 极端环境下的测量系统/装备 | 无硬件，只有算法与 USGS 栅格 | 不满足 |
| 计量标定与不确定度预算 | 无 pads/黑体/标准环，无实测 | 不满足 |
| 高低温/振动/EMI 实验 | 无环境舱/振动台/暗室 | 不满足 |
| “significant advance” | WLS+Kalman 成熟方法组合 | 不足 |
| 系统级制造/集成创新 | 无结构、无 PCB、无固件 | 不满足 |

即使写成 Review/Perspective，IJEM 的综述通常是 invited/high-profile，第一作者无硬件工作很难被接受；不作为主方案。

---

## 推荐方案：把现有工作改成“可复现基准 + 方法审计”论文

**一句话**：不假装做硬件系统，而是回答一个真实、可复现、对社区有价值的问题——

> **“多模态融合在航空矿产勘探中到底什么时候有用？我们用真实 USGS 伽马数据 + 物理一致的合成 TIR/EM，建立统一基准，发现常被忽略的 H 矩阵混用、合成数据循环依赖和指标口径问题，并给出负结果与修正建议。”**

这不是“失败结果”，而是 **benchmark / reproducibility / methods audit**，在方法学期刊中是成立的贡献。

### 题目（三选一）

1. **When does multi-modal fusion help airborne mineral exploration? A reproducible benchmark and audit**
2. **A reproducible benchmark for multi-modal mineral exploration: response-matrix consistency, synthetic-data circularity and metric definitions**
3. **Beyond a single modality: an open benchmark and negative-result analysis for gamma–TIR–EM fusion**

首选 1：问题清晰，审稿人一眼知道贡献不是“找矿”。

### 摘要草案（约 220 词）

> Multi-modal fusion is widely proposed for mineral exploration, but reported gains are difficult to compare because studies use different response matrices, synthetic data recipes and metric definitions. We present a reproducible benchmark built on the real USGS airborne radiometric survey of the Ivanpah–Clark Mountain area (NV–CA, 2019–2020), with physically informed synthetic TIR and EM modalities generated from documented endmembers and AEM statistics. The benchmark fixes one response matrix, one valid-pixel mask and one contingency-table metric, and then varies modality set, sensor degradation, temperature, domain shift, H perturbation, resolution and random seed. Legacy tri-modal fusion fails because EM uses raw resistivity with five mineral responses; replacing it with log10 resistivity and a clay-only response raises F1 from 0.267 to 0.498 and AP from 0.126 to 0.513, significantly above the independent and GLS baselines. The widely quoted +104 % fusion gain remains a matrix artefact. We release the code, data recipe, trained-free pipeline and audit scripts, and recommend reporting recall, precision and F1 together with an explicit statement of the evaluation target.

### 四条贡献

1. **可复现基准**：真实伽马 + 文档化合成 TIR/EM + 固定 H + 固定指标 + 固定有效像元掩膜；一键复现。
2. **方法审计**：两套 H 混用、两个 clay 真值、指标口径混用、自适应权重方向颠倒——逐条量化。
3. **负结果**：三模态不优于 gamma+TIR；EM 误配反而有害；CORAL 对逐通道缩放无效；温度是主退化轴。
4. **修正建议**：EM 应用 log10(ρ) + clay-only 响应；合成数据应由单一真值场生成；报告 recall/precision/F1 与目标定义。

### 结构（7000–8000 词，7 图，4 表）

| 章节 | 内容 |
|---|---|
| 1 Introduction | 多模态融合的承诺 vs 不可比的结果；本文问题 |
| 2 Data and benchmark design | USGS Ivanpah 真实伽马；TIR/EM 合成配方；有效掩膜；指标定义 |
| 3 Methods | WLS + Kalman；质量权重；深度递归；基线 |
| 4 Audit | H 混用、真值不一致、指标混用、权重方向 |
| 5 Experiments | 消融、退化、温度、跨域、H 扰动、分辨率、多 seed |
| 6 Results and discussion | 负结果；何时融合有用；修正建议 |
| 7 Reproducibility | 代码/数据/环境；运行时间；限制 |
| 8 Conclusion | 4 条 |

### 图

1. 数据与真值场（真实伽马 / 合成 TIR / 合成 EM / proxy）。
2. 基准流程与固定 H/指标。
3. 消融：Clay、F1、梯度、不确定度。
4. 退化与温度。
5. H 混用审计（A vs B）。
6. 真值不一致（TIR clay vs EM clay）。
7. 分辨率/种子/权重诊断。

---

## 目标期刊（按匹配度）

| 期刊 | 匹配点 | 风险 | 备注 |
|---|---|---|---|
| **Computers & Geosciences** | 可复现方法/软件/benchmark | 要求代码质量、文档、测试 | 首选；订阅制，无强制 APC |
| **IEEE JSTARS** | 遥感方法、真实 gamma、合成辅助 | 要求遥感新意 | 次选；IEEE 模板 |
| **Remote Sensing (MDPI)** | 快速、接受方法/负结果 | APC 约 2600 CHF；声誉一般 | 时间紧的备选 |
| **Earth Science Informatics** | 数据/工作流/可复现 | 影响因子较低 | 稳 |
| **IEEE Access** | 快速、 broad | APC；声望一般 | 保底 |
| **Ore Geology Reviews** | 矿产/蚀变案例 | 需要地质发现，不适合负结果 | 不推荐 |

**推荐顺序**：Computers & Geosciences → JSTARS → Remote Sensing → Earth Science Informatics。

---

## 8 周改写计划

| 周 | 任务 |
|---|---|
| 1 | 冻结题目/摘要/贡献；把 `docs/RESULTS.md` 变成论文结果表 |
| 2 | 重画 7 张图；统一图注与指标定义 |
| 3 | 写 Data & benchmark、Methods（复用 `docs/METHODS.md`） |
| 4 | 写 Audit（复用 `docs/MODEL_AUDIT.md`） |
| 5 | 写 Experiments/Results（复用 JSON/CSV） |
| 6 | 写 Introduction/Discussion/Conclusion；补 30–40 篇参考文献 |
| 7 | 代码清理、README、复现脚本、环境锁定；英文润色 |
| 8 | 投稿包：cover letter、highlights、graphical abstract、supplementary |

不需要新实验；需要的是**英文写作、文献、图件和代码打包**。

---

## 如果 IJEM 是硬性毕业/考核指标

必须和导师/学院沟通换刊。用 6 个月硬凑硬件+环境试验的风险远高于换一篇合适的 SCI。若指标只要求“SCI 论文”，上述四本都满足；若要求中科院分区，需按单位目录确认（C&G/JSTARS 通常 Q1/Q2，Remote Sensing Q2）。

---

## 现在就能做的三件事

1. 确认硬约束：**必须 SCI？必须几区？截止时间？** 这决定选 C&G 还是 Remote Sensing。
2. 确认是否接受“负结果/benchmark”叙事；如果不接受，就需要补真实 TIR/EM 或硬件，另当别论。
3. 我可以直接开始写 **IJEM 版以外的英文稿**：先出 Title/Abstract/Introduction，再按 C&G 或 JSTARS 模板搭全文。
