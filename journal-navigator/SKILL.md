---
name: journal-navigator
description: 用可追溯证据完成跨期刊筛选，或在目标期刊确定后建立期刊轨道与领域轨道的中文写作画像和 confirmed 交接契约。用于用户要求推荐、比较、排除或选择投稿期刊，核验期刊范围、论文类型、收录、费用和投稿要求，分析目标期刊近期论文写法，或把已选期刊的明确规则与领域论证惯例交给 paper-navigator；不负责撰写全文、英译或投稿操作。
---

# 期刊导航

只在当前任务需要的模式中加载资料。先建立稳定的期刊决策接口，再做目标期刊写作画像；若作者已经明确指定期刊，可以跳过多候选比较，但仍须先生成简化的选择证据和决策文件，并记录这是作者决定。

## 选择模式

| 用户目标 | 使用模式 | 必读资料 | 固定产物 |
| --- | --- | --- | --- |
| 推荐、比较、排除或选择期刊 | 模式一：跨期刊筛选 | [journal-selection.md](references/journal-selection.md) + [evidence-and-currentness.md](references/evidence-and-currentness.md) + [contracts-and-handoffs.md](references/contracts-and-handoffs.md) | `journal-selection-evidence.md` + `target-journal-decision.md` |
| 已选期刊，建立栏目、结构、风格和证据要求 | 模式二：双轨写作画像 | [writing-profile.md](references/writing-profile.md) + [evidence-and-currentness.md](references/evidence-and-currentness.md) + [contracts-and-handoffs.md](references/contracts-and-handoffs.md) | 若稳定决策接口尚不存在，先生成两份简化选刊产物；再生成三份画像/契约文件，共五份 |
| 既要选刊又要适配写作 | 依次运行模式一、模式二 | 先只读模式一资料；作者选定后再读模式二资料 | 五份产物（两份选刊产物 + 三份画像/契约产物） |

禁止为了方便把两种评分混在一起：

- 选刊只使用“硬门结果 + 软偏好评分 + 作者最终选择”；不得使用论文样本的 `J/R/E/U`。
- 写作画像才使用 `O/A/B/C/D` 分类和 `J/R/E/U`，用于解释样本选择与章节用途；不得反推期刊录用概率。

## 共同起点

1. 建立研究快照：论文类型、研究对象、核心问题、主要方法、关键结果、贡献、当前成熟度。
2. 询问作者约束：必须收录体系、学科范围、OA/APC 上限、语言、时间、地域或机构政策、明确排除项。
3. 把会改变候选集合或写作契约的缺失项放入确认门；不能替作者补造偏好。
4. 需要联网时优先读取官方期刊、出版社、索引数据库和正式论文页面；所有正式判断附来源与核验日期。

## 模式一：跨期刊筛选

1. 按研究快照生成候选池，并说明每个候选的进入理由。
2. 逐刊核验硬门，并把候选分别写入 frontmatter 的 `shortlist_candidate_ids`、`unknown_hard_gate_candidates` 和 `failed_hard_gate_candidates`。任一硬门失败即淘汰；硬门未知则进入“待核验”，不得视为通过。
3. 仅对硬门通过者应用作者确认的软偏好和权重。每个分数必须附事实、来源与不确定性。
4. 输出淘汰表、待核验表和不超过 3—5 本的短名单；不要伪造接受率或预测录用概率。
5. 请作者最终选择。Skill 可以推荐顺序，但不得代替作者把状态改为 `confirmed`；confirmed 要求 unknown 列表严格为空，且 `selected_candidate_id` 属于短名单、不属于 failed 列表。
6. 生成选择证据和 `target-journal-decision.md`，运行：

```powershell
python scripts/validate_journal_artifacts.py <path-to-target-journal-decision.md>
```

校验通过只表示选刊交接完整，不表示目标期刊写作画像已完成。

## 模式二：选定期刊后的双轨画像

1. 锁定目标期刊、栏目、论文类型和选择依据；从筛选报告进入时核对作者选择一致。若作者直接指定期刊且两份稳定决策文件尚不存在，先按 `contracts-and-handoffs.md` 生成并校验简化的 `journal-selection-evidence.md` 与 `target-journal-decision.md`，再继续画像。
2. 建立统一来源池：官方 `[O#]`、目标期刊论文、其他期刊高度相关论文、用户范文和二手线索。
3. 将论文样本按 A/B/C/D 分类并记录 `J/R/E` 理由；再按章节分别记录用途 `U`。
4. 运行期刊轨道：用官方、A、C 生成 `journal-writing-profile.md`。
5. 运行领域轨道：用 A、B 生成 `field-writing-blueprint.md`。
6. 逐项融合硬要求、期刊偏好、领域论证规律和当前论文条件，生成 `target-journal-writing-contract.md`。
7. 高影响冲突交给作者确认。只有状态为 `confirmed`、阻塞项为空、三份文件的 `writing_profile_evidence_id` 一致，且契约已绑定选刊证据版本和决策文件哈希时，才允许交给 `paper-navigator`。
8. 运行：

```powershell
python scripts/validate_journal_artifacts.py <path-to-target-journal-writing-contract.md>
```

## 确认门

出现以下任一情形时暂停最终确认，同时继续完成不依赖该决定的证据整理：

- 论文类型、目标收录、费用上限或时间约束会改变候选集合；
- 官方来源缺失、互相冲突或已经过期；
- 作者要在“更匹配、影响力、速度、费用、开放获取”之间改变权重；
- 目标期刊、栏目或高影响写作规则尚未由作者确认；
- 全文不足以支持稳定画像。

固定确认块：

```text
需要作者确认：
已有证据：
推荐默认值及理由：
其他选项的影响：
若不确认的处理：保持 pending_confirmation，不进入下一正式交接。
```

## 交付边界

- 默认使用中文，明确区分“官方硬要求、可重复观察、谨慎推断、未知、作者决定”。
- 不把影响因子、分区、收录、APC、审稿周期或投稿政策当作长期不变事实；正式使用前按核验日期更新。
- 不复制样本文献的句子，不把单篇文章写法升级为期刊规则。
- 不直接修改中文论文，不执行英译、投稿或付费操作。
- 选刊报告只交给画像模式；confirmed 写作契约才交给 `paper-navigator`。
- 校验器失败时报告失败项，不得宣称已经完成交接。
