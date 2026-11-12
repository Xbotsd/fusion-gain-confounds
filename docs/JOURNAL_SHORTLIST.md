# 免费 SCI 期刊评估（核实版，2026-11-12）

**最终选择：_Computers & Geosciences_（Elsevier）。** 免费订阅路径（0 APC、
0 版面费）、JCR Q1 / 中科院 地球科学 2 区，且与“基准 + 软件 + 审计”的稿型最匹配。
Earth Science Informatics 作为兜底：3 区、录用率更高、同样免费。

**若只看录用率**：首投 _Earth Science Informatics_；它对“基准 + 审计 + 部分负
结果”的接受度高于 C&G。选择 C&G 的代价是录用率，换来的是 2 区与更强的期刊匹配。

**免费、无版面费的录用率排序：ESI → Journal of Applied Geophysics →
Acta Geophysica → Pure and Applied Geophysics。** 录用率没有官方数字，这个排序
依据“主题匹配度 × 期刊定位 × 审稿门槛”，不是承诺；见 §2.1。

**不要再把 IEEE JSTARS 或 IJAEOG 当免费选项**：两者已转为全 OA，强制 APC（见 §3）。

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

### 2.1 按录用率排序（免费、无版面费）

“录用率”没有公开数字，以下按**主题匹配度**与**审稿门槛**排序；这是判断，不是保证。

| 序 | 期刊 | 版面费/APC | 2yr 被引 | JIF 约 | 为什么更容易 | 主要风险 |
|---:|---|---|---:|---|---|---|
| 1 | **Earth Science Informatics** | 订阅 0；无版面费 | 6.94 | 2.6–3.2 | 主题即地学数据、工作流与复现；接受 benchmark 和负结果 | 中科院 3 区；审稿人可能要求更明确的“信息学”贡献 |
| 2 | **Journal of Applied Geophysics** | 订阅 0；无版面费 | 2.70 | 2.0–2.6 | 应用地球物理读者；审计可转写为勘查启示 | 可能被要求野外验证或新的反演方法 |
| 3 | **Acta Geophysica** | 订阅 0；无版面费 | 2.94 | 1.8–2.4 | 综合地球物理，门槛较低、体量适中 | 遥感数据融合可能被判偏题，引言要重写 |
| 4 | **Pure and Applied Geophysics** | 订阅 0；无版面费 | 2.58 | 1.8–2.4 | 综合地球物理，接收面宽 | 偏物理机制，需补物理讨论 |

C&G 不在此表：它免费、无版面费，但定位更高、录用率低于上述四者；仅当需要
Q1/中科院 2 区时首选。

### 2.2 二区（中科院）免费选项

先分清两种“二区”：

* **JCR Q2**：ESI 本身就是 Q2（JIF 约 2.6–3.2），已是二区，无需换刊。
* **中科院二区**：ESI 是 3 区；免费且方向匹配的 2 区选项主要是 C&G。

| 期刊 | 中科院（估） | 费用 | 匹配与风险 | 录用率 |
|---|---|---|---|---|
| **Computers & Geosciences** | 地球科学 2 区 | 订阅 0；无版面费 | 最匹配；要求软件可用性、复现证据（已具备） | 中 |
| **Natural Resources Research** | 2 区（估） | 订阅 0；无版面费 | IAMG 系、定量资源评价；需按“资源潜力/不确定性”重构引言与讨论 | 中（可能高于 C&G） |
| **JGR: Solid Earth** | 2 区（估） | 订阅 0 | 偏固体地球物理机制，需补物理讨论；门槛高 | 低 |
| IEEE GRSL | 2 区（估） | 订阅 0（超页费） | 5 页限制，本稿放不下 | 低 |

已排除：**Ore Geology Reviews**（2 区，但已转全 OA，约 $3,310，且要矿床结果）、
**IEEE TGRS**（1 区，但超页费不可控）、**RSE / ISPRS JPRS**（1 区，门槛极高）。
分区为近年近似值，投稿前以本单位认定口径复核。

**格式代价（重要）**：ESI 用 Springer Basic（作者-年份）引用制，本稿目前是
IEEE 数字编号（24 条参考文献）；投 ESI 前必须把正文引用标记和参考文献表转成
作者-年份，工作机械但需逐条校对。JAG 与 C&G 用数字制，几乎不用改引用格式。
若不想动参考文献，选 JAG；若以录用率为先，选 ESI 并接受这次转换。

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
C&G（最终选择：免费、无版面费、Q1 / 中科院 2 区、最匹配）
  └─ 3 个月无进展 → ESI（免费、3 区、录用率更高）
       └─ JAG（免费保底）→ Acta Geophysica / PAGEOPH
```

**不建议** Ore Geology Reviews、Economic Geology：它们要正向找矿/矿床结果，本稿会被判
“没有地质结论”。Natural Resources Research 只在愿意把论文重构为资源评价/不确定性
框架时考虑（2 区、免费，但属于改稿，不是换模板）。
**不建议** 任何全 OA 遥感刊：APC 是硬成本，且审稿口味偏“应用新方法”，与本稿的
“审计 + 负结果”不合。

## 5. 投稿前清单（C&G）

1. **软件可用性段落**：名称、版本、许可证、仓库、归档 DOI、运行环境、复现命令。
   已在正文 “Reproducibility and data availability” 中加入 `Software availability`
   段落（2026-11-12）；C&G 明确要求软件可用性。
2. **摘要** ≤ 250 词（现 247）、关键词 6 个、Highlights 5 条（每条 ≤ 85 字符，
   现最大 77）。均已就绪（`docs/submission/`）。
3. **图表**：正文 8 表 6 图；原 Table 8（TES 敏感性）已移为 Supplementary Table S1，
   §7.6 引用，随稿上传 `Supplementary_Tables.docx`。
4. **生成式 AI 声明**：Elsevier 要求披露。是否添加由作者决定（`docs/submission/README.md`
   仍标为待定）。
5. **Cover letter**：已恢复为 C&G 版本（`docs/COVER_LETTER.md`）；ESI 版本在 git
   提交 `87e9797` 中可取回。
6. **费用确认**：订阅路径无 APC、无版面费；彩图印刷可能另计且可选，投稿系统里
   选 subscription / no open access 即保持 0 费用。
7. **参考文献格式**：正文 `[n]` 数字引用可直接用；C&G 为 Elsevier numbered 制，
   参考文献列表的标点/作者写法可能需按期刊模板微调（不影响正文与表）。

## 6. 证据链接（可复核）

- OpenAlex 期刊元数据（本次查询）：
  `https://api.openalex.org/sources?filter=issn:0098-3004|1865-0473|0926-9851|0812-3985|1874-8961|1939-1404|0143-1161|1569-8432`
- Crossref 近作许可（JSTARS 全 CC BY）：`https://api.crossref.org/journals/1939-1404/works?filter=from-pub-date:2025-01-01`
- Crossref 近作许可（C&G 无 CC，订阅）：`https://api.crossref.org/journals/0098-3004/works?filter=from-pub-date:2025-06-01`
- Crossref 近作许可（JAG 无 CC，订阅）：`https://api.crossref.org/journals/0926-9851/works?filter=from-pub-date:2025-06-01`
- Crossref 近作许可（ESI 无 CC，订阅）：`https://api.crossref.org/journals/1865-0473/works?filter=from-pub-date:2025-06-01`
- 本稿归档：`https://doi.org/10.5281/zenodo.24130421`；仓库：
  `https://github.com/Xbotsd/fusion-gain-confounds`
