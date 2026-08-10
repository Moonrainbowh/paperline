# 选定期刊后的双轨写作画像

本模式回答两个不同问题：期刊怎样要求和表达；相关领域怎样完成科学论证。两轨共享来源卡，但不得混写证据职责。

## 1. 来源与分类

| 类别 | 条件 | 用途 |
| --- | --- | --- |
| O | 官方 `[O#]` | 范围、格式、论文类型、伦理与声明等硬要求 |
| A | 目标期刊且研究高度相关 | 两轨交集锚点 |
| B | 其他期刊但研究高度相关 | 领域问题、方法、指标、基线和证据门槛 |
| C | 目标期刊但研究不高度相关 | 期刊结构、标题摘要、语气和编辑侧重 |
| D | 两轴均弱或证据不足 | 排除或发现线索 |

用户范文只校准作者声音；二手来源只作发现线索。A 类进入两轨但保留一个来源 ID，避免重复抓取。

## 2. J/R/E/U 只用于画像

- `J 0—3`：是否属于目标期刊、相同论文类型和兼容栏目。
- `R_obj/R_q/R_m/R_out` 各 `0—3`：对象、问题、方法、输出指标的相关度；必须逐项给理由。
- `E_full/E_recent/E_source` 各 `0—2`：全文完整度、近期性、来源/版本质量。
- `U 0—3`：对标题、摘要、引言、方法、结果、讨论、结论、图表或证据门槛的具体用途。

禁止只给总分。每个非零 U 必须记录“为什么选、来源锚点、能迁移什么、不能迁移什么、交叉核验”。这些分数不得回流为跨期刊排名或录用概率。

## 3. 期刊轨道

用 `[O#]`、A、C 生成 `journal-writing-profile.md`。规则 ID 使用 `JP-001`。

固定覆盖：

- 目标读者、编辑范围、论文类型与官方要求；
- 标题、摘要、Highlights、章节顺序与结构弹性；
- 全文及章节篇幅、图表、补充材料、术语和语气；
- A/C 样本分母、全文完整度、例外和低置信度观察；
- 每条规则的来源选择理由、适用章节、锚点和边界。

C 类不能证明领域方法或指标规范；单篇文章只能形成个案观察。

## 4. 领域轨道

用 A、B 生成 `field-writing-blueprint.md`。规则 ID 使用 `FB-001`。

固定覆盖：

- 问题与缺口如何建立；
- 理论、方法、数据和复现链；
- 基线、指标、验证和结果顺序；
- 图表证据阶梯、讨论问题、工程含义、局限和术语；
- 实验、模拟、机器学习、优化、现场监测等方法子群的不可迁移条件。

B 类不能单独决定目标期刊格式、摘要节奏或语气。

## 5. 固定三产物

```text
journal-profile/<journal-slug>/<article-type-slug>/
  journal-writing-profile.md
  field-writing-blueprint.md
  target-journal-writing-contract.md
```

前两份产物共享 `writing_profile_evidence_id`，契约通过相对路径引用它们。该 ID 只标识双轨画像的来源池，不与选刊证据的 `evidence_version` 混用。新建画像统一使用版本 `2.0`。

`journal-writing-profile.md` 至少包含：

```text
## 1. 目标期刊与论文类型
## 2. 官方规则与编辑范围
## 3. A/C 样本选择和评分摘要
## 4. 期刊结构、表达与边界
## 5. 章节用途矩阵
## 6. 期刊轨道规则清单
```

其 YAML 头部至少包含：`artifact_type: journal_writing_profile`、`profile_version: "2.0"`、`writing_profile_evidence_id`、`manuscript_id`、`manuscript_revision`、`target_journal`、`article_type`、`generated_at`、`last_verified_at`。

`field-writing-blueprint.md` 至少包含：

```text
## 1. 当前论文研究画像
## 2. A/B 样本选择和评分摘要
## 3. 领域论证链与方法子群
## 4. 章节用途矩阵
## 5. 领域轨道规则清单
```

其 YAML 头部至少包含：`artifact_type: field_writing_blueprint`、`blueprint_version: "2.0"`、`writing_profile_evidence_id`、`manuscript_id`、`manuscript_revision`、`research_field`、`generated_at`、`last_verified_at`。

## 6. 融合原则

- 格式、栏目、字数、声明：官方优先。
- 期刊范围、标题摘要和表达：官方 → A → C。
- 问题、方法、基线、指标和验证：A/B 中最相近的方法子群优先。
- 结果和讨论：A → B；C 只校准期刊表达。
- 专业术语：B → A；不得复制原句。

融合规则使用 `FR-001`。除纯格式硬约束外，每条高影响 FR 至少引用期刊轨道和领域轨道各一条规则，并说明当前论文条件、冲突裁决和不采用风险。
