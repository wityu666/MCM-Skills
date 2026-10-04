# machine-learning 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## AdaBoost


模型ID `ml-adaboost`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


通过样本重权弱学习器组合分类。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 经典式标签±1且弱分类器e<0.5；多类/回归是不同变体。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- e_m加权误差；w_i样本权重；α_m投票系数。

二类α_m=0.5 log[(1-e_m)/e_m]；w_i←w_i exp(-α_m y_i h_m(x_i))归一；H=signΣα_m h_m。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.ensemble.AdaBoostClassifier
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcensemble(Method="AdaBoostM1")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 一轮手算e/α/权重；e=0或≥0.5明确停止/处理。
- expected 权重非负和为1，变体与损失一致。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 噪声/异常点权重膨胀、混用SAMME/二类式。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Ensembles
- url https://scikit-learn.org/stable/modules/ensemble.html
- checked_at 2026-10-04
- evidence verified_primary


## ANFIS神经模糊推断


模型ID `ml-anfis`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


拟合Sugeno规则系统的前件/线性后件。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 规则数量、隶属度和分母正；可解释不代表因果。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- μ隶属度；r规则；a_r,b_r线性后件。

Sugeno规则r：权w_r=Πj μ_rj(x_j)，f_r=a_rᵀx+b_r；ŷ=Σw_rf_r/Σw_r；交替拟合前件/后件。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创membership+加权线性后件；第三方ANFIS先核验
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - genfis
- tunefis(tunefisOptions(Method="anfis"))
- dependencies - MATLAB
- Fuzzy Logic Toolbox
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 线性回归/少量规则

- - check 核心数学/小例
- method 手工两条规则输出、权重归一；训练/检查数据分离。
- expected 输出符合Sugeno式，规则未激活时定义明确。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 规则组合指数增长、sumw=0、过拟合；anfis非推荐旧接口。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks anfis / tunefis
- url https://www.mathworks.com/help/fuzzy/anfis.html
- checked_at 2026-10-04
- evidence verified_primary


## Apriori关联规则


模型ID `ml-association-apriori`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


挖掘频繁项集和阈值关联规则。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 事务去重/粒度、最低support/confidence预先定义；关联不等因果。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- A∩B=∅项集；N事务数；support为频数/N。

support(A→B)=P̂(A∪B)；confidence=P̂(A∪B)/P̂(A)；lift=confidence/P̂(B)；频繁项集满足支持度反单调。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 按事务去重和阈值定义频数。
- 连接候选，用支持反单调剪枝，再扫描计数。
- 从频繁集合生成规则并核算confidence/lift及独立事务验证。

Python - apis - mlxtend.frequent_patterns.apriori/association_rules
- dependencies - mlxtend
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创频数计数/候选剪枝
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 直接计数枚举

- - check 核心数学/小例
- method 小事务表枚举支持度、置信度和lift；A空支持分母拒绝。
- expected 频数与集合事件吻合，规则在独立事务验证。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 低基率巨大lift、重复交易、组合爆炸、选择偏差。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Agrawal and Srikant Apriori
- url https://www.vldb.org/conf/1994/P487.PDF
- checked_at 2026-10-04
- evidence verified_primary


## FP-growth频繁模式


模型ID `ml-association-fpgrowth`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


以压缩条件模式挖掘同口径频繁项集。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 与Apriori同事务/阈值口径；压缩不更改频数。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- FP-tree节点count；条件模式基；minsup频数/比例明确。

按频率顺序把事务压缩为FP-tree，对条件模式基递归挖掘频繁项集；规则指标沿用支持/置信/lift。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 按频数排序并建FP-tree。
- 递归条件模式基/树挖掘频繁项集。
- 用独立枚举/Apriori对照后生成规则。

Python - apis - mlxtend.frequent_patterns.fpgrowth
- dependencies - mlxtend
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创FP-tree或核验外部接口
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Apriori/直接枚举

- - check 核心数学/小例
- method 小表与Apriori/枚举的频繁项集完全对照。
- expected 同阈值得到同项集，顺序只影响树组织。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 稠密长事务低阈值输出爆炸、计数丢失。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title mlxtend fpgrowth
- url https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/
- checked_at 2026-10-04
- evidence verified_primary
- - title Agrawal and Srikant Apriori
- url https://www.vldb.org/conf/1994/P487.PDF
- checked_at 2026-10-04
- evidence verified_primary


## 有向无环贝叶斯网络


模型ID `ml-bayesian-network`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用有向无环图及条件分布表示联合概率，并对已观察证据作条件推断。


### 输入和适用条件

- 变量及类型
- DAG或明确的结构学习方案
- 条件概率表/分布参数及数据来源
- 图无有向环
- 条件分布正规化并覆盖状态
- 从观测学到的图不能自动认定为因果图；因果解释需额外识别条件


### 数学核心

- X_i为随机变量；Pa_i为其父节点；E为观测证据

p(x_1,...,x_n)=∏_i p(x_i|x_{Pa_i})；查询p(Q|E)=Σ_{H}p(Q,H,E)/p(E)，连续隐变量将求和换成积分。

依具体应用设定；此方法本身不自动定义预算、控制或因果目标。


### 求解和实现

- 明确结构来源和变量状态
- 在训练内估计CPT或连续条件模型，声明先验和缺失机制
- 用变量消元/树传播或条件合适的采样推断
- 检查概率、预测校准和结构敏感性

Python - apis - 维护版本的pgmpy离散/连续接口，先核对具体类名
- dependencies - 按实际接口确认维护版本
- implementation_notes - 接口方向，不代表已运行当前问题；在训练/拟合范围内确定数据处理。

MATLAB - apis - 用户授权且版本/许可已检查的BNT；或按定义实现小型CPT推断
- dependencies - 按实际工具箱和版本确认
- implementation_notes - 本次未运行MATLAB；不把同名函数或外部工具箱视作已经可用。


### 验证和回退

Baseline 独立变量模型或两节点CPT手算

- - check 联合概率
- method 小离散网络枚举全状态
- expected 概率非负且和为1
- - check 推断
- method 两节点Bayes公式独立核算
- expected 条件概率与手算一致
- - check 结构边界
- method 检查环、Markov等价和识别假设
- expected 不把关联推断升级因果效果

- 循环图、零证据概率、稀疏CPT、结构非识别、先验支配、把HMM当任意DAG

简化DAG/独立或朴素Bayes基准；保留不确定性，不补造隐藏关系


### 来源边界

- - title Bayes Net Toolbox original-maintainer project locator
- url https://github.com/bayesnet/bnt
- checked_at None
- evidence reference_only
- inspection_scope 材料中的BNT名称与本库按概率定义独立审阅；此网页未读取。


## 树提升组件、LambdaMART与RGF选型指南

模型ID `ml-boosting-components`　类别 `auxiliary`　知识等级 `THEORY_GUIDE_REVIEWED`

区分加速组件、按query排序树与正则森林；给出可冻结的数学起点。

### 输入和适用条件

- 监督任务X/y；排序任务还需query组和组内相关度标签；切分按实际时点/群组。
- 加速组件需原GBDT目标、梯度/Hessian、稀疏特征冲突与内存预算。
- GOSS/EFB/分位草图是实现组件，不能被报告成新增独立预测模型。
- LambdaMART只在同一query内配对；NDCG的gain、discount、cutoff、全零标签约定要声明。
- RGF必须声明损失与正则形式，不能和普通随机森林或不重估旧权重的GBDT混用。

### 数学核心

**记号**

- g_i负梯度；A为最大|g|的a*n个样本，B从其余样本抽b*n个，0<b≤1-a。
- 排序s_i=F(x_i)，y_i>y_j为同query偏好，D_ij=|交换i/j后的NDCG变化|，σ>0。
- 森林叶规则b_v(x)=I(x落在叶v)，系数α_v；λ_reg≥0。

**定义与更新**

- GOSS切分统计：高梯度项权1，小梯度B项重权(1-a)/b；用于恢复被抽样小梯度部分的和。不可混用“抽余集比例”的b定义。
- EFB将互斥/受限冲突的稀疏特征用不同bin偏移合并，保留原特征到bin区间的映射；发生冲突时按实际库规则处理。
- 加权分位定义F_w(z)=Σ_i w_i I(x_i≤z)/Σ_i w_i；w_i≥0且Σw_i>0，近似草图须另声明rank误差和merge/prune规则。
- LambdaMART采用增加高相关项分数的负梯度约定：p_ij=1/(1+exp[σ(s_i-s_j)])，λ_i+=σ D_ij p_ij，λ_j-=同量；h_i,h_j+=σ² D_ij p_ij(1-p_ij)。
- 将各样本λ拟合为回归树，叶R的Newton值γ_R=Σ_R λ_i/Σ_R h_i；F←F+ηΣ_R γ_R I(x∈R)。分母为0要停止/声明正则策略；这是lambda伪梯度路线，不称NDCG的普通可导梯度或全局最优。
- RGF选定叶L2变体：h_F=Σ_leaf α_v b_v；Q(F,α)=L(h_F(X),y)+(λ_reg/2)Σ_leaf α_v²。贪心比较分裂一叶或新增stump，再周期性对全部已有叶权重重优化。原论文更复杂的min-penalty正则是另一个变体。

**目标与边界**

- 预测损失/排序指标由任务确定；query之间不构造配对。RGF固定结构下的权重优化不能证明全森林结构全局最优。

### 求解和实现

- 先选择组件或完整模型并冻结目标、组定义和具体变体。
- 仅训练数据建立bin/稀疏映射或迭代树；保留参数、随机源和训练预算。
- 排序每轮按当前分数计算组内D/λ/h，再拟合树和叶值；RGF交替结构贪心与全叶权重优化。
- 在独立query/时间留出和相同资源预算下与简单基准比较。

**PYTHON**

- apis: lightgbm.LGBMRanker (group/eval_group必须与实际组顺序一致)
- apis: RGF选定变体可按叶指示矩阵+权重优化原创实现；无包内RGF可运行程序承诺
- dependencies: lightgbm
- dependencies: xgboost
- implementation_notes: 本卡为理论与实现指南，未运行LightGBM/XGBoost/RGF。当前API配置需按安装版本文档核对，组件开关不是独立模型。

**MATLAB**

- apis: 明确外部接口，未承诺内置支持
- dependencies: MATLAB
- implementation_notes: 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。

### 验证和回退

Baseline：精确GBDT/每query排序基准

- GOSS/EFB/分位：小精确统计对照抽样加权和；还原bundle bin映射；比较精确加权CDF及声明误差。 验收：采样率定义和权重一致，冲突及近似误差明确。
- LambdaMART：两项目高低相关小例，λ等量反号且高相关项向上；单query交换手核D，禁止跨query配对。 验收：Σ_query λ≈0；全同相关或D=0不产生NaN；报告query留出NDCG而非训练拟合。
- RGF：固定小树对照叶指示矩阵的L2权重目标；固定结构优化前后比较Q；加入叶分裂与新增stump的预算记录。 验收：损失+正则定义一致，所有旧叶权重允许重估；只声明局部/贪心结果。

- 失败边界：query切错或跨query泄漏；NDCG全零分母未处理；lambda符号相反；采样率重权失配；bundle冲突丢信息；把叶L2冒称全部RGF正则。

- 回退：精确GBDT；每query固定规则排序；固定小树+L2叶权重优化。

### 来源边界

- [Ke et al LightGBM](https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)；verified_primary
- [Chen and Guestrin XGBoost](https://arxiv.org/pdf/1603.02754)；verified_primary
- [Burges, From RankNet to LambdaRank to LambdaMART (MSR-TR-2010-82)](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2010-82.pdf)；Targeted read of sections 3, 4.1 and 7; NDCG/lambda convention and algorithm.
- [Johnson and Zhang, Learning Nonlinear Functions Using Regularized Greedy Forest](https://arxiv.org/pdf/1109.0887)；Targeted read of sections II and V, Algorithm 3 and leaf-only L2 regularizer. Other regularizers are not included as tested variants.

本卡补全日期：2026-10-04。新等级仅证明限定数学指南已核验；Python／MATLAB 实现及原场景未运行。

## 卷积神经网络CNN


模型ID `ml-cnn`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用局部共享卷积结构拟合有空间结构的输入。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 局部结构/权重共享适合数据；通道/轴/stride/padding明确。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- W核；c输入通道；k输出通道；i,j空间索引。

y_{i,j,k}=b_k+Σ_{u,v,c}W_{u,v,c,k}x_{i+u,j+v,c}后接激活；深层参数以BP拟合。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - PyTorch Conv2d/TensorFlow Keras Conv2D（API方向待本地确认）
- dependencies - PyTorch或TensorFlow（按所选方向，仅选需要者）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - convolution2dLayer
- trainnet
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 扁平特征线性/小网络

- - check 核心数学/小例
- method 小核手工cross-correlation；输出尺寸与padding；组留出避免同对象图泄漏。
- expected 实现卷积/互相关约定一致，标签按对象分组。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 错轴/空间泄漏、过小样本、把生成图片当新观测。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks Convolution2DLayer
- url https://www.mathworks.com/help/deeplearning/ref/nnet.cnn.layer.convolution2dlayer.html
- checked_at 2026-10-04
- evidence verified_primary


## 协同过滤与评分矩阵分解


模型ID `ml-collaborative-filtering`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


从稀疏评分/反馈为用户物品估计偏好。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- missing不是0分，显式/隐式反馈目标不同；按用户/物品/时间任务切分。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- Ω观察评分集合；u用户,i物品；p/q潜因子；λ≥0。

显式评分：r̂_ui=μ+b_u+b_i+p_uᵀq_i；minΣ_{(u,i)∈Ω}(r-r̂)²+λ(||P||²+||Q||²+||b||²)；邻域型另记录相似度。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 保留观测mask和信息时点并建均值baseline。
- 只对Ω内评分更新偏置/潜因子及正则。
- 独立用户/物品/时间留出与cold-start回退。

Python - apis - surprise.SVD；原创观测mask+SGD
- dependencies - scikit-surprise
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创mask低秩最小二乘/SGD
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 全局/用户/物品均值

- - check 核心数学/小例
- method 低秩小矩阵只在Ω核算损失；cold-start回退测试。
- expected 观测mask未丢，新用户/物品明确回退，避免随机评分拆分夸大冷启动能力。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 稀疏/偏置、曝光选择、未来评分泄漏、把SVD名称当普通完整矩阵分解。

流行度/内容基准，记录冷启动限制。


### 来源边界

- - title Surprise matrix factorization
- url https://surprise.readthedocs.io/en/stable/matrix_factorization.html
- checked_at 2026-10-04
- evidence verified_primary


## DBSCAN密度聚类


模型ID `ml-dbscan`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


按密度可达找到簇并识别噪声。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 距离/尺度和密度阈值适合数据；noise不是缺失观测。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- eps距离阈值；min_samples整数；noise标签。

eps邻域至少min_samples点为核心；按密度可达扩展簇，非可达点标noise。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.cluster.DBSCAN
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - dbscan
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 距离图/单簇

- - check 核心数学/小例
- method 手工核心/边界/噪声点；邻域计数与eps敏感性。
- expected 可达关系与标签可对照，全部noise不伪造簇。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 密度变化大、高维距离退化、边界点顺序依赖。

K-means或层次聚类但改变形状假设。


### 来源边界

- - title scikit-learn Clustering
- url https://scikit-learn.org/stable/modules/clustering.html
- checked_at 2026-10-04
- evidence verified_primary


## 分类/回归树CART


模型ID `ml-decision-tree`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以可检查叶分割拟合分类或连续回归。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 树深度/叶样本限制训练内选择，分类标签与回归响应区分。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- p_k叶类别份额；R叶区域；n_R叶样本数。

分割选择最大加权纯度改善；分类Gini=1-Σp_k²，回归叶内SSE；叶预测类频率/均值。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.tree.DecisionTreeClassifier
- DecisionTreeRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitctree
- fitrtree
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 单层两特征小例手算候选纯度/SSE与叶预测。
- expected 切分与叶输出符合定义；不以训练纯叶当泛化。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过深、少数类叶、ID泄漏、训练范围外回归不能线性外推。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Ensembles
- url https://scikit-learn.org/stable/modules/ensemble.html
- checked_at 2026-10-04
- evidence verified_primary


## 极限学习机ELM


模型ID `ml-elm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用固定随机隐藏层与线性输出拟合预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 随机节点分布/数量和激活明确；随机投影不保证本题泛化。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- H∈R^{n×m}隐藏输出；β输出权重；g激活。

随机固定w_j,b_j，H_ij=g(w_jᵀx_i+b_j)；β̂=H⁺Y；正则变体可min||Hβ-Y||²+λ||β||²。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创numpy随机隐藏层+scipy.linalg.lstsq
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - randn形成H；mldivide/明确pinv阈值
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 固定H独立QR/SVD求解；多seed而不挑最好seed。
- expected 最小二乘残差可核算，秩/条件数与验证误差公开。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 病态H、小样本巨大隐藏层、把速度结论当精度承诺。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Huang Zhu Siew ELM
- url https://extreme-learning-machines.org/pdf/ELM-NC-2006.pdf
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary


## 模糊C-means


模型ID `ml-fuzzy-cmeans`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习模糊隶属度和簇中心。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 模糊隶属度不是自动校准概率；距离和K,m明确。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- m模糊指数；u隶属度；c簇中心。

min ΣiΣk u_ik^m||x_i-c_k||²；Σk u_ik=1,u≥0,m>1；中心为u^m加权均值。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - skfuzzy.cluster.cmeans；版本需核验
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fcm(data,fcmOptions(...))
- dependencies - MATLAB
- Fuzzy Logic Toolbox
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline K-means

- - check 核心数学/小例
- method U每样本和1，中心加权重算；距离0专门处理。
- expected U有效且独立重算目标与中心一致。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 0距离除零、全部相同点、尺度/重叠解释错误。

硬聚类并注明信息丢失。


### 来源边界

- - title MathWorks fcm
- url https://www.mathworks.com/help/fuzzy/fcm.html
- checked_at 2026-10-04
- evidence verified_primary


## 高斯混合GMM


模型ID `ml-gaussian-mixture`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


拟合有限高斯混合密度与软责任。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 有限高斯混合，协方差形式与有效样本量匹配；标签可置换。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- π混合权重；μ均值；Σ协方差；r责任。

p(x)=Σkπ_k N(x|μ_k,Σ_k)；EM责任r_ik=π_kN_k/Σjπ_jN_j。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 选K和协方差结构并初始化。
- EM责任/加权均值协方差更新。
- 检查likelihood、权重/正定、多初值和密度验证。

Python - apis - sklearn.mixture.GaussianMixture
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitgmdist
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 单高斯

- - check 核心数学/小例
- method π≥0和1、Σ正定、责任行和1；likelihood及多初值。
- expected 概率域有效，不要求簇序号在不同运行字面一致。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 协方差塌陷、局部解、过多成分、密度误当类别真值。

少成分+协方差正则或非参数描述。


### 来源边界

- - title scikit-learn Gaussian mixture models
- url https://scikit-learn.org/stable/modules/mixture.html
- checked_at 2026-10-04
- evidence verified_primary


## 高斯过程回归GPR


模型ID `ml-gaussian-process`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以核和噪声生成连续响应的后验均值/方差。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 核PSD、噪声/尺度与超参数明确；有限Gaussian假设而非普遍真实区间。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- K训练核矩阵；k*交叉核；k**自核；σ²>0。

f~GP(m,k)，y=f(X)+ε，C=K+σ²I；m*=k*ᵀC⁻¹(y-m)+m(x*)，v*=k**-k*ᵀC⁻¹k*（latent；观测另加噪声）。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - GaussianProcessRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitrgp
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Ridge/线性GP

- - check 核心数学/小例
- method 小矩阵posterior手算、对称PSD与Cholesky；重复点/noise。
- expected 方差不负于数值容差，latent/观测区间不混淆。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- n大O(n³)、高维/域漂移、优化局部、jitter掩盖非法核。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Gaussian Processes
- url https://scikit-learn.org/stable/modules/gaussian_process.html
- checked_at 2026-10-04
- evidence verified_primary


## 梯度提升树GBDT


模型ID `ml-gradient-boosting`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以损失负梯度逐步加树作监督预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 可导损失、学习率/树深/早停选择只用训练内验证。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- F加性预测；η学习率；ρ步长；L损失。

r_im=-∂L(y_i,F(x_i))/∂F；拟合h_m到负梯度；F_m=F_{m-1}+ηρ_m h_m。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - GradientBoostingClassifier/Regressor
- HistGradientBoostingRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitrensemble(Method="LSBoost")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 平方损失下首轮伪残差是y-F；独立重算每阶段损失。
- expected 所选损失和任务匹配，不由训练下降推断泛化。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过多轮过拟合、未来数据早停、类别域错配。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Ensembles
- url https://scikit-learn.org/stable/modules/ensemble.html
- checked_at 2026-10-04
- evidence verified_primary


## 广义回归网络GRNN


模型ID `ml-grnn`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用核归一回归预测连续响应。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- σ>0且距离/尺度适用；MATLAB spread参数与σ映射要核对。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- K非负核；σ宽度；y_i训练响应。

核回归形式ŷ(x)=Σ_i y_i K_σ(x,x_i)/Σ_i K_σ(x,x_i)，常用Gaussian核；宽度按训练内选择。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创Gaussian核+加权均值
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 自定义kernel；newgrnn仅旧接口
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline kNN回归

- - check 核心数学/小例
- method 两点等距时输出均值；分母0/数值下溢处理。
- expected 核归一和输出范围可核算，宽度不靠测试集选。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 远点下溢、存储全部训练、尺度支配；旧接口将移除。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks newgrnn
- url https://www.mathworks.com/help/deeplearning/ref/newgrnn.html
- checked_at 2026-10-04
- evidence verified_primary


## 层次聚类与链接准则


模型ID `ml-hierarchical-clustering`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


从距离或观测建立嵌套分组，说明链接准则与截断选择。


### 输入和适用条件

- 同尺度样本或合法凝聚距离
- 链接准则和所需分组层次
- 距离的定义符合对象含义
- Ward准则适用Euclidean平方误差几何，不任意用于非Euclidean预计算距离
- 不把树图当作真实类别证据


### 数学核心

- A,B为待合并簇；n_A,n_B为样本数；μ_A,μ_B为均值

single=min_{i∈A,j∈B}d_ij，complete=max d_ij，average=平均d_ij；Ward增量ΔSSE=n_A*n_B/(n_A+n_B)*||μ_A-μ_B||²。

依具体应用设定；此方法本身不自动定义预算、控制或因果目标。


### 求解和实现

- 先确定训练范围内尺度和距离
- 从单点簇开始合并使链接准则最小的一对
- 记录合并高度与成员数
- 按任务选截断并做扰动稳定性

Python - apis - scipy.cluster.hierarchy.linkage
- sklearn.cluster.AgglomerativeClustering
- dependencies - 按实际接口确认维护版本
- implementation_notes - 接口方向，不代表已运行当前问题；在训练/拟合范围内确定数据处理。

MATLAB - apis - linkage
- cluster
- dendrogram
- dependencies - 按实际工具箱和版本确认
- implementation_notes - 本次未运行MATLAB；不把同名函数或外部工具箱视作已经可用。


### 验证和回退

Baseline 两簇/三点距离手算，或与K-means的另一种分组假设对照

- - check 成员守恒
- method 逐层查每对象恰出现一次
- expected 合并后总样本数不变
- - check 链接定义
- method 三点独立手算首个合并及高度
- expected 符合所选链接，不混用准则
- - check 稳定性
- method 尺度和小扰动重算
- expected 报告稳定范围，非强行固定簇数

- 尺度改变导致结果改变
- single链化、异常点、非Euclidean Ward、过度解读树高度

保留距离与描述性树；不能稳定分组时停止类别解释


### 来源边界

- - title scipy.cluster.hierarchy.linkage installed first-party documentation
- url https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.cluster.hierarchy.linkage.html
- checked_at 2026-10-04
- evidence verified_primary
- version 1.15.3
- inspection_scope Local first-party documentation read; web page not represented as visited.
- doc_sha256 0af66d47985fd7f4fc4b65317b56c1954c15f570ff6c311e62ca789a6ee1664e


## 隐马尔可夫模型HMM


模型ID `ml-hmm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


从有序观测推断隐状态概率/路径和发射机制。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 隐状态一阶Markov，给定状态观测条件独立；发射/多序列边界明确。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- z隐状态；A转移；π初态；b发射分布。

p(z,x)=π_{z1}Π_{t>1}A_{z_{t-1},z_t}Π_t b_{z_t}(x_t)；forward/backward求似然与后验，Viterbi求最可能路径。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 明确多序列边界、状态数、发射与初值。
- forward/backward+EM估计；Viterbi/后验按所求输出。
- 检查归一、停止状态、短序列枚举和独立序列。

Python - apis - hmmlearn.GaussianHMM/Discrete variants
- dependencies - hmmlearn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - hmmtrain/hmmdecode/hmmviterbi（离散）；连续发射原创
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 单状态发射模型

- - check 核心数学/小例
- method A行和1、π和1；两状态短序列枚举似然与forward对照。
- expected 概率归一与递推相符，EM局部解/标签置换公开。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 发射错配、奇异协方差、跨序列串接、多初值敏感。

单混合/简单状态描述；Markov观测态主卡转simulation。


### 来源边界

- - title hmmlearn tutorial
- url https://hmmlearn.readthedocs.io/en/stable/tutorial.html
- checked_at 2026-10-04
- evidence verified_primary


## 经典Hopfield关联记忆与优化接口


模型ID `ml-hopfield`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


登记关联记忆/能量型网络并限制同步和连续变体。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 仅本卡对称零对角、bipolar、异步且零场不变的定义；公平更新到无变化。
- 局部固定点/存储模式稳定性与全局最优不同；连续TSP和newhop内部设计需分别核验。


### 数学核心

- v状态；W对称耦合；E能量；b阈值偏置。

经典bipolar离散模型：v∈{-1,1}^n，W=Wᵀ，Wii=0；E=-vᵀWv/2-bᵀv。异步单坐标v_i′=sign(Σj≠i Wijv_j+b_i)，局部场0保持旧态。ΔE=-(v_i′-v_i)H_i≤0。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 明确状态、W对称/零对角、b和初态；可选Hebb权重也要实查所存模式是否稳定。
- 一次更新一个神经元，零场保持；每步独立算ΔE与实际E。
- 无变化完整扫描后输出固定点；同步周期/虚假记忆反例必须报告。

Python - apis - 原创异步更新
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创异步；newhop旧接口需核验
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 直接最近存储模式/小优化枚举

- - check 核心数学/小例
- method 逐次单点更新独立核算E；两点同步振荡反例。
- expected 经典条件下E不增加，约束问题仍独立检验排列/可行性。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 非对称/同步、虚假记忆、TSP处罚/动力不同式。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn neural networks
- url https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- checked_at 2026-10-04
- evidence verified_primary


## K-means


模型ID `ml-kmeans`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


寻找欧氏惯性低的硬簇原型。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 欧氏距离、近球状簇与尺度合理；K训练内/领域确定。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- K簇数；z_i簇指派；c_k中心。

min_{c,z}Σ||x_i-c_{z_i}||²；交替分配最近中心与重算簇均值。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 训练内确定尺度与K/初始化。
- 最近中心分配，非空簇重算均值，按停准则迭代。
- 独立算惯性与空簇，多seed稳定性。

Python - apis - sklearn.cluster.KMeans
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - kmeans
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 单簇/手工两簇小例

- - check 核心数学/小例
- method 两簇小点集核算惯性；空簇/重复点与多初值稳定性。
- expected 迭代不增加目标（精确步骤），空簇明确处理。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 非球状/不均匀密度、常数特征、空簇、局部解。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Clustering
- url https://scikit-learn.org/stable/modules/clustering.html
- checked_at 2026-10-04
- evidence verified_primary


## k近邻分类与回归


模型ID `ml-knn`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以训练邻居的均值/类票作局部预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 距离/尺度符合任务；k和权重训练内选，不把ID当距离。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- k正整数；d距离；N_k邻域。

N_k(x)按距离取k邻居；回归加权均值，分类加权类票归一。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - KNeighborsClassifier
- KNeighborsRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcknn；回归原创邻居均值
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 二维小点集独立算距离、邻居/同距处理与预测。
- expected 邻居集合/投票一致，概率和1。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 维度灾难、量纲支配、标签泄漏、不平衡类。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Nearest Neighbors
- url https://scikit-learn.org/stable/modules/neighbors.html
- checked_at 2026-10-04
- evidence verified_primary


## LightGBM高效树提升


模型ID `ml-lightgbm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以高效树学习组件实现GBDT预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- GOSS/EFB为算法变体，原论文条件及当前参数需区分。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- g样本梯度；a保留大梯度比例；b小梯度采样比例。

GBDT目标；GOSS保留大梯度并对子采样小梯度重加权；EFB把近互斥稀疏特征合并以减少扫描。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - lightgbm.LGBMClassifier
- LGBMRegressor
- dependencies - lightgbm
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 明确外部bridge；未验证当前MATLAB实现
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 与GBDT基准对照；抽样权重和稀疏合并冲突审计。
- expected 未将速度宣传当任务精度，留出/早停可追溯。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 小数据叶式生长过拟合、特征bundle冲突、类别映射漂移。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Ke et al LightGBM
- url https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf
- checked_at 2026-10-04
- evidence verified_primary


## 长短期记忆LSTM


模型ID `ml-lstm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以门和记忆状态学习序列监督映射。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 门/状态/序列输出布局明确；需足够数据而非自动优于AR。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- i/f/o∈(0,1)输入/遗忘/输出门；c记忆；⊙逐元素乘。

i,f,o=σ(W[x_t,h_{t-1}]+b)，g=tanh(...); c_t=f_t⊙c_{t-1}+i_t⊙g_t，h_t=o_t⊙tanh(c_t)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - PyTorch LSTM/TensorFlow Keras LSTM（方向）
- dependencies - PyTorch或TensorFlow（按所选方向，仅选需要者）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - lstmLayer
- trainnet
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline AR/seasonal-naive

- - check 核心数学/小例
- method 门饱和/清零小例、状态shape；多步滚动留出与naive。
- expected c/h递推核对，训练与未来评估隔离。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 大量参数小样本、随机时序划分、归一化/窗口泄漏。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks LSTMLayer
- url https://www.mathworks.com/help/deeplearning/ref/nnet.cnn.layer.lstmlayer.html
- checked_at 2026-10-04
- evidence verified_primary


## 学习向量量化LVQ


模型ID `ml-lvq`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


登记监督原型量化的经典LVQ1更新。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 原型有类标签，η计划明确；LVQ变体不是同一更新式。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- w_c原型；η>0；c最近原型。

经典LVQ1：最邻近原型w_c；若类标签匹配w_c+=η(x-w_c)，否则w_c-=η(x-w_c)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 训练内选择尺度与带类标签原型，定义最近赢家/并列规则。
- 按classic LVQ1正确类拉近、错误类推远，0<η<1并有停止上限。
- 独立核算方向和距离、原型标签；LVQ2/OLVQ等更新不得直接套同式。

Python - apis - 原创prototype更新
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 自定义loop；lvqnet旧接口需再核验
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline kNN

- - check 核心数学/小例
- method 二维单步拉近/推远手算，η=0不变。
- expected 原型标签/方向一致，验证独立。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 错误距离尺度、稀有类原型不足、变体混用。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Nearest Neighbors
- url https://scikit-learn.org/stable/modules/neighbors.html
- checked_at 2026-10-04
- evidence verified_primary
- - title MathWorks learnlv1 algorithm, read this round
- url https://www.mathworks.com/help/deeplearning/ref/learnlv1.html
- checked_at 2026-10-04
- evidence verified_primary


## 前馈MLP与BP训练


模型ID `ml-mlp-bp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用前馈非线性网络与BP拟合监督目标。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- BP是训练方法，拓扑/损失由任务决定；尺度、初始化与容量需验证。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- h_l层状态；W_l矩阵；σ激活；L任务损失。

h_l=σ(W_lh_{l-1}+b_l)；按链式法则∂L/∂W反向传播，min empirical loss+regularization。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - MLPClassifier
- MLPRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcnet/fitrnet
- trainnet/dlnetwork
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 小网络有限差分检验梯度；单层退化线性/Logit。
- expected 梯度与维数一致，验证早停独立。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 非凸局部解、饱和梯度、小样本过拟合、全数据缩放。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn neural networks
- url https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- checked_at 2026-10-04
- evidence verified_primary


## 朴素贝叶斯


模型ID `ml-naive-bayes`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


从类先验和条件独立似然作分类概率。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 给定类的条件独立是假设；计数/二值/连续分布不能混用。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- c类别；j特征；类别先验和类条件似然。

P(c|x)∝P(c)∏jP(x_j|c)，在log域求和；Gaussian/Multinomial/Bernoulli各有观测域。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - GaussianNB
- MultinomialNB
- BernoulliNB
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcnb
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 二特征二类手算后验；稀疏0计数检查平滑。
- expected 后验非负归一，观测域符合分布。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 强相关特征导致过度置信、负计数、零概率。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Naive Bayes
- url https://scikit-learn.org/stable/modules/naive_bayes.html
- checked_at 2026-10-04
- evidence verified_primary


## NARX外生非线性自回归


模型ID `ml-narx`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以响应历史/外生延迟学习非线性时序映射。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 外生u在预测起点可用；0延迟变量不可偷用未来信息。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- p/q反馈/输入延迟；u外生输入；f非线性映射。

y_t=f(y_{t-1:t-p},u_{t:t-q})；开环训练用真实历史反馈，闭环多步用先前预测。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创lag features+MLP/递归闭环
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - trainnet/dlnetwork；narxnet仅旧接口
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline ARX/naive

- - check 核心数学/小例
- method 同数据比较开环一步与真实闭环多步；边界state初始化。
- expected 多步反馈确用预测值，exog来源可追溯。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 闭环用未来真实y、随机划分时序、未知未来u、旧接口将移除。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks narxnet
- url https://www.mathworks.com/help/deeplearning/ref/narxnet.html
- checked_at 2026-10-04
- evidence verified_primary


## 单层感知机


模型ID `ml-perceptron`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习单层线性二类分类器。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 二类线性决策边界；可分条件才有相应收敛结论。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- y±1；w权重；b截距；η>0。

ŷ=sign(wᵀx+b)；误分时w←w+ηyx，b←b+ηy。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.linear_model.Perceptron
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创更新；不是任意BP网络
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method OR可分小例与XOR不可分反例；X/y长度严格一致。
- expected 更新仅在误分，XOR失败如实报告。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 非线性可分、标签/样本zip截断、无最大迭代。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary


## 概率神经网络PNN


模型ID `ml-pnn`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用类条件核密度与先验估计分类后验。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 类先验/核宽度和密度单位明确；密度值不直接等于概率。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- n_c类样本数；π_c先验；K核密度。

Parzen形式p(x|c)=(1/n_c)Σ_{i:y_i=c}K_σ(x,x_i)；P(c|x)∝π_c p(x|c)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创类条件核密度
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 自定义kernel；newpnn仅旧接口
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Naive Bayes/kNN

- - check 核心数学/小例
- method 两类对称小例、后验行和1、宽度敏感。
- expected 先归一后验，正确区别密度/概率与类先验。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 高维核退化、先验不匹配、极度置信；旧接口将移除。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks newpnn
- url https://www.mathworks.com/help/deeplearning/ref/newpnn.html
- checked_at 2026-10-04
- evidence verified_primary


## 学习管道与预测指标


模型ID `ml-preprocessing-validation`　类别 `auxiliary`　知识等级 `THEORY_GUIDE_REVIEWED`


构建不泄漏的学习管道和定义一致的预测指标。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 数值/类别变换、缺失意义、对象/时点划分与零分母政策固定。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- TP/FP/FN事件计数；e=y-ŷ；T只训练估计。

训练fold拟合变换T；ŷ=f(T(X))；MAE=mean|e|，MSE=mean e²；precision=TP/(TP+FP)，recall=TP/(TP+FN)，F1=2TP/(2TP+FP+FN)。；AUC的排序定义为P(score_pos>score_neg)+0.5P(tie)，不是固定分类阈值accuracy；具体ROC实现/变体仍按接口核验。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - Pipeline
- ColumnTransformer
- sklearn.metrics
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 训练内fit/apply参数及独立评估原创流程
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline DummyClassifier/Regressor与时间朴素

- - check 核心数学/小例
- method 独立算混淆矩阵；只改测试数据不得改变训练变换参数；group/time泄漏检查。
- expected 所有指标含对象/阈值/样本集口径；调参/校准/最终评估分离。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- ID/未来变量、全样本缩放插补/PCA、未分离群组、零分母伪0。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Common pitfalls
- url https://scikit-learn.org/stable/common_pitfalls.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Probability calibration
- url https://scikit-learn.org/stable/modules/calibration.html
- checked_at 2026-10-04
- evidence verified_primary


## 概率校准


模型ID `ml-probability-calibration`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在独立校准预测上改进概率口径。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 校准数据独立于模型拟合，类别基率与应用一致。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- s原分数；q校准概率；A,B拟合参数。

校准器q(s)：sigmoid q=1/(1+exp(As+B))或单调isotonic；按留出预测分数与y拟合。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - CalibratedClassifierCV
- calibration_curve
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 独立校准集+Logit/isotonic方向
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 原概率/类频率

- - check 核心数学/小例
- method 可靠度分箱、logloss/Brier以及校准样本量；测试标签不参与校准。
- expected 区分概率区分能力和校准，低Brier不单独宣称更好校准。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 复用训练标签、isotonic少样本过拟合、基率漂移。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Probability calibration
- url https://scikit-learn.org/stable/modules/calibration.html
- checked_at 2026-10-04
- evidence verified_primary


## 随机森林


模型ID `ml-random-forest`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


聚合随机树作分类/回归并检查稳定性。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 树和随机特征依赖样本；OOB可辅助但不能替代时间/群组留出。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- B树数；T_b树预测；特征随机子集。

对bootstrap样本/随机特征的B棵树取平均或投票；ŷ=B⁻¹ΣT_b(x)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.ensemble.RandomForestClassifier
- RandomForestRegressor
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - TreeBagger
- fitcensemble(Method="Bag")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 多棵预测独立求平均；分类概率和为1；种子重复区间。
- expected 聚合吻合且独立留出不泄漏。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 时间相关时OOB误解释、重要性偏好高基数、模型很大。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Ensembles
- url https://scikit-learn.org/stable/modules/ensemble.html
- checked_at 2026-10-04
- evidence verified_primary


## 径向基网络RBF


模型ID `ml-rbf-network`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用径向基与线性输出逼近响应函数。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 中心/宽度训练内确定，s_j>0；RBF不同于RBF-SVM。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- c_j中心；s_j宽度；a_j线性输出权重。

φ_j(x)=exp[-||x-c_j||²/(2s_j²)]；f(x)=Σa_jφ_j(x)+b；给定基后线性拟合输出。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创basis+scipy.linalg.lstsq
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 自定义层/核特征；newrb仅旧接口
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 固定基核算输出/最小二乘；宽度极限与病态矩阵。
- expected 输出与基/权重吻合，不由训练MSE目标宣称泛化。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过窄宽度过拟合、过宽秩退化、newrb将移除。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks newrb
- url https://www.mathworks.com/help/deeplearning/ref/newrb.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary


## 简单递归网络RNN


模型ID `ml-rnn`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


登记有状态反馈的序列预测网络及边界。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 序列有序，状态重置边界/截断长度明确；未来标签不可输入。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- h_t隐藏态；t序列步；W_x/W_h输入/递归矩阵。

经典Elman/RNN一层：h_t=tanh(W_x x_t+b_x+W_h h_{t-1}+b_h)，ŷ_t=g(W_y h_t+c)。完整BPTT沿时间链求导；relu是实际接口支持的激活变体。多层/双向/延迟需明确状态布局。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 定义序列边界、初始h0、输入/隐藏/输出矩阵和因果时点。
- 按递推前向；采用完整时间链梯度或明确的截断/旧简化规则，不静默混同。
- 核验两步手算/状态重置、训练窗口和真正多步留出。

Python - apis - torch.nn.RNN（本机2.12.1文档已读，未训练运行）
- dependencies - PyTorch或TensorFlow（按所选方向，仅选需要者）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - dlnetwork自定义递归层
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。
- 已读elmannet官方说明：旧Elman训练staticderiv忽略延迟连接，不能与完整BPTT混同；它与newelm均为旧流程，未执行。


### 验证和回退

Baseline AR/naive

- - check 核心数学/小例
- method h初值0的两步手算；短序列有限差分梯度；边界重置。
- expected 状态和时间索引一致，预测只消费已知信息。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 梯度消失/爆炸、跨独立序列状态污染、teacher forcing漏未来。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title MathWorks LSTMLayer
- url https://www.mathworks.com/help/deeplearning/ref/nnet.cnn.layer.lstmlayer.html
- checked_at 2026-10-04
- evidence verified_primary
- - title Installed PyTorch 2.12.1 torch.nn.RNN first-party docstring
- url https://docs.pytorch.org/docs/2.12/generated/torch.nn.RNN.html
- checked_at 2026-10-04
- evidence verified_primary
- source_kind installed_first_party_documentation
- source_sha256 45ba488838119cda365fa304f3638335b584c4c4b6da353a43d4f368da8f0e67
- docstring_sha256 16803eab32a680551a7d269c1431d0fffdc7d38abb54c381704ba0685eba95bf


## 相关向量机RVM/ARD


模型ID `ml-rvm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


登记Gaussian回归ARD/RVM候选及待核验原理论。


### 输入和适用条件

- 回归：连续y、固定Φ基矩阵、Gaussian噪声/ARD先验；二分类另需Bernoulli标签和Laplace近似。
- 超参数域、bias基、初始化、精度/裁剪/停止规则及独立留出。
- 此处仅Gaussian回归型，分类近似另议；超参数识别和数值稳定需补理论核验。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- Φ基矩阵；α>0精度；σ²噪声方差；m/Σ后验均值/协方差。

Gaussian回归：y=Φw+ε，ε~N(0,σ²I)，w~N(0,A^-1)，A=diagα>0；Σ=(ΦᵀΦ/σ²+A)^-1，m=ΣΦᵀy/σ²。C=σ²I+ΦA^-1Φᵀ，log evidence=-[n log2π+log|C|+yᵀC^-1y]/2；γ_i=1-α_iΣ_ii，αnew_i=γ_i/m_i²，σ²new=||y-Φm||²/(n-Σγ)。新观测var=σ²+φ*ᵀΣφ*；hyperparameter mode是full Bayes近似。

uniform scale-hyperprior条件下type-II证据最大化；α,σ²>0，近0均值/非正有效自由度/病态需明确处理。不是任意RVM版本共享固定剪枝阈值。


### 求解和实现

- 定义Φ/噪声/ARD先验，固定初值及参数域。
- 条件Gaussian posterior用线性求解；更新证据或所选作者再估计式，检查正定/有效自由度与停止，多初值。
- 按实际裁剪规则作独立预测/区间检查；Bernoulli版本改MAP+Laplace而不沿用Gaussian噪声方差。

Python - apis - 原创核Φ+ARD证据优化；ARDRegression仅线性ARD方向
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创ARD/似然方向，无内置RVM承诺
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Ridge

- - check 核心数学/小例
- method 固定α/σ与手算Gaussian posterior比较；多初值/pruning敏感。
- expected 不由稀疏结果声称真实重要变量；原论文关键段核验后再升级。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- m_i≈0、α无穷/裁剪、n-Σγ≤0、病态基、多证据局部解；不同hyperprior更新不同。
- 二分类没有Gaussian噪声σ²，须MAP/Laplace；概率预测的后验积分不等于直接sigmoid(MAP)。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Tipping Sparse Bayesian Learning and the Relevance Vector Machine
- url https://www.jmlr.org/papers/volume1/tipping01a/tipping01a.pdf
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04
- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary


## SHAP模型预测解释


模型ID `ml-shap`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按明确背景分布解释已训练模型的预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 解释对象是已训练模型；条件/干预式背景及依赖特征选择改变归因。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- φ₀背景基值；φ_j模型预测贡献；p特征数。

f(x)=φ₀+Σφ_j；φ_j对所有特征子集的边际预测贡献按Shapley权重平均，value函数/背景分布必须明确。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - shap.Explainer/TreeExplainer（方向需版本）
- dependencies - shap
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - shapley（功能范围需实际版本核对）
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 线性系数/置换重要性（非同一对象）

- - check 核心数学/小例
- method 线性两特征模型枚举所有子集；检查base+sumφ=f(x)和背景敏感性。
- expected local accuracy成立于所选解释定义，不由归因推出因果。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 相关特征任意拆分、背景不代表应用、把SHAP占比当真实因果重要度。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Lundberg and Lee SHAP
- url https://arxiv.org/pdf/1705.07874
- checked_at 2026-10-04
- evidence verified_primary


## SMOTE训练内过采样


模型ID `ml-smote`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


仅在训练内生成少数类插值样本。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 连续特征距离适用，少数类样本>邻居数；类别/混合特征需相应变体。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- δ插值比例；k邻居数；x_new合成训练点。

少数类邻居x_j，x_new=x_i+δ(x_j-x_i)，δ∈[0,1]；只对训练fold插值，之后再拟合分类器。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 先隔离训练/验证/测试。
- 训练fold内找少数类邻居并插值，再拟合模型。
- 原验证分布评估及检查合成样本身份。

Python - apis - imblearn.over_sampling.SMOTE
- imblearn.pipeline.Pipeline
- dependencies - scikit-learn
- imbalanced-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 原创邻域插值，MATLAB接口不作承诺
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 类权重/不重采样

- - check 核心数学/小例
- method 新点在线段内；保留验证/测试原始分布；不把生成点当新观测。
- expected 采样只训练内，评价原基率与业务代价。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 全数据SMOTE后再切分、噪声过采样、高维距离/稀有小类。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title imbalanced-learn Over-sampling
- url https://imbalanced-learn.org/stable/over_sampling.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Common pitfalls
- url https://scikit-learn.org/stable/common_pitfalls.html
- checked_at 2026-10-04
- evidence verified_primary


## 自组织映射SOM


模型ID `ml-som`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习保留网格拓扑的无监督原型映射。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 固定网格拓扑/距离；有序映射不是监督分类概率。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- w_j原型；η学习率；h邻域核；BMU最佳匹配单元。

BMU=argminj||x-w_j||；w_j←w_j+η h_{j,BMU}(x-w_j)，邻域和η逐步缩小。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 原创numpy SOM循环；第三方接口先核验
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - dlnetwork自定义SOM；selforgmap仅旧接口
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline K-means

- - check 核心数学/小例
- method BMU小例、η=0不更新、邻域半径极限与拓扑误差。
- expected 邻域更新方向正确；多seed量化/拓扑误差公开。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 尺度支配、拓扑扭曲、参数任意、旧MATLAB接口将移除。

K-means失去网格拓扑解释。


### 来源边界

- - title MathWorks selforgmap
- url https://www.mathworks.com/help/deeplearning/ref/selforgmap.html
- checked_at 2026-10-04
- evidence verified_primary


## 支持向量分类SVC


模型ID `ml-svc`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习核间隔分类边界。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 核/尺度有依据，C/gamma训练内选择；概率需单独拟合。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- y_i∈{-1,1}；C>0；ξ松弛；φ特征映射。

min 0.5||w||²+CΣξ_i；y_i(wᵀφ(x_i)+b)≥1-ξ_i，ξ_i≥0；核K=φᵀφ。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.svm.SVC
- LinearSVC
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcsvm
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 线性可分小例手核间隔；核矩阵对称PSD（适用核）。
- expected 约束/分类方向成立，概率不直接等于间隔分数。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 大样本核矩阵、错误尺度/核、不平衡类、概率未校准。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Support Vector Machines
- url https://scikit-learn.org/stable/modules/svm.html
- checked_at 2026-10-04
- evidence verified_primary


## 支持向量回归SVR


模型ID `ml-svr`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习epsilon不敏感核回归函数。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 响应/特征尺度、ε的业务单位及核参数明确。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- ε不敏感带宽（响应单位）；C松弛惩罚。

min 0.5||w||²+CΣ(ξ_i+ξ_i*)；|y_i-f(x_i)|≤ε+相应松弛；epsilon-insensitive损失。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.svm.SVR
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitrsvm
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method ε=0和线性小例核算双侧残差约束。
- expected 管道与变量单位一致，留出误差对照baseline。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- ε单位错、样本量大核计算、非平稳、训练R²当未来预测。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn Support Vector Machines
- url https://scikit-learn.org/stable/modules/svm.html
- checked_at 2026-10-04
- evidence verified_primary


## 小波NN：本资料Morlet-like激活前馈变体


模型ID `ml-wavelet-network`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


审查已见源码的非线性激活网络、尺度/平移和训练导数；不冒称唯一小波网络或正交变换。


### 输入和适用条件

- X/连续Y的真实训练与未来留出，M/N与层数、basis及输出偏置定义。
- 本资料scalar basis函数；多输出更新应按输出索引，不能复用来源广播错误。
- 本卡仅已见Morlet-like激活前馈结构；其未零均值校正，不主张严格admissible/正交wavelet基。
- 梯度按明确训练损失推导；不能照抄源d_a；a避免0，时序数据按信息集划分。


### 数学核心

- x∈R^M；w_j输入方向；a_j≠0尺度（可选择a_j>0重参数化）；b_j平移。
- z_j=(w_jᵀx-b_j)/a_j；v_j输出权重；q输出偏置若选用。

h_j=ψ(z_j)，ψ(z)=exp(-z²/2)cos(1.75z)，ŷ=Σ_j v_j h_j（本来源无输出偏置）。ψ′=exp(-z²/2)[-1.75sin(1.75z)-zcos(1.75z)]；dz/da=-z/a，dz/db=-1/a，dz/dw=x/a。

采用明确的平方误差训练目标（原代码显示的绝对误差不是其更新对应的同一损失）；尺度远离0，训练内归一化及输出域。


### 求解和实现

- 冻结psi、层维数、尺度/平移和损失；训练内fit归一化。
- 按前向式与链式导数原创实现，先验证尺度/平移/权重梯度；修正来源d_a分母与多输出索引。
- 独立保留时间/群组留出，检查0尺度/远场下溢、梯度和baseline。

Python - apis - numpy/PyTorch按该具体结构原创前向与导数方向
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 按已核验psi/导数原创scalar/elementwise实现或dlnetwork自定义激活，不执行原wavenn
- dependencies - MATLAB
- Deep Learning Toolbox（按所选方向）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 原特征MLP/线性

- - check 核心数学/小例
- method 先核验特征/激活定义与可重构性，再按网络验梯度/留出。
- expected 未完成结构核验保持INDEXED_ONLY。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 源d_a含不应出现的b分母，与dilation链式导数不符；源绝对误差记录与平方误差梯度混用。
- a接近0、向量乘法/多输出广播、归一化/窗口泄漏；不可把此激活当零均值正交基。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title scikit-learn neural networks
- url https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- checked_at 2026-10-04
- evidence verified_primary


## XGBoost正则树提升


模型ID `ml-xgboost`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以二阶梯度/叶正则训练树提升预测。


### 输入和适用条件

- 按任务组织的X与标签/无监督样本，独立验证单位及输入布局。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 所选损失可作一/二阶展开；稀疏缺失与类别方式由实际实现固定。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- G_j=Σg_i；H_j=Σh_i；T叶数；λγ复杂度惩罚。

目标Σl(y,ŷ)+Σ[γT+λ||w||²/2]；二阶近似用g,h构造叶权重w_j=-G_j/(H_j+λ)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - xgboost.XGBClassifier
- XGBRegressor
- dependencies - xgboost
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 需明确外部接口/版本；无标准MATLAB内置XGBoost接口承诺
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练均值/多数类，或任务相符线性模型

- - check 核心数学/小例
- method 单叶小例核算G/H及正则叶权重；冻结预测迭代轮数。
- expected 数学叶值与所用参数吻合；独立验证非挑轮训练分数。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 旧wrapperAPI、损失/标签域、错用缺失值为0、调参泄漏。

简化到baseline，报告损失与未满足前提。


### 来源边界

- - title Chen and Guestrin XGBoost
- url https://arxiv.org/pdf/1603.02754
- checked_at 2026-10-04
- evidence verified_primary
