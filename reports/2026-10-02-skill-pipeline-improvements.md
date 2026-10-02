# Pipeline Skill 改进与验收记录

日期：2026-10-02。范围：本仓库的 `paperline`、`paper-navigator` 和相关专业 Skill。保留现有 Skill 划分、中文优先、正式 P1→P5、期刊确认和 S6/S7 作者锁规则；不新增 Skill 或 Router 状态机。

本轮改变的是 Skill 的编排、材料继承、专业入口和交付约定。仓库源码已修改；未覆盖用户全局安装的 Skills，也未运行真实论文或联网选刊。本轮未修改 WebUI。

## 全部 12 点的落点

| 点 | 为什么采用 | 采用哪些点 | 采用在 pipeline 的哪个地方 |
| --- | --- | --- | --- |
| 1. 职责闭合 | 原有编排把画像/写作交给 Router，但 Router 已是轻量路由，实际责任需要接上 | paperline 管阶段与确认，Router 分派，专业 Skill 产出内容及检查证据 | `paperline/SKILL.md` 的 P1/P3 执行；`paper-navigator/SKILL.md` |
| 2. 区分调用来源 | 独立“先写再定刊”路线不能覆盖正式选刊前置依赖 | 正式调用继承阶段、期刊状态、允许动作；独立调用保留混合路径 | Router 主入口与 `references/router-rules.md` |
| 3. 规则可达 | 拆分专业 Skill 后，旧详细规则不能只留在兼容目录里 | 主入口直达各自 rules；共享协议按需接详细主张/反向提纲；正式工作流由 paperline 读取 | 五个 writer 主入口、Router `references/README.md`、既有质量门 |
| 4. 文件接力 | 下一轮需要知道当前采用稿及证据在哪里，避免候选稿覆盖作者稿 | 产物归属、实际路径、作者采用版本、下游用途；旧文件名和格式复用 | 新增 `paperline/references/project-relay.md`；可选 `paper_context` 位置 |
| 5. 每轮任务约定 | 每次只做一个可检查任务，交付可被下一步直接读取 | 目标、输入、范围、输出、完成条件、下一步；已有信息不重复填表或追问 | 文件接力规则、Router 路由输出、paperline 每轮输出 |
| 6. 可回查证据卡 | 文献真实存在、读过摘要和支持当前句子是不同判断 | 主张、阅读状态、原文位置、支持/不支持范围及待补项；使用同一共享证据文件 | `literature-research/references/citation-support.md`、`paper-reading.md` |
| 7. 结果摘要 | 零散图表、日志和草稿转述容易混用条件、数值与数据划分 | 来源/核对状态、条件、数值、单位、对照、不确定性、边界和冲突；按需整理 | 新增 `results-writer/references/results-summary.md`；Results → Discussion 交接 |
| 8. 可读论文地图 | 完整稿需先明确各章问题及证据，避免扩写后才发现承诺无支撑 | writer 提供局部蓝图，paperline 汇总章节—主张—证据—缺项—输出；reviewer 检查闭环 | `project-relay.md` 的 `paper-map.md` 约定、paperline P3 |
| 9. 分节起草与检查 | 整稿一次生成不利于核对，英文写作顺序也不能替换当前中文定稿规则 | 蓝图→正文→局部检查；引言第0版/最终版；正文稳定后定摘要；简单改写直接完成 | 新增 `paper-navigator/references/shared/section-writing.md`、五个 writer 本地规则 |
| 10. 逐句主张审计 | 总体评价不能指出具体句子缺什么证据、如何修复 | 原子主张、位置、数据/原文、支持理由、候选修订、待补；补源与改稿分别路由 | 新增 `manuscript-reviewer/references/claim-audit.md`；Router 审计入口 |
| 11. 变更与恢复 | 改题、补结果、换期刊后必须找到受影响位置并处理旧锁 | 变化→句段/图表/引用/摘要→修复输入输出与下一任务；保留正式失效与历史 | `paperline/SKILL.md` 恢复规则、`shared/local-editing.md`、文件接力规则 |
| 12. 选刊报告与正式锁定 | 候选报告或指南可用于写作，但不足以完成正式 P2 | 逐字段官方来源/日期/unknown，匹配范围复用指南；真实作者确认+两份正式文件校验后锁定 | `journal-navigator` 主入口、verification/target analysis、Router journal bridge |

文中提及的 ARS-Codex、paper-skill、Anti-Defensive Writing、ref-verify、journal-recommender 的相关方法，由现有文献、章节、审查和选刊 Skill 分担。本轮没有把这些外部包安装成必需依赖，也没有据文章描述宣称它们已通过本仓库集成验证。引用核验与主张支持仍分别检查，语言压缩放在逻辑与证据稳定后。

## S1–S8 独立监督

这里的 S1–S8 是本次修改的监督阶段，与论文质量状态 S0–S7 分开。实施稿形成后，独立 agent 按下表顺序检查；每阶段通过后才交下一阶段。具体监督结果如下：

| 阶段 | 检查范围 | 监督结果 |
| --- | --- | --- |
| S1 | 编排、Router、专业 Skill 职责和正式/独立路线 | PASS；现有正式交接标识与校验器一致 |
| S2 | 文件接力、作者采用稿继承、轻量任务约定 | PASS；没有强制全套文件或新增审批门 |
| S3 | 文献证据卡、阅读/定位/支持、结果摘要 | PASS；沿用既有支持等级，不补造分析或显著性 |
| S4 | 规则可达、论文地图、分节写作和中文顺序 | PASS；章节入口可达，蓝图不成为额外作者批准门 |
| S5 | 逐句主张审计及补源/修订分派 | PASS；候选句不自动覆盖作者稿，只审所需范围 |
| S6 | 选刊普通报告、正式合同、官网来源与指南复用 | PASS；真实确认及两份正式产物校验仍保留 |
| S7 | 变更影响、局部恢复及正式失效/作者锁 | PASS；具体材料恢复不放松正式失效或复用旧锁 |
| S8 | 跨 Skill 集成、校验结果与行为演练 | PASS；12 点落点实存，职责与入口一致，合成演练与既有正式契约相容 |

## 已执行验证

| 验证 | 实际结果与范围 |
| --- | --- |
| `quick_validate.py` | 10 个改动 Skill 的元数据与基础结构通过 |
| Markdown 相对链接检查 | 主入口、相关 references 与本报告的 65 个相对链接目标均存在 |
| `python -X utf8 -m unittest discover -s tests -p test_paper_navigator_router.py -q` | 6 项现有路由静态检查通过 |
| `python -X utf8 paperline/scripts/run_contract_dry_run.py` | 现有期刊、状态、作者锁、翻译和 P4→P5 交接链通过；使用合成测试制品 |
| `python -X utf8 paperline/scripts/validate_pipeline_state.py --self-test` | 76 项状态/绑定/回退检查通过 |
| `python -X utf8 journal-navigator/scripts/validate_journal_artifacts.py --self-test` | 专属实施 agent 执行通过；合成测试 |
| 独立 Skill 行为演练 A | Val 原始记录与作者 Test 表述冲突时，列冲突、给受限候选段落、保留当前采用稿；未描述看不到的图像细节 |
| 独立 Skill 行为演练 B | abstract-read 与 DOI 核验未升级为正文支持；英文审计收窄因果表述，保留引文编号并交文献 Skill 补全文 |
| 限定范围 `git diff --check` | 通过；未跟踪参考文件另由元数据和链接检查覆盖 |

上述检查验证入口、材料边界和既有正式契约的相容性。两组行为演练只使用给定合成材料，不能作为真实论文科学质量、官方期刊政策或全流程运行的验收。

## 兼容与交付

- 主入口：[paperline](../paperline/SKILL.md)、[paper-navigator](../paper-navigator/SKILL.md)。
- 新共享约定：[项目文件接力](../paperline/references/project-relay.md)、[分节写作](../paper-navigator/references/shared/section-writing.md)。
- 新专业参考：[结果摘要](../results-writer/references/results-summary.md)、[逐句审计](../manuscript-reviewer/references/claim-audit.md)。
- 旧参考规则继续保留。现有状态枚举、作者锁、交接 schema 与校验器判定逻辑没有因本次 Skill 修改而变更。
- journal 主入口移除了工作台候选池导出指令；历史兼容参考保留，不进入当前默认路线。

## GitHub 发布前复验

推送前从 Git 暂存区导出隔离源码，验证实际发布内容。专业路由所需的 `rebuttal-writer` 等此前未跟踪目录一并纳入；WebUI、真实论文、运行产物、未关联的后端功能继续留在本地。README 的 Skill 分工及同级目录部署说明同步更新。

隔离源码的路由 6 项检查、正式交接 dry-run 和 11 个新建/更新 Skill 的元数据检查通过，相对链接无缺失。首次隔离复验发现原有 Windows 自测期望路径未解析，与校验器输出的绝对路径不一致；发布内容仅纳入该一行自测修正，不改变校验逻辑，也不纳入同文件其他后端扩展。
