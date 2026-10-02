# 参考文件说明

`paper-navigator` 的默认读取范围只有：

- `router-rules.md`：任务到 Skill 的轻量路由；
- `paper-context.md`：可选的最小共享上下文；
- `shared/`：下游写作 Skill 可复用的共同原则。

同目录中原有的详细文件没有删除，用于兼容、人工查阅和 Paperline 旧文档引用。它们不再代表 Router 的默认流程，也不应在一次简单章节任务中全部加载。

当前读取入口：

- 章节 Skill 的 `SKILL.md` 直接链接其本地章节规则；共同的分节协议是 [shared/section-writing.md](shared/section-writing.md)。
- `paperline/SKILL.md` 在完整 P3 任务中按需读取 [中文定稿工作流](manuscript-finalization-workflow.md) 和 [质量门](manuscript-status-quality-gates.md)，分派专业任务并汇总状态。
- 主张地图、详细中文规则与反向提纲保留为专业 Skill 的按需参考，不再把 Router 当作正文作者。
- [journal-navigator-bridge.md](journal-navigator-bridge.md) 区分独立期刊分析与正式 P2，不复制现有合同 schema。
