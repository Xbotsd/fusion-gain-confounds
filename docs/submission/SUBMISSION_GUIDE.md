# 投稿操作指南 — Computers & Geosciences（Editorial Manager）

目标期刊：*Computers & Geosciences*（Elsevier，ISSN 0098-3004）
投稿系统：Editorial Manager，期刊代码 `cageo`

## 1. 官方链接

| 用途 | 链接 |
|---|---|
| 期刊主页（ScienceDirect） | https://www.sciencedirect.com/journal/computers-and-geosciences |
| Guide for Authors（投稿指南） | https://www.sciencedirect.com/journal/computers-and-geosciences/publish/guide-for-authors |
| **投稿入口（Editorial Manager）** | **https://www.editorialmanager.com/cageo/default.aspx** |
| Elsevier 作者支持 | https://service.elsevier.com/app/home/supporthub/publishing/ |
| 作者 ORCID | https://orcid.org/0009-0002-3231-0444 |

> 本机脚本访问 ScienceDirect / Elsevier 会返回 403（反爬），用浏览器正常打开即可。
> Editorial Manager 页面已验证可访问（HTTP 200）。

## 2. 投稿文件（`docs/submission/upload/`）

| 系统槽位 | 文件 | 说明 |
|---|---|---|
| Cover Letter | `Cover_Letter.docx` | 日期 13 November 2026，致 C&G 主编 |
| Manuscript | `Manuscript.docx` | 正文：标题页、摘要、8 表、6 图、行号、双倍行距 |
| Highlights | `Highlights.docx` | 5 条，最长 77 字符（上限 85） |
| Figure | `figures/figure01.png` … `figure06.png` | 逐张上传，RGB / 300 dpi |
| Graphical Abstract | `Graphical_Abstract.png` | 可选，建议上传 |
| Supplementary Material | `Supplementary_Material.docx` | Table S1（热红外敏感性） |

表单里需要粘贴的内容都在 **`paste_fields.txt`**（标题、作者、摘要、6 个关键词、5 条 Highlights）。
整套文件也有压缩包 `CG_submission_package.zip`，但**投稿时请逐项上传单个文件，不要传 zip**。
清单与 SHA-256 见 `upload_manifest.json`。

## 3. 注册 / 登录

1. 打开 https://www.editorialmanager.com/cageo/default.aspx
2. 首次使用：点 **Register Now**，填写
   - First/Given name: `Yudong`；Last/Family name: `Xu`
   - E-mail: `3468858545@qq.com`
   - Affiliation: `Heilongjiang University of Science and Technology`
   - Country: `China`
   - 设置用户名和密码；建议在 Profile 里关联 ORCID `0009-0002-3231-0444`。
3. 已有账号直接 **Login**；忘记密码用 "Forgot Username/Password"。

### 3.1 注册页的 “Areas of Interest or Expertise”（必填）

EM 注册页要求 **Personal Classifications 至少 1 个**、**Personal Keywords 至少 5 个**，
否则不能继续（截图里的红字 `Select 1+ Classifications` / `Enter 5+ Keywords`）。
这两项只用于匹配审稿人，不影响稿件内容。

**Personal Classifications**：点 `Select Personal Classifications`。C&G 的列表只有两个
顶层节点，先点 `+` 展开，再选子项：

- **1: Computational & Methods**（实际子项）：`1.1 Machine learning & deep
  learning`、`1.2 Geostatistics & stochastic modelling`、`1.3 Numerical modelling &
  simulation`、`1.4 Signal processing`、`1.5 Inverse problems & data assimilation`、
  `1.6 Image processing & classification`、`1.7 Spatial data analysis`、`1.8
  Uncertainty quantification`、`1.9 High-performance computing`、`1.10
  Geovisualization`
- **2: Geoscience Domain**（实际子项）：`2.1 Seismology & seismic imaging`、`2.2
  Remote sensing in a geoscience context`、`2.3 Hydrogeology & groundwater`、`2.4
  Surface hydrology & flood modelling`、`2.5 Reservoir & subsurface
  characterisation`、`2.6 Natural hazards & risk`、`2.7 Geochemistry & mineral
  exploration`、`2.8 Near-surface geophysics`、`2.9 Electromagnetic & potential
  field methods`、`2.10 GIS & geoinformatics`、`2.11 Structural geology &
  geodynamics`、`2.12 Geophysics`

**本稿推荐勾选这 6 项**（点中 → `Add`，重复）：

| 分类 | 对应论文内容 |
|---|---|
| `1.5 Inverse problems & data assimilation` | 欠定反演、秩 3/5、条件数 κ、方差增益 |
| `1.8 Uncertainty quantification` | 滤波方差、68/95 % 覆盖率、N_eff |
| `2.2 Remote sensing in a geoscience context` | 真实 ASTER 热红外、航空测量 |
| `2.7 Geochemistry & mineral exploration` | 伽马能谱、K/eU/eTh、找矿目标 |
| `2.9 Electromagnetic & potential field methods` | 航空伽马/航磁属位场方法，EM 为受控合成 |
| `2.12 Geophysics` | 审稿人池的宽口径归属 |

可选补充：`1.7 Spatial data analysis`（空间掩膜、块交叉验证）、`2.8 Near-surface
geophysics`（浅表航空测量）、`1.2 Geostatistics & stochastic modelling`（块
bootstrap）。选 6–8 项都合理，1 项即满足系统要求。

操作方式：展开节点 → 点中一个子项（高亮）→ 点中间的 `Add` → 右侧
`Selected Classifications` 出现该条目，红字 `Select 1+ Classifications` 消失。
可重复添加 2–4 项（1 项就满足要求）。搜索框可输入 `geophys`、`remote`、
`mineral`，匹配项会以红字显示。

> **必须点对话框底部的 `Submit` 保存**（页面提示 "To save changes you must
> click Submit before you leave this window"）；直接关闭或点浏览器返回不会保存。
> 这里的 Submit 只是保存分类，不是提交稿件。

**Personal Keywords**：点 `Edit Personal Keywords`，在 “New Keyword” 里**逐个输入**
下面的词并点 `Add`（至少 5 个，建议 8 个）：

1. airborne geophysics
2. gamma-ray spectrometry
3. thermal infrared remote sensing
4. ASTER
5. multi-modal data fusion
6. inverse problems
7. identifiability
8. mineral exploration
9. reproducible research
10. spatial statistics

填完点 `Continue` / `Save` 完成注册；之后可在 `Update My Information` 里随时补充。

## 4. 新建投稿（Submit New Manuscript）

按系统向导逐页填写：

1. **Article Type**：选 `Research paper`（若列表里叫 `Full length article` 或类似项，选最接近的）。
2. **Title**：粘贴 `paste_fields.txt` 的 TITLE 一行。
3. **Abstract**：粘贴 ABSTRACT 段（247 词，系统上限通常 250）。
4. **Keywords**：6 个，逐个填或用分号分隔（见 paste_fields.txt）。
5. **Authors**：Add Author →
   - Given name `Yudong`，Family name `Xu`
   - Affiliation `Heilongjiang University of Science and Technology, Harbin, China`
   - E-mail `3468858545@qq.com`
   - 勾选 **Corresponding Author**
   - ORCID `0009-0002-3231-0444`
6. **Cover Letter**：把 `Cover_Letter.docx` 的正文粘进文本框；若系统允许上传，也可上传该文件。
7. 若出现 **Data Availability / Declaration** 之类的必填项：数据可用性粘
   `The code and the derived results are archived at https://doi.org/10.5281/zenodo.24130421 (all versions: https://doi.org/10.5281/zenodo.24130420).`
   生成式 AI 声明正文里已有，按需粘贴同段文字。

## 5. 上传文件（Item Type 对照）

| 顺序 | 上传文件 | Item Type |
|---:|---|---|
| 1 | `Cover_Letter.docx` | Cover Letter |
| 2 | `Manuscript.docx` | Manuscript |
| 3 | `Highlights.docx` | Highlights |
| 4–9 | `figures/figure01..06.png` | Figure（每张单独一条） |
| 10 | `Graphical_Abstract.png` | Graphical Abstract |
| 11 | `Supplementary_Material.docx` | Supplementary Material |

要点：文件名只用字母/数字/下划线；图不要合并成一张；**不要上传 zip**；上传后可用 "Order" 调整顺序。

## 6. 生成 PDF 并检查

1. 点 **Build PDF for my Approval**，等 1–3 分钟。
2. 点 **View Submission**，重点检查：
   - 标题、作者、单位、邮箱正确；ORCID 已显示；
   - 摘要完整（247 词），关键词 6 个；
   - 正文 8 张表、6 张图都在，图注顺序正确；
   - 行号连续、双倍行距；
   - 参考文献 1–24 连续、无缺号；
   - Supplementary Material 已附上；
   - 没有乱码（尤其 `×`、`–`、`±`、`µ`）。
3. 确认无误 → **Approve Submission** → **Submit**。

## 7. 提交之后

- 通讯作者邮箱会收到带稿件编号（如 `CAGEO-D-26-xxxxx`）的确认信。
- 状态流程：`Submitted to Journal` → `With Editor` → `Under Review` → `Required Reviews Complete` → 决定。
- 通讯作者可在 EM 的 "Submissions Sent Back to Author" / "In Press" 里跟踪；修改稿同样从 EM 提交。

## 8. 常见问题

| 问题 | 处理 |
|---|---|
| 系统提示图片分辨率不足 | 现在图是 300 dpi；若坚持要 500/1000 dpi，告诉我，我从管线重新导出 TIFF |
| Highlights 必须是 3–5 条、每条 ≤85 字符 | 已满足（5 条，最长 77） |
| 需要单独 Title Page | 从 `Manuscript.docx` 第 1 页复制，或让我生成单独文件 |
| 是否双盲 | C&G 为单盲，保留作者信息即可 |
| 费用 | 订阅路径 **0 APC、0 版面费**；提交时不要勾选 Open Access / Open Choice |
| 生成式 AI 声明 | 正文 Declarations 已含；若系统单独询问，粘贴同段文字 |
| 数据 / 代码可用性 | 正文已写；仓库与 Zenodo DOI 见上 |

## 9. 提交前最后核对（30 秒）

- [ ] `upload/` 里 11 个文件齐全（`upload_manifest.json` 可核对 SHA-256）
- [ ] 稿件编号前确认通讯作者邮箱 `3468858545@qq.com` 可收信
- [ ] 系统里 Article Type 选的是 Research paper
- [ ] 没有勾选 Open Access（保持免费）
- [ ] 生成的 PDF 里图表、行号、参考文献完整
