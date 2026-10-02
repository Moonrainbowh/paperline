---
name: methods-writer
description: 撰写和局部修改数据、实验、数值模拟、模型、参数、工艺、研究流程和评价指标，确保读者理解并能够复现关键方法。
---

# 方法写作（methods-writer）

先读取 `paper_context`，再盘点用户提供的实验设置、数据、代码、日志、参数和评价定义。方法回答“本文具体做了什么”，不提前写结果。

起草或实质重写时读取 [方法规则](references/methods-rules.md) 和 [分节写作协议](../paper-navigator/references/shared/section-writing.md)。需要核对流程、数据或执行产物时读取 [方法与结果溯源](references/experiment-provenance.md)。语言及局部修改遵循 [共同原则](../paper-navigator/references/shared/writing-principles.md) 与 [局部修改规则](../paper-navigator/references/shared/local-editing.md)。

若提供了与当前目标期刊、研究方向和 Article Type 匹配的 `target-journal-guide.md`，使用其中的方法细节、复现和验证呈现建议；它不能补出用户材料中不存在的方法事实。

必须明确对象、输入、处理步骤、参数、比较规则、数据划分、评价指标、失败条件和适用边界。没有材料支持的参数、样本量或流程不得补写成事实。

如果用户只要求改一个方法小节，遵循局部修改规则，并检查该小节与 Results 中直接相关的指标和条件是否一致。

完整章节交付包括本轮方法正文、已用来源和会影响复现的缺项，默认中文。章节检查不替代 `paperline` 的正式阶段确认。
