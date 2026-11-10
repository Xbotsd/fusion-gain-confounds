# Continuity check against the shared conversation record

Shared link: <https://chat.deepseek.com/share/tyx1zoi0krktr12w6i>

## Access limitation (stated honestly)

The share page is a JavaScript single-page app. A non-browser fetch returns only
the HTML shell plus a **256-character** `og:description` preview of the first
reply. No API endpoint exposes the full transcript without a browser session.
The check below is therefore based on (a) that preview and (b) this repository's
own audit trail of the original manuscript *A Unified Kalman Framework with
Environment-Aware Adaptation*, which is the same lineage. For a line-by-line
comparison the full text of the conversation must be pasted here.

## What the preview says the conversation was about

> 技术方案评审与补强：野外/无人机载多模态矿产探测与边缘智能解译体系，
> 主线：多物理场感知 → MCU 级边缘 AI → 卡尔曼统一融合 → 花岗岩干扰补偿 →
> 三维地质建模 → 低功耗离线集成。伽马、电磁、热红外三者互补；AI 解谱放
> MCU 端；卡尔曼滤波统一稳[定]…

## Element-by-element continuity

| 对话记录中的要素 | 本仓库状态 | 证据 |
|---|---|---|
| 多物理场感知（伽马/电磁/热红外互补） | **已实现**：10 通道观测（K, eU, eTh + TIR×4 + EM×3） | `common.py`, `run_fusion.py` |
| 伽马数据 | **真实**：USGS Ivanpah–Clark Mountain 航测 | `raw/K.gxf` 等，`DATA_PROVENANCE.md` |
| TIR / EM 传感 | **合成**（USGS splib07 端元；Wisconsin AEM 层统计） | `prepare_tir.py`, `prepare_em.py` |
| 卡尔曼统一融合 | **已实现并强化**：WLS + 空间 Kalman + 40 层深度 Kalman；修正 EM 后 F1 0.267→0.498 | `run_fusion.py`, `run_depth.py`, `EM_FIX.md` |
| 三维地质建模 | **已实现（合成外推）**：40 层 0–600 m 丰度体 | `depth_kalman_3d.npy` |
| 环境自适应（f(T, RH)） | **部分实现**：真实 T/RH 网格质量权重；振动/EMI 强度未测 | `run_environment.py` |
| MCU 级边缘 AI（1-D CNN, INT8, <300 KB） | **未实现**（无 torch/tf/onnx 代码、无模型、无基准） | `PAPER_VS_IMPLEMENTATION.md` L12 |
| Jetson/<200 ms 离线部署 | **未实现/未测量** | `PAPER_VS_IMPLEMENTATION.md` L13 |
| 花岗岩干扰补偿 | **零痕迹**：全库 grep 无 `granite/花岗岩` 匹配 | 本次检查 |
| 低功耗离线集成 | **未实现**（无硬件、无功耗测量） | `GAP_AUDIT.md` |
| 三级退化规则引擎 | **未按描述实现**：现有的是质量降权 + 通道剔除 | `PAPER_VS_IMPLEMENTATION.md` L14 |

**结论：延续性成立。** 本项目是该对话研究路线的**审计—基准—修正**延续：
保留了模态设计与卡尔曼主线并做出可复现结果；不可实现的边缘 AI/硬件
部分被明确记录为放弃，而不是保留为无证据声明。

## Number-by-number consistency

| 对话记录/原稿数字 | 本仓库实测 | 判定 |
|---|---|---|
| 三模态融合 +104 %（0.198→0.403） | 不复现；来自两套不兼容 H 矩阵混用 | **已撤销**（`MODEL_AUDIT.md`） |
| 检出率 65.26 % | 指标重定义：legacy 平均 proxy recall 65.94 %；修正 EM 后 **83.3 %** | **已修正** |
| CORAL 域差 5.22 %→0.27 % | 重算：0.08 %（直接）/0.17 %（CORAL）；修正 EM 下 CORAL 为**负收益**（0.858→0.799） | **已修正** |
| −60…+80 °C 稳定 | 仅仿真；legacy 温度族 recall 0.476，修正 EM 后 **0.912** | **范围不变，数值更新** |
| 数据：USGS Colorado Mineral Belt, 2023, 28,472 line-km | **原稿错误**：实际为 Ivanpah（NV–CA），2019-12→2020-03 | **已纠正**（`DATA_PROVENANCE.md` §1） |
| 5 矿物（石英/长石/黏土/方解石/白云石），黏土为目标 | 一致 | `common.py` |
| 13 项系统实验 | 清洗后为 8 个脚本族 + 变体/敏感性/独立验证，共 71 项产物 | **口径更新** |

## Dataset consistency verification (current state)

| 检查 | 结果 |
|---|---|
| 测区身份 | 35°N/115°W，Ivanpah–Clark Mountain，NV–CA（坐标证据无歧义） |
| 时间 | 2019-12-13 → 2020-03-21，47 架次，631 条测线 |
| 样本 | 295,943 行 @1 Hz；50 m 网格 1772×1075；有效像元 66.44 % |
| CSV↔GXF 交叉验证 | 校正通道中位数一致到三位小数（K 3.23/3.24，eU 6.695/6.693，eTh 5.816/5.812） |
| 完整性 | `pipeline_validation.json` **71/71 PASS** |
| 清单 | `data_manifest.json` 6,701 文件 / 11.24 GB，SHA-256 |
| 外部对照 | USGS SIM 3206 基质检查（Kruskal p<0.001，定性） |

**最大的数据集分歧**（必须如实报告）：对话记录暗示真实三模态传感；实际
数据集中只有伽马是真实的，TIR/EM 是文档化合成。这不是数据损坏，而是
数据获取限制，已在 `REAL_DATA_SEARCH.md` 记录（无同区 AEM；ASTER/ECOSTRESS
需 Earthdata 凭据）。

## Actions taken by this continuation

1. 纠正测区标签（Colorado→Ivanpah）与全部数字口径；
2. 撤销 +104 %、65.26 %、CORAL 5.22→0.27 % 三个无证据声明；
3. 把“融合是否有效”变成可检验问题，并找到根因（EM 响应误配）；
4. 修正 EM（log10 + clay-only）后给出正结果：F1 0.498，ΔF1 +0.167
   [0.146, 0.188]（200/200 block bootstrap 胜）；
5. 增加独立地质对照、阈值敏感性、结构化 H 扰动、多次重复平均；
6. 未实现模块（MCU AI、花岗岩补偿、硬件）保留为明确的未做事项，
   不进入论文声明。

## If a full line-by-line check is needed

Paste the conversation text (or export it) into this session; the element table
above will then be extended message by message.

