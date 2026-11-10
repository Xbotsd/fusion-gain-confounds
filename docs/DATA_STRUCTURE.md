# 数据结构与数据链（v2）

本文件描述 `A_MineralProspecting` 的完整数据链：从原始 USGS 数据到最终论文图表，每个文件的形状、类型、单位、生成脚本和依赖关系。机器可读清单见 `processed/data_manifest.json`，完整性检查见 `processed/pipeline_validation.json`。

## 1. 目录树

```
A_MineralProspecting/
├─ raw/                         # 原始数据（只读）
│  ├─ K.gxf, eU.gxf, eTh.gxf    # 真实伽马，1772×1075，50 m
│  ├─ TMI.gxf                   # 航磁，未进入 10 通道观测
│  ├─ ASCIIdata_splib07a/b/     # USGS 光谱库（TIR 端元）
│  └─ em/                       # Wisconsin AEM / 挪威 AEM / Silverton AMT
├─ code/                        # 脚本 + requirements
├─ processed/                   # 中间产物、结果、图表
│  ├─ spectra/                  # 5 种矿物 TIR 端元
│  ├─ em/                       # AEM 层统计中间数组
│  ├─ *.npy                     # 立方体、掩膜、结果
│  ├─ *.json / *.csv            # 指标与记录
│  └─ fig_*.png, kf_*.png ...   # 图
├─ docs/                        # 方法、审计、结构、策略
└─ 根目录原始矢量/报告/CSV
```

## 2. 数据链（stage → script → output）

| Stage | Script | 主要输入 | 主要输出 | 状态 |
|---|---|---|---|---|
| 1 伽马 | `prepare_gamma.py` | `raw/K,eU,eTh.gxf` | `gamma_cube.npy`, `clay_prior.npy`, `truth_abundance.npy`, `valid_mask.npy`, `ratio_*.npy` | PASS |
| 2 TIR | `prepare_tir.py` | `gamma_cube`, `truth_abundance`, `processed/spectra` | `tir_cube.npy` | PASS |
| 3 EM | `prepare_em.py` | `clay_prior`, `processed/em_layer_*` | `em_cube.npy` | PASS |
| 3b ASU 端元 | `fetch_asu_spectra.py` + `run_asu_variant.py` | `raw/ASU_spectra/*.txt` | `asu_endmembers.npy`, `tir_cube_asu.npy`, `H_asu.npy`, `fusion_asu.json`, `ablation_asu.*`, `fig_asu_endmembers.png` | PASS |
| 3c V2 单真值场 | `run_v2.py` | 伽马、`clay_prior` | `processed/v2/*`（TIR/EM/H/ablation/fig） | PASS |
| 4b 不确定度校准 | `uncertainty_calibration.py` | `kf_*`、`clay_prior` | `calibration.json/csv/png` | PASS |
| 4c 优势分析 | `run_advantage.py` | 全部方法输出、掩膜 | `advantage.json/csv/png` | PASS |
| 4d 空间 bootstrap | `block_bootstrap.py` | 方法输出、掩膜 | `bootstrap.json/csv` | PASS |
| 4e EM 修正 | `run_em_fix.py` | 方法输出、log10 EM | `em_fix.json/csv/png` | PASS |
| 4f 结构扰动 | `structured_perturbation.py` | H、观测 | `structured_perturbation.json/csv/png` | PASS |
| 4g 独立地质 | `independent_validation.py` | SIM 3206、丰度 | `independent_validation.*`, `geology_substrate.npy` | PASS |
| 4h 阈值扫描 | `threshold_sensitivity.py` | 方法输出、proxy | `threshold_sensitivity.*`, `threshold_summary.json` | PASS |
| 4 融合 | `run_fusion.py` | 三立方体、掩膜、H | `kf_mineral_abundance.npy`, `kf_uncertainty.npy`, `wls_initial.npy`, `fusion.json`, `kf_fusion_final.png` | PASS |
| 5 深度 | `run_depth.py` | 三立方体、掩膜、EM 层深 | `depth_kalman_3d.npy`, `depth_uncertainty.npy`, `depth.json`, `depth_*.png` | PASS |
| 5b 修正深度 | `run_depth_emfix.py` | log10 EM、clay-only H | `depth_kalman_3d_emfix.npy`, `depth_emfix.json`, `depth_*_emfix.png` | PASS |
| 6 消融 | `run_ablation.py` | 三立方体、H、掩膜 | `ablation.csv/json/png` | PASS |
| 7 验证 | `run_validation.py` | 三立方体、H、掩膜 | `validation.csv/json/md/png` | PASS |
| 8 基线 | `run_baselines.py` | 三立方体、H、掩膜 | `baselines.csv/json/png` | PASS |
| 9 环境 | `run_environment.py` | CSV T/RH、三立方体 | `env_*.npy`, `environment.json/png` | PASS |
| 10 敏感性 | `run_sensitivity.py` | 三立方体、H | `sensitivity.json/png`, `resolution.csv` | PASS |
| 11 重复平均 | `run_repeats.py` | 三立方体、H | `repeats.json`, `repeat_mean_abundance.npy`, `repeat_std_abundance.npy` | PASS |
| 12 图 | `make_figures.py` | 结果 JSON/npy | `fig_data/method/results.png` | PASS |
| 13 审计 | `audit_data.py` | 原始/processed | `docs/data_audit.json`, `docs/model_audit.json` | PASS |
| 14 完整性 | `validate_pipeline.py` | 全部输出 | `pipeline_validation.json` | PASS |
| 15 清单 | `build_manifest.py` | 全部文件 | `data_manifest.json` | PASS |

## 3. 数组 schema

| 文件 | 形状 | dtype | 单位/范围 | 说明 |
|---|---|---|---|---|
| `gamma_cube.npy` | (3, 1772, 1075) | float32 | K %, eU ppm, eTh ppm | 真实；无效像元 NaN |
| `tir_cube.npy` | (200, 1772, 1075) | float32 | 发射率 0.65–0.99 | 合成；无效像元 NaN |
| `em_cube.npy` | (40, 1772, 1075) | float32 | 2.5–6526 Ω·m | 合成；全网格有限 |
| `asu_endmembers.npy` | (200, 5) | float32 | 0.5–1.0 | ASU 实测发射率，8–14 µm |
| `tir_cube_asu.npy` | (200, 1772, 1075) | float32 | 0.65–0.99 | ASU 端元生成的 TIR 变体 |
| `H_asu.npy` | (10, 5) | float64 | 响应矩阵 | ASU TIR 行的 H |
| `v2/truth_abundance_v2.npy` | (5, 1772, 1075) | float32 | 0–1，和为 1 | V2 单真值场 |
| `v2/tir_cube_v2.npy` | (200, 1772, 1075) | float32 | 0.65–0.99 | V2 TIR |
| `v2/em_cube_v2.npy` | (40, 1772, 1075) | float32 | 2.5–6526 Ω·m | V2 EM |
| `v2/H_v2.npy` | (10, 5) | float64 | 响应矩阵 | V2 H（EM clay-only log10） |
| `geology_substrate.npy` | (1772, 1075) | int16 | 0–8 | USGS SIM 3206 基质分组栅格 |
| `clay_prior.npy` | (1772, 1075) | float32 | 0.30–0.67 | 伽马派生蚀变 proxy |
| `truth_abundance.npy` | (5, 1772, 1075) | float32 | 0–1，和为 1 | TIR 生成用真值；无效像元 NaN |
| `valid_mask.npy` | (1772, 1075) | bool | 0/1 | 66.4% 有效测区 |
| `kf_mineral_abundance.npy` | (5, 1772, 1075) | float32 | 0–1，和为 1 | 主融合结果 |
| `kf_uncertainty.npy` | (5, 1772, 1075) | float32 | ≥0 | 前向滤波方差 |
| `wls_initial.npy` | (5, 1772, 1075) | float32 | 0–1 | Kalman 前 WLS |
| `depth_kalman_3d.npy` | (40, 5, 1772, 1075) | float32 | 0–1，和为 1 | 40 层三维丰度 |
| `depth_uncertainty.npy` | (40,) | float32 | ≥0 | 每层平均方差 |
| `depth_kalman_3d_emfix.npy` | (40, 5, 1772, 1075) | float32 | 0–1，和为 1 | 修正 EM 三维丰度 |
| `depth_uncertainty_emfix.npy` | (40,) | float32 | ≥0 | 修正 EM 每层方差 |
| `env_temperature.npy` | (1772, 1075) | float32 | °C | CSV 网格化 |
| `env_humidity.npy` | (1772, 1075) | float32 | % | CSV 网格化 |
| `env_count.npy` | (1772, 1075) | int32 | 样本数/格 | 网格化计数 |
| `ratio_K_eU/eTh, eU_eTh` | (1772, 1075) | float32 | 比值 | 伽马比值 |
| `repeat_mean_abundance.npy` | (5, 1772, 1075) | float32 | 0–1 | N 次重复平均 |
| `repeat_std_abundance.npy` | (5, 1772, 1075) | float32 | ≥0 | 重复标准差 |

## 4. JSON schema

### `fusion.json`
| key | type | 说明 |
|---|---|---|
| `grid` | [h,w] | 网格 |
| `valid_fraction` | float | 有效像元比例 |
| `weights` | [10] | 通道权重 |
| `clay_mean_full` | float | 全网格 clay 均值 |
| `clay_mean_valid` | float | 有效像元 clay 均值 |
| `spatial_gradient` | float | 空间梯度 |
| `mean_uncertainty` | float | 平均方差 |
| `proxy` | object | recall/precision/F1/IoU/positive_rate |
| `recovery` | object | 每矿物 RMSE/MAE/bias/r |
| `residual_rms` | object | 10 通道残差 |
| `runtime_s` | float | 运行时间 |

### `fusion_asu.json`
| key | type | 说明 |
|---|---|---|
| `endmember_source` | string | ASU 光谱库 |
| `ids` | object | 每个矿物的 ASU id |
| `proxy` | object | ASU 变体的 recall/precision/F1 |
| `main_proxy` | object | 主结果的指标 |
| `delta_recall`, `delta_f1` | float | 与主结果的差 |

### `bootstrap.json`
| key | type | 说明 |
|---|---|---|
| `n_rep` | int | 重采样次数 |
| `block` | [h,w] | 区块大小 |
| `point` | object | 点估计 F1 |
| `methods` | object | 每方法 bootstrap 均值/std/CI |
| `delta_ours_minus_independent` | object | 差值 CI 与胜率 |

### `em_fix.json`
| key | type | 说明 |
|---|---|---|
| `H_em_rows` | array | 修正后的 EM 行 |
| `rows` | array | 各方法 F1/AP/连通域 |
| `bootstrap` | object | ΔF1 CI 与胜率 |

### `structured_perturbation.json`
数组，每项 `{variant, clay, recall, precision, f1, gradient}`。

### `independent_validation.json`
| key | type | 说明 |
|---|---|---|
| `source`, `doi` | string | SIM 3206 |
| `rows` | array | 各基质 clay/quartz/calcite 均值 |
| `kruskal` | object | H/p |
| `felsic_vs_carbonate` | object | 单侧 p |

### `advantage.json`
| key | type | 说明 |
|---|---|---|
| `prevalence` | float | proxy 正例率 |
| `methods` | array | 每种方法的 F1/AP/mP/容差/连通域 |
| `qr_sweep` | array | 12 组 Q/R |
| `best_qr` | object | 最佳 Q/R |
| `noise` | array | 5%/10% 噪声下的 F1/AP 变化 |

### `calibration.json`
| key | type | 说明 |
|---|---|---|
| `n` | int | 有效像元数 |
| `bias`, `rmse`, `mean_sigma` | float | clay 误差统计 |
| `coverage_68/95` | float | 名义覆盖率 |
| `variance_scale` | float | 方差缩放因子 |
| `coverage_68/95_scaled` | float | 缩放后覆盖率 |
| `reliability` | array | 10 个分箱的 sigma/RMSE |

### `validation.json`
| key | type | 说明 |
|---|---|---|
| `definition` | object | 指标定义 |
| `family_recall` | object | 6 类场景平均 recall |
| `overall_recall` | float | 六类平均 |
| `overall_f1` | float | 六类平均 F1 |
| `scenarios` | array | 28 条场景记录 |
| `temperature` | array | 温度扫描 |
| `H_sensitivity` | array | H 扰动 |
| `degradation` | object | 退化场景 |
| `runtime_s` | float | 运行时间 |

### `validation_emfix.json`
与 `validation.json` 相同，使用修正 EM H 和 log10 EM。

### `depth_emfix.json`
与 `depth.json` 相同，使用修正 EM H；`layer_mean` 为 40×5。

### `ablation.json` / `baselines.json`
数组，每条形如 `{config/method, clay_mean, gradient, recall, precision, f1, ...}`。

### `sensitivity.json`
`multi_seed`（20 条）、`multi_seed_stats`、`resolution`（5 条）、`weighting`（2 条）。

### `environment.json`
`cells`, `temperature_range`, `humidity_range`, `scenarios`, `subsets`, `clay_diff_*`。

### `repeats.json`
`n_runs`, `noise_frac`, `runtime_s`, `baseline`, `runs`（N 条）, `stats`（mean/std/CI）, `mean_map`。

### `pipeline_validation.json`
`status`, `generated_at`, `grid`, `metric_recalc`, `metric_stored`, `metric_delta`, `yield`, `files`, `checks`。

### `data_manifest.json`
`generated_at`, `n_files`, `total_bytes`, `summary`（按 stage 计数）, `files`（path/stage/size/sha256/schema）。

## 5. 数据完整性规则

1. 所有空间数组共享同一网格 `(1772, 1075)`；`valid_mask` 为唯一评价掩膜。
2. `gamma_cube`、`tir_cube`、`truth_abundance` 在无效像元为 NaN；`load_cubes` 分别填中位数/0.5/100。
3. 丰度输出满足 `x >= 0`、`sum_i x_i = 1`（闭包）。
4. `depth_kalman_3d` 的每层同样满足闭包。
5. 所有指标只在 `valid_mask=True` 上计算；不得把 NoData 填充区计入。
6. `fusion.json` 的 `proxy` 必须与 `kf_mineral_abundance.npy` 重算结果一致（`validate_pipeline.py` 检查，容差 1e-3）。
7. 同名文件只保留最终版；旧版本已删除，见 `docs/CHANGELOG.md`。
8. 每个文件在 `data_manifest.json` 中有 SHA-256，可校验。

### 5.1 大文件策略

`report_large_files.py` 统计并写入 `processed/large_files.json`。当前有 7 个文件
超过 200 MB，合计 7.8 GB，全部是派生的 `.npy` 立方体：

| 规则 | 说明 |
|---|---|
| 本地保留 | 便于检查与重跑，`processed/` 下 200 MB 以内的文件全部保留 |
| 不上传 | 超过 200 MB 的 `.npy` 不进仓库、不进 Zenodo；它们由 `run_all.py` 从 `raw/` + 固定 seed 重新生成，`data_manifest.json` 的 SHA-256 用于验证复现 |
| 永不删除 | `raw/`、`processed/*.json`、`processed/*.csv`、`processed/*.png` |

2026-11-07 清理了一个 1.45 GB 的历史残留文件
`depth_kalman_3d.npy_emfix.npy`（旧版命名 bug 的产物，全库无引用，正确文件
`depth_kalman_3d_emfix.npy` 存在）。

## 6. 产出率（yield）定义

`validate_pipeline.py` 计算并写入 `pipeline_validation.json`；同一组指标也导出为
`processed/output_yield.csv`（metric/value/definition 三列）：

| 指标 | 定义 |
|---|---|
| `valid_fraction` | 有效像元 / 全网格（预期 0.664） |
| `abundance_finite_fraction_on_valid` | 有效像元中丰度有限的占比（预期 1.0） |
| `predicted_positive_rate` | clay>0.25 且 top-2 的像元比例 |
| `artifact_rate` | 实际存在且通过检查的产物 / 预期产物 |
| `runtime_s` | 主融合运行时间 |
| `valid_pixels_per_s` | 有效像元 / 运行时间 |
| `experiment_records` | 消融/验证/基线/敏感性记录数 |

## 7. 命名约定

- `prepare_*`：原始 → 立方体；
- `run_*`：实验/分析；
- `kf_*`：主融合输出；
- `depth_*`：深度反演；
- `fig_*`：论文图；
- `*_validation.json`：完整性检查；
- `*_manifest.json`：清单。
