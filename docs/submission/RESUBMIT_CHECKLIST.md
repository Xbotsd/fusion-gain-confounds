# 重投操作清单 — CAGEO-D-26-02178

退回原因：参考文献格式（必须作者-年份、列出全部作者、期刊名不缩写）。
状态：**已在仓库改好并校验通过**，你只需要在 Editorial Manager 里替换文件、改两处
元数据、再提交一次。期刊明确写了只有一次机会，再不合格直接 desk review 拒稿。

## 0. 本地文件（直接上传，不要改名）

`D:\A_MineralProspecting\docs\submission\upload\`

| 文件 | 大小 | EM 里的 Item Type |
|---|---:|---|
| `Manuscript.docx` | 9.1 MB | Manuscript |
| `Cover_Letter.docx` | 38 KB | Cover Letter |
| `Highlights.docx` | 36 KB | Highlights |
| `Declaration_of_Competing_Interests.docx` | 36 KB | Declaration of competing interests |
| `figures\figure01.png` … `figure06.png` | 4.8 MB / 240 / 101 / 2.8 MB / 123 / 123 KB | **Figure**（每张单独一条） |
| `Graphical_Abstract.png` | 149 KB | **Graphical Abstract** |
| `Supplementary_Material.docx` | 37 KB | Supplementary Material |

> 上一次六张图和图形摘要全被记成了 Supplementary Material，这次务必在下拉框里
> 选对类型。

## 1. 进入返修

1. 打开 https://www.editorialmanager.com/cageo/ ，用作者账号登录。
2. 主菜单点 **`Submissions Sent Back to Author`**。
3. 找到 **CAGEO-D-26-02178**，点 **`Edit Submission`**。

## 2. 逐页修改

| 步骤（左侧菜单） | 要做什么 |
|---|---|
| **Edit Submission**（作者/标题页） | 点 `Edit Author Details`：国家选 **China**（去掉 `--- Select One ---`）；头衔 `B.E. Candidate` 可清空。标题、摘要（235 词）、6 个关键词不用动。 |
| **Remove / Replace Files** | 删除旧的 `Manuscript.docx` 与 `Cover_Letter.docx`，重新上传新的两份。 |
| **Attach Files** | 逐条上传并**核对 Item Type**：Manuscript、Cover Letter、Highlights、Declaration of competing interests、Figure ×6、Graphical Abstract、Supplementary Material。 |
| **Additional Information** | 数据链接保留 `https://doi.org/10.5281/zenodo.24130421`；预印本保持 **NO**；subject area 保持原选择。 |

## 3. 生成并检查 PDF

1. 点 **`Build PDF for my Approval`**，等 1–3 分钟。
2. 点 **`View Submission`**，重点看这五处：

- [ ] 参考文献页：条目是否 `Bar-Shalom, Y., Li, X.-R., Kirubarajan, T., 2001. …`（年份在作者后、无 `[1]` 编号）
- [ ] 正文引用：是否为 `(Dickson and Scott, 1997; IAEA, 2003; …)`，而不是 `[1–4,21]`
- [ ] 是否有独立的 **Code availability** 章节（名称/联系人/硬件/语言/软件/规模/仓库）
- [ ] 表 8 的 reference 列是否为 `IAEA (2003)` 这类写法
- [ ] 图 1–6、表 1–8 齐全，图注紧跟图

3. 无误 → **`Approve Submission`** → **`Submit`**。

## 4. 提交后

- 通讯作者邮箱会收到带新稿件编号的确认信（编号通常沿用 CAGEO-D-26-02178）。
- 状态：`Submitted to Journal` → `With Editor` → `Under Review`。

## 5. 如果 PDF 里还有问题

把那一页截图发我，我直接改 `docs/Manuscript_v2_draft.md` 并重跑
`python code/make_submission_package.py`，再从第 2 步重传即可（在 Approve 之前
可以反复 Build PDF）。
