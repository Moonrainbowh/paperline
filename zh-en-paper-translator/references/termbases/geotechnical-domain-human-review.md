# Final Human Review Register

This register records reusable defaults that deserve user review. They are intentionally `context-dependent`, not `locked`. The translator may choose them directly when the manuscript supplies decisive context; otherwise it must ask once and persist the answer at the confirmed scope.

| Chinese form | Context-based default | Alternative | Ask when |
| --- | --- | --- | --- |
| 特征 | `feature` for an ML input | `property` for a material characteristic | The sentence mixes feature engineering and material properties without defining the variable |
| 验证 | `validation` for model assessment | `verification` for checking implementation/specification | The manuscript uses one Chinese word for both activities |
| 精度 | `accuracy` for closeness to truth | `precision` for repeat-measurement scatter | No metric, reference value, or repeatability context is supplied |
| 反演 | `inverse analysis` for parameter back-analysis | `inversion` for geophysical imaging | The observation type and objective are unclear |
| 相似材料 | `analogue material` in international physical modelling | `similar material` when preserving a Chinese author's established English | No author terminology or discourse community is identifiable |
| 类岩材料 | `rock-like material` for artificial specimens | `rock-analogue material` for a scaled model material | It is unclear whether similitude requirements were imposed |
| 相似比 | Preserve the author's defined `similarity ratio` | `scale factor` for a named physical quantity | The numerator/denominator direction or symbol definition is absent |
| 渗透率 | `intrinsic permeability` for m², D, or mD | `hydraulic conductivity` for m/s | Units and governing definition are missing |
| 抗拉强度 | `tensile strength` generally | `splitting tensile strength` for a Brazilian/splitting test | The test method is not identified |
| 重复性 | `repeatability` under the same conditions | `reproducibility` across laboratories/batches/conditions | Experimental conditions are not specified |
| 造腔 | `cavern construction` for the engineering activity | `cavern development` for geometric evolution | Both project execution and shape evolution are discussed in one undefined use |
| 溶腔 | `leach a cavern` as a verb | `solution-mined cavern` as a noun | Chinese grammar does not reveal the syntactic role |
| 采卤 | `brine production` for a salt product | `brine withdrawal` in the leaching loop | The process objective is not stated |
| 排卤 | `brine withdrawal` during construction | `debrining` during commissioning | The project stage is unclear |
| 夹层 | `interlayer` in mechanical failure analysis | `interbed` in stratigraphic description | The passage shifts between mechanics and stratigraphy |
| 盐岩 / 岩盐 | `rock salt` for the rock mass | `halite` for the mineral | The passage reports composition and mechanics without distinguishing material level |
| 气垫 | `gas blanket` during solution mining | `cushion gas` only for storage operation | The passage does not identify construction versus operation |
| 扩腔 / 扩容 | `cavern enlargement` for leaching geometry | `dilatancy` for inelastic volumetric expansion | The Chinese source uses “扩容” without a process or mechanics definition |

## Review Outcome Fields

When the user confirms a choice, copy the applicable master row into the project or personal termbase and record:

- `selection=selected`;
- `decision_scope=occurrence|paragraph|section|document|project|personal`;
- `confirmed_by=user`;
- `confirmed_at=<ISO date>`;
- `status=locked` and `authority=user` only for the confirmed scope.

Do not rewrite the reusable master row as globally locked unless the user explicitly makes a personal-scope decision.
