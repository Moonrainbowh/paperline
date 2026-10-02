---
name: literature-research
description: 为科研论文检索、阅读和核验文献。负责检索式、代表性与最新论文、seed/backward/forward/related 检索、合法全文、阅读卡和主张级证据；不直接代写整篇论文。
---

# 文献研究（literature-research）

负责把“找论文”推进到“这篇论文能支持什么”。先读取当前对话或用户提供的 `paper_context`，复用已有文献证据，再按本轮目标读取规则：

- 检索或增量补缺：[文献发现](references/literature-discovery.md)。
- 找到全文但尚未核验：[全文获取](references/fulltext-access.md)。
- 阅读、摘录和整理原文位置：[论文阅读](references/paper-reading.md)。
- 判断具体句子能否引用、建立证据卡：[引用支持](references/citation-support.md)。

## 工作范围

- 理解研究主题、问题、方法、对象和证据需求；
- 设计多组检索词，不依赖单一关键词；
- 找代表性、最新、seed、backward、forward 和 related papers；
- 合法获取并核验全文；
- 阅读论文并提取方法、结果、图表、局限和可引用语境；
- 将原子主张与正文来源锚点对应起来；
- 为写作和选刊维护同一份可复用文献证据池；收到已有结果时先增量补缺，不重复检索。

## 输出

按用户需要返回检索策略、候选表、阅读卡或引用支持表。多阶段任务将可复用结果写入已有文献证据文件，尚无文件时可用 `literature-evidence.md`。其中的证据卡按原子主张记录阅读状态、原文位置、摘录、支持与不支持范围、已知元数据及待定位项，具体格式见引用支持规则。局部查询可直接在对话交付，不强迫建文件。标题、摘要或 DOI 元数据不能替代正文证据。

`literature-evidence.md` 同时供章节写作和 `journal-navigator` 使用。为选刊补检时，可增加期刊分布、年份、Article Type、对象、方法和证据形态，但不判断 Scope、APC、索引或投稿政策；这些动态期刊判断属于 `journal-navigator`。目标期刊确定后，如需目标刊近期近邻文章，由本 Skill 按 `journal-navigator` 给出的范围检索和获取全文，再把可核验材料交回分析。

不使用复杂文献评分。只说明“值得看”“可支持什么”“不能支持什么”和“下一步需要全文还是进一步检索”。
