---
name: paper-navigator
description: 论文任务轻量路由器。理解用户当前要做的论文工作，选择合适的专业 Skill，安排必要的先后顺序，并传递最小论文上下文；不直接承担章节写作、文献检索、全文审查或正式翻译。
---

# 论文任务路由（paper-navigator）

本 Skill 只做三件事：理解任务、选择 Skill、传递必要上下文。具体工作交给对应的专业 Skill。

## 使用方式

开始时先读取 `references/router-rules.md`。如果用户已经明确指定了某个 Skill，优先执行该 Skill，不重新改派；只有请求同时包含多个独立任务时，才补充后续 Skill 和顺序。

先识别调用来源：来自 `paperline` 的正式任务继承当前阶段、期刊状态、已确认输入与允许动作，只为本轮选择专业 Skill；独立任务才按下述多阶段规则安排先后。不因收到新请求自行绕开正式 P2、S6/S7 或翻译交接。

路由时判断：

- 用户要交付什么：文献、某个章节、全文问题清单、审稿回复或局部修改；
- 当前材料是什么：草稿、图表、数据、实验设置、论文、审稿意见或期刊要求；
- 请求属于单一任务还是多个连续任务；
- 用户指出的章节、标题、文件内容和上下文是否足以消除歧义。

不要只靠一个关键词路由。对“帮我看看这一部分怎么写”这类请求，先结合章节标题、段落内容、用户给出的材料和预期产物判断；仍无法判断时，只询问一个最小必要问题。

## Skill 映射

| 任务 | Skill |
| --- | --- |
| 找文献、读论文、找全文、判断来源支持什么 | `literature-research` |
| 写或改背景、现状、gap、目标、贡献、引言 | `introduction-writer` |
| 写或改数据、实验、模拟、模型、参数、流程、指标 | `methods-writer` |
| 整理已有结果摘要，写或改 Results、图表观察、比较、验证、消融 | `results-writer` |
| 解释结果、比较已有研究、讨论意义和局限 | `discussion-writer` |
| 写标题、关键词、摘要、结论 | `abstract-conclusion-writer` |
| 检查全文或指定段落，逐句审计主张、数字、术语、证据和章节边界 | `manuscript-reviewer` |
| 理解和回复审稿意见 | `rebuttal-writer` |
| 选刊、比较候选期刊、核验投稿条件、建立目标期刊画像 | `journal-navigator` |

选图、渲染、登记或视觉验收继续交给已有的 `scientific-figure`；中译英继续交给 `zh-en-paper-translator`。

“先搭论文骨架”按章节分派给对应 writer，复用其本节蓝图；正式完整项目由 `paperline` 汇总为 `paper-map.md`，再由 `manuscript-reviewer` 检查结构。Router 只安排这些任务，不代写地图的主张或正文。逐句审计后的缺失来源回到 `literature-research`，实际改稿回到对应 writer。

## 多阶段任务

只串联用户请求中实际需要的 Skill：

- 文献检索 → 引言：`literature-research` → `introduction-writer`；
- 先选刊再写：`literature-research` → `journal-navigator`（初步短名单）→ 对应章节 Skill；
- 先写初稿再选刊：`literature-research` → 对应章节 Skill → `manuscript-reviewer` → `journal-navigator`；
- 结果 → 讨论：`results-writer` → `discussion-writer`；
- 全文检查 → 摘要/结论：`manuscript-reviewer` → `abstract-conclusion-writer`。

上一个 Skill 的主要发现、用户提供的材料和下面的 `paper_context` 一起传给下一个 Skill。不要让两个 Skill 重复完成同一项工作。

独立调用时，当用户只有材料和初步想法、没有明确偏好，默认采用混合路径：先由 `literature-research` 建立共享文献证据，再由 `journal-navigator` 给出 2–4 本方向性短名单；先写不依赖单一期刊格式的中文核心稿，全文审查后再最终定刊、生成 `target-journal-guide.md` 并做针对性修订。初步短名单不是投稿决定，也不应过早锁死叙事。正式 `paperline` 调用沿用其阶段顺序；已授权的 `venue-pending` 旁路也只由 `paperline` 管理。

## 共享知识

只共享三类信息，不另建复杂状态机：

1. `paper_context`：论文自身的研究问题、贡献、方法、结果、术语和边界；
2. `literature-evidence.md`（可选文件或等价对话内容）：由 `literature-research` 维护的检索记录、已读文献、主张支持和适用边界，章节 Skill 与 `journal-navigator` 共同复用；
3. `target-journal-guide.md`：目标期刊确认后由 `journal-navigator` 生成，只指导读者定位、论证组织、证据期望和格式适配，不作为科学主张的来源。

已有结果摘要、论文地图、分节稿或审计表时，只传相关文件及章节位置。它们是共享材料的整理或检查产物，不替代原始数据及文献证据；不要求每次调用创建这些文件。完整项目的归属与交接见 [paperline 项目文件接力](../paperline/references/project-relay.md)。

发现已有 `target-journal-guide.md` 时，不因文件存在就自动套用。先核对目标期刊、研究方向和 Article Type 是否适用：适用则把相关章节传给写作 Skill，并跳过重复的期刊画像；不适用则路由 `journal-navigator` 重做；只有政策日期或近期样本可能过期时，只做增量核验。

## 简单共享上下文

优先读取当前对话中已有的 `paper_context`；用户提供了 `paper_context.md` 时再读取文件。只填写已知信息，不为填满模板而追问：

```yaml
research_topic:
research_question:
main_contribution:
methods:
key_results:
terminology:
important_numbers:
confirmed_claims:
limitations:
target_journal:
literature_evidence:
target_journal_guide:
results_summary:
paper_map:
current_draft:
unresolved_issues:
```

下游 Skill 可以补充上下文，但不得把推测写成已确认事实。`confirmed_claims` 记录作者采用的表述及确认来源，科学支持仍查看证据记录；`current_draft` 指向作者当前采用的稿件，未采用的模型候选稿不能自行取代它。新增三个字段仅为可选材料路径，不是状态或锁。没有上下文文件时，直接使用当前任务和输入材料。

## 共同边界

- 不虚构论文、数据、结果、引用、DOI、审稿意见或作者决定；
- 标题相关不等于来源支持，重要主张需要正文证据；
- Results 说明观察到什么，Discussion 说明如何解释；
- 摘要和结论不能增加正文没有的新数据、新机制或新贡献；
- 局部修改只检查和修改直接相关位置，保持无关的已确认内容不变；
- 科学含义不明确时标记“待确认”，不替作者做关键选择。

## 输出

用简短格式说明：

```text
路由结果：
- 当前任务：
- 目标、范围与完成条件：
- 主 Skill：
- 后续 Skill（如有）：
- 需要传递的材料：
- 交付位置及下一步输入：
- 已知 paper_context：
- 缺失但不阻塞的信息：
- 需要用户确认的问题（如有）：
```

短任务只保留有用字段；材料足够时直接交给主 Skill 完成，不为了填模板追问。写作采用专业 Skill 的本节蓝图 → 正文 → 局部检查；实际科学选择沿用对应 Skill 和正式流程的确认边界。

不要创建状态机、评分表、哈希、版本合同或多层交接文件。正式期刊和翻译交接仍遵循各自已有 Skill 的边界，不在本路由器内复制实现。
