---
name: mcm-modeling-library
description: "为 MCM A、B、C 题学习、检索和选择模型，按问题结构连接假设、数学、Python 或 MATLAB 实现与验证；用于赛时、历年题训练及复现。"
---

# MCM 建模技能库

本技能用于 MCM A、B、C 题的赛时建模、历年题训练与指定材料复现。默认中文协作、英文论文，Python 与 MATLAB 按当前主路线选择；年度规则、数据许可、冻结与交付由 `mcm-suite` 及当前题目合同负责。

先读[交接约定](references/contracts.md)，遵循用户目标、实际数据与已授权范围。模型知识是候选方法，不是当前题目的参数、证据或结论。

模型知识、公式、实现方向和已有原创参考脚本随本技能集发布，无需作者机器或原资料目录。来源标签只作溯源；带 `HISTORICAL_METADATA_ONLY` 的旧证据不验收当前包，运行状态以当前源码对应的新报告为准。

## 从题目到方法

先给当前建议、依据/条件与下一步的[可行动简报](assets/model-selection-brief.md)。首次或复杂判断按[问题到模型协议](references/problem-to-model-protocol.md)相关节核对任务、数据、依赖和候选前提；正式字段/冻结仍沿用原合同。恢复只处理变化影响并引用有效证据，不重复全库检索或同一事实。需要机器分析交接才用[可选旁表](assets/task-method-analysis.json)，不要求简单任务另填表。

## 选择入口

| 问题结构 | 家族技能 |
|---|---|
| 目标函数、资源/容量、连续或整数决策 | `$mcm-modeling-optimization` |
| 图、路径、网络流、组合、动态规划 | `$mcm-modeling-discrete` |
| 指标、权重、评分、排序 | `$mcm-modeling-evaluation` |
| 分布、回归、关联、效应、检验与区间 | `$mcm-modeling-statistics` |
| 未来序列、趋势、季节与波动 | `$mcm-modeling-time-series` |
| 分类、聚类、非线性学习、神经网络 | `$mcm-modeling-machine-learning` |
| 状态、守恒、动力系统、ODE/PDE | `$mcm-modeling-mechanisms` |
| 随机过程、事件、排队、个体和蒙特卡洛 | `$mcm-modeling-simulation` |
| 隐变量、反推、校准、病态与识别 | `$mcm-modeling-inverse` |
| 插值、拟合基础、求根、积分、线性代数数值 | `$mcm-modeling-numerical` |
| 信号、频谱、图像、几何与特征 | `$mcm-modeling-signals-images` |
| 策略、联盟、合作与竞争 | `$mcm-modeling-games` |
| 反馈、状态估计、稳定性与控制 | `$mcm-modeling-control` |

先确定输出、数据形态、决策、动力学、不确定性及验收；混合任务按依赖串联。读选中兄弟技能实际SKILL.md，再只加载相关模型卡，不把整库放进上下文。

## 按需检索

用`scripts/query_models.py --query 关键词`检索；用`--family optimization`筛选，用`--id 模型ID --full`读取完整卡。登记的模型、方法、求解器和领域辅助工具分别标注。名字相似不能替代假设适配。排序是检索定位，不能把首项或关键词得分直接当最合适模型；读所选卡的minimum_data、assumptions、failure_modes及实际语言实现证据后，给出保留/条件/排除理由。

根据卡的最低数据、假设和失败边界排除不适用方法，选择一个可验证baseline，再考虑新增解释、精度或约束能力的候选。有些模型需要估计或先验，有些只能支持关联；不将其结果升级为因果或真实隐变量。

## 学习所有模型

用户要求整体学习时，按[学习路线](references/learning-map.md)读家族与卡，输出覆盖清单、先修关系、数学和实现要点、已测试范围与缺项。不要把所有工具箱函数、别名或重复源码累计为模型。原资料的新名称若尚无可靠模型卡，保留INDEXED_ONLY并补查数学依据；不标成已经掌握。

本包模型学习直接使用内嵌卡、公式和原创脚本，不需原始资料。若另做指定外部案例复现，用户提供原文件后再检查来源及已知问题；历史来源标签不充当可打开路径。参见[便携来源说明](references/source-provenance.md)。比赛中沿用上层的数据许可、资料和AI政策，不搜索当前题成品答案。

## 从知识到当前问题

MCM 训练可推导小例，不要求虚构比赛输入；实际任务逐项映射题设、变量、单位、参数和约束。已有 MCM `contracts/model.json` 则沿用它；单独学习或尚未进入正式冻结的局部设计可用[模型学习合同](assets/model-contract.json)记录草稿。参见[MCM 流程适配](references/competition-adapters.md)，避免两套状态或模型定义冲突。

实现选择Python或MATLAB主路线，读真实源码、检查当前依赖与版本；本库参考实现也有适用边界。Python通过不说明MATLAB已运行。按风险做独立目标/约束、解析特例、边界、时间/分组验证及敏感性，而不是把同一脚本重跑当正确性证明。

数据、公式、参数或代码变化使受影响证据STALE；重新冻结并重验相关链。只将真实运行、同版本有效复核的结果交给论文/决策；卡中合成数字和资料宣传标签不能消费为证据。

结束时说明选用模型、理由、真实运行/验证范围、未识别量与回退。知识覆盖、理论指南、参考实现测试和真实案例复现分开报告。

## 模型知识与论文表达

选中模型的数学对象、适用条件、选择理由与验证边界可交给[$mcm-modeling-paper-writing](../mcm-modeling-paper-writing/SKILL.md)组织为英文论文论证，并用中文协作说明依据。模型卡是知识来源；卡中合成例子、实现测试和历史论文标签不能变成本题结果。保持现有比赛入口的规则、冻结与复核合同，不新建第二条论文状态链。
