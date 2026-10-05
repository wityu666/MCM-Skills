---
name: mcm-suite
description: 协调 MCM 美赛 A、B、C 题的选题、建模、数据检索、代码、独立复核及完整中英两版论文交付。英文版用于正式提交，适用于赛时解题、历年题训练和复现；不处理 ICM D、E、F 题。
---

# MCM 美赛技能集入口

中文协作，给用户完整中文与英文两版论文；英文版用于正式提交，中文版供阅读和复核，两版同结构、同模型、同结果。遵循[双语交付约定](../mcm-paper-writer/references/bilingual-delivery.md)及用户当前数据、路线与已有授权。A 连续、B 离散、C 数据洞察是初始标签，真实题设决定模型。本套件仅处理 MCM A–C；正式提交要求依据当年 COMAP 规则与当前题设。

模型、方法检索与论文行文支持使用本套件的 `mcm-modeling-*` 兄弟技能；所有技能调用与本地资源引用都在同一 MCM 安装包内解析。

## 启动与恢复

先读 [交接合同](references/contracts.md)。确定年度、live/practice/reproduce 模式、题面附件、剩余时间和已有产物。只询问改变行动的缺项。用 `scripts/init_project.py` 建工作区和原件副本；恢复时比对哈希，找首个缺失/失效阶段，保留有效成果。

初始化先校验参数与资产，再从私有临时目录发布新/空项目；失败不留下半个项目，不覆盖已有内容。脚本须与同目录 `artifact_safety.py` 一起保留。冻结/预检输出拒绝输入别名、符号链接、硬链接、只读冻结文件或无关既有文件；已有合法同类清单/报告可原子更新，历史冻结证据仍按既有归档/失效要求保存。JSON重复键、非有限值和错误结构不得作为通过输入。

初始化同时建立空的 `paper/en/`、`paper/zh/` 和未检查的双语复核模板；单任务分析无需填写论文记录。交付两版时，依[双语约定](../mcm-paper-writer/references/bilingual-delivery.md)用原冻结工具登记论文资源并运行 [双语静态预检](scripts/audit_bilingual_delivery.py)，检查两版字节、源依赖清单、中文实际页数与逐页记录，保留原英文链。预检不替代人工一致性、视觉和结果复核，英文通过不能隐藏中文版缺失或过期。

赛时重新访问当年官方规则与题面，读 [规则核验](references/official-rules.md)。`assets/rules-2027.json` 是 2026-10-02 核对的参考，复制不等于现场已更新。规则未确认可继续分析，最终可提交结论等待关键规则确认。

## 路由

| 当前请求 | 技能 | 输出 |
|---|---|---|
| 刚发题、选题、盘点、拆解任务 | `$mcm-problem-analyst` | `contracts/problem.json` |
| baseline、方法适配性 | `$mcm-method-retriever` | `contracts/methods.md` |
| 外部数据、引用、代理量 | `$mcm-data-researcher` | `sources/sources.csv` |
| 变量、公式、约束、验证 | `$mcm-model-designer` | `contracts/model.json` |
| Python / MATLAB 实现 | `$mcm-python-coder` / `$mcm-matlab-coder` | `results/run_manifest.json` |
| 独立核对与数字追踪 | `$mcm-result-verifier` | `verification/result_review.json` |
| 中英两版论文和 Summary Sheet | `$mcm-paper-writer` | 两版源稿/PDF、论文清单及双语复核 |
| 渲染、计页、匿名、阅读检查 | `$mcm-layout-verifier` | `verification/layout_review.json` |
| 冻结提交文件、完整性终审 | `$mcm-final-auditor` | `verification/final_audit.json` |

各模块与入口应作为同一套安装。读兄弟模块实际 SKILL.md 再执行；缺模块则明示并完成可执行范围，不假称已过该门禁。

窄请求先给[可行动简报](../mcm-modeling-library/assets/model-selection-brief.md)，只接续当前缺口。按[任务到方法协议](../mcm-modeling-library/references/problem-to-model-protocol.md)相关节协作：拆题定交付/输入，匹配筛前提，设计器确认数学接口；复用有效合同/来源/检查，变化才更新受影响链。正式交接/冻结仍补齐原接口，不能以调用次数或辅助表数量算完成；微检查不能跳过生产求解的模型冻结。

完整解题走任务覆盖→baseline→模型→实现→复核→论文→排版→终审。方法和数据检索可并行，Python/MATLAB 选一条主路线。窄任务只走相关阶段。实质模型选择给出简短差异；已有授权则继续，影响研究目标且未获授权时待用户决定，同时继续独立工作。

时间不足时降低复杂度，保留可解释 baseline、可行性检查、关键独立核对、题设交付物和数字来源，明示未完成项。不得捏造数据或将预检查改名通过。

数据/模型/代码改变使受影响结果和下游检查失效；重新冻结并核对相关链。PDF重新导出后重做渲染检查。AI使用从第一步记入日志，依当年政策生成披露。

结束时准确报告实际完成范围、运行证据和缺项。本地交付通过与 COMAP 正式接收分别记录；只有真实提交凭证才能说明已提交。

## 通用模型库衔接

已安装 `$mcm-modeling-library` 时，模型学习、细分方法或复杂数学机制可调用其相关家族卡，再回到本套件的问题、模型和结果合同。按需读取实际技能文件，不加载全部模型，不自动访问卡中原资料路径。模型卡及合成参考实现属于候选知识，只有本题真实数据与同版本复核才能产生论文证据。未安装时仍可使用本套件的原有方法卡。

## 论文论证与行文

正式比赛论文默认采用用户提供框架提炼的[行文结构](../mcm-paper-writer/references/user-preferred-structure.md)，从准备阶段即按其章节功能安排材料。各模型任务保留准备、建立、结果与结果分析，实际问数和专项交付由题面决定；框架中的旧格式说明不覆盖当届规则。完整结构和大纲在包内，不需要原 Word 文件。

摘要、方法说明、结果解释、结论或memo/letter的起草与修订可由[$mcm-modeling-paper-writing](../mcm-modeling-paper-writing/SKILL.md)辅助；正式论文仍走本套件writer、layout与final链。它连接当前任务与真实证据，保持完整中英交付及 A–C 范围；英文终审通过不等于两版交付完成。普通语言修改更新相应母版/导出及双语检查，数学含义变化回传上游，旧PDF审查不能覆盖新稿。
