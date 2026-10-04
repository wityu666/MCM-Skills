# statistics 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 方差分析


模型ID `stat-anova`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


比较组/因素差异及交互，明确平方和口径。


### 输入和适用条件

- 连续响应、组标签/因素、设计是否平衡/重复测量。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 独立性、误差形状/方差、交互项和contrast编码决定F的解释。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- g组数；n总样本；SS平方和；F比较统计量。

一因素：F=[SS_between/(g-1)]/[SS_within/(n-g)]；一般线性模型按明确I/II/III型比较嵌套项。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.stats.anova_lm
- AnovaRM
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - anova1
- anovan
- fitrm/ranova
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 组均值及差异区间

- - check 核心数学/小例
- method 手算小例SS_total=SS_between+SS_within；不平衡设计检查项顺序。
- expected 平方和分解与所选类型一致，不将解释方差当因果贡献。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 遗漏交互、重复观测独立处理、换编码改变III型解释。

Welch/稳健或混合效应模型，报告适用性。


### 来源边界

- - title statsmodels anova_lm
- url https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html
- checked_at 2026-10-04
- evidence verified_primary


## Bootstrap重采样


模型ID `stat-bootstrap`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按真实抽样单位估计统计量的抽样不确定性。


### 输入和适用条件

- 原样本、统计量、抽样单位和配对/群组/时间结构。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 简单观测重抽假设可交换；时间依赖需块/适当重采样而非逐行IID。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- T目标统计量；b重采样编号；SE是T_b的SD。

从经验分布有放回抽样D_b；T_b=T(D_b)；SE=sd(T_b)，CI按percentile/basic/BCa的定义。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 确定真实重采样单位及配对/块规则。
- 有放回重抽并计算每个统计量。
- 按区间方法汇总，检查退化和重复次数稳定性。

Python - apis - scipy.stats.bootstrap
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - bootstrp
- bootci
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 适用时的解析标准误

- - check 核心数学/小例
- method 成对数据同索引重抽；退化数据/区间NaN；增加重复次数检查数值稳定。
- expected 抽样单位保留依赖，名义覆盖不是一次区间承诺。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 小样本偏差、依赖破坏、退化BCa、只挑一个seed。

解析/置换/块Bootstrap或仅报告描述范围。


### 来源边界

- - title SciPy bootstrap
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- checked_at 2026-10-04
- evidence verified_primary


## Bradley–Terry成对比较


模型ID `stat-bradley-terry`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


从成对比较估计有尺度锚点的相对能力。


### 输入和适用条件

- 两两对比结果、对象ID映射和比较图。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 比较机制可用Logit差分表示；图断开/完美胜负导致识别或有限MLE问题。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- s_i相对能力log尺度；每行设计i=+1,j=-1。

P(i胜j)=exp(s_i)/[exp(s_i)+exp(s_j)]；Bernoulli对数似然；s整体加常数不变，需固定一项或Σs=0。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - 用statsmodels.GLM对对比设计矩阵估计
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitglm对差分设计或原创似然
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 等胜率/成对频率

- - check 核心数学/小例
- method 所有s加常数概率不变；两对象平衡胜负概率=0.5。
- expected 尺度锚点明确；稀疏/分離不报告伪精确排名。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 断开的比较图、分离、时间变化或上下文遗漏。

正则Logit/仅报告可比较子图。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary


## Pearson与Spearman相关


模型ID `stat-correlation`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


描述线性或单调关联，条件性检验并限制解释。


### 输入和适用条件

- 成对观测、缺失/并列秩规则与时空依赖结构。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 线性和单调相关不同；默认p值适用条件与系数计算区分。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- r无量纲；rank并列通常平均秩；x/y单位各自。

Pearson r=Σ(x-x̄)(y-ȳ)/√[Σ(x-x̄)²Σ(y-ȳ)²]；Spearman为带并列秩规则的rank(x),rank(y)的Pearson。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - pearsonr
- spearmanr
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - corr(Type="Pearson"/"Spearman")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 散点/成对描述

- - check 核心数学/小例
- method 正线性变换r不变，反号变换反号；常量列应返回未定义。
- expected r∈[-1,1]，小样本/依赖采用适当置换或块方法。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 常量/异常点、群组混合、相关直接解释因果。

分组描述/稳健或秩相关并说明对象变化。


### 来源边界

- - title SciPy pearsonr
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy spearmanr
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- checked_at 2026-10-04
- evidence verified_primary


## 离散时间Logistic风险模型


模型ID `stat-discrete-time-survival`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


按风险集估计离散期事件风险和生存函数。


### 输入和适用条件

- 事件/删失时点、每期风险集、仅已知时点的协变量。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 删失机制/随时间协变量可用性需说明；事件后不再进入risk rows。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- T_i事件期；h条件风险；S生存概率；α_t基准风险。

h_it=P(T_i=t|T_i≥t,X)=logit⁻¹(α_t+x_itᵀβ)；S_i(t)=Π_{s≤t}(1-h_is)；person-period Bernoulli似然。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.GLM(Binomial)对person-period
- dependencies - statsmodels
- scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitglm对person-period
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 常风险几何生存/风险表

- - check 核心数学/小例
- method h∈[0,1]，S单调；删失后不编造未事件标签。
- expected 风险集与事件定义成立；不把Logistic人口映射混入此模型。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 删失忽略、同对象当IID、事件后补0、未来协变量。

非参数风险表/简化区间，明确估计对象。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy statistical functions
- url https://docs.scipy.org/doc/scipy/reference/stats.html
- checked_at 2026-10-04
- evidence verified_primary


## 概率分布族与拟合


模型ID `stat-distribution-families`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按支持集/机制选择概率族并拟合、模拟和核查。


### 输入和适用条件

- 响应支持集、抽样机制、是否删失及有限样本。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 先匹配支持与生成机制；rate/scale、shape/variance参数不能混用。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- p∈[0,1]；λ>0；σ>0；k非负整数；参数单位随变量。

Bernoulli: p^x(1-p)^(1-x)；Binomial: C(n,k)p^k(1-p)^(n-k)；Poisson: e^-λ λ^k/k!；Normal: exp[-(x-μ)²/(2σ²)]/(σ√2π)；Exponential: λe^-λx,x≥0；其他Gamma/Beta/Weibull/Lognormal/t依真实参数化。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - scipy.stats分布对象的pmf/pdf/cdf/logpdf/fit
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - makedist
- fitdist
- pdf/cdf
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 经验CDF/直方图及领域基准分布

- - check 核心数学/小例
- method PMF求和/PDF积分=1；CDF单调[0,1]，参数/单位与模拟矩匹配。
- expected 不在域外赋正概率；估参数后检验须重新校准。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 零方差、非正scale、删失当完整数据、极端尾部外推。

经验分布/截断或明确仅描述区间。


### 来源边界

- - title SciPy statistical functions
- url https://docs.scipy.org/doc/scipy/reference/stats.html
- checked_at 2026-10-04
- evidence verified_primary


## 弹性网


模型ID `stat-elasticnet`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


兼顾稀疏与相关变量收缩的线性预测。


### 输入和适用条件

- 连续y和X，训练内尺度处理、正则参数候选。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 缩放影响惩罚；系数是正则估计，不直接套OLS标准误。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- β回归系数；λ惩罚强度；n样本数。

minβ ||y-Xβ||²/(2n)+λ[α||β||₁+(1-α)||β||²/2]；通常不惩罚截距。

λ≥0，0≤α≤1


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.linear_model.ElasticNet
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。

MATLAB - apis - lasso(Alpha=...)
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline OLS/均值模型

- - check 核心数学/小例
- method λ趋0与OLS预测比较；标准化、调参置于Pipeline内。
- expected 零惩罚极限与模型约定一致，留出信息不参与fit。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 全数据先缩放、调参后硬写另一个λ、稀疏选择不稳定。

简化变量/固定更强正则并报告选择不稳定。


### 来源边界

- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary


## EM潜变量估计方法


模型ID `stat-em`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在明确潜变量似然下迭代估计参数。


### 输入和适用条件

- 明确观测y、潜变量z和完整数据似然。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 可计算E/M步；标签置换与局部最优不代表唯一解释。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- θ参数；z潜变量；Q条件完整似然期望。

E步Q(θ|θold)=E_{z|y,θold}[log p(y,z|θ)]；M步θnew=argmaxθ Q；精确步骤使观测log-likelihood不下降。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 定义完整数据似然、latent和初值。
- E步条件期望，M步最大化Q。
- 检查观测likelihood/退化，多初值与识别验证。

Python - apis - 按模型使用GaussianMixture/HMM；EM本身不另造统一接口
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 按完整似然写E/M或fitgmdist
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 无潜变量模型/单成分

- - check 核心数学/小例
- method 独立重算观测likelihood，迭代单调性；多初值与小例解析E步。
- expected 精确EM在数值容差内不下降；收敛仍需识别与泛化检查。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 奇异协方差、近似M步下降、局部解、latent标签置换。

正则协方差/简化潜结构或直接优化似然。


### 来源边界

- - title scikit-learn Gaussian mixture models
- url https://scikit-learn.org/stable/modules/mixture.html
- checked_at 2026-10-04
- evidence verified_primary


## 广义线性模型


模型ID `stat-glm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


让响应支持集、均值和方差结构匹配的回归。


### 输入和适用条件

- X、响应域/观测方式、link、exposure/offset（若需要）。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- family/link/均值方差关系符合数据；独立性或相关结构明示。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- μ条件均值；g链接；φ离散度；V均值方差函数。

响应属选定指数族；g(μi)=xiᵀβ，Var(yi)=φV(μi)；最大化该family的似然。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.GLM
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitglm
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 与响应域相符的截距模型

- - check 核心数学/小例
- method 核验逆link输出域；残差/离散度与拟合family比较。
- expected 预测不越响应允许域，过/欠离散如实诊断。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 任意比例做logit后OLS、family不符、完全分离、遗漏exposure。

更合适family/准似然/正则或聚合口径修正。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary


## 假设检验与效应量


模型ID `stat-hypothesis-tests`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在明确抽样机制下比较预定假设并报告效应量。


### 输入和适用条件

- 预先H0/H1、抽样/配对结构、检验方向、效应量和多重检验计划。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 独立t与配对t不同；KS在分布参数由同样本估计时不能套固定分布p值。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- n1,n2样本数；s1²,s2²样本方差；H0零假设。

Welch t=(ȳ1-ȳ2)/√(s1²/n1+s2²/n2)，自由度按Welch；一般p=P_{H0}(统计量至少同样极端)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - scipy.stats.ttest_ind(equal_var=False)
- ttest_rel
- chi2_contingency
- kstest
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - ttest2
- ttest
- chi2gof
- kstest
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 效应量/描述统计，不用任意0.05当通用验收

- - check 核心数学/小例
- method 两组交换时t变号、双侧p不变；检查同样本估参数和多重检验。
- expected 检验设计与数据对应；不拒绝H0不写为已证明H0。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 小样本重尾/依赖、挑检验挑阈值、p值替代影响大小。

置换/非参数/重采样，透明报告效应和区间。


### 来源边界

- - title SciPy ttest_ind
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
- checked_at 2026-10-04
- evidence verified_primary


## 置信区间与预测区间


模型ID `stat-intervals`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


区分并计算估计量区间、均值和新观测的预测不确定性。


### 输入和适用条件

- 估计对象、样本设计、标准误/误差模型及名义覆盖水平。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- t公式要求相应抽样/误差前提；频率CI不等同参数的后验概率。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- n有效样本数；s样本SD；SE估计量抽样标准差；α显著水平。

均值CI: ȳ±t·s/√n；线性新均值Var=σ²x₀ᵀ(XᵀX)⁻¹x₀，新观测另加σ²。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.get_prediction
- scipy.stats.t
- dependencies - statsmodels
- scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - predict
- confint
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 报告点估计和未经推断的样本散布

- - check 核心数学/小例
- method 相同x₀预测区间不窄于均值区间；多次重复抽样评估覆盖。
- expected 区间含义明确，重复覆盖在预设模拟误差内。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 把SD当SE、把参数CI当个体预测范围、相关样本用n独立计。

重采样/稳健协方差或明确仅描述范围。


### 来源边界

- - title MathWorks Confidence and Prediction Bounds
- url https://www.mathworks.com/help/curvefit/confidence-and-prediction-bounds.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy bootstrap
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- checked_at 2026-10-04
- evidence verified_primary


## Kolmogorov–Smirnov分布检验


模型ID `stat-ks-test`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


比较经验CDF和指定分布/另一独立样本。


### 输入和适用条件

- 独立样本和完全指定的连续F0，或双独立样本。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- F0参数若从同样本估计，经典固定分布p值不适用；离散/并列需专门校准。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- n样本数；Fn右连续经验CDF；F0完全指定连续CDF；D±考察跳点两侧。

连续单样本KS：排序x_(i)，D+=max[i/n-F0(x_(i))]，D-=max[F0(x_(i))-(i-1)/n]，D=max(D+,D-)；双样本sup|Fn-Gm|。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - scipy.stats.kstest
- ks_2samp；拟合后用重新fit的parametric bootstrap
- dependencies - scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - kstest
- kstest2（口径核对）
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline QQ/经验CDF

- - check 核心数学/小例
- method 小数组在跳点两侧手算sup；若拟合参数，null模拟每次重估参数。
- expected 统计量可核算；不拒绝不写成证明分布。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 同样本估参数还套p表、相关、离散观测。

拟合后校准/图形描述。


### 来源边界

- - title SciPy statistical functions
- url https://docs.scipy.org/doc/scipy/reference/stats.html
- checked_at 2026-10-04
- evidence verified_primary
- - title Installed SciPy 1.15.3 kstest/ks_1samp first-party docstrings
- url https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.kstest.html
- checked_at 2026-10-04
- evidence verified_primary
- source_kind installed_first_party_documentation
- source_sha256 01b665feba503fd53684d00ca6f322550fa41d414e09da482ab97f48d64b8a5b
- docstring_sha256 85012dcc2a5d18451a9b6dd7bdd421622ea3e2e1274b397c7986228871a8b4fc


## 套索回归


模型ID `stat-lasso`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以稀疏线性系数拟合/预测并审查选择稳定性。


### 输入和适用条件

- 连续y和X，训练内尺度处理、正则参数候选。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 缩放影响惩罚；系数是正则估计，不直接套OLS标准误。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- β回归系数；λ惩罚强度；n样本数。

minβ ||y-Xβ||²/(2n)+λ||β||₁；通常不惩罚截距。

λ≥0


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.linear_model.Lasso
- LassoCV
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。

MATLAB - apis - lasso
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline OLS/均值模型

- - check 核心数学/小例
- method λ趋0与OLS预测比较；标准化、调参置于Pipeline内。
- expected 零惩罚极限与模型约定一致，留出信息不参与fit。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 全数据先缩放、调参后硬写另一个λ、稀疏选择不稳定。

简化变量/固定更强正则并报告选择不稳定。


### 来源边界

- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary


## 线性判别LDA与Fisher方向


模型ID `stat-lda`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


对类条件高斯模型判别类别或作Fisher监督投影。


### 输入和适用条件

- 类别标签、连续特征、各类足够样本与先验。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 类协方差共享/高斯是分类模型假设；Fisher投影与分类阈值分开。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- μ_c类均值；Σ共享协方差；π_c类先验；S_W类内散布。

X|c~N(μ_c,Σ)共用Σ；δ_c=xᵀΣ⁻¹μ_c-μ_cᵀΣ⁻¹μ_c/2+logπ_c；二类Fisher方向w∝S_W⁻¹(μ1-μ0)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - LinearDiscriminantAnalysis
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitcdiscr
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Logistic/类均值

- - check 核心数学/小例
- method 两类对称均值等先验时边界在中点；投影维≤类数-1；协方差秩检查。
- expected 概率/判别方向合理，奇异协方差不直接inverse。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- p大n小、类协方差不同、只作投影却声称分类通过。

收缩LDA/QDA或Logistic。


### 来源边界

- - title scikit-learn LDA/QDA
- url https://scikit-learn.org/stable/modules/lda_qda.html
- checked_at 2026-10-04
- evidence verified_primary


## 二项Logistic回归


模型ID `stat-logit`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


估计二值/二项成功概率。


### 输入和适用条件

- 二值标签或成功次数/总次数，不能混淆连续比例。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 标签和试验数可靠；独立/分组关系以及分离需要检查。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- Yi∈{0,1}；pi条件概率；β系数。

Yi~Bernoulli(pi)，log(pi/(1-pi))=xiᵀβ；min -Σ[y logp+(1-y)log(1-p)]。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.GLM(Binomial)
- sklearn.linear_model.LogisticRegression
- dependencies - statsmodels
- scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitglm(Distribution="binomial")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 训练类频率常数概率

- - check 核心数学/小例
- method 小例逆logit始终在(0,1)；留出logloss与校准。
- expected 概率域满足，评估切分独立；0/1观测无需预先取logit。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 完全分离、稀有类、类别泄漏或训练accuracy。

正则Logit/精简特征，保留概率与阈值分离。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary


## 线性混合效应


模型ID `stat-mixed-effects`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


分析重复/分组数据的固定与随机效应。


### 输入和适用条件

- 响应、固定效应X、群组/重复标识和随机效应设计Z。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 随机效应分布/协方差结构、组间独立和样本量需检查。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- β固定；b_i组随机效应；G,R协方差。

y_i=X_iβ+Z_i b_i+ε_i，b_i~N(0,G)，ε_i~N(0,R_i)；组间独立、组内可相关。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.MixedLM
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitlme
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 固定效应/随机截距最简结构

- - check 核心数学/小例
- method G和R半正定；组留出或时间留出，检查方差边界与收敛。
- expected 协方差有效、拟合状态透明，组效应非随意固定数值。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 少量组、奇异G、收敛不稳定、将舞伴相关当因果。

删随机斜率、简化为固定效应/聚类稳健SE。


### 来源边界

- - title statsmodels Linear Mixed Effects Models
- url https://www.statsmodels.org/stable/mixed_linear.html
- checked_at 2026-10-04
- evidence verified_primary


## 负二项计数回归


模型ID `stat-negative-binomial`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在NB参数化下描述过离散计数均值/方差。


### 输入和适用条件

- 非负计数、X、暴露量及足够离散信息。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 明确NB参数化；α固定或估计不能混淆。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- μ>0，α离散参数；NB1/NB2非同一方差式。

NB2参数化：E[Y]=μ，Var(Y)=μ+αμ²，logμ=Xβ+offset；α>0。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.GLM(NegativeBinomial)
- statsmodels.NegativeBinomial
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 自定义似然+fmincon
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Poisson

- - check 核心数学/小例
- method α趋0与Poisson分布比较；重复模拟检查均值/方差。
- expected 所选参数化和离散度吻合；仍作样本外验证。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 把GLM family默认α当已估计、识别弱、零膨胀未处理。

Poisson稳健推断或更简洁计数模型。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary


## 普通最小二乘回归


模型ID `stat-ols`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


估计连续响应的线性条件均值，说明系数/预测及其误差。


### 输入和适用条件

- n×p设计矩阵X与连续y，截距明确。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 满列秩保证唯一系数；推断需指定误差相关/方差，因果需额外识别。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- X∈R^{n×p}；β系数与响应/特征单位对应；ε残差。

y=Xβ+ε；β̂=argminβ ||y-Xβ||²；满秩时β̂=(XᵀX)⁻¹Xᵀy，实现用QR/SVD而非直接逆。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 定义截距和设计矩阵，查rank/单位。
- 用QR/SVD估β并重算残差。
- 按误差设计计算不确定性或作留出预测。

Python - apis - statsmodels.OLS
- scipy.linalg.lstsq
- dependencies - statsmodels
- scikit-learn
- scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitlm
- mldivide
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 均值模型/单自变量线性拟合

- - check 核心数学/小例
- method 用y=2+3x无噪声小例；独立算残差与Xᵀr。
- expected 可识别系数复原，法方程残差在设定数值容差内。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 秩亏、遗漏变量、内生性、时空相关或训练R²误当预测。

删冗余参数、正则或明确仅预测；相关误差用适当协方差。


### 来源边界

- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary


## 面板固定效应


模型ID `stat-panel-fixed-effects`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


利用实体内变化估计面板关联并控制实体常量。


### 输入和适用条件

- 实体i、时间t、响应和随时间变化的X，缺失/不平衡结构。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- within识别需实体内变化；严格外生性等因果解释另论，SE按依赖聚类。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- i实体，t时点；α_i实体常量；δ_t共同时间效应。

y_it=α_i+δ_t+x_itᵀβ+ε_it；within变换减个体均值，或虚拟变量估计。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - linearmodels.PanelOLS
- statsmodels公式虚拟变量
- dependencies - statsmodels
- linearmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitlm含实体/时间分类；原创within变换
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline pooled OLS

- - check 核心数学/小例
- method within与虚拟变量在同设计比较；时间不变变量可识别性。
- expected 共有可识别系数相符；不估不可识别的实体常量系数。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 只个体间变化、内生性、错误聚类、样本外新实体。

pooled/差分或混合效应并解释信息损失。


### 来源边界

- - title linearmodels panel examples
- url https://bashtage.github.io/linearmodels/panel/examples/examples.html
- checked_at 2026-10-04
- evidence verified_primary


## 偏最小二乘回归


模型ID `stat-pls`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用监督潜变量预测多变量响应。


### 输入和适用条件

- 成对X,Y、可匹配样本及训练内缩放。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 线性潜变量关系；组件数不能超过有效秩，监督降维需训练内。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- w,c单位范数方向；t得分；Y可多输出。

首组件max_{||w||=||c||=1} wᵀXᵀYc；t=Xw，逐组件投影/deflation后回归Y。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 训练内中心化/缩放X,Y。
- 逐组件求最大交叉协方差方向并deflation。
- 在组件得分上回归，按训练CV选组件数再留出预测。

Python - apis - sklearn.cross_decomposition.PLSRegression
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - plsregress
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline Ridge/OLS

- - check 核心数学/小例
- method 低秩线性合成关系恢复与组件数CV；与PCA对比目标参与情况。
- expected 只训练数据决定组件，预测维数与原变量一致。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过多组件、目标泄漏、把PLS与PCA等同。

Ridge/少量有依据变量。


### 来源边界

- - title scikit-learn Cross decomposition
- url https://scikit-learn.org/stable/modules/cross_decomposition.html
- checked_at 2026-10-04
- evidence verified_primary


## Poisson计数回归


模型ID `stat-poisson`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


估计非负计数或按暴露量的发生率。


### 输入和适用条件

- 非负整数响应，X和观测暴露量/时间窗。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 计数单位一致；Poisson均值方差假设需诊断。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- μ计数均值；exposure>0；β按log率解释。

Yi~Poisson(μi)，log μi=xiᵀβ+log exposurei；条件Var(Y)=μ。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.GLM(Poisson)
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitglm(Distribution="poisson")
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 每单位暴露的常数率

- - check 核心数学/小例
- method exposure翻倍且特征不变时均值翻倍；检验离散度。
- expected 非负均值与offset口径成立，异常离散明确。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 零/负exposure、额外零、过离散、不同观测窗直接比。

Negative Binomial/零膨胀模型需额外论证，或稳健SE。


### 来源边界

- - title statsmodels Generalized Linear Models
- url https://www.statsmodels.org/stable/glm.html
- checked_at 2026-10-04
- evidence verified_primary


## 岭回归


模型ID `stat-ridge`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


缓解共线性/过拟合并预测连续响应。


### 输入和适用条件

- 连续y和X，训练内尺度处理、正则参数候选。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 缩放影响惩罚；系数是正则估计，不直接套OLS标准误。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- β回归系数；λ惩罚强度；n样本数。

minβ ||y-Xβ||²/(2n)+λ||β||²；通常不惩罚截距。

λ≥0


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - sklearn.linear_model.Ridge
- RidgeCV
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。
- 数学λ与库alpha及RSS/n归一化须按实际接口换算，不能只凭同名数值。

MATLAB - apis - fitrlinear(Regularization="ridge")
- ridge
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline OLS/均值模型

- - check 核心数学/小例
- method λ趋0与OLS预测比较；标准化、调参置于Pipeline内。
- expected 零惩罚极限与模型约定一致，留出信息不参与fit。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 全数据先缩放、调参后硬写另一个λ、稀疏选择不稳定。

简化变量/固定更强正则并报告选择不稳定。


### 来源边界

- - title scikit-learn Linear Models
- url https://scikit-learn.org/stable/modules/linear_model.html
- checked_at 2026-10-04
- evidence verified_primary


## 空间滞后回归SAR


模型ID `stat-spatial-lag`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在明确空间W下估计滞后关联和间接传播。


### 输入和适用条件

- 空间单元对齐的y/X、基于机理的W、邻接/距离口径。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- I-ρW可逆，X外生；W变换/零对角和邻居定义须固定。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- W∈R^{n×n}空间权；ρ空间系数；β效应非直接边际影响。

y=ρWy+Xβ+ε；E[y]=(I-ρW)⁻¹Xβ；ML含log|det(I-ρW)|。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - pysal.spreg.ML_Lag
- dependencies - spreg/libpysal
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 按ML构造logJacobian+fmincon；旧jplv7仅来源线索
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline OLS与空间残差检查

- - check 核心数学/小例
- method ρ=0退化OLS；独立算逆映射/谱域和W行列对齐。
- expected 退化关系与对齐成立，直接/间接效应按乘数解释。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 内生Wy却用普通OLS、错误W、域外ρ、空间留出泄漏。

OLS+空间稳健描述或重新定义W。


### 来源边界

- - title PySAL ML_Lag
- url https://pysal.org/spreg/generated/spreg.ML_Lag.html
- checked_at 2026-10-04
- evidence verified_primary


## 方差膨胀因子VIF


模型ID `stat-vif`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


诊断设计矩阵的线性共线性与估计精度膨胀。


### 输入和适用条件

- 设计矩阵（不把ID/常数列作为待测预测量）。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 诊断线性共线性，不提供通用删除阈值；惩罚/因果目标另论。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- R_j²辅助回归R²；VIF无量纲。

VIF_j=1/(1-R_j²)，R_j²为X_j对其余X（含截距）的回归拟合优度。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - variance_inflation_factor
- dependencies - statsmodels
- scipy
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 逐列fitlm/回归计算
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline rank/奇异值/相关矩阵

- - check 核心数学/小例
- method 重复列R²=1导致无穷；正交已中心化列VIF≈1。
- expected 范围和极端例正确，不把VIF小当模型正确。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 常量列、n≤p、近共线数值爆炸、机械5或10门。

删有依据冗余或Ridge，公开解释变化。


### 来源边界

- - title statsmodels variance_inflation_factor
- url https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- checked_at 2026-10-04
- evidence verified_primary
- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary


## 加权最小二乘


模型ID `stat-wls`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在有可靠异方差权重时估计线性均值并明确推断口径。


### 输入和适用条件

- X,y及每条观测的可靠逆方差权重。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 权重含义是方差而非任意重要性；估计权重需检查额外不确定性。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- wi正；W=diag(wi)；β与y单位同OLS。

β̂=argmin Σi wi(yi-xiᵀβ)²，wi∝1/Var(εi)>0；等价sqrt(W)白化后OLS。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 确认逆方差w及其来源。
- sqrt(W)白化X/y后最小二乘。
- 核验等权退化、残差与权重估计不确定性。

Python - apis - statsmodels.WLS
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - fitlm(Weights=...)
- dependencies - MATLAB
- Statistics and Machine Learning Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline OLS

- - check 核心数学/小例
- method 设所有wi相同，与OLS对照；独立白化求解。
- expected 等权解一致，权重重标统一常数不改系数。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 误用方差作为权重、负权/零方差、数据驱动权重推断失真。

OLS+异方差稳健协方差或重新估计权重。


### 来源边界

- - title statsmodels WLS
- url https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.WLS.html
- checked_at 2026-10-04
- evidence verified_primary
