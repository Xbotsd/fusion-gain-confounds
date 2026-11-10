# IJEM 路线 A：极端环境多模态测量系统

> 目标期刊：*International Journal of Extreme Manufacturing*（IOP，JCR Q1，制造/测量领域顶刊）
> 论文类型：Paper（原创研究）
> 核心定位：**不是“矿产勘探算法”，而是“能在 −60 ~ +80 °C、强振动、强 EMI 下工作的多模态测量节点 + 计量/不确定度体系 + 容错融合”**。
> 矿产资源只作为应用场景（demo），标题与摘要的主角是“测量系统”。

---

## 1. 一句话卖点（IJEM 版）

> 一个可现场部署的极端环境多模态测量节点，首次把伽马能谱、8–14 µm 热红外、多频电磁与 IMU/GNSS 在硬件层同步，在 −60 ~ +80 °C 下完成温度相关的通道标定与不确定度传播，并用环境质量加权的卡尔曼融合在传感器退化时保持可用输出。

三个必须写进 introduction 的“新”：

1. **系统级集成**：四类传感器 + FPGA 同步 + 边缘计算 + 增材制造轻量化/热管理壳体，整体可在极端环境连续工作。
2. **计量级标定**：不是“跑个算法”，而是给出每个模态的温度系数、漂移、噪声、串扰和**不确定度预算**，并传递到最终丰度。
3. **环境感知容错融合**：用可观测的质量因子（温度、湿度、振动、EMI、通道噪声）动态降权，传感器失效时输出不崩，并给出不确定度。

---

## 2. 题目与摘要草案

### 题目（三选一）

1. **A ruggedized, environment-aware multi-modal measurement system for subsurface material characterization in extreme environments**
2. **An extreme-environment multi-sensor node with traceable calibration and fault-tolerant fusion for field material sensing**
3. **Thermal–EMI–vibration co-designed multi-modal sensing system for reliable subsurface measurement from −60 to +80 °C**

首选 1：既有“系统”，又有“测量”，避免“mineral exploration”触发 scope 质疑。

### 摘要草案（约 220 词）

> Reliable subsurface material characterization in extreme environments is limited by sensor drift, detector degradation, EMI and the absence of traceable calibration. We present a ruggedized, edge-deployed multi-modal measurement system that integrates gamma-ray spectrometry, 8–14 µm thermal infrared sensing, multi-frequency electromagnetic induction, and IMU/GNSS on a single synchronized platform. The node uses an FPGA trigger (jitter < 1 ms), a thermally managed additively manufactured housing, and an embedded quality monitor that estimates per-channel noise, temperature and EMI stress. A temperature-dependent calibration transfers laboratory reference artifacts to field conditions, and a weighted least-squares plus Kalman estimator propagates the resulting uncertainty into five material abundances. The system is characterized in a climate chamber from −60 to +80 °C, on a vibration table, and in an EMI chamber; calibration repeatability, drift, cross-talk and detection limits are reported as a full uncertainty budget. Fault-injection tests show that the estimator down-weights degraded channels and maintains a bounded output, while full-image inference runs on the edge node at < X W and < Y ms. A field trial at a known geological site demonstrates end-to-end operation. The contribution is a measurement-system architecture and metrology framework, not a geological discovery claim.

（X/Y 用实测填；不要写 Jetson/<200 ms，除非真的测到。）

---

## 3. 论文结构（建议 8000–9000 词，8–10 图，4 表）

| 章节 | 内容 | 字数 | 图/表 |
|---|---|---:|---|
| 1 Introduction | 极端环境测量需求；单模态局限；为什么现有系统不够；本文贡献 4 条 | 1200 | — |
| 2 System architecture | 传感器头、FPGA 同步、边缘节点、供电/热/EMI、增材制造壳体 | 1800 | 图 1 系统框图；图 2 爆炸图/实物 |
| 3 Metrology and calibration | 伽马 pads/本底/宇宙射线；TIR 黑体；EM 标准环；IMU/GNSS 杆臂；温度系数；不确定度预算 | 1800 | 图 3 标定装置；表 1 传感器规格；表 2 不确定度预算 |
| 4 Fusion and fault tolerance | WLS + Kalman；质量因子；深度递归；失效检测；不确定度传播 | 1500 | 图 4 算法流程；公式 8–10 个 |
| 5 Experimental setup | 高低温舱、振动台、EMI 暗室、野外场地；测试矩阵 | 800 | 表 3 环境试验矩阵 |
| 6 Results | 温度、振动、EMI、漂移、故障注入、边缘延迟/功耗、野外 | 2200 | 图 5–9 |
| 7 Discussion | 与商用系统对比；制造可扩展性；局限 | 900 | 表 4 对比 |
| 8 Conclusion | 3–4 条结论 | 300 | — |

**图规划**

1. 系统总框图（四传感器 + FPGA + 边缘 + 电源/热）。
2. 传感器头与增材制造壳体爆炸图/实物照片。
3. 标定装置：伽马 pads、黑体、EM 标准环。
4. 融合与质量加权流程。
5. 温度扫描：增益/噪声/漂移/检测限。
6. 振动与 EMI 下的噪声/误码/漂移。
7. 故障注入：通道失效后的权重与输出。
8. 边缘延迟 vs 分辨率、功耗 vs 温度。
9. 野外试验路线与结果图。
10. （可选）不确定度预算瀑布图。

---

## 4. 实验矩阵（IJEM 审稿人最看重的部分）

| 编号 | 目的 | 方法/设备 | 关键指标 | 周期 | 当前状态 |
|---|---|---|---|---|---|
| E1 | 通道同步 | FPGA 触发 + 示波器 | 抖动 < 1 ms；时间戳一致性 | 1 周 | 未开始 |
| E2 | 伽马标定 | K/U/Th 校准 pads、本底、宇宙射线 | 能量分辨率、剥谱系数、计数率线性 | 3 周 | 未开始 |
| E3 | TIR 标定 | 黑体 0–100 °C、发射率参考板 | 辐射定标、NETD、镜头温度系数 | 3 周 | 未开始 |
| E4 | EM 标定 | 标准电导环/线圈、频率扫描 | 幅值/相位误差、温度漂移 | 3 周 | 未开始 |
| E5 | 温度试验 | 高低温舱 −60/−40/−20/0/25/50/70/80 °C | 增益、噪声、漂移、功耗、启动时间 | 4 周 | 未开始 |
| E6 | 振动试验 | 振动台 5–500 Hz，1–3 g | 共振点、噪声增量、结构完好 | 2 周 | 未开始 |
| E7 | EMI 试验 | 10 V/m，80 MHz–6 GHz | 噪声增量、误码、数据完整性 | 2 周 | 未开始 |
| E8 | 湿热/防尘 | 95% RH、IP67、温度循环 | 结露、密封、绝缘 | 2 周 | 未开始 |
| E9 | 长期漂移 | 24–72 h 连续 | 零点/增益漂移、Allan 方差 | 2 周 | 未开始 |
| E10 | 故障注入 | 断线/遮光/屏蔽/降采样 | 权重变化、输出误差、恢复时间 | 2 周 | 算法已做，硬件待做 |
| E11 | 边缘性能 | 节点实测 | 延迟、内存、功耗、温升 | 2 周 | 部分（CPU 7.7 s/帧） |
| E12 | 野外试验 | 已知地质场地，1–2 周 | 与地面/已知资料一致性 | 2 周 | 未开始 |

**最小可发表集**：E1 + E2/E3/E4（至少两个模态）+ E5 + E6 + E7 + E10 + E11 + E12。  
**理想集**：全部 12 项 + 与商用系统对比。

---

## 5. 6 个月时间表

| 月份 | 里程碑 | 交付物 |
|---|---|---|
| M1 | 需求冻结、BOM、结构/PCB 设计、采购 | 系统规格书、BOM、风险清单 |
| M2 | 传感器头装配、FPGA 同步、边缘节点点亮 | 台架系统、E1 报告 |
| M3 | 伽马/TIR/EM 标定、不确定度预算 | E2–E4 报告、表 2 |
| M4 | 高低温/振动/EMI/湿热 | E5–E8 报告、图 5–6 |
| M5 | 漂移、故障注入、边缘性能、硬件在环融合 | E9–E11 报告、图 7–8 |
| M6 | 野外试验、数据锁定、论文初稿 | E12 报告、完整 draft |
| M7–M8 | 补实验、审稿人预案、投稿 | IJEM 投稿包 |

**止损点（M2 末）**：如果硬件未点亮或环境舱/振动台/EMI 暗室无法排期，立即改投 JSTARS/Remote Sensing 的方法论文，不要把时间耗在 IJEM 上。

---

## 6. 硬件 BOM 与预算（量级，按国内采购估算）

| 项 | 规格 | 预算（万元） |
|---|---|---:|
| 伽马探测器 | CeBr3/NaI(Tl) + SiPM + 前置放大 | 4–12 |
| TIR | 8–14 µm 非制冷机芯/光谱仪 | 3–15 |
| EM | 多频线圈/商用 EM 传感器 | 3–10 |
| IMU/GNSS | 战术级 IMU + RTK | 1–3 |
| 边缘 | FPGA + Jetson/STM32H7 + PCB | 1–3 |
| 结构 | AlSi10Mg 增材制造 + 热设计 + EMI 屏蔽 | 2–5 |
| 标定 | pads/黑体/标准环（或外协） | 2–8 |
| 环境试验 | 高低温舱/振动/EMI（外协按天） | 3–10 |
| 合计 | — | **20–65 万元** |

不含人工、差旅、野外许可。

---

## 7. 当前资产怎么用、缺什么

| 现有 | 在 IJEM 论文中的角色 | 缺口 |
|---|---|---|
| `code/` 的 WLS + Kalman + 质量权重 | 第 4 章算法；可复现 | 必须换成硬件在环/实测数据重跑 |
| 真实伽马 CSV + K/eU/eTh 网格 | 算法预研、野外对比 | 不是系统实测；不能当主结果 |
| 合成 TIR/EM | 仅用于硬件前的算法调试 | IJEM 论文中只能放补充材料，不能当主证据 |
| `docs/MODEL_AUDIT.md` | 数据诚信/局限说明 | 可转为 supplementary |
| 无硬件、无标定、无环境舱 | — | 路线 A 的 80% 工作量 |

---

## 8. 审稿人问题库（提前准备）

1. **“This is remote sensing, not manufacturing.”**  
   答：贡献是极端环境测量节点、计量与不确定度体系、增材制造热/EMI 共设计；矿产只是应用。引言必须引用 IJEM 的 “Measurements and systems / extreme environment manufacturing and system” 文章。
2. **“What is new beyond integrating COTS sensors?”**  
   答：同步、热/EMI 共设计、温度相关标定、质量因子与不确定度传播、故障注入下的有界输出；给出与商用系统的定量对比。
3. **“Where is the uncertainty budget?”**  
   答：表 2 给出每个模态的 A/B 类不确定度、温度/振动/EMI 贡献、合成标准不确定度、扩展不确定度。
4. **“How do you separate sensor degradation from geology?”**  
   答：故障注入 + 独立质量通道 + 参考场地；不宣称地质发现。
5. **“Synthetic TIR/EM?”**  
   答：只用于硬件前算法调试；主结果全部来自硬件在环/实测。合成数据不进主图。
6. **“Statistical significance?”**  
   答：每个环境条件 ≥5 次重复，均值±标准差，配对检验；给出置信区间。
7. **“Calibration traceability?”**  
   答：pads/黑体/标准环的溯源证书；不确定度传递链。
8. **“Power/latency at −60/+80?”**  
   答：E5/E11 实测表；不要引用 Jetson  datasheet。
9. **“Field validation?”**  
   答：已知地质场地 + 与独立资料对比；只谈测量一致性，不谈找矿成功。
10. **“Why IJEM?”**  
    答：系统在极端环境下的测量能力、热/EMI/振动共设计、增材制造壳体、计量体系，符合 IJEM 的 Measurements and systems。

---

## 9. 未来 14 天行动清单

1. 冻结题目、摘要、4 条贡献（本文件第 1–2 节）。
2. 确认实验室/外协资源：高低温舱、振动台、EMI 暗室、伽马 pads、黑体、EM 标准环。
3. 出 BOM 与结构/PCB 初版；确定增材制造材料与热设计。
4. 写 E1–E5 的详细测试规程（每项：目的、设备、步骤、指标、通过标准）。
5. 把现有 `run_validation.py` 改成“硬件在环”接口：输入改为实测通道，输出权重/不确定度。
6. 建 IJEM 版 figure 模板（9 张）+ 表 2 不确定度预算模板。
7. 选 2–3 篇 IJEM 近年 “Measurements and systems” 论文做对标（结构、图、审稿语言）。

---

## 10. 需要你确认的 3 件事

1. **硬件条件**：高低温舱、振动台、EMI 暗室、伽马 pads、黑体、EM 标准环，哪些已有、哪些要外协？
2. **团队与预算**：是否有 PCB/结构/固件工程师？20–65 万元的 BOM 预算是否可行？
3. **时间与场地**：IJEM 的 deadline 是哪天？野外试验能否在本国安排（还是只能继续用美国 USGS 数据）？

这三点决定路线 A 是“6 个月可落地”，还是“必须改成路线 B/换刊”。
