---
name: mcm-modeling-numerical
description: "为 MCM A、B、C 题按函数域与误差需求选择求根、插值、求积及线性代数方法；用于学习、数学设计和风险定向复核。"
---

# MCM mcm-modeling-numerical 建模指南

本技能用于 MCM A、B、C 题的赛时建模、历年题训练与指定材料复现。默认中文协作，完整中英两版论文交付沿用 `mcm-suite` 约定，英文版用于正式提交；Python 与 MATLAB 按当前主路线选择；年度规则、数据许可、冻结与交付由 `mcm-suite` 及当前题目合同负责。

先读 [共享合同](../mcm-modeling-library/references/contracts.md)，再按任务需要从 [模型卡](references/cards.json) 选择，不一次加载全部13卡。括区间求根、Newton/割线、Newton/Lagrange/分段/样条/多维插值、差分/求积、符号/Laplace、线性系统与谱。

先确认函数域、重复节点、边界/初值和停止标准；误差估计/数值收敛不证明模型机理或外推正确。

- 教学按用户深度解释并手核；实际解题把题设映射到变量/单位、数据与假设、目标/约束、baseline、输出和验证计划。已有上层合同直接承接，不重复造状态。
- 卡中API是实现方向。检查knowledge_level、references的实际核对范围和implementation_evidence；INDEXED_ONLY先补定义/来源，不能用目录名填出“已学会/已验证”。未确认的原始变体保留缺项，当前可继续已审清baseline。
- 需要代码时按冻结定义原创编写，并限当前工作区/依赖环境；教材错误、安装器、未知工具箱、网络/bridge调用不自动继承。Python或MATLAB按用户选择走一条分支，另一语言未运行明确标记。
- 按卡选择解析小例、枚举、独立目标/不变量、边界和敏感性；容差在看差异前按量纲与数值方法声明。不以重复运行同一求解对象替代独立验算。
- 交接模型卡ID/变体、变量单位与假设、来源/输入、参数/切分/求解器、结果/日志、验证证据与限制。上游定义、数据或代码变动使受影响结果/结论STALE，重验相关链。

本库原创 [Python参考](assets/numerical_reference.py) 与 [测试](tests/test_reference.py) 可作小规模起点；仅测试记录列明的Python范围通过，不代表真实案例或所有算法通过。

模型知识、公式、实现方向和已有原创参考脚本随本技能集发布，无需作者机器或原资料目录。来源标签只作溯源；带 `HISTORICAL_METADATA_ONLY` 的旧证据不验收当前包，运行状态以当前源码对应的新报告为准。

## 归并后的完整模型卡

本家族的补充卡也已编入入口catalog。用入口query_models.py按family/ID读取，或查看[生成的完整指南](references/models.md)；原材料名称与实际模型不一致时，以来源纠正和知识等级为准。
