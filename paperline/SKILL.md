---
name: paperline
description: 编排科研论文从研究画像、正式选刊、中文全文S6/S7定稿到忠实英译和投稿前检查。负责阶段、文件接力、作者确认、失效与恢复；由 paper-navigator 分派文献、章节写作、审查等专业任务，不在编排层代写正文。用于推进完整论文项目或恢复中断的正式流程。
---

# 论文全流程编排（paperline）

将本 Skill 用作一个薄编排入口。只管理阶段、文件接力、交接包、确认门、失效传播和恢复位置；专业方法归文献、章节、审查、选刊和翻译 Skill。

`paperline` 决定正式阶段能否推进，`paper-navigator` 只分派当前阶段所需的任务，专业 Skill 负责内容及检查证据。研究画像或中文稿不是 Router 自己撰写的产物；S6 判定、S7 作者锁和正式交接由本 Skill 汇总专业结果与作者决定后管理。

## 开始或恢复

1. 查找现有 `pipeline-state.json`。存在时先运行：

   ```text
   python scripts/validate_pipeline_state.py pipeline-state.json --verify-files
   ```

2. 读取 `references/pipeline-contract.md`，按其中的状态、交接外壳和恢复规则执行。
3. 没有状态文件时，根据用户材料建立新状态，并将未开始选刊标为 `venue.mode=unselected`；不得把“有草稿”直接判定为阶段完成。
4. 只激活一个阶段。先报告当前阶段、已锁定输入、阻塞项、下一项安全动作，再进入专业 Skill。
5. 读取 [项目文件接力](references/project-relay.md)，识别已有材料和作者采用的稿件。沿用已有文件路径；不为使用本流程重建全部文件。

给 Router 的调用应带上当前阶段、期刊状态、已确认边界及本轮允许动作。这些是当前正式状态的简短摘录，不让 Router 再建立状态文件或自行选择“先写再选刊”的路线。用户只要求独立局部工作且未接入正式流程时，直接使用对应专业 Skill，不要求创建 `pipeline-state.json`。

在源码树首次接通、升级任一交接字段或准备用新案例前，运行 `python scripts/run_contract_dry_run.py`。该脚本需要三个专业 Skill 作为同级目录，只验证交接契约，不替代真实稿件验收。

## 五阶段主流程

| 阶段 | 专业路由 | 完成条件 | 下一交接 |
| --- | --- | --- | --- |
| P1 中文研究画像 | Router 分派 `literature-research` 及所需章节/审查任务，本 Skill 汇总研究画像 | 一句话主旨、贡献排序、证据画像、论文类型与边界经作者确认 | 把研究画像交给 P2 |
| P2 期刊筛选与规则锁定 | `$journal-navigator` | `target-journal-decision.md` 与 `target-journal-writing-contract.md` 均为 `confirmed`，官方证据、版本和哈希已锁定 | 把两个正式文件的版本与哈希交回 P3 |
| P3 中文全文定稿 | Router 分派各章节 writer 与 `manuscript-reviewer`，本 Skill 管理整合及定稿判定 | 全文按期刊合同达到 S6；作者审阅确切版本并明确锁定为 S7 | 把 S7 中文稿和术语交给 P4 |
| P4 中译英 | `$zh-en-paper-translator` | 英文稿、术语台账、完整性审计及所需格式/视觉检查完成，形成 `english-translation-package@1.0` | 以精确 P4→P5 正式交接把英文制品交给 P5 |
| P5 投稿前检查 | `manuscript-reviewer`、`journal-navigator`、`zh-en-paper-translator` 等按检查项复核 | 已消费当前 P4 精确产物；科学内容、期刊硬规则、翻译与文档完整性均通过，形成 `pre-submission-check-report@1.0` | 形成投稿前检查包 |

阶段名在状态文件中固定为：`chinese-evidence-profile`、`journal-contract`、`chinese-finalization`、`english-translation`、`pre-submission-check`。

## 路由规则

- 中文主旨、贡献、证据、章节和科学一致性：由 `$paper-navigator` 分派到具体专业 Skill；阶段推进、S6/S7 判定及正式交接留在本 Skill。
- 跨期刊筛选、候选比较、作者选刊、官方要求核验和期刊合同：调用 `$journal-navigator`。P2 完成前必须分别对决策和契约运行其 `validate_journal_artifacts.py`；只引用通过的正式产物，不把期刊规则复制进编排状态。
- 已锁定期刊合同下的中文 S7 全稿忠实英译、术语、格式和翻译完整性：调用 `$zh-en-paper-translator` 的 `pipeline` 模式。期刊未锁定时，仍可脱离本正式流程使用翻译 Skill 的 `standalone` 模式。
- P3→P4 中的 `author_lock_record` 必须绑定当前稿件 ID、修订、SHA-256、P3 `content_state` 和外壳 `author_decisions` 的同一个 `lock_id`；五个锁定台账只接受合同定义的 `{inline}` 或 `{path, sha256}` 联合类型。
- 投稿前检查由本 Skill 汇总，但各专业判断仍由对应 Skill 给出；不要自行发明期刊规则、科学结论或译法。
- P5 进入 `active`、`waiting-human` 或 `complete` 前，必须存在 `references/pipeline-contract.md` 定义的精确 P4→P5 正式交接；不能只凭“英文稿已生成”推进。
- 用户只要求某一局部任务时，直接路由到相应 Skill，同时更新该阶段产物与下游有效性；不要强迫重跑无关阶段。

## P1/P3 的实际执行与交接

- P1：使用已有研究材料和 `literature-research` 的共享证据；需要核对贡献承诺或方法/结果边界时，分别调用对应 writer 或 `manuscript-reviewer`。本 Skill 汇总研究问题、主旨、贡献及未决项，取得已有确认门要求的作者决定；作者采用某项表述不替代来源支持核验。
- P3：按需读取既有 [中文定稿工作流](../paper-navigator/references/manuscript-finalization-workflow.md) 和 [质量门](../paper-navigator/references/manuscript-status-quality-gates.md)，将其中每个当前任务交给实际专业 Skill。完整中文稿通常先形成引言第0版，再写方法、结果、讨论和结论/相关工作，正文稳定后回写最终引言及摘要；不把此顺序强加给单节任务或不同论文类型。
- 各章节 writer 先产出本节的问题、证据和局部蓝图，本 Skill 只汇总为 `paper-map.md`，不替它们发明主张或扩写正文；由 `manuscript-reviewer` 检查结构闭环。已有合适地图时增量更新，不先重做全文规划。
- 每节起草后按需要做局部主张审计及反向提纲，问题回到对应 writer；缺失来源交给 `literature-research`。全文整合后，由 `manuscript-reviewer` 提供质量门证据，本 Skill 据此判定 S6 并组织作者对确切版本的 S7 锁定。
- 正式交接保持现有 schema、版本和哈希规则。P2→P3、P3→P4 中的 `paper-navigator` 是既有路由接口标识；由本 Skill 汇总实际专业产物和作者决定制作正式外壳，不要求 Router 创建状态、哈希或作者锁。

## 期刊未定旁路

正常尚未完成 P2 时使用 `venue.mode=unselected`。只有用户明确要求先推进中文稿而暂不选刊时，才把它改为 `venue-pending`，让 P3 在通用中文学术规则下继续，但在 paperline 状态中最多推进到 S6，不得完成 P3、声明 S7 或建立作者锁。必须同时记录：

- 跳过 P2 的原因和作者授权；
- 回退检查点 `journal-contract`；
- 旁路开始时各阶段版本；
- 期刊锁定后必须重新检查的下游阶段。

旁路不允许启动 P4。目标期刊锁定后，先使受影响的 P3/P4/P5 产物失效，回到 P3 应用期刊合同并重新取得 S6/S7；不得把旁路期间的通用稿，或在独立 `venue-unselected` 路线形成的 S7 历史，当作期刊适配后仍然有效。

## 确认门

以下决策标记为 `waiting-human`，并停止跨门推进：

- 一句话主旨、贡献取舍和排序、核心证据边界；
- 目标期刊的最终选择及费用、时间、收录等硬约束取舍；
- 中文全文确切版本从 S6 锁定为 S7；
- 歧义术语、源文矛盾、可能改变科学含义的翻译选择；
- 作者、单位、基金、伦理、利益冲突、数据代码公开和正式投稿行为。

缺输入但可安全产出脚手架时继续；继续会导致虚构或替作者决策时标记 `blocked` 或 `waiting-human`，不要猜测。

## 变更、失效与恢复

- 每个完成阶段必须记录产物版本和 SHA-256；每个交接必须记录所消费的上游版本。
- 上游主旨、证据、期刊合同或 S7 稿件变化时，按 `references/pipeline-contract.md` 标记所有受影响下游产物失效。
- 失效不删除历史产物。保留版本、哈希、失效原因和回退点，从最早失效阶段恢复。
- 恢复时先核对文件哈希和作者决策，再把该阶段设为唯一 `active`；不要仅凭文件名或“最新版”判断。
- 同时按 `paper-map.md` 的主张与证据对应关系列出受影响的章节、句段、图表和引用，以及下一轮应读取的文件和修复任务。改动影响不清时先审查范围；不能以局部恢复建议跳过正式失效规则或重新使用旧作者锁。
- 不带 `--verify-files` 的结果只是 `STRUCTURALLY_VALID`，不得据此推进阶段。带该参数通过只说明状态、路径和哈希一致，仍不证明论文科学质量、期刊规则真实性或翻译正确。

## 每轮输出

保持紧凑并区分事实与待确认项：

```text
流程编号：
当前阶段与状态：
本轮调用的专业 Skill：
已确认输入及版本：
本轮目标、修改范围与交付位置：
本轮完成条件及检查结果：
本轮产物及 SHA-256：
阻塞或待作者确认：
失效的下游产物：
下一项安全动作：
恢复位置：
```

不要把阶段完成、作者确认、英译完成、期刊合规和已投稿相互混称。未经用户明确要求，不执行投稿、上传、发送、发布、安装或覆盖全局 Skill。
