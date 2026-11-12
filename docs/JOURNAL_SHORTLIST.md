# 免费 SCI 期刊评估（核实版，2026-11-12）

**结论：首投 _Computers & Geosciences_（Elsevier）。** 它是本稿内容匹配度最高的
免费选项：订阅路径不收 APC，且 2026-11 我们已有公开仓库和 Zenodo DOI，上一版评估里
它唯一的大短板已经消失。备选顺序 **Earth Science Informatics → Journal of Applied
Geophysics**。**不要再把 IEEE JSTARS 或 IJAEOG 当免费选项**：两者已转为全 OA，强制
APC（见 §3）。

## 1. 口径与核实方法

- **“免费”指订阅路径**：hybrid 期刊不选 Gold OA 时不收文章处理费（APC）；只有
  作者主动选 OA 才付标价。全 OA 期刊（is_oa = true）则强制收费。
- 数据源与日期（2026-11-12）：
  - OpenAlex `sources` API：`is_oa`、`is_in_doaj`、`apc_usd`、2 年平均被引；
  - Crossref 近期文章（2025–2026）的 `license`：出现 CC 协议 = OA 文章；只有
    出版商 TDM/STM 协议 = 订阅文章，说明该刊仍可免费订阅发表；
  - 出版商 APC 页面在本机被 ScienceDirect 403 拦截，**最终金额以投稿系统报价为准**。
- JIF 与中科院分区为近年近似值（本机无法连 JCR/分区表），标“约”；投稿前按本单位
  认定口径复核。

## 2. 免费候选（已核实出版模式）

| 期刊 | 出版商 | 模式（核） | 免费路径 | 选 OA 时 APC | 2yr 被引* | JIF 约 | 中科院约 | 与本稿匹配 | 命中率 |
|---|---|---|---|---|---|---|---|---|---|
| **Computers & Geosciences** | Elsevier | hybrid（近期文章无 CC） | **订阅，0** | ~$4,010 | 5.97 | 4.0–4.8 | 地球科学 2 区 | 方法+软件+基准+复现，几乎量身 | 中 |
| **Earth Science Informatics** | Springer | hybrid（无 CC） | **订阅，0** | ~$3,890 | 6.94 | 2.6–3.2 | 3 区 | 地学数据/工作流/复现 | **高** |
| **Journal of Applied Geophysics** | Elsevier | hybrid（无 CC） | **订阅，0** | ~$3,180 | 2.70 | 2.0–2.6 | 3 区 | 应用地球物理、多源融合 | 中高 |
| Mathematical Geosciences | Springer | hybrid | 订阅，0 | ~$3,090 | 3.61 | 2.3–3.0 | 3 区 | 可识别性、估计理论 | 中 |
| Geophysical Prospecting | Wiley | hybrid | 订阅，0 | ~$4,150 | 2.03 | 1.9–2.4 | 3 区 | 地球物理方法 | 中 |
| Exploration Geophysics | Taylor & Francis | hybrid | 订阅，0 | 未标价 | 1.75 | 1.3–1.8 | 4 区 | 勘查地球物理、航空测量 | 中高 |
| International Journal of Remote Sensing | Taylor & Francis | hybrid | 订阅，0 | 未标价 | 3.37 | 2.8–3.4 | 3 区 | 遥感应用 | 中 |
| IEEE TGRS | IEEE | hybrid | 订阅，0，但**超页收费** | ~$2,645 | 9.38 | 7.0–8.0 | 1–2 区 | 要遥感新意；长文易触超页费 | 低 |

\* OpenAlex 2 年平均被引，2026-11-12 直接查询，可复核；与 JIF 不完全等价。

JCR 分区（估，按近年 JIF）：C&G、TGRS 为 Q1；ESI、JAG、Mathematical Geosciences、
Geophysical Prospecting、IJRS 为 Q2；Exploration Geophysics 为 Q3。若只要求
“SCI + Q2”，上表除 Exploration Geophysics 外都满足；若要求 Q1，免费选项实际只有
C&G（TGRS 的超页费不可控）。

**若单位硬性要求中科院 2 区**：免费选项里实际上只有 **C&G** 稳（TGRS 分区更高，但
超页费不可控）。ESI/JAG 是 3 区。

## 3. 已转全 OA、不再免费（核实）

| 期刊 | 证据 | APC |
|---|---|---|
| IEEE JSTARS | 2025 年文章全部 CC BY 4.0（Crossref） | ~$1,800 |
| IJAEOG | is_oa = true, 在 DOAJ；近期文章 CC BY / CC BY-NC-ND | ~$3,550 |
| Journal of Geophysics and Engineering | is_oa = true, 在 DOAJ | ~$1,550 |

其余强制 APC、不建议：Remote Sensing (MDPI)、IEEE Access、Scientific Reports、
PLOS ONE、Frontiers 系列、Solid Earth / Geoscientific Model Development (Copernicus)。

## 4. 推荐路线

```
C&G（首选，免费，2 区，最匹配）
  └─ 3 个月无进展 → Earth Science Informatics（稳，免费，3 区）
       └─ Journal of Applied Geophysics（保底，免费，3 区）
```

纯求稳、不追分区：`ESI → JAG → Exploration Geophysics`。

**不建议** Ore Geology Reviews、Natural Resources Research、Economic Geology：
它们要正向找矿/矿床结果，本稿会被判“没有地质结论”。
**不建议** 任何全 OA 遥感刊：APC 是硬成本，且审稿口味偏“应用新方法”，与本稿的
“审计 + 负结果”不合。

## 5. 针对 C&G 的投稿前清单

1. **软件可用性段落**：名称、版本、许可证、仓库、归档 DOI、运行环境、复现命令。
   已在正文 “Reproducibility and data availability” 中加入 `Software availability`
   段落（2026-11-12）。
2. **Highlights** ≤ 5 条、每条 ≤ 85 字符；**摘要** ≤ 250 词（现 247）；关键词 6 个。
   均已就绪（`docs/submission/`）。
3. **图表**：正文 9 表 6 图。C&G 无硬性页数，但建议把 Table 8（TES 敏感性）或
   Table 9（已发表实践）移入补充材料，正文留 7–8 表，审稿更顺。
4. **生成式 AI 声明**：Elsevier 要求披露。是否添加由作者决定（`docs/submission/README.md`
   第 41 行仍标为待定）。
5. **Cover letter**：已按 C&G 写（`docs/COVER_LETTER.md`），数字与当前产物一致。
6. **费用确认**：订阅路径无 APC；彩图印刷、超页可能另计，投稿系统会显示，选
   “subscription / no open access” 即可保持免费。

## 6. 证据链接（可复核）

- OpenAlex 期刊元数据（本次查询）：
  `https://api.openalex.org/sources?filter=issn:0098-3004|1865-0473|0926-9851|0812-3985|1874-8961|1939-1404|0143-1161|1569-8432`
- Crossref 近作许可（JSTARS 全 CC BY）：`https://api.crossref.org/journals/1939-1404/works?filter=from-pub-date:2025-01-01`
- Crossref 近作许可（C&G 无 CC，订阅）：`https://api.crossref.org/journals/0098-3004/works?filter=from-pub-date:2025-06-01`
- Crossref 近作许可（JAG 无 CC，订阅）：`https://api.crossref.org/journals/0926-9851/works?filter=from-pub-date:2025-06-01`
- Crossref 近作许可（ESI 无 CC，订阅）：`https://api.crossref.org/journals/1865-0473/works?filter=from-pub-date:2025-06-01`
- 本稿归档：`https://doi.org/10.5281/zenodo.24130421`；仓库：
  `https://github.com/Xbotsd/fusion-gain-confounds`
