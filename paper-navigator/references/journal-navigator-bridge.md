# 与相邻 Skill 的边界

- 需要候选期刊、官方范围、费用、近期发文或目标期刊写作画像时，`paper-navigator` 路由到 `journal-navigator`；两者是逻辑上的一条流程，但保持独立 Skill。
- 先把已有 `literature-evidence.md` 或等价文献结果交给 `journal-navigator`。若证据池不足，先路由 `literature-research` 补齐，避免两个 Skill 重复做通用检索与全文阅读。
- `journal-navigator` 负责研究定位、候选期刊比较、官方条件核验和目标期刊文章簇分析；`literature-research` 负责论文发现、合法全文、阅读卡和主张级证据。
- `paper-navigator` 不自行猜测期刊规则。
- 独立调用时，候选短名单和 `journal-analysis.md` 只支持后续选择；确定目标后可将 `target-journal-guide.md` 作为章节写作建议，不能称为正式锁刊或期刊合规。
- 被 `paperline` 调用时，继承其当前阶段、稿件修订、期刊状态、约束与已确认决定，不重新安排一次独立选刊流程。P2 路由给 `journal-navigator` 时说明这是正式交付入口；既有入口授权不再重复询问，但作者的最终选刊和确切合同确认仍须真实存在。
- 正式 P2→P3 只接收已确认并通过既有校验的 `target-journal-decision.md` 与 `target-journal-writing-contract.md`，具体字段、引用绑定和应用边界读取[journal-contract-intake.md](journal-contract-intake.md)。Router 只传递路径、版本与状态；`paperline` 负责阶段推进，章节 Skill 只读取当前任务适用的合同规则。未确认或未知硬条件未解决时，保留草稿与缺项，不将短名单或指南当成 `locked`。
- 已有 `target-journal-guide.md` 时，先核对目标期刊、研究方向与 Article Type。匹配则将相关部分交给章节 Skill；不匹配则重做画像；仅动态信息过期则增量核验。
- `target-journal-guide.md` 是写作适配指南，不是科学证据，不能替代 `literature-evidence.md` 中的来源锚点。
- 需要中文稿英译时，路由到 `zh-en-paper-translator`；不要在论文写作 Skill 中直接承诺英译。
- 选图、渲染、登记和视觉质量检查交给 `scientific-figure`；章节 Skill 只说明图表应支持的观察或主张。

正式合同、状态和翻译交接参考文件不属于轻量 Router 独立局部任务的默认读取范围；在 `paperline` 正式调用或用户明确要求该类交接时，按需读取对应规则，避免遗漏下游必须消费的正式产物。
