# 轻量路由规则

## 调用来源

- 来自 `paperline`：接收当前阶段、期刊状态、作者已确认边界及本轮允许动作的简短摘录，分派该阶段的专业任务后返回实际产物和检查结果；正式状态、S6/S7 及交接外壳仍归编排层。
- 独立任务：按用户当前交付物和已知材料路由；多个任务才安排下面的顺序。不要让独立混合路径覆盖正式 P 阶段。

## 单任务路由

| 用户请求示例 | 路由 |
| --- | --- |
| 找文献、设计检索式、读论文、判断来源支持什么 | `literature-research` |
| 写引言、研究背景、研究现状、research gap、贡献 | `introduction-writer` |
| 写方法、实验设置、数值模拟、模型、参数、评价指标 | `methods-writer` |
| 整理 results-summary、写结果、分析表格、比较模型性能、验证或消融 | `results-writer` |
| 解释结果、分析原因、比较已有研究、写讨论 | `discussion-writer` |
| 写标题、关键词、摘要或结论 | `abstract-conclusion-writer` |
| 检查全文或指定范围，逐句主张审计、逻辑、数字、术语、证据和图表引用 | `manuscript-reviewer` |
| 回复审稿人、起草 response letter、安排正文修改 | `rebuttal-writer` |
| 选刊、比较候选期刊、核验投稿条件或建立目标期刊画像 | `journal-navigator` |

## 多任务顺序

| 用户请求 | 顺序 |
| --- | --- |
| 找文献，然后写引言 | `literature-research` → `introduction-writer` |
| 根据结果写结果和讨论 | `results-writer` → `discussion-writer` |
| 检查全文，然后重写摘要 | `manuscript-reviewer` → `abstract-conclusion-writer` |
| 有材料和想法，先选刊再写论文 | `literature-research` → `journal-navigator`（初步短名单）→ 对应章节 Skill |
| 有材料和想法，先写初稿再选刊 | `literature-research` → 对应章节 Skill → `manuscript-reviewer` → `journal-navigator` |

独立调用且用户未指定先后时，默认采用混合路径：共享文献证据 → 方向性短名单 → 通用中文核心稿 → 全文审查 → 最终定刊与针对性适配。只有用户明确要求立即定刊，或目标期刊已经确定，才在写作前生成完整 `target-journal-guide.md`。正式 P2 调用直接沿用 `paperline` 的要求和已有授权，候选分析不等于正式锁刊。

论文骨架任务由各 writer 提供本节问题、证据和段落蓝图，完整正式项目交给 `paperline` 汇总地图，再交 `manuscript-reviewer` 检查结构。审计 → 修订任务先由 reviewer 定位缺口，缺来源交 literature，正文修改交对应 writer；不让 reviewer 的候选句自动成为采用稿。

## 共享产物与复用

- 通用论文检索、全文获取、阅读卡和主张级证据统一由 `literature-research` 产出为 `literature-evidence.md` 或等价对话内容；后续 Skill 复用，不重新做一轮相同检索。
- `journal-navigator` 可以提出为选刊所缺的证据条件，但新增论文的检索、获取和阅读仍路由到 `literature-research`；它自己负责期刊官方信息、目标刊近邻样本分析和动态投稿条件。
- 已有 `target-journal-guide.md` 且“目标期刊 × 研究方向 × Article Type”匹配时，直接把相关部分交给章节 Skill；guide 不替代科学文献证据。
- guide 范围不匹配时重新运行 `journal-navigator`；仅政策或近期样本过期时做增量核验，不完整重跑。
- 优先传递作者当前采用稿件及相关材料位置，补充本轮目标、范围、输出位置、完成条件与下一步输入；已有决定和充分材料不重复询问。任务简单时在对话内完成，不要求建立整套文件。
- 结果摘要、地图与审计表只按需复用。作者确认与证据支持分别记录；文件存在或作者采用不证明主张已经核验。

## 模糊请求

“帮我看看这一部分怎么写”不能直接按关键词决定。按以下顺序判断：

1. 读取用户指出的章节名、标题或文件名；
2. 读取相关段落、表格、图注和前后文；
3. 判断用户要的是起草、局部修改、解释、核验还是审查；
4. 仍有歧义时，只询问“希望得到什么产物”或“这部分属于哪一章”中的一个问题。

如果用户明确写出 `$methods-writer` 等 Skill 名称，直接尊重该指定。

## 路由边界

- 选刊和目标期刊画像：路由到 `journal-navigator`，但通用文献证据仍来自 `literature-research`；
- 图表绘制、登记、渲染和视觉验收：`scientific-figure`；
- 中译英和格式保真：`zh-en-paper-translator`。

Router 不生成章节正文，不建立评分体系，不维护 S0–S7 状态，不创建 SHA 或正式 handoff package。
