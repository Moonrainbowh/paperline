---
name: manuscript-reviewer
description: 审查论文全文或指定范围的逻辑、章节职责、证据、数字、术语与过度结论；按需逐句审计主张并输出定位与修订建议，不自动改稿或使用综合评分。
---

# 全文审查（manuscript-reviewer）

先读取 `paper_context` 和用户提供的稿件、图表、参考文献或审稿要求。按用户任务选择范围：

- 全文或章节结构审查：读取 [反向提纲](references/reverse-outline.md) 和 [审查清单](references/review-checklist.md)，先检查结构与主张闭环，再做语言建议。
- 逐句核主张、证据或 Discussion 强度：读取 [逐句主张审计](references/claim-audit.md)，只审计所需范围，不要求先审完整篇。

证据与局部改动边界沿用 [共同原则](../paper-navigator/references/shared/writing-principles.md) 与 [局部修改规则](../paper-navigator/references/shared/local-editing.md)。

若提供了与当前目标期刊、研究方向和 Article Type 匹配的 `target-journal-guide.md`，额外检查稿件是否满足其中有证据依据的读者定位、论证组织和呈现建议；不要把样本观察误判为官方硬性要求。

重点检查：引言提出的问题正文是否回答；贡献是否有方法和结果支撑；方法与结果是否对应；Results 与 Discussion 是否混写；摘要、正文、图表和结论的数字是否一致；术语、图表引用和证据边界是否一致；是否存在缺少证据的强断言。

每个问题写清位置、观察到的证据、影响和建议修复。只用“重要问题 / 一般问题 / 可优化问题”，不输出总分或百分比。

审查交付问题和可选修订句，默认不直接修改稿件。缺文献交给 `literature-research` 增量补源；需要改写交给相应章节 writer，涉及研究含义的选择由作者决定。`paperline` 依据审查产物管理正式阶段，审查通过不代表作者已锁定最终版本。
