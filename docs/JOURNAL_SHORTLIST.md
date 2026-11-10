# 免费 SCI 期刊评估（2026-11 版，按当前论文状态重排）

约束：**SCIE 收录、不选 Gold OA 即无 APC、与论文实际内容匹配、命中率优先**。

> 影响因子为近年近似区间，以最新 JCR 为准；"命中率"是基于论文成熟度与期刊偏好的判断，不是承诺。

## 论文现在的实际状态（决定了选刊）

**强项**
- 真实数据占多数：USGS 航空放射性（295,943 样点）、真实 TMI、真实 USGS SIM 3206 地质图、**真实 ASTER L1T 热红外**（2006-10-18，4 景 100% 覆盖，5 波段，含 TES）。
- 工程可复现性罕见地完整：97 个受检产物、21 条交叉校验、25 项单测、生产者覆盖率守卫、SHA-256 清单、锁定依赖、一键复跑。
- 统计口径严谨：128 px 空间块 bootstrap、BH 多重比较校正、N_eff 110–175（而非 1.27M 伪样本）、独立地质目标 AUC 验证。
- 有真正的科学发现：融合增益的符号由"目标是否与模态同源"和"反演是否可识别"共同决定；gamma 单独在独立地质目标上 AUC 0.387（欠定），加入真实 ASTER TIR 后 0.913，但同形零通道得到 0.922——说明大部分增益是条件改善而非信息。

**弱项（审稿人会打的地方）**
- **EM 仍是合成**：本地无实测 AEM（`raw/` 只有 K/eU/eTh/TMI），这一点无法补。
- 无钻孔/蚀变标签，地质检查只是岩性一致性。
- 结论是"基准 + 方法审计 + 部分负结果"，不是"找到矿"。
- 单测区，单期次。

**因此**：最适合"方法/数据/可复现"类期刊；最不适合要求找矿成果或硬件验证的期刊。

## 推荐排序

| 序 | 期刊 | 出版商 | APC | IF 约 | 匹配点 | 命中率判断 | 审稿 |
|---:|---|---|---|---:|---|---|---|
| 1 | **Computers & Geosciences** | Elsevier | 订阅制免费 | 3.5–4.5 | 方法+软件+benchmark+可复现，几乎为本稿量身 | 中（若按软件/复现框架写，明显高于平均） | 2–4 月 |
| 2 | **Earth Science Informatics** | Springer | 订阅制免费 | 2.5–3.5 | 地学数据/工作流/可复现 | **高**（门槛低于 C&G，偏好数据与方法） | 2–4 月 |
| 3 | **Journal of Applied Geophysics** | Elsevier | 订阅制免费 | 1.8–2.5 | 应用地球物理方法、多源融合 | 中高 | 2–3 月 |
| 4 | **Exploration Geophysics** | Taylor & Francis | 订阅制（需查彩图/页面费） | 1.3–2.0 | 勘查地球物理、航空测量 | 中高 | 2–4 月 |
| 5 | **Mathematical Geosciences** | Springer | 订阅制免费 | 2.0–2.8 | 可识别性、估计理论、可复现 | 中 | 3–5 月 |
| 6 | **IEEE JSTARS** | IEEE | 订阅制免费（超页收费） | 4–5 | 遥感融合、真实 ASTER | 中偏低（要遥感新意，且限 8 页） | 3–5 月 |
| 7 | **International Journal of Remote Sensing** | T&F | 订阅制免费 | 2.5–3.5 | 遥感应用 | 中 | 3–5 月 |

**不建议**：Remote Sensing (MDPI)、IEEE Access、Scientific Reports、PLOS ONE、GeoHazards 等——均收 APC。
**也不建议**：Ore Geology Reviews、Natural Resources Research、Economic Geology——要正向找矿/矿床结果，本稿会被认为"没有地质结论"。

## 两条路线

### 路线 A：命中率优先（推荐给"必须尽快见刊"）
**首投 Earth Science Informatics**。理由：订阅制免费、SCIE、明确覆盖地学数据与计算工作流、对"基准 + 审计 + 部分负结果"接受度高、门槛低于 C&G。按现有稿件改模板即可，正文结构不用动。

### 路线 B：性价比优先（推荐给"要 Q1/较高 IF"）
**首投 Computers & Geosciences**。它是本稿最好的归宿：审稿人就是做方法/软件/复现的人，我们的 97 产物 + 21 交叉校验 + 覆盖率守卫 + 清单在 C&G 是加分项而不是附件。风险是它要求"软件可用性"证据更强（仓库、许可证、安装说明），而仓库 DOI 我们还没有。

### 转投顺序（省时间）

```
C&G（3 个月无进展 → 转）
  └→ Earth Science Informatics（稳）
       └→ Journal of Applied Geophysics（保底）
```
或纯求稳：`ESI → JAG → Exploration Geophysics`。

## 每个候选需要改什么

| 期刊 | 必须调整 |
|---|---|
| C&G | 摘要与引言改成"可复现基准 + 开源实现"，突出软件可用性；补仓库/归档 DOI 与安装说明；表格压到 8 个以内 |
| ESI | 突出数据工作流与元数据；把 TES、镶嵌、掩膜写成一节"数据处理流水线" |
| JAG | 把"方法审计"翻译成"对勘查实践的启示"；强调真实 ASTER 与真实放射性联合使用的工程价值 |
| Exploration Geophysics | 加一段与勘查习惯的对接（比值法、三元图），弱化深度学习式表述 |
| JSTARS | 必须压到 8 页、图减到 4–5 张、突出遥感新意（真实 ASTER + 融合），并接受超页费 |

## 投稿前必须补的三件事（否则哪个都危险）

1. **仓库 + 归档 DOI**（Zenodo/Figshare）。没有它，C&G 与 ESI 的"可复现"卖点落空。
2. **EM 的表述**：全文所有 EM 结果必须带 "synthetic EM" 限定词；摘要不能暗示 EM 为实测。这是最容易被拒的表述问题。
3. **图与表**：12 表 6 图对多数期刊偏多，建议主文留 7–8 表，其余进补充材料。

## 需要你确认

1. 单位对**分区/IF**是否有硬门槛？（只要 SCIE → ESI 最稳；要 Q1/IF>4 → C&G 或 JSTARS）
2. **截止时间**？（3 个月内要录用通知，只能选 ESI/JAG；6 个月以上可冲 C&G）
3. 是否接受把 EM 明确写成"受控合成"，而不是继续等实测 AEM？（决定稿件能否立刻投）

## 按分区口径重排（Q2 保底、Q1 目标）

> 分区以最新 JCR 与中科院升级版为准，下表为近似判断，投稿前须核对本单位认定口径。

| 期刊 | JCR 分区（估） | 中科院分区（估） | APC | 命中率 | 主要风险 |
|---|---|---|---|---|---|
| Computers & Geosciences | Q1 | 地球科学 2 区 | 无 | 中 | 要求软件可用性证据（缺仓库 DOI） |
| IEEE JSTARS | Q1 | 地球科学 2 区 | 无（超页收费） | 中偏低 | 8 页限制、要遥感新意 |
| International Journal of Applied Earth Observation and Geoinformation | Q1 | 2 区 | 订阅制可选 | 中 | 偏应用，需强化找矿/填图价值 |
| Mathematical Geosciences | Q1–Q2 | 2–3 区 | 无 | 中 | 读者偏统计，需弱化工程细节 |
| Journal of Applied Geophysics | Q2 | 3 区 | 无 | 中高 | 需把审计写成勘查启示 |
| Earth Science Informatics | Q2 | 3–4 区 | 无 | 高 | 分区可能不满足 2 区要求 |
| International Journal of Remote Sensing | Q2 | 3 区 | 无 | 中高 | 审稿慢、影响力一般 |

**若单位要求中科院 2 区**：只能在 C&G / JSTARS / IJAEOG / Mathematical Geosciences 中选，ESI 与 JAG 不达标。
**若只要求 JCR Q2**：上面全部满足，此时 ESI 是命中率最高的选择。

## 建议的组合

- **目标 Q1 + 可接受中等风险**：Computers & Geosciences（免费、最匹配、期刊本身对基准+复现友好）。
- **必须稳、且接受 Q2**：Earth Science Informatics 首投，JAG 兜底。
- **既想 Q1 又怕 C&G 慢**：IJAEOG（应用地球观测，真实 ASTER 可作卖点），但需要重写引言的应用价值。
