---
name: journal-navigator
description: 复用已有文献证据并核验官方期刊信息，识别研究定位、比较投稿期刊；目标期刊确定后，分析该刊近期近邻论文并生成写作参考。用于选刊、论文完成后重新选刊和目标期刊适配；不负责通用文献检索、代写全文、预测录用概率或执行投稿。
---

# Journal Navigator｜研究定位与选刊分析

这个 Skill 只回答三个问题：

1. 研究属于哪些学术方向或研究社区？
2. 哪些期刊真正适合这项研究？
3. 目标期刊中相似研究通常怎样组织论证和证据？

默认提供可读的分析报告，不把选刊过程包装成复杂 workflow。普通任务不要求 YAML、固定 H2、候选 ID、版本号、SHA-256、状态机或机械确认块。

独立调用与 `paperline` 的正式 P2 使用同一套选刊分析方法，但交付不同：独立调用默认交付报告与写作指南；正式 P2 还须形成已确认的选刊决定和写作合同，供下游按既有契约接收。短名单、用户指定一个期刊或已有指南，都不能单独证明 P2 已完成。

开始时优先读取 `paper_context` 与已有 `literature-evidence.md`（或等价对话内容）。通用论文发现、全文获取、阅读卡和主张级证据由 `literature-research` 统一维护；本 Skill 不从零重复同一轮检索。证据不足时，明确缺少的对象、问题、方法、年份或 Article Type，并让 `paper-navigator` 先路由 `literature-research` 增量补齐。本 Skill 可直接核验期刊官方信息，并提出目标期刊近期近邻文章的定向检索范围。

## 先判断入口

先识别当前调用边界，再选择模式 A 或 B：

- **独立分析**：只做用户要求的研究定位、候选比较或目标期刊分析，不自行启动正式 `paperline` 流程。
- **正式 P2**：由 `paperline` 调用，或用户已明确要求接入该流程时，继承当前稿件 ID/修订、研究画像、作者约束、期刊状态与已有确认记录；这已经授权本 Skill 准备正式交付，无需再问是否要接入流程。仍缺的作者选刊或合同内容确认不能由该入口授权代替。
- **已有目标或合同**：先检查目标期刊、研究方向、Article Type 与当前稿件是否匹配。复用有效证据与真实作者确认；只补变化的官方条件、样本或受影响规则，不重新做同一轮通用文献检索。

### 模式 A：研究内容 → 期刊 → 写作参考

适用于研究想法、摘要、提纲、部分初稿或尚未确定投稿方向的论文。

按以下顺序执行：

1. 读取[研究定位](references/research-positioning.md)，先理解对象、问题、方法、数据/实验、结果、创新、场景和完成程度。
2. 提出 2–4 个 Research Positioning，区分主要、次要和边缘定位；说明各自读者、期刊类型和检索方向。
3. 读取[文献与期刊发现](references/literature-and-journal-discovery.md)，复用近 3–5 年真实相关论文的证据池，从论文分布反向发现期刊。证据不足时先交由 `literature-research` 定向补齐；不要根据模型记忆直接列期刊。
4. 形成 3–8 本候选，再收敛到不超过 3–5 本主要候选。对每本写进入理由、近期连续性、代表性近邻论文、理论/方法/工程定位和投稿时应强调的贡献。
5. 读取[期刊核验](references/journal-verification.md)，核验 Scope、Article Type、SCI/EI/Scopus 等索引、OA/APC、官方投稿要求、投稿状态和明显风险。未知写 `unknown`，不等于通过。
6. 输出 `journal-analysis.md`（或直接在聊天中输出），包含研究理解、Research Positioning、相关文献、论文发表分布、候选期刊、官方条件、对比、推荐和适用条件。不要计算虚假的精确综合分，不预测录用概率。
7. 用户确定目标期刊后，读取[目标期刊分析](references/target-journal-analysis.md)，先复用证据池；缺少目标刊近邻样本时，由 `literature-research` 按限定范围补齐该刊近 3–5 年同 Article Type、同领域、同对象/方法/证据的约 5–15 篇论文，再由本 Skill 分析并输出可长期复用的 `target-journal-guide.md`。它的适用范围是“目标期刊 × 研究方向 × Article Type”，不是某一篇论文的一次性报告。

### 模式 B：完整论文 → 适合投稿的期刊

适用于用户说“我的论文已经写好了，适合投哪里”。不要简单重复模式 A：

1. 先读取[研究定位](references/research-positioning.md)，检查 Title、Abstract、Introduction、Methods、Results、Discussion、Conclusion、Figures/Tables 和 References，识别论文真实定位、主要贡献、证据强度和当前叙事方向。
2. 利用 References 和已有 `literature-evidence.md` 观察论文连接的学术社区和高频期刊；如需扩展近年相关论文，交由 `literature-research` 增量补齐。
3. 按[期刊核验](references/journal-verification.md)检查候选条件，回答当前稿件更适合哪些期刊、哪些期刊虽相关但写法不合适、投不同期刊需要改哪些部分，以及属于小幅适配还是明显改变叙事。
4. 输出同样的 `journal-analysis.md`；用户选定目标后，再输出 `target-journal-guide.md`。

用户直接指定目标期刊时，可跳过候选发现，直接进入[目标期刊分析](references/target-journal-analysis.md)，但仍须用官方页面核验当前要求。

## 正式 P2 的交付与确认

正式调用继续复用上面的 `journal-analysis.md`、共享文献证据和匹配的 `target-journal-guide.md`，再按[现有合同接收规则](../paper-navigator/references/journal-contract-intake.md)及 `scripts/validate_journal_artifacts.py` 的既有格式准备正式文件，不另建一套合同 schema。

1. 将当前稿件画像、作者约束、逐字段官方来源/核验日期、候选取舍整理为 `journal-selection-evidence.md`；未知硬条件保留为未知，不能改写成通过。
2. 根据作者实际选择准备 `target-journal-decision.md`。缺少最终选择或尚未确认费用、收录等取舍时，保留 `draft` 或 `pending_confirmation`，列出具体待决策项。已有针对当前稿件与条件的明确确认，直接引用，不重复索取。
3. 复用指南中的双轨分析，按既有正式格式形成 `journal-writing-profile.md`、`field-writing-blueprint.md` 和 `target-journal-writing-contract.md`。这些是当前稿件的合同证据快照，不重建通用文献池；官方要求与样本观察分开，影响贡献、科学边界或内容取舍的事项交作者确认。
4. 作者确认确切的合同内容后才写 `confirmed`，记录真实确认与版本。对决定和合同分别运行 `scripts/validate_journal_artifacts.py`，将通过的路径、版本与 SHA-256 交回 `paperline`；它负责推进 P2 并交接 P3。候选报告、指南、未确认文件或单独通过的决定不能充当锁刊完成证据。

先完成可审查的报告和合同草稿，再就仍缺的具体决定请求作者确认；未确认时可继续准备证据和草稿，但不把 P2 标为完成。校验通过只证明既有格式与文件绑定一致，不代替官方真实性核验或作者确认。

## 目标期刊分析的双轨边界

保留简化双轨画像：

- **期刊轨**：官方指南、栏目和目标期刊近期论文，回答编辑范围、读者和文章组织；
- **领域轨**：跨期刊高相关论文，回答问题、方法、基线、验证和工程证据门槛。

两轨在指南中融合，不强制拆分多个画像文件。样本观察不能升级成官方规则，不能复制样本文句，也不能把整本期刊的泛化“风格”套到当前研究上。

`target-journal-guide.md` 应把相对稳定的研究写法，与需要持续更新的政策和样本信息分开保存。后续论文默认先做增量核对；只有研究方向、Article Type、栏目、期刊政策或近年发文重点发生实质变化时，才完整重做。

## 信息来源原则

官方期刊/出版社页面优先于第三方信息；索引使用指定数据库官方记录；近期论文使用 DOI、出版社页面或可确认全文。当前 Scope、APC、Indexing、政策和投稿状态注明核验日期，并在投稿前复核。

不伪造接受率、审稿周期或录用概率；找不到的信息写 `unknown`，并说明它影响哪个判断。单篇相似论文只能证明存在先例，多篇跨年份相关论文才支持持续发表判断。

## 输出边界

如果用户只需要研究定位、候选期刊或目标期刊论文分析，只完成对应部分，不强制跑完整流程。`paperline` 正式 P2 调用沿用上面的合同交付与校验；独立分析不默认生成正式合同。
