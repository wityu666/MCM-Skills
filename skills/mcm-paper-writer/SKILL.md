---
name: mcm-paper-writer
description: "把已冻结并复核的 MCM A–C 结果写成完整中文与英文两版论文，交付可编辑源及 PDF；英文版用于正式提交，适用于起草、修订和结果到论文的交接。"
---

# MCM 中英两版论文

指令与讨论用中文，给用户完整中文与英文两版论文，英文版用于正式提交。先读[交接合同](../mcm-suite/references/contracts.md)、[年度规则](../mcm-suite/references/official-rules.md)和[双语交付约定](references/bilingual-delivery.md)，使用项目的 `context.json`、`rules.json` 与实际 A/B/C 题面。正式比赛默认采用用户指定的[论文结构](references/user-preferred-structure.md)及对应的[英文大纲](assets/paper-outline.md)、[中文大纲](assets/paper-outline-zh.md)；章节主线与论证功能保留，实际题数、专项交付和合并理由按当前任务记录。行文调用 [$mcm-modeling-paper-writing](../mcm-modeling-paper-writing/SKILL.md)，按其[论证协议](../mcm-modeling-paper-writing/references/narrative-protocol.md)组织证据；模板不提供可直接照搬的句子、结果或强制满页要求。

## 输入与写作

- 读取冻结的 `contracts/problem.json`、`contracts/model.json`、`results/run_manifest.json`、`results/numeric_bindings.json`、`verification/result_review.json`、`sources/sources.csv` 和实际 AI 日志。用[冻结工具](../mcm-suite/scripts/freeze_artifacts.py)执行 `verify --root PROJECT --manifest results/run_manifest.json`。结果定稿须 `result_review.status=PASS`，且绑定当前清单哈希；不满足时可写结构草稿，明确缺项，不填造数字。
- 依 `tasks` 逐项安排论证、模型、结果与验收证据；实际题面的 memo、letter 等放入任务映射。2026 的专项输出不能推断成其他年份要求。
- 使用[用户结构及整合规则](references/user-preferred-structure.md)、[英文大纲](assets/paper-outline.md)和[英文论证检查](references/english-argument-checks.md)。主线为 Introduction → Problem Description and Analysis → Basic Assumptions → Glossary and Symbols → Models → Error Analysis and Sensitivity Analysis → Model Evaluation and Extensions → Conclusions → References → Appendices。每个模型任务按 Preparation → Establishment → Results → Analysis of Results 展开；公共模型/数据引用而非重复。Summary Sheet 独立一页、置于第一物理页，最后定稿：尽早给任务相关的关键答案，说明必要的方法机制、比较对象、单位、验证程度与使用条件。没有已证实的优势或创新时如实报告 baseline，不凑亮点；摘要不能强于正文。
- 方法从对象、观测或决策结构解释选择，写明基础模型不足与必要改动；公式前交代用途，之后解释符号、单位、参数来源和下游输出。假设说明依据、影响和可检验性，“为简化”不是唯一理由，算法先进或复杂也不证明适用。
- 结果按实际任务解释对象、差异、意义和条件，明确观测、拟合、预测、模拟、反演及候选方案的区别。图表正文说明它支持哪个判断，保留有意义的失败结果。论文数字逐项绑定结果 ID，图表绑定真实数据与生成代码，显示取整另记；内部 ID 留在清单，正文用真实量、公式/图表编号和引文。
- 验证决定结论强度：训练拟合不写样本外准确，可行/最好已检方案不写保证全局最优，关联/SHAP贡献不写因果，未拒绝原假设不写证明不存在或存在。敏感性说明改变什么、怎样改变、重算哪些输出及何种范围；参数扫描、随机仿真、区间覆盖和数值收敛分别命名。指标或方程与模型名称矛盾时回查上游，不能润色为可靠。
- 局限落到受影响的参数、情景或建议；结论回收已回答的任务，不引入新结果。题设 memo/letter 把已支持的结果转为该受众能执行的动作、条件、代价和风险。旧获奖稿、译文和合辑只供获授权时学习组织方式，不带入原句、模型参数、数值或旧年规则。
- 最多页数读取 `rules.json`。Summary Sheet、目录、参考文献、附录、代码及专项材料均计页；仅适用政策确认的 AI 报告可排除。最多 25 页不等于必须写满，篇幅依据当年 COMAP 规则，没有额外最低页数门。
- 引用核查原始来源，外来数据、思想、图像和直接引语在使用处标明出处。按实际用途引用 AI 工具并填写[AI 报告](assets/ai-use-report.md)；包含翻译、内嵌 AI 与代码补全，生成内容与翻译/补全分别披露，不伪造日志或模型版本。

## 源稿与导出

沿用用户选定的 Word 或 LaTeX 路线，为中文与英文各保留一份可编辑源和一份 PDF；不把“两版”理解为同时生成 Word 和 LaTeX。默认分开存于 `paper/zh/` 与 `paper/en/`，最终官方上传仅选择英文 `ControlNumber.pdf`。两版内容和图表依据同一冻结结果，译文不独立更改模型、数值、结论或限制。Word 使用当前可用的 documents/PDF 技能及导出工具。单独 `.tex` 默认保存并用 Codex `open_in_codex` 打开内置编辑器，调用 `compile_latex_document` 确认编译；内置预览成功不等于已经导出提交 PDF。多文件 TeX 用已存在且实际可用的编译工具。无可用导出工具时保留源稿，报告具体哪一版未导出/未验证，不安装工具或声称成功来掩盖缺口。

导出前检查所有页及 AI 报告的身份信息：正文、页眉、图中文字、链接、作者属性和 PDF 元数据都只保留允许的 Control Number 标识。所有解答页顶部加 Control Number 与页码，字体按当年规则易读且达最低字号。

## 交接与失效

在 `paper/paper_manifest.json` 写入合同规定的结果冻结 ID、结果清单与复核文件哈希、两版源稿/图/PDF 哈希、数字 ID、引用 ID、任务覆盖和 `ai_used`，并按双语约定登记语言对应关系。交给 `$mcm-layout-verifier` 英文提交 PDF、中文复核 PDF 及这些真实文件，另做[双语对应复核](assets/bilingual-review.json)；一版缺失或未复核时不能报告两版交付完成。

交接前对照标题、Summary Sheet、任务正文、图表、结论及专项材料中的对象、数值、方向、单位和限定语。核对用户默认结构、各实际任务的四步功能及后半部分分工；目录由最终标题生成，模板旧页码、重复编号、错误标题级别和编辑提示清除。若因题面或共享模型调整章节，在任务覆盖/交接记录中给出结构映射与理由，不丢任务或凭空补验证。较大论文可沿用通用行文技能的内部主张表；语句长度、词频或 `CLAIM_PRECHECK_PASS` 只能帮助定位，不代替论证审阅、结果 PASS 或逐页视觉复核。

结果、模型解释或代码改变回到相应上游并同步两版；纯文字/引用/排版改变更新相应语言清单、该 PDF 版面和双语对应检查，未变字节的另一版页面证据保留。`mode=live` 到停止工作时间后不得再修改解答、翻译、引用、版式或 AI 报告，只能只读核验和交付已冻结文件。内部复现源码/数据、中文复核稿与英文上传 PDF 分开保存。
