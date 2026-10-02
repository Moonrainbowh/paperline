# 简单 paper_context

`paper_context` 是可选的短上下文，不是状态文件、版本合同或交接包。它可以直接出现在对话中，也可以由用户以 `paper_context.md` 提供。

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

规则：

- 只填写已有信息；
- `confirmed_claims` 只放作者已采用的主张及确认来源；材料核验结果仍记录在证据表，作者采用不替代科学支持；
- 不确定内容放入 `unresolved_issues`，不要伪装成结论；
- 下游 Skill 读取后可在回复中补充，但不要求用户补齐所有字段；
- `literature_evidence` 和 `target_journal_guide` 可填写文件路径，也可说明内容已在当前对话中；
- `results_summary`、`paper_map`、`current_draft` 同样是可选路径或内容位置；没有时不要求新建，它们不替代原始图表、数据或文献；
- `current_draft` 优先引用作者当前采用的修订，不以未采用的候选稿或旧稿覆盖；
- `target_journal_guide` 只有在目标期刊、研究方向和 Article Type 匹配时才适用，且不替代科学证据；
- 共享上下文的目的只是避免术语、数字、贡献和结果前后矛盾。

正式 `paperline` 的阶段、期刊状态、允许动作和作者锁只作为调用约束传入，不写成 Router 自己的另一份状态。下一轮只携带本轮确实需要的上下文与输入位置。
