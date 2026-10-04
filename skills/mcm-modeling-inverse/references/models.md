# inverse 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 局部/实际可识别性与参数剖面


模型ID `inverse-identifiability`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


区分能拟合、数值稳定和参数可识别


### 输入和适用条件

- 前向F、参数域、观测/噪声、参数尺度
- Jacobian满列秩只支持适当光滑条件下局部可识别，不保证全球唯一
- 置信阈值依统计假设，不能套固定百分比


### 数学核心

- J_ij=partial F_i/partial theta_j；W噪声权；L(theta)损失

- 局部信息候选I=J' W J；小奇异值/零空间表示弱或未识别方向
- 参数剖面L_i(p)=min_(theta_-i) L(theta_i=p,theta_-i)
- F(theta1,theta2)=theta1+theta2只识别和；F(theta)=theta²在theta≠0可局部满秩但全域有±二解

- 无新拟合目标；检查既有目标与参数域/尺度


### 求解和实现

- 校验前向/参数单位
- 独立差分/解析Jacobian并尺度化
- 检查谱/等价解与多初值
- 求相关剖面，记录未识别方向

Python - apis - numpy.linalg.svd
- scipy.optimize.least_squares
- 原创profile循环
- dependencies - NumPy
- SciPy
- implementation_notes - 实现方向；本卡未有独立运行复现证据。

MATLAB - apis - svd
- lsqnonlin
- 原创profile
- dependencies - MATLAB
- Optimization Toolbox(可选)
- implementation_notes - 实现方向；本卡未有独立运行复现证据。


### 验证和回退

Baseline 两个参数只以和进入观察，零空间(1,-1)可手核

- - check 结构反例
- method 代入多个同和参数
- expected 观测完全相同
- - check 局部/全球区别
- method theta²的±二解
- expected 不把局部rank冒充全球唯一
- - check 实际识别
- method 噪声/采样/参数尺度变化及剖面
- expected 报告可信区间或集合

- 直接求逆信息阵忽略病态
- 参数尺度让rank阈值误导
- 剖面只取一次局部解

- 合并/固定不可识别参数
- 设计新增观测，保留多解


### 来源边界

- - title Per Christian Hansen Regularization Tools 4.1 原作者报告
- url https://www.imm.dtu.dk/~pcha/Regutools/RTv4manual.pdf
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已打开作者128页报告并读病态、正则化定义与相关目录；卡中公式/手核独立验算，不称整报告所有变体已读
- - title SciPy least_squares 官方本机文档
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机SciPy 1.15.3文档；网页未读取，路径/hash留local_primary_source_checks.json


## 带界非线性校准与Gaussian MAP组件


模型ID `inverse-nonlinear-calibration`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


从观测反推有定义域的前向模型参数


### 输入和适用条件

- F(theta)、观测/噪声、参数界、初值/先验及留出
- 噪声/观测结构有依据；F输出与数据同单位
- 局部优化不证明参数唯一或全局最优
- MAP仅在明确似然/先验时称MAP


### 数学核心

- r_i=(F_i(theta)-y_i)/sigma_i；theta参数；Sigma噪声协方差

- 基础min_(lb<=theta<=ub) .5 sum_i rho(r_i²)
- Gaussian prior theta~N(mu0,C0)时加.5||C0^(-1/2)(theta-mu0)||²；相关噪声用Sigma白化
- 线性Gaussian时与适当Tikhonov同类，统计Bayesian泛类由statistics引用

- 参数界、正值/对数域和loss必须声明


### 求解和实现

- 确认观察/误差和参数单位
- 冻结界、loss/先验及切分
- 用审阅最小二乘方法/多初值校准
- 独立前向、梯度、剖面和留出核验

Python - apis - scipy.optimize.least_squares
- scipy.linalg.solve_triangular
- dependencies - SciPy
- implementation_notes - 实现方向；本卡未有独立运行复现证据。

MATLAB - apis - lsqnonlin
- lsqcurvefit
- dependencies - Optimization Toolbox
- implementation_notes - 实现方向；本卡未有独立运行复现证据。


### 验证和回退

Baseline 一参数F(theta)=2theta、sigma=1的有界LS可手解

- - check 解析特例
- method 手解线性/一参数模型
- expected 符合界与驻点
- - check 前向/雅可比
- method 独立重算F与有限差分导数
- expected 无错单位/索引
- - check 泛化/先验
- method 留出/多初值/先验扰动
- expected 报告多解与先验依赖

- 目标项断行遗漏
- 分母/对数域错
- 残差小但不可识别
- 鲁棒loss未解释

- 固定有依据参数
- 减少自由度/报告可行集合


### 来源边界

- - title SciPy least_squares 官方本机文档
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机SciPy 1.15.3文档；网页未读取，路径/hash留local_primary_source_checks.json
- - title Per Christian Hansen Regularization Tools 4.1 原作者报告
- url https://www.imm.dtu.dk/~pcha/Regutools/RTv4manual.pdf
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已打开作者128页报告并读病态、正则化定义与相关目录；卡中公式/手核独立验算，不称整报告所有变体已读


## Tikhonov二次正则化逆问题


模型ID `inverse-tikhonov`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


为病态/欠定线性反演加入明确的平滑或先验约束


### 输入和适用条件

- 观测b、算子A、噪声尺度、L、参考x0与lambda选择政策
- 先验/正则约束确有依据，不能以低残差证明真值
- 归一尺度或lambda单位配平数据与惩罚


### 数学核心

- x未知状态；A前向算子；L正则；lambda>=0

- min_x ||Ax-b||2²+lambda²||L(x-x0)||2²
- 增广LS：[A;lambda L]x≈[b;lambda Lx0]，用QR/SVD
- L=I,x0=0时x=sum_i sigma_i/(sigma_i²+lambda²)*(u_i'b)*v_i
- lambda>0且null(A)∩null(L)={0}时目标严格凸、解唯一

- 目标如上；附加物理界须显式加入，不能求解后剪裁冒充原问题


### 求解和实现

- 定义算子/噪声与单位
- 冻结L/x0和lambda选择依据
- 解增广LS并保存残差/惩罚
- 合成恢复、独立前向/扰动核验

Python - apis - scipy.linalg.lstsq
- numpy.linalg.svd
- 原创增广系统
- dependencies - SciPy
- NumPy
- implementation_notes - 实现方向；本卡未有独立运行复现证据。

MATLAB - apis - [A;lambda*L]\[b;lambda*L*x0]
- svd
- dependencies - MATLAB
- implementation_notes - 实现方向；本卡未有独立运行复现证据。


### 验证和回退

Baseline 标量A=a,L=1,x0=0时x=a*b/(a²+lambda²)

- - check 标量解析
- method 与手解驻点对照
- expected 满足正则目标
- - check 驻点/前向
- method 独立算A'(Ax-b)+lambda²L'L(x-x0)与Ax
- expected 与容差/数据误差一致
- - check 噪声和选择
- method 扰动b、留出/已知噪声准则
- expected 说明偏差-稳定权衡而非挑最好结果

- 惩罚错量纲
- 先验不合理
- lambda事后选
- 只报告拟合

- 低维/可识别子空间
- 报告解区间/先验依赖


### 来源边界

- - title Per Christian Hansen Regularization Tools 4.1 原作者报告
- url https://www.imm.dtu.dk/~pcha/Regutools/RTv4manual.pdf
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已打开作者128页报告并读病态、正则化定义与相关目录；卡中公式/手核独立验算，不称整报告所有变体已读
- - title SciPy lstsq 官方本机文档
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机SciPy 1.15.3文档；网页未读取，路径/hash留local_primary_source_checks.json


## 截断奇异值分解反演


模型ID `inverse-tsvd`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在明确子空间内抑制小奇异值导致的噪声放大


### 输入和适用条件

- A/b、奇异值、噪声或截断选择依据
- 小奇异方向可牺牲的信息需有理由
- 截断与PCA方差保留不是同一目标


### 数学核心

- A=U diag(sigma) V'；sigma1>=...；k<=有效秩

- x_k=sum_(i=1)^k (u_i'b/sigma_i)*v_i
- 等价于在span(v1..vk)内最小化||Ax-b||2
- 滤波因子i<=k为1，i>k为0

- 子空间LS目标；截断维数预声明，不除零奇异值


### 求解和实现

- 核对算子/数据单位
- SVD与谱/Picard诊断
- 按噪声/留出政策选k
- 独立前向/扰动与被删方向核验

Python - apis - numpy.linalg.svd
- scipy.linalg.svd
- dependencies - NumPy
- SciPy
- implementation_notes - 实现方向；本卡未有独立运行复现证据。

MATLAB - apis - svd
- 原创截断组合
- dependencies - MATLAB
- implementation_notes - 实现方向；本卡未有独立运行复现证据。


### 验证和回退

Baseline A=diag(1,1e-6),b=(1,1e-3)：全解(1,1000)，k1解(1,0)

- - check 解析对角
- method 逐方向手算
- expected 展示噪声放大和信息损失
- - check 子空间残差
- method 独立投影/前向重算
- expected 符合所选子空间
- - check 截断选择
- method 噪声/真值小例与多k
- expected 不能因解小就判更真实

- 真实信号位于被删方向
- 有效秩阈值随结果改
- 病态和结构缺失混用

- 较低维可信解
- Tikhonov/新增观测


### 来源边界

- - title Per Christian Hansen Regularization Tools 4.1 原作者报告
- url https://www.imm.dtu.dk/~pcha/Regutools/RTv4manual.pdf
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已打开作者128页报告并读病态、正则化定义与相关目录；卡中公式/手核独立验算，不称整报告所有变体已读
