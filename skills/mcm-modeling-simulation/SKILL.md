---
name: mcm-modeling-simulation
description: "为 MCM A、B、C 题定义随机机制与决策时间，按分布、链、事件和队列结构选择仿真方法；用于模型设计及风险定向复核。"
---

# MCM mcm-modeling-simulation 建模指南

本技能用于 MCM A、B、C 题的赛时建模、历年题训练与指定材料复现。默认中文协作，完整中英两版论文交付沿用 `mcm-suite` 约定，英文版用于正式提交；Python 与 MATLAB 按当前主路线选择；年度规则、数据许可、冻结与交付由 `mcm-suite` 及当前题目合同负责。

先读 [共享合同](../mcm-modeling-library/references/contracts.md)，再按任务需要从 [模型卡](references/cards.json) 选择，不一次加载全部14卡。Monte Carlo/方差缩减、observed Markov/MDP、MCMC/MH/Gibbs、事件、开放/有限源/有限容量队列、元胞/Brownian/主体。HMM主卡在machine-learning。

把情景与观测分开；平稳分布不等于任意初态的极限。明确源人口、容量、到达率，避免混套排队公式。

- 教学按用户深度解释并手核；实际解题把题设映射到变量/单位、数据与假设、目标/约束、baseline、输出和验证计划。已有上层合同直接承接，不重复造状态。
- 卡中API是实现方向。检查knowledge_level、references的实际核对范围和implementation_evidence；INDEXED_ONLY先补定义/来源，不能用目录名填出“已学会/已验证”。未确认的原始变体保留缺项，当前可继续已审清baseline。
- 需要代码时按冻结定义原创编写，并限当前工作区/依赖环境；教材错误、安装器、未知工具箱、网络/bridge调用不自动继承。Python或MATLAB按用户选择走一条分支，另一语言未运行明确标记。
- 按卡选择解析小例、枚举、独立目标/不变量、边界和敏感性；容差在看差异前按量纲与数值方法声明。不以重复运行同一求解对象替代独立验算。
- 交接模型卡ID/变体、变量单位与假设、来源/输入、参数/切分/求解器、结果/日志、验证证据与限制。上游定义、数据或代码变动使受影响结果/结论STALE，重验相关链。

模型知识、公式、实现方向和已有原创参考脚本随本技能集发布，无需作者机器或原资料目录。来源标签只作溯源；带 `HISTORICAL_METADATA_ONLY` 的旧证据不验收当前包，运行状态以当前源码对应的新报告为准。
