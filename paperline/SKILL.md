---
name: paperline
description: 编排科研论文从中文研究主旨、贡献与证据画像，到期刊筛选和规则锁定、中文全文S6/S7定稿、忠实英译及投稿前检查的端到端 Skill。用于用户希望“一条流程跑完整篇论文”、接续中断的论文项目、在中文写作/选刊/英译之间交接、查看当前阶段或处理上游变更导致的返工；实际专业工作分别路由到 paper-navigator、journal-navigator 和 zh-en-paper-translator，不在本 Skill 内重复其方法。
---

# 论文全流程编排（paperline）

将本 Skill 用作一个薄编排入口。只管理阶段、交接包、确认门、失效传播和恢复位置；不要复制三个专业 Skill 的写作、选刊或翻译方法。

## 开始或恢复

1. 查找现有 `pipeline-state.json`。存在时先运行：

   ```text
   python scripts/validate_pipeline_state.py pipeline-state.json --verify-files
   ```

2. 读取 `references/pipeline-contract.md`，按其中的状态、交接外壳和恢复规则执行。
3. 没有状态文件时，根据用户材料建立新状态，并将未开始选刊标为 `venue.mode=unselected`；不得把“有草稿”直接判定为阶段完成。
4. 只激活一个阶段。先报告当前阶段、已锁定输入、阻塞项、下一项安全动作，再进入专业 Skill。

在源码树首次接通、升级任一交接字段或准备用新案例前，运行 `python scripts/run_contract_dry_run.py`。该脚本需要三个专业 Skill 作为同级目录，只验证交接契约，不替代真实稿件验收。

## 五阶段主流程

| 阶段 | 专业路由 | 完成条件 | 下一交接 |
| --- | --- | --- | --- |
| P1 中文研究画像 | `$paper-navigator` | 一句话主旨、贡献排序、证据画像、论文类型与边界经作者确认 | 把研究画像交给 P2 |
| P2 期刊筛选与规则锁定 | `$journal-navigator` | `target-journal-decision.md` 与 `target-journal-writing-contract.md` 均为 `confirmed`，官方证据、版本和哈希已锁定 | 把两个正式文件的版本与哈希交回 P3 |
| P3 中文全文定稿 | `$paper-navigator` | 全文按期刊合同达到 S6；作者审阅确切版本并明确锁定为 S7 | 把 S7 中文稿和术语交给 P4 |
| P4 中译英 | `$zh-en-paper-translator` | 英文稿、术语台账、完整性审计及所需格式/视觉检查完成，形成 `english-translation-package@1.0` | 以精确 P4→P5 正式交接把英文制品交给 P5 |
| P5 投稿前检查 | 三个专业 Skill 分项复核 | 已消费当前 P4 精确产物；科学内容、期刊硬规则、翻译与文档完整性均通过，形成 `pre-submission-check-report@1.0` | 形成投稿前检查包 |

阶段名在状态文件中固定为：`chinese-evidence-profile`、`journal-contract`、`chinese-finalization`、`english-translation`、`pre-submission-check`。

## 路由规则

- 中文主旨、贡献、证据、章节、S6/S7 和科学一致性：调用 `$paper-navigator`。
- 跨期刊筛选、候选比较、作者选刊、官方要求核验和期刊合同：调用 `$journal-navigator`。P2 完成前必须分别对决策和契约运行其 `validate_journal_artifacts.py`；只引用通过的正式产物，不把期刊规则复制进编排状态。
- 已锁定期刊合同下的中文 S7 全稿忠实英译、术语、格式和翻译完整性：调用 `$zh-en-paper-translator` 的 `pipeline` 模式。期刊未锁定时，仍可脱离本正式流程使用翻译 Skill 的 `standalone` 模式。
- P3→P4 中的 `author_lock_record` 必须绑定当前稿件 ID、修订、SHA-256、P3 `content_state` 和外壳 `author_decisions` 的同一个 `lock_id`；五个锁定台账只接受合同定义的 `{inline}` 或 `{path, sha256}` 联合类型。
- 投稿前检查由本 Skill 汇总，但各专业判断仍由对应 Skill 给出；不要自行发明期刊规则、科学结论或译法。
- P5 进入 `active`、`waiting-human` 或 `complete` 前，必须存在 `references/pipeline-contract.md` 定义的精确 P4→P5 正式交接；不能只凭“英文稿已生成”推进。
- 用户只要求某一局部任务时，直接路由到相应 Skill，同时更新该阶段产物与下游有效性；不要强迫重跑无关阶段。

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
- 不带 `--verify-files` 的结果只是 `STRUCTURALLY_VALID`，不得据此推进阶段。带该参数通过只说明状态、路径和哈希一致，仍不证明论文科学质量、期刊规则真实性或翻译正确。

## 每轮输出

保持紧凑并区分事实与待确认项：

```text
流程编号：
当前阶段与状态：
本轮调用的专业 Skill：
已确认输入及版本：
本轮产物及 SHA-256：
阻塞或待作者确认：
失效的下游产物：
下一项安全动作：
恢复位置：
```

不要把阶段完成、作者确认、英译完成、期刊合规和已投稿相互混称。未经用户明确要求，不执行投稿、上传、发送、发布、安装或覆盖全局 Skill。
