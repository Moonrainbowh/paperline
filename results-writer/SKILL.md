---
name: results-writer
description: 撰写和局部修改 Results，分析用户提供的图表、表格、模型性能、实验结果、验证和消融；重点描述实际观察，不扩写未经证据支持的机制。
---

# 结果写作（results-writer）

先读取 `paper_context` 和用户提供的图表、表格、统计输出或原始记录。每个结果小节围绕研究问题组织，而不是按图 1、图 2 机械罗列。

起草或实质重写时读取 [结果规则](references/results-rules.md) 和 [分节写作协议](../paper-navigator/references/shared/section-writing.md)。结果材料零散、来源混杂或用户先要求整理结果时，按 [结果摘要](references/results-summary.md) 先整理；已有核对摘要时增量补缺。语言及局部修改遵循 [共同原则](../paper-navigator/references/shared/writing-principles.md) 与 [局部修改规则](../paper-navigator/references/shared/local-editing.md)。

若提供了与当前目标期刊、研究方向和 Article Type 匹配的 `target-journal-guide.md`，使用其中的结果顺序、图表证据任务和定量呈现建议；它不能补出未提供的结果。

每项数字都绑定条件、样本/工况、指标、单位、比较对象和不确定性。明确区分观察、有限的局部判断和需要转入 Discussion 的解释。

分析已有图表时读取 [图表分析边界](references/figure-planning-qa.md)，核对正文与编号、单位、图例及误差信息。图表绘制、登记、渲染和视觉验收交给 `scientific-figure`；本 Skill 只负责已有证据的文字分析和结果叙述。

多轮写作可维护 `results-summary.md`，再交给本节正文和 `discussion-writer` 使用；简单段落有充分材料时直接写，不强迫补齐整篇摘要表。交付默认中文，报告本节检查和缺项，不自行确认整稿阶段。
