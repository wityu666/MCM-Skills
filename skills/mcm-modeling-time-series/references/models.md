# time-series 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 单位根与残差相关诊断


模型ID `ts-adf-ljungbox`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


对单位根与残差相关作条件诊断。


### 输入和适用条件

- 序列/模型残差、频率、确定项、滞后和样本量。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- ADF不是普通t临界值；Ljung–Box不拒绝不证明完全独立。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- γ单位根系数；ρ̂_k残差lag-k相关；m检验lag。

ADF: Δy_t=γy_{t-1}+确定项+Σφ_iΔy_{t-i}+ε，H0γ=0；Ljung–Box Q=n(n+2)Σ_{k≤m}ρ̂_k²/(n-k)，自由度考虑已拟合参数。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - adfuller
- acorr_ljungbox
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - adftest
- lbqtest
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline ACF/残差时图

- - check 核心数学/小例
- method 固定定义重算Δ/ACF/Q；检查lags-model_df非正情况。
- expected 检验零假设/自由度与软件结果一致，有限样本限制公开。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 错趋势项、过多lag、缺期、按单p机械选模型。

少阶/稳定化并用外推验证决定效用。


### 来源边界

- - title statsmodels adfuller
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html
- checked_at 2026-10-04
- evidence verified_primary
- - title statsmodels acorr_ljungbox
- url https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html
- checked_at 2026-10-04
- evidence verified_primary


## ARIMA


模型ID `ts-arima`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以差分和ARMA动态预测非季节序列。


### 输入和适用条件

- 固定频率历史序列、候选滞后阶与预测起点信息。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 差分后AR部分平稳、MA可逆；创新及趋势项形式需诊断。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- L滞后算子；m季节长度；p,d,q/P,D,Q阶；ε创新。

φ(L)(1-L)^d y_t=θ(L)ε_t；ARMA取d=D=0，趋势/外生项须按实际参数化。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.ARIMA
- SARIMAX
- dependencies - statsmodels
- scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - arima
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive/seasonal-naive

- - check 核心数学/小例
- method AR(1)在φ=0退化白噪声；滚动起点验证、残差相关与根检查。
- expected 拟合/预测状态明确，误差计算只在未来留出，差分正确还原。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过差分、根近单位、少量样本高阶、未来exog泄漏。

减少阶数、ETS/朴素基准；不能挑最优留出阶后再报同一留出。


### 来源边界

- - title statsmodels SARIMAX
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## ARMA


模型ID `ts-arma`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


描述平稳序列的AR/MA创新动态并预测。


### 输入和适用条件

- 固定频率历史序列、候选滞后阶与预测起点信息。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 差分后AR部分平稳、MA可逆；创新及趋势项形式需诊断。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- L滞后算子；m季节长度；p,d,q/P,D,Q阶；ε创新。

φ(L)y_t=θ(L)ε_t；ARMA取d=D=0，趋势/外生项须按实际参数化。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.ARIMA
- SARIMAX
- dependencies - statsmodels
- scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - arima
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive/seasonal-naive

- - check 核心数学/小例
- method AR(1)在φ=0退化白噪声；滚动起点验证、残差相关与根检查。
- expected 拟合/预测状态明确，误差计算只在未来留出，差分正确还原。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过差分、根近单位、少量样本高阶、未来exog泄漏。

减少阶数、ETS/朴素基准；不能挑最优留出阶后再报同一留出。


### 来源边界

- - title statsmodels SARIMAX
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## 协整关系与Engle-Granger检验


模型ID `ts-cointegration`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


检验I(1)序列是否存在稳定线性长期关系。


### 输入和适用条件

- 对齐的多条I(1)序列、趋势/截距、无缺期口径。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 检验null为无协整；近完全共线数值边界须处理。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- I(d)积分阶；β协整向量；u_t关系残差。

I(1)序列y,x存在β使u_t=y_t-βᵀx_t为I(0)；先估关系，再对残差作专门临界值的单位根检验。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.tsa.stattools.coint
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - egcitest
- jcitest
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 差分关系/独立趋势描述

- - check 核心数学/小例
- method 模拟有/无共同随机趋势小例；趋势项、lag和时间稳定性检查。
- expected 使用协整专门临界值，不用普通ADF阈值替换。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- I(0)/I(2)混合、结构突变、缺期、近完全共线。

差分VAR或分段描述；不由显著性宣称因果/投资机会。


### 来源边界

- - title statsmodels coint
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html
- checked_at 2026-10-04
- evidence verified_primary


## ETS指数平滑


模型ID `ts-ets`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用水平/趋势/季节状态递推预测。


### 输入和适用条件

- 频率/季节m、足够完整周期、响应允许加性或乘性结构。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 创新形式与Holt-Winters参数约定区分；系数/初始状态在所选变体可容许域。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- l水平、b趋势、s季节，均与响应单位匹配；αβγ平滑参数。

加性ETS(A,A,A)：ŷ_t=l_{t-1}+b_{t-1}+s_{t-m}；e_t=y_t-ŷ_t；l_t=l_{t-1}+b_{t-1}+αe_t，b_t=b_{t-1}+βe_t，s_t=s_{t-m}+γe_t。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.ETSModel
- ExponentialSmoothing
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 按ETS状态式原创或适用工具箱指数平滑
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive/seasonal-naive

- - check 核心数学/小例
- method α=β=γ=0时状态按设定趋势外推；滚动验证加性/乘性选择。
- expected 公式与拟合变体一致，乘法结构不接受非法零/负值。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 短季节、突变、错参数化、乘性零值。

简化到无趋势/季节或naive。


### 来源边界

- - title statsmodels ETSModel
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.exponential_smoothing.ets.ETSModel.html
- checked_at 2026-10-04
- evidence verified_primary


## GARCH条件方差


模型ID `ts-garch`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


估计/预测时变条件方差而非默认收益方向。


### 输入和适用条件

- 均值模型残差、按时点排列序列与误差分布约定。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 均值/方差分别建模；有限方差条件与严格平稳不是同一命题。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- σ²条件方差，ω同响应平方单位；αβ无量纲。

ε_t=σ_t z_t，E[z]=0,Var[z]=1；σ²_t=ω+αε²_{t-1}+βσ²_{t-1}；ω>0,αβ≥0；α+β<1时有限无条件二阶矩ω/(1-α-β)。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - arch.arch_model
- dependencies - arch
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - garch
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 常方差模型

- - check 核心数学/小例
- method 检查正方差/标准化残差与残差平方相关；滚动方差预测。
- expected 预测为正，参数及持久性有明确解释；不声称普遍收益能力。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 近IGARCH、重尾分布错配、缩放错误、估计不收敛。

常方差/EWMA描述基准；简化结构。


### 来源边界

- - title arch univariate volatility
- url https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html
- checked_at 2026-10-04
- evidence verified_primary


## 灰色GM(1,1)


模型ID `ts-gm11`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


登记短序列灰色GM11结构并限制未核验外推。


### 输入和适用条件

- 等步原序列x0；至少提供足够行拟合2参数且背景设计矩阵满列秩；正值/趋势前提按变体确认。
- 明确AGO起点、观察步长、未来跨度及参数/残差验证口径。
- 近似指数趋势才有合理性；短样本不等于能可靠长预测。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- x⁰原序列；x¹AGO；a每步发展系数；b白化驱动。

x¹(k)=Σ_{j≤k}x⁰(j)，z¹(k)=[x¹(k)+x¹(k-1)]/2；x⁰(k)+az¹(k)=b；白化解x̂¹(k)=[x⁰(1)-b/a]exp[-a(k-1)]+b/a，再差分还原。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 构造1-AGO与相邻均值z，B=[-z,1]、Y=x0(2:n)。
- 用QR/SVD估计a,b，核对rank；从X′+aX=b及X(0)=x0(1)求白化解，a≈0用极限。
- 按相邻差还原，区分拟合与滚动留出；不照搬来源的10步固定外推。

Python - apis - 原创AGO+最小二乘+还原
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - cumsum
- mldivide
- diff
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive/指数趋势拟合

- - check 核心数学/小例
- method a→0需用线性极限；常量/指数小例；滚动外推对照。
- expected 重构/还原与参数域一致；不把拟合后验差比当未来验证。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- a≈0除零、非正序列、病态B、周期/突变、过长外推。

naive/ETS并报告GM适用性不足。


### 来源边界

- - title Deng Control problems of grey systems
- url https://www.sciencedirect.com/science/article/pii/S016769118280025X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## GM(1,N)单响应灰色估计与离散递推

模型ID `ts-gm1n`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`

用响应背景值与外生驱动AGO构建单响应线性灰色关系；条件预测须给未来驱动路径。

### 输入和适用条件

- 同频、对齐、非负且相对平滑的响应x_1^(0)和N-1驱动序列；单位与AGO起点。
- 训练m-1≥N且B满列秩才可能唯一估计；可靠预测另需足够验证点与未来驱动路径。
- 选择无常数项、响应邻均值背景、驱动右端AGO值的明确变体；AGO不保证真实系统满足灰色关系。
- 同一预测起点只用当时已知信息；未知未来驱动应另预测或设情景并传播不确定性。
- 这是单响应GM(1,N)，与闭合多响应MGM耦合系统分开；系数不是因果效应。

### 数学核心

**记号**

- i=1,...,N；k=1,...,m；θ=(a,b_2,...,b_N)；训练步长按一个采样间隔计。

**定义与更新**

- AGO：x_i^(1)(k)=Σ_{t=1}^k x_i^(0)(t)；z_1^(1)(k)=[x_1^(1)(k-1)+x_1^(1)(k)]/2，k≥2。
- 明确估计式：x_1^(0)(k)+a z_1^(1)(k)=Σ_{i=2}^N b_i x_i^(1)(k)。
- B每行=(-z_1^(1)(k),x_2^(1)(k),...,x_N^(1)(k))；Y=x_1^(0)(2:m)。θ̂=argmin ||Bθ-Y||²，用QR/SVD/lstsq，不显式求(BᵀB)^-1。
- 由同一离散式直接整理：x̂_1^(0)(k)=[Σ b̂_i x_i^(1)(k)-â x̂_1^(1)(k-1)]/(1+â/2)；随后x̂_1^(1)(k)=x̂_1^(1)(k-1)+x̂_1^(0)(k)。首次递推使用已知响应AGO初值。
- 连续白化式dx_1^(1)/dt+a x_1^(1)=Σ b_i x_i^(1)(t)只是一种另需指定驱动插值的连续解释；不能把时变驱动任意当常数后宣称精确响应。

**目标与边界**

- B的rank/条件数和1+â/2远离0；累计量拟合后必须还原到原序列评价。N=1无驱动的本式不是含常数输入的GM(1,1)。

### 求解和实现

- 按时间切训练/验证并冻结变量、采样和背景变体。
- 训练窗AGO，构B/Y，用QR/SVD估计并报告秩与条件数。
- 按当前已知驱动或公开情景生成驱动AGO，使用一致的离散递推；禁止混用其他GM响应公式。
- 滚动留出比较naive/ARX/GM11，报告驱动误差传播及参数敏感性。

**PYTHON**

- apis: numpy.cumsum
- apis: numpy.linalg.lstsq
- apis: 按本卡递推原创实现
- dependencies: Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes: 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

**MATLAB**

- apis: cumsum
- apis: mldivide/lsqminnorm (按秩与具体版本选择)
- apis: 按本卡递推原创循环
- dependencies: MATLAB
- implementation_notes: 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。

### 验证和回退

Baseline：naive/seasonal-naive；可比较已确认的GM11或ARX，但不把它们当本式退化证明。

- AGO与设计矩阵：小序列独立求累加和/背景值/B行，核对响应和驱动列索引。 验收：Y=Bθ对应k≥2且无未来泄漏。
- 递推一致性：把递推解代回估计方程；检测1+a/2≈0、秩不足、缺驱动。 验收：代数残差在预声明容差，无法识别或缺未来驱动时不出无条件预测。
- 预测价值：真实预测起点滚动留出；驱动由同起点已知值/另预测/情景提供。 验收：原序列误差优于或不优于baseline如实报告；不以AGO高R²代替预测验证。

- 失败边界：AGO共趋势和强共线性；背景值近似不适配；1+a/2≈0导致病态递推；未来驱动泄漏；误把Pex15_3的MGM闭合系统认成单响应GM1N。

- 回退：naive、已确认的单变量模型或有留出支持的ARX；未来驱动未知则给条件情景。

### 来源边界

- [Deng Control problems of grey systems](https://www.sciencedirect.com/science/article/pii/S016769118280025X)；reference_only
- [Pai, Chen and Lo, Grey and neural network prediction of suspended solids and chemical oxygen demand in hospital wastewater treatment plant effluent (2007)](https://ir.lib.cyut.edu.tw/bitstream/310901800/7482/1/12Grey%2Band%2Bneural%2Bnetwork%2Bprediction%2Bof%2Bsuspended%2Bsolids%2Band%2Bchemical%2Boxygen%2Bdemand%2Bin%2Bhospital%2Bwastewater%2Btreatment%2Bplant%2Beffluent.pdf)；Targeted section 2.2, equations (2)-(5), including AGO/background matrix and algebraic discrete recursion; no application results reproduced.
- [Tien, A research on the grey prediction model GM(1,n) (2012)](https://www.sciencedirect.com/science/article/pii/S0096300311013014)；Publisher abstract/intro excerpt via search retrieval only: warns against treating time-varying accumulated associated series as constants; full PDF not retrieved.

本卡补全日期：2026-10-04。新等级仅证明限定数学指南已核验；Python／MATLAB 实现及原场景未运行。

## GM(2,1)：本资料二阶AGO边值型


模型ID `ts-gm21`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


审查并估计本资料的二阶AGO白化/边值重构；不把同名灰色变体混同。


### 输入和适用条件

- 等步序列，至少足够差分行识别3个白化参数；初/末AGO边值在同训练窗口。
- 未来时间跨度、矩阵秩和边值可解性。
- 本卡只采用Pex15_4_1/_2给出的二阶1-AGO边值型；初值型/其它背景值型必须另确认。
- 二阶白化为原数据变化的近似；根/稳定性、时点和样本外验证不可省略。


### 数学核心

- x0原序列；X=1-AGO；z(k)邻均值；Δx0(k)=x0(k)-x0(k-1)；t以观察步计。
- a1,a2,b白化参数；n观察数；两边值均属于当前拟合窗口。

Δx0(k)+a1*x0(k)+a2*z(k)=b；B=[-x0(k),-z(k),1]估(a1,a2,b)。采用白化X″+a1X′+a2X=b与X(0)=x0(1)、X(n-1)=sum x0，再相邻差还原。

拟合最小二乘min||Bθ-Δx0||²；要求识别的设计rank与所选边值问题唯一性。不是默认初值导数型。


### 求解和实现

- 计算1-AGO、Δx0、z并最小二乘估3参数。
- 按二阶白化方程和明确两边值求解；重复根/复根/a2=0及共振单独处理。
- 还原x0并在滚动窗口重建边值，未来留出与基准比较，不把原脚本拟合图当预测通过。

Python - apis - 定位变体后原创累加/矩阵估计方向
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 定位变体后cumsum/mldivide方向
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline GM11/naive

- - check 核心数学/小例
- method 先按原式重构/退化例，再滚动留出与矩阵rank检查。
- expected 只有变体定义完整且证据可查才升级THEORY_GUIDE_REVIEWED。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 源代码b/a2在a2=0失效；重复根或边值共振令直接两指数公式/求常数失败。
- 高阶差分放大噪声、病态矩阵、未知变体混用、训练窗口末值误作未来已知。

naive或已确认的单变量模型。


### 来源边界

- - title Deng Control problems of grey systems
- url https://www.sciencedirect.com/science/article/pii/S016769118280025X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 结构化多变量AGO白化方法（本资料MGM）


模型ID `ts-mgm-ago-white`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按本资料的四维稀疏线性白化系统联合估计、重构多序列。


### 输入和适用条件

- 同频对齐的四条序列、稀疏支撑、常数项与单位；各行设计矩阵可识别。
- 首观测、拟合窗口和外推跨度；源Pdata列语义还需原表说明。
- 此为联合闭合系统MGM，不是单目标已知外生驱动GM1N。
- 邻均值白化近似、耦合系数可解释性、根稳定性与时间外推需检验。


### 数学核心

- x0(k)∈R^4原序列；X=逐列AGO；Z(k)=[X(k)+X(k-1)]/2。
- A∈R^{4×4}稀疏耦合系数；c常量；观察步为单位时间。

逐方程拟合x0(k)=A Z(k)+c。本资料A行支撑为{1}、{1,2}、{3}、{1,3,4}，常数仅行1/3。白化X′=AX+c，X(0)=x0(1)；X(t)=exp(At)X0+∫0^t exp[A(t-s)]c ds，还原逐步差。

各行按明确零结构最小二乘并检查rank；X初值来自首个观测，非硬编码案例常量。无需A可逆，不能无条件用A^-1公式。


### 求解和实现

- 逐列AGO/邻均值，按四行明确设计矩阵估A/c。
- 从首观测构造初值并求线性白化系统；A奇异时用积分/增广矩阵而非直接逆。
- AGO差分重构，检查拟合/滚动未来误差与朴素基准。

Python - apis - 定位变体后原创累加/矩阵估计方向
- dependencies - Python标准库/numpy（原创实现方向按实际选择）
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - 定位变体后cumsum/mldivide方向
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline GM11/naive

- - check 定义与退化
- method A=0时X=X0+ct；对角A时退化独立白化方程；逐行重算设计残差。
- expected 设计稀疏结构、AGO/还原与闭合系统一致，不能把目录名当数学定义。
- - check 未来验证
- method 按实际窗口而非源硬写14步/固定X0运行原创实现。
- expected 未来输入与单位明确，误差比较只在真正留出。

- 设计共线/耦合不识别、未来频率/参数漂移、增长根不稳定；源代码硬编码初值和时间长度不可直接迁移。

独立GM11/VAR或朴素预测，注明失去的耦合信息。


### 来源边界

- - title Deng Control problems of grey systems
- url https://www.sciencedirect.com/science/article/pii/S016769118280025X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 历史移动平均基准


模型ID `ts-moving-average`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


计算历史窗口平滑/预测基准并避免中心窗口泄漏。


### 输入和适用条件

- 连续m步历史、m/权重只用训练期间确定。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 这是平滑/预测基准，不是ARMA的MA创新项；中心窗口会泄漏未来。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- m历史窗口；w无量纲；T信息截止。

ŷ_{T+1}=Σ_{j=0}^{m-1}w_j y_{T-j}，w≥0,Σw=1；m期SMA取w=1/m。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - pandas.rolling；原创历史窗口
- dependencies - scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - movmean指定历史窗口；原创dot
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive

- - check 核心数学/小例
- method 常量输出常量；趋势序列检查滞后；不能用centered window预测过去。
- expected 只历史输入，权重和/单位正确。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 不规则缺期、突变、中心平滑伪预测。

naive或ETS。


### 来源边界

- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## 朴素预测


模型ID `ts-naive`　类别 `model`　知识等级 `REFERENCE_IMPL_TESTED`


提供只使用最后已知值的未来预测基准。


### 输入和适用条件

- 按时间排序的至少一个有限历史观测，预测期h。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 持久性基准；预测只消费截止T可用数据。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- T预测起点；h未来步；y单位保留。

ŷ_{T+h|T}=y_T，对所有h≥1。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 定位截止时间T的最后已知值。
- 复制该值到预测跨度。
- 与真实未来留出比较，保留基准表现。

Python - apis - 原创seasonal_naive(period=1)
- dependencies - Python标准库
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - repmat(y(end),h,1)
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 它本身就是基准

- - check 核心数学/小例
- method 常量序列及多步手核，输入不可引用未来。
- expected 所有预测等于最后已知观测。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 季节/趋势显著时偏差大，但不能隐藏比较结果。

均值/漂移基准并说明额外假设。


### 来源边界

- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## 季节ARIMA


模型ID `ts-sarima`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以季节差分/动态预测固定频率季节序列。


### 输入和适用条件

- 固定频率历史序列、候选滞后阶与预测起点信息。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 差分后AR部分平稳、MA可逆；创新及趋势项形式需诊断。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- L滞后算子；m季节长度；p,d,q/P,D,Q阶；ε创新。

φ(L)(1-L)^d Φ(L^m)(1-L^m)^D y_t=θ(L)Θ(L^m)ε_t；ARMA取d=D=0，趋势/外生项须按实际参数化。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.ARIMA
- SARIMAX
- dependencies - statsmodels
- scikit-learn
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - arima
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline naive/seasonal-naive

- - check 核心数学/小例
- method AR(1)在φ=0退化白噪声；滚动起点验证、残差相关与根检查。
- expected 拟合/预测状态明确，误差计算只在未来留出，差分正确还原。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 过差分、根近单位、少量样本高阶、未来exog泄漏。

减少阶数、ETS/朴素基准；不能挑最优留出阶后再报同一留出。


### 来源边界

- - title statsmodels SARIMAX
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
- checked_at 2026-10-04
- evidence verified_primary
- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## 季节朴素预测


模型ID `ts-seasonal-naive`　类别 `model`　知识等级 `REFERENCE_IMPL_TESTED`


提供重复最后完整季节的多步预测基准。


### 输入和适用条件

- 至少m个按固定频率排列的有限观测、m正整数、预测h。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- m有领域或训练数据依据；不规则采样/缺期先明示处理。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- m季节周期（观测步）；h非负预测长度。

ŷ_{T+h|T}=y_{T-m+1+((h-1) mod m)}；重复最后完整季节。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核验频率、period和截止历史长度。
- 取最后period个有限观测。
- 重复该周期到所需horizon并独立手核。

Python - apis - scripts/seasonal_naive.py:seasonal_naive
- dependencies - Python标准库
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - repmat最后m项并截取h项
- dependencies - MATLAB
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 非季节naive

- - check 核心数学/小例
- method 历史[1,2,3,4,5,6],m=3,h=7→[4,5,6,4,5,6,4]。
- expected 手核序列相同；拒绝短历史/非有限值/非法m。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 错季节长度、未处理缺期、预测起点越界。

naive或重新聚合频率。


### 来源边界

- - title scikit-learn Cross-validation
- url https://scikit-learn.org/stable/modules/cross_validation.html
- checked_at 2026-10-04
- evidence verified_primary


## 向量自回归VAR


模型ID `ts-var`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


联合建模和预测多条平稳序列。


### 输入和适用条件

- K条对齐的平稳序列、时间长度足够拟合K²p参数。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- 同频率、滞后可用；创新协方差与稳定性须检验。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- Y_t∈R^K；A_i∈R^{K×K}；u_t创新。

Y_t=c+Σ_{i=1}^p A_iY_{t-i}+u_t；稳定VAR要求伴随矩阵特征值模<1。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.tsa.api.VAR
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - varm
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 各变量单独AR/naive

- - check 核心数学/小例
- method A_i=0退化均值模型；独立谱检验、残差whiteness与滚动预测。
- expected 稳定域和维数一致；Granger预测增益不直接因果。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 高维小样本、非平稳水平、内生识别解释过度。

减少变量/lag、正则VAR，协整时考虑VECM。


### 来源边界

- - title statsmodels VAR/VECM
- url https://www.statsmodels.org/stable/vector_ar.html
- checked_at 2026-10-04
- evidence verified_primary


## 向量误差修正VECM


模型ID `ts-vecm`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用协整误差修正和短期动态建模多序列。


### 输入和适用条件

- 同频I(1)序列、协整秩r与确定性项约定。
- 样本/时点/群组定义及变量单位；已有上层数据边界。
- β列为协整关系，α调整；归一化不唯一，识别/趋势项须明确。
- 预测验证切分与实际使用匹配；预处理和调参仅用训练数据。


### 数学核心

- α调整矩阵、β协整矩阵；Γ短期项；r协整秩。

ΔY_t=αβᵀY_{t-1}+ΣΓ_iΔY_{t-i}+d_t+u_t；rank(αβᵀ)=r<K。

估计目标与机制见core；无额外任务优化目标时不编造目标函数。


### 求解和实现

- 核对输入域、口径、假设与baseline。
- 按core构造估计/求解，记录参数、停止状态与依赖版本。
- 按verification独立核验并在任务匹配的留出数据评估。

Python - apis - statsmodels.tsa.vector_ar.vecm.VECM
- dependencies - statsmodels
- implementation_notes - 接口为实现方向，本卡未运行；需锁定实际版本、随机源和数据布局。

MATLAB - apis - vecm
- estimate
- forecast
- dependencies - MATLAB
- Econometrics Toolbox（按所选接口）
- implementation_notes - 本轮无MATLAB运行证据；旧教材函数不视作当前推荐接口。


### 验证和回退

Baseline 差分VAR

- - check 核心数学/小例
- method r=0时与对应差分VAR比较；秩/残差/时点验证。
- expected 跨参数化关系空间一致，不要求β列逐字相等。
- - check 任务验收
- method 与baseline比较；留出/分组/时间边界由任务确定，报告不确定性及实际失败。
- expected 不使用训练拟合或资料旧输出冒充新验证，阈值预先按任务定义。

- 错协整秩、趋势项错位、结构突变、小样本。

差分VAR或简化协整关系。


### 来源边界

- - title statsmodels VECM
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.vector_ar.vecm.VECM.html
- checked_at 2026-10-04
- evidence verified_primary
- - title statsmodels coint
- url https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html
- checked_at 2026-10-04
- evidence verified_primary
