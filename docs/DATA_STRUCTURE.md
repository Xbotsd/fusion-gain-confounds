# 数据结构与数据链（真实 ASTER 主线）

更新：2026-11-12。机器可读清单是 `processed/data_manifest.json`，完整性检查是
`processed/pipeline_validation.json`。本文件描述**当前主线**：11 通道观测 =
3 个真实伽马 + 5 个真实 ASTER L1T 发射率波段 + 3 层合成 EM。

v2 时代的 10 通道/合成 TIR/`run_fusion` 结构已归档在
`docs/archive/DATA_STRUCTURE_V2.md`，不属于投稿内容。

## 1. 目录树

```
A_MineralProspecting/
├─ raw/                          # 原始数据（只读，不入库）
│  ├─ K.gxf, eU.gxf, eTh.gxf     # 真实 USGS 伽马，1772×1075，50 m
│  ├─ TMI.gxf                    # 真实航磁（边缘实验用）
│  ├─ aster/<date>/              # ASTER L1T GeoTIFF + manifest.json（STAC id + SHA-256）
│  ├─ sim3206_database/          # USGS SIM 3206 地质图
│  ├─ ASCIIdata_splib07a/b/      # USGS 光谱库（TIR 端元）
│  └─ em/                        # AEM 层统计（仅用于合成 EM 配方）
├─ code/                         # 流水线脚本 + dev/ 一次性工具
├─ processed/                    # 立方体、结果 JSON/CSV、图
├─ docs/                         # 论文、来源、审计、投稿材料
└─ 根目录原始矢量/报告/CSV
```

## 2. 数据链（stage → script → 主要输出）

| Stage | Script | 主要输出 | 说明 |
|---|---|---|---|
| prepare | `prepare_gamma.py` | `gamma_cube.npy`, `clay_prior.npy`, `truth_abundance.npy`, `valid_mask.npy`, `ratio_*.npy` | 真实伽马与测区掩膜 |
| prepare | `prepare_tir_real.py` | `tir_cube_real.npy`, `analysis_mask.npy`, `tir_real.json` | 真实 ASTER：镶嵌、辐亮度、亮温、归一化 TES、物理门限 |
| prepare | `prepare_tir.py` | `tir_cube.npy` | splib07 **合成对照**，非主线 |
| prepare | `prepare_em.py` | `em_cube.npy` | **合成** EM（seed 12345，配方见 `DATA_PROVENANCE.md`） |
| prepare | `prepare_geology.py` | `geology_substrate.npy`, `geology_groups.json` | SIM 3206 基质栅格（独立目标） |
| main | `run_main.py` | `kf_main_abundance.npy`, `kf_main_uncertainty.npy`, `main_results.json`, `main_ablation.*`, `main_baselines.csv`, `main_maps.png` | 消融、基线、bootstrap、重复、校准、自相关 |
| controls | `run_tir_controls.py` | `tir_controls.json/csv` | 全零、高斯噪声、块/像元置换、ridge 对照 |
| controls | `run_tir_information.py` | `tir_information.json/csv` | 不用响应矩阵的信息检验 |
| controls | `run_geology_multiclass.py` | `geology_multiclass.json/csv/png` | 4 类基质、128 px 块 CV、20 次重复 |
| controls | `run_identifiability.py` | `identifiability.json/csv/png` | 秩、条件数、方差增益指数 |
| controls | `run_real_tir_robust.py` | `real_tir_robust.json/csv/png` | TES 假设与第二期次敏感性 |
| aux | `run_depth.py`, `run_depth_emfix.py` | `depth_kalman_3d*.npy`, `depth*.json`, `depth_*png` | 40 层深度 Kalman |
| aux | `run_published_baselines.py` | `published_baselines.*` | 5 个已发表单模态指数 |
| aux | `independent_validation.py` | `independent_validation.*` | 按基质分组、Kruskal-Wallis、AUC |
| aux | `uncertainty_calibration.py` | `calibration.*` | 覆盖率与可靠性（非预测区间） |
| aux | `autocorr_sample_size.py` | `autocorr.*` | 积分尺度、设计效应、N_eff |
| aux | `run_edge_ai.py`, `prepare_granite.py`, `run_granite_compensation.py`, `prepare_tmi.py` | `edge_ai.*`, `granite_*`, `tmi_grid.npy` | 边缘部署与花岗岩补偿实验 |
| legacy | 14 个脚本（见 `run_all.py`） | `ablation*.json`, `validation*.json`, `fusion.json`, `real_tir.json`, `em_fix*.json` 等 | 合成 TIR 参考支线，**论文不引用** |
| figures | `make_figures.py`, `make_graphical_abstract.py` | `fig_*.png`, `main_maps.png`, `graphical_abstract.png` | 论文图与图文摘要 |
| audit | `test_core.py`, `check_coverage.py`, `audit_data.py`, `validate_pipeline.py`, `report_large_files.py`, `build_manifest.py` | `pipeline_validation.json`, `output_yield.csv`, `large_files.json`, `data_manifest.json`, `docs/data_audit.json` | 36 断言、生产者覆盖、53 产物/22 不变量、SHA-256 清单 |

`python code/run_all.py all` 依次运行 prepare → main → controls → aux → figures →
audit；`run_all.py legacy` 单独复跑旧支线（可选）。

## 3. 观测、掩膜与响应矩阵

| 项 | 值 |
|---|---|
| 网格 | 1772 × 1075，50 m |
| 通道顺序 | K, eU, eTh \| ASTER b10–b14 \| EM layer 1–3 |
| ASTER 波段中心 | 8.291, 8.634, 9.075, 10.657, 11.289 µm |
| `valid_mask` | 放射性测区，1,265,683 px（66.4 % 网格） |
| `analysis_mask` | 测区 ∩ 五波段 ASTER 全覆盖，1,237,644 px（65.0 % 网格，97.8 % 测区） |
| 响应矩阵 `H` | 11 × 5；伽马块人工设定，TIR 行由 splib07 在 ASTER 波段内积分，EM 行为合成 |
| EM 模型 | 主线用 corrected（log10 Ω·m + clay-only 行）；legacy 行只用于消融对比 |
| 关闭模态 | 删除对应行；`H` 的列归一化只在**活动行**上进行（两个开关不变式由单测锁定） |

`clay_prior = 0.5·K + 0.3·(1−eTh) + 0.2·|eU−eTh|`（p2–p98 归一化，σ=15 px 平滑），
是伽马派生的**循环目标**；地质目标来自 SIM 3206，不依赖任何观测模态。

## 4. 数组 schema

| 文件 | 形状 | dtype | 单位/范围 | 说明 |
|---|---|---|---|---|
| `gamma_cube.npy` | (3, 1772, 1075) | float32 | K %, eU ppm, eTh ppm | 真实；无效像元 NaN |
| `tir_cube_real.npy` | (5, 1772, 1075) | float32 | 发射率 0.87–0.98 | 真实 ASTER；无效像元 NaN |
| `tir_cube.npy` | (200, 1772, 1075) | float32 | 0.65–0.99 | 合成对照 |
| `em_cube.npy` | (40, 1772, 1075) | float32 | 2.5–6526 Ω·m | 合成；全网格有限 |
| `clay_prior.npy` | (1772, 1075) | float32 | 0.30–0.67 | 伽马派生 proxy |
| `truth_abundance.npy` | (5, 1772, 1075) | float32 | 0–1，和为 1 | 合成 TIR 的真值场 |
| `valid_mask.npy` | (1772, 1075) | bool | 0/1 | 测区掩膜 |
| `analysis_mask.npy` | (1772, 1075) | bool | 0/1 | 测区 ∩ ASTER |
| `geology_substrate.npy` | (1772, 1075) | int16 | 0–8 | SIM 3206 基质分组 |
| `kf_main_abundance.npy` | (5, 1772, 1075) | float32 | 0–1，和为 1 | 主线融合丰度 |
| `kf_main_uncertainty.npy` | (5, 1772, 1075) | float32 | ≥0 | 滤波方差（不是置信区间） |
| `depth_kalman_3d.npy` | (40, 5, 1772, 1075) | float32 | 0–1，和为 1 | 40 层三维丰度 |
| `depth_uncertainty.npy` | (40,) | float32 | ≥0 | 每层平均方差 |
| `depth_kalman_3d_emfix.npy` | (40, 5, 1772, 1075) | float32 | 0–1，和为 1 | 修正 EM 三维丰度 |
| `depth_uncertainty_emfix.npy` | (40,) | float32 | ≥0 | 修正 EM 每层方差 |
| `tmi_grid.npy` | (1772, 1075) | float32 | nT | 航磁网格（边缘实验） |
| `granite_indicator.npy` | (1772, 1075) | float32 | 0–1 | 花岗岩补偿指示 |
| `ratio_K_eU/eTh.npy`, `ratio_eU_eTh.npy` | (1772, 1075) | float32 | 比值 | 伽马比值 |

## 5. JSON schema（主线）

### `main_results.json`
`definition`（掩膜、proxy、地质目标、正例、EM 说明）、`mask_pixels`、
`geology_pixels`, `geology_positive`, `tir_source`, `H_tir_real`（5×5）、
`ablation`（24 行：branch × em_model × config）、`baselines`（8 行）、
`bootstrap_f1`、`bootstrap_geo_auc`、`repeats`、`calibration`、`autocorr`、
`runtime_s`。

### `tir_controls.json`
`rows`（gamma、zeros、noise、block/pixel shuffle、ridge 的 F1 与 geological AUC 等）、
`r2_tir_on_gamma`、`note`。

### `tir_information.json`
`n_samples`, `block_px`, `n_folds`, `geology_positive_fraction`,
`raw_separability`, `rows`（每配置平衡准确率与 CI）、`summary`, `note`。

### `geology_multiclass.json`
`classes`, `per_class`, `chance`, `block_px`, `n_folds`, `n_repeats`, `summary`
（gain 与 CI）、`repeats`（20 条）、`note`。

### 其他
- `identifiability.json`：`lambda`, `branch`, `models`, `f1_reproduction_max_dev`,
  `sign_agreement_f1/geo`。
- `real_tir_robust.json`：`variants`（eps_max、去波段、第二期次）、`rows`,
  `bootstrap`。
- `tir_real.json`：`source`, `date`, `scene_files`, `bands_um`,
  `unit_coefficients`, `eps_max_assumed`, `coverage_*`, `bt/eps/t_surface`
  分位数、`corr_eps_with_tsurf`。
- `autocorr.json`：`cell_m`, `bootstrap_block_px/m`, `fields`（每场积分尺度、设计
  效应、N_eff）, `checks`, `edge_ai_block_ap`。
- `published_baselines.json`：`rows`（5 个指数）, `prevalence`, `note`。
- `independent_validation.json`：`source`, `doi`, `groups`, `rows`, `kruskal`,
  `felsic_vs_carbonate`, `binary_target`。
- `calibration.json`：`n`, `bias`, `rmse`, `mean_sigma`, `coverage_68/95`,
  `variance_scale`, `reliability`。
- `depth.json` / `depth_emfix.json`：`layers`, `depth_m`, `layer_mean`（40×5）,
  `uncertainty`, `runtime_s`。
- `geology_groups.json`：`source`, `doi`, `url`, `groups`, `pixels_on_survey`,
  `unmapped_on_survey`, `grid_geotransform`。
- `pipeline_validation.json`：`status`, `generated_at`, `grid`, `metric_recalc`,
  `metric_stored`, `yield`, `cross_checks`（22 条）, `checks`（53 条）。
- `data_manifest.json`：`generated_at`, `n_files`, `total_bytes`, `summary`
  （按 stage）, `files`（path/stage/size/sha256/schema）。

legacy 支线的 `fusion.json`、`validation.json`、`ablation.json` 等不在上述清单，
也不被 `validate_pipeline.py` 检查；需要时用 `run_all.py legacy` 生成。

## 6. 完整性规则

1. 所有空间数组共享 `(1772, 1075)` 网格；主线指标只在 `analysis_mask` 上计算。
2. `gamma_cube`、`tir_cube_real`、`tir_cube` 的无效像元为 NaN；载入时按列填中位数
   （EM 为有限值，不做填充）。
3. 丰度输出满足 `x ≥ 0`、`Σx = 1`；depth 每层同样满足闭包。
4. 预测正例定义为 `clay > 0.25` 且 clay 位于 top-2 矿物（`definition` 中固定）。
5. 每个文件在 `data_manifest.json` 有 SHA-256；清单在 `audit` 阶段最后重建。
6. `validate_pipeline.py` 校验 53 个产物、22 条不变量（含零/噪声/置换对照、
   bootstrap 一致性、ASTER 物理门限，以及从论文 Markdown 解析表 4–7、9 后与产物
   逐格比对）。
7. `check_coverage.py` 要求每个受检产物在 `run_all.py` 中有生产者，防止“有产物、
   无脚本”。
8. `test_core.py` 的 36 条断言锁定闭包、指标、EM 变换、两个开关不变式和 ASTER
   波段构造。

## 7. 大文件与产出率

- `report_large_files.py` → `large_files.json`：当前 7 个文件超过 200 MB，合计
  7.85 GB，全部是可重生成的 `.npy` 派生立方体；策略记录在
  `processed/large_files.json` 与 `docs/DATA_PROVENANCE.md`（不入仓库、不入
  Zenodo，用清单 SHA-256 验证复现）。
- `pipeline_validation.json` 的 `yield`：`grid_pixels`, `analysis_pixels`,
  `analysis_fraction`, `survey_pixels`, `aster_fraction_of_survey`,
  `predicted_positive_rate`, `artifact_rate`, `artifacts_present/expected`,
  `experiments`（ablation/baseline/bootstrap/multiclass 记录数）, `runtime_s`；
  同一组指标导出为 `processed/output_yield.csv`。

## 8. 命名约定

- `prepare_*`：原始 → 立方体/掩膜；
- `run_*`：实验与分析；
- `kf_main_*`：主线融合输出；`depth_*`：深度反演；
- `fig_*`, `main_maps.png`：论文图；
- `*_validation.json`：完整性检查；`*_manifest.json`：清单；
- `*_emfix`：修正 EM 模型的对应产物。
