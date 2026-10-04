---
name: mcm-modeling-time-series
description: "为 MCM A、B、C 题按频率、预测起点和动态结构选择并验证时序模型，涵盖朴素基准、ARIMA、ETS、灰色、GARCH、VAR 与协整。"
---

# MCM 时序模型与未来验证

本技能用于 MCM A、B、C 题的赛时建模、历年题训练与指定材料复现。默认中文协作、英文论文，Python 与 MATLAB 按当前主路线选择；年度规则、数据许可、冻结与交付由 `mcm-suite` 及当前题目合同负责。

先读[共享合同](../mcm-modeling-library/references/contracts.md)，按当前问题读取[相关模型卡](references/cards.json)。INDEXED_ONLY的灰色变体/来源不冒充已核验模型；卡中API方向未运行不升级为实现通过。

先冻结观测频率、发生时间/可知时间、预测起点、跨度、对象群组与数据边界。原序列、差分、对数、季节/外生变量及缺期处理各有单位与还原规则。预测只能消费该起点可用信息，未来外生量未知时给条件情景，不用事后实际值。

- 建立naive/seasonal-naive；历史移动平均不同于ARMA的MA创新项。再按均值、方差、季节、多序列或协整目标选ARMA/ARIMA/SARIMA、ETS、GARCH、VAR/VECM等，不单凭AIC或p值决定。
- 平稳/可逆、协整秩、滞后、确定项、季节长度和有效样本量进入合同。GARCH有限二阶矩与严格平稳不同；灰色模型短样本不意味着可靠长外推，高阶/多变量变体要先读完整原式。
- 使用expanding/rolling起点和任务匹配的留出，调参及缩放/插补/特征选择只用各训练窗口。报告逐跨度误差、区间与baseline，区别一步拟合和真正多步闭环预测；需要群组隔离时同时执行。
- ADF/Ljung–Box是条件诊断，零假设、lag/model_df和确定项要一致；不拒绝不证明模型或独立性。

可用[原创朴素与划分辅助函数](scripts/seasonal_naive.py)并运行[手核/边界测试](scripts/test_seasonal_naive.py)。它们只覆盖该函数与数字时点分割检查，不证明全套时序模型或每个特征的可知时间。本轮MATLAB只给实现方向。

交付公式、符号域、基准、预测信息集、拟合/预测步骤和验收证据。Kalman/状态空间主卡归control，NARX/LSTM/HMM主卡归ML，MDP/MCMC/观测Markov归simulation，通过引用交接。输入、切分、参数或代码改变后按上层合同使受影响验证失效。

模型知识、公式、实现方向和已有原创参考脚本随本技能集发布，无需作者机器或原资料目录。来源标签只作溯源；带 `HISTORICAL_METADATA_ONLY` 的旧证据不验收当前包，运行状态以当前源码对应的新报告为准。
