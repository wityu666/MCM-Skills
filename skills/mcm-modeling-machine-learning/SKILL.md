---
name: mcm-modeling-machine-learning
description: "为 MCM A、B、C 题按标签、距离、时点与预测目标选择和验证监督或无监督模型，覆盖树、核、邻域、混合及神经模型；用于设计与资料迁移。"
---

# MCM 机器学习模型与验证

本技能用于 MCM A、B、C 题的赛时建模、历年题训练与指定材料复现。默认中文协作、英文论文，Python 与 MATLAB 按当前主路线选择；年度规则、数据许可、冻结与交付由 `mcm-suite` 及当前题目合同负责。

先读[共享合同](../mcm-modeling-library/references/contracts.md)，按id/别名检索[模型卡](references/cards.json)。具名组件、INDEXED_ONLY总类与模型/算法区分：GOSS/EFB/分位草图不是独立预测模型；BP是训练方法；含保存输出的教材代码不是新验证。

明确任务是分类、回归、密度、聚类、序列、频繁模式还是推荐，并定义标签、评价单位、应用群组/时间及数据边界。排除ID、未来信息和未经许可的替代输入。先建多数类/均值/线性或时序朴素baseline，再根据数据与机制给候选。

- 先切分，再在训练内拟合缩放、插补、特征选择、PCA/PLS或SMOTE。调参、早停、校准和最终评估分别记录数据；同对象/患者/比赛/用户/时点的重叠按实际泛化目标处理。
- 根据目标/样本选树/森林/boosting、SVM/SVR、kNN/NB或网络。逐项解释真实损失、参数域、更新/估计与失败条件；非凸/随机模型报告多初值或seed稳定性，不挑最好运行当结论。
- 聚类先定义距离/尺度和簇含义；隶属度/密度不等于校准类别概率。GMM用统计EM方法，HMM保留隐状态及多序列边界。关联/SHAP/推荐只支持对应的统计或模型解释，不自动给因果证据。
- 预测指标包括对象、阈值、基率、样本集和零分母政策，按任务选择，不设通用accuracy门。序列网络验证真正多步信息集；teacher forcing拟合不当未来预测。

卡中的Python/MATLAB是方向而非已运行证明。核对实际版本/依赖与许可；MathWorks已将newrb/selforgmap/newgrnn/newpnn/narxnet标为将移除，anfis非推荐，使用已读的迁移方向而不直接执行旧包。结构未明的RVM/Hopfield/小波或boost组件保留范围和待核验点，不补造资料没给的完整变体。

交付变量/损失/算法/分割、baseline、独立核验与实际结果证据，并按上层合同处理失效。PCA归evaluation、Shapley合作博弈值归games、观测Markov/MDP/MCMC归simulation、Kalman归control；通过链接交接，避免重复主卡。

模型知识、公式、实现方向和已有原创参考脚本随本技能集发布，无需作者机器或原资料目录。来源标签只作溯源；带 `HISTORICAL_METADATA_ONLY` 的旧证据不验收当前包，运行状态以当前源码对应的新报告为准。

## 归并后的完整模型卡

本家族的补充卡也已编入入口catalog。用入口query_models.py按family/ID读取，或查看[生成的完整指南](references/models.md)；原材料名称与实际模型不一致时，以来源纠正和知识等级为准。
