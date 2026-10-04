# control 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## ARX系统辨识


模型ID `ctrl-arx-identification`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


从有输入输出的时序实验识别线性离散系统


### 输入和适用条件

- 同步u/y、采样、时延、候选阶数、训练与留出
- 输入有充分激励，回归矩阵能识别系数
- 残差假设与闭环输入关联需检查；时间顺序不打乱


### 数学核心

- A(q)=1+sum_i a_i q^-i；B(q)=sum_{j=1}^nb b_j q^-(d+j-1)；e创新

- A(q)y_k=B(q)u_k+e_k
- y_k=-sum_i a_i y_(k-i)+sum_j b_j u_(k-d-j+1)+e_k
- theta最小化训练sum residual²，回归用QR/SVD

- 阶数/时延来自任务与验证；参数稳定性另检验


### 求解和实现

- 先按时间切分
- 构造滞后设计并核验索引
- 估计系数并选择阶数
- 分别检验一步/多步与残差

Python - apis - numpy.linalg.lstsq
- 原创滞后矩阵
- dependencies - NumPy
- implementation_notes - 实现方向；本卡未有完整运行验证。

MATLAB - apis - arx
- iddata
- compare
- resid
- dependencies - System Identification Toolbox
- implementation_notes - 实现方向；本卡未有完整运行验证。


### 验证和回退

Baseline 一阶已知y_k=.5y_(k-1)+2u_(k-1)无噪声回归

- - check 系数特例
- method 有充分激励的小序列独立手核
- expected 回收已知系数
- - check 残差
- method 检验自相关和输入相关
- expected 假设不满足时说明偏差
- - check 时序留出
- method 比较一步和自由滚动误差
- expected 不把训练拟合代替动态验证

- 激励不足
- 闭环相关造成LS偏差
- 阶数太大/预处理泄漏

- 低阶固定参数模型
- 改变实验/使用适当辨识方法


### 来源边界

- - title MathWorks polynomial models/ARX 官方文档（未读）
- url https://www.mathworks.com/help/ident/ug/what-are-polynomial-models.html
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 线性Kalman滤波


模型ID `ctrl-kalman-linear`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


融合状态预测与带噪测量估计状态/不确定性


### 输入和适用条件

- A/B/H、输入、测量、初始mean/cov、Q/R与采样
- 线性状态与观察；噪声零均值、白且交叉独立
- Gaussian条件给精确后验；仅二阶条件时不得称完整后验
- 创新协方差可解，Q/R需有依据
- 精确Gaussian后验还要求Gaussian初值并与后续噪声独立；已知输入u的不确定性必须另建过程噪声/联合状态。


### 数学核心

- x_k状态；w~(0,Q)、v~(0,R)；P状态误差协方差；H观测矩阵

- x_k=A*x_(k-1)+B*u_k+w_k；y_k=H*x_k+v_k
- m-=A*m+B*u；P-=A*P*A'+Q
- S=H*P-*H'+R；K=P-*H'/S；m+=m-+K*(y-H*m-)
- Joseph更新P+=(I-KH)P-(I-KH)'+K*R*K'

- 协方差对称半正定；无控制优化目标


### 求解和实现

- 核对状态/观察及噪声/初值
- 预测mean/cov
- 用线性解求K并更新
- 保存创新和后验，检查协方差/覆盖

Python - apis - 原创NumPy/SciPy线性解
- scipy.linalg.solve
- dependencies - NumPy
- SciPy
- implementation_notes - 实现方向；本卡未有完整运行验证。

MATLAB - apis - kalman(需模型配置)
- 原创矩阵递推
- dependencies - Control System Toolbox(可选)
- implementation_notes - 实现方向；本卡未有完整运行验证。


### 验证和回退

Baseline 标量先验m=0,P=4，y=2,H=1,R=1时K=.8，m+=1.6，P+=.8

- - check 手核更新
- method 与标量Gaussian组合公式比较
- expected 均值/方差一致
- - check 协方差
- method 特征值/对称残差及Joseph式
- expected 数值误差在预声明范围内
- - check 创新/覆盖
- method 留出观测检查创新相关与预测区间
- expected Q/R及模型误差主张有依据

- Q/R只为平滑曲线设置
- 未可观测状态或奇异创新
- 非线性/重尾却照称最优

- 预测-only或固定增益baseline
- 适合噪声/非线性的新估计器需单独建卡


### 来源边界

- - title Särkkä & Svensson Bayesian Filtering and Smoothing
- url https://users.aalto.fi/~ssarkka/pub/bfs_book_2023_online.pdf
- checked_at None
- evidence reference_only
- checked_scope 作者链接已定位；滤波章节本次网页未读，手核式独立验算
- metadata_recorded_at 2026-10-04


## 离散无限时域LQR


模型ID `ctrl-lqr-discrete`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在已验证线性对象上权衡状态误差与控制代价


### 输入和适用条件

- 离散A/B、状态、Q/R及成本尺度
- (A,B)可稳定，(Q^1/2,A)可检测；Q半正定、R正定
- 本卡无硬输入/状态界，饱和后保证须重验


### 数学核心

- x_(k+1)=Ax_k+Bu_k；P对称；Q/R成本矩阵

- J=sum_{k>=0}(x_k'Qx_k+u_k'Ru_k)
- P=A'PA-A'PB(R+B'PB)^(-1)B'PA+Q
- K=(R+B'PB)^(-1)B'PA；u=-Kx

- 目标J；原无硬界，不得把LQR当约束MPC


### 求解和实现

- 核对离散系统/成本单位和前提
- 解DARE并用线性解组K
- 核对Riccati残差和闭环极点
- 扰动/饱和/模型误差检验

Python - apis - scipy.linalg.solve_discrete_are
- numpy.linalg.solve
- control.dlqr(可选)
- dependencies - SciPy
- NumPy
- python-control(可选)
- implementation_notes - 实现方向；本卡未有完整运行验证。

MATLAB - apis - dlqr
- dare
- dependencies - Control System Toolbox
- implementation_notes - 实现方向；本卡未有完整运行验证。


### 验证和回退

Baseline A=B=Q=R=1时P=(1+sqrt(5))/2，K=P/(1+P)

- - check 标量解析
- method 与黄金比P/K比较
- expected DARE残差为0
- - check 闭环
- method 独立计算eig(A-BK)
- expected 在前提成立时位于单位圆内
- - check 主张边界
- method 引入真实饱和/扰动场景
- expected 不沿用无约束保证

- 不可稳定/检测
- Q/R尺度不合理
- 饱和或时变对象

- 可手核反馈或有限时域设计
- 约束控制另用MPC模型


### 来源边界

- - title SciPy solve_discrete_are 官方本机文档（1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读DARE方程与可解条件，本机源路径/版本留档
- - title Stanford EE363 Discrete LQR（链接未读）
- url https://web.stanford.edu/class/ee363/lectures/dlqr.pdf
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## PID及滤波/抗饱和策略


模型ID `ctrl-pid`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


依据误差反馈调节系统响应


### 输入和适用条件

- 对象/采样、参考与输出、执行器界、噪声、目标性能
- 增益和控制形式必须声明；对象动力适合当前操作域
- 理想微分不能直接用于高噪声实际测量


### 数学核心

- e=r-y；Kp[u/e]、Ki[u/(e*time)]、Kd[u*time/e]；N[1/time]

- 理想u=Kp*e+Ki*integral(e dt)+Kd*de/dt
- 滤波传函C(s)=Kp+Ki/s+Kd*N*s/(s+N)
- 饱和后抗积分累积策略必须另说明，不由PID名字自动包含

- 执行器u_min≤u≤u_max；性能指标来自任务


### 求解和实现

- 先辨识/验证对象
- 选PI/PID及导数滤波/离散法
- 以小信号与扰动仿真调参
- 核对饱和、积分、噪声和时间指标

Python - apis - 原创离散控制循环
- python-control.tf/feedback（可选）
- dependencies - NumPy
- python-control(可选)
- implementation_notes - 实现方向；本卡未有完整运行验证。
- 可选库在本机未安装；不能声称已调用

MATLAB - apis - pid
- pidstd
- feedback
- step
- dependencies - Control System Toolbox
- implementation_notes - 实现方向；本卡未有完整运行验证。
- 核对并联/标准形式与微分滤波参数


### 验证和回退

Baseline Kp反馈或开环固定输入；积分仅在持续误差时积累

- - check 量纲
- method 逐项核对输出单位
- expected 三项同单位
- - check 饱和试验
- method 阶跃/扰动含执行器界
- expected 积分不会持续无界累积
- - check 采样/噪声
- method 减小dt并增加测量噪声
- expected 说明性能和导数敏感性

- 饱和后仍按线性闭环结论
- 误把神经PID权重律等同固定增益PID
- 延迟/噪声忽略

- PI或滤波微分
- 缩小控制域并重新识别


### 来源边界

- - title MathWorks PID controller types 官方入口（未读）
- url https://www.mathworks.com/help/control/ug/pid-controller-types-for-tuning.html
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 线性状态空间与采样模型


模型ID `ctrl-state-space`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


表示被控对象、状态与测量的动态关系


### 输入和适用条件

- A/B/C/D或可辨识实验、采样周期、初值、输入与测量定义
- 当前窗口线性时不变或有明确线性化域
- 采样/延迟/输入保持方式由任务确定


### 数学核心

- x状态、u输入、y输出；A∈R^(n×n)、B∈R^(n×m)、C∈R^(p×n)、D∈R^(p×m)

- 连续x'=A*x+B*u，y=C*x+D*u；离散x_(k+1)=Ad*x_k+Bd*u_k
- 零阶保持Ad=exp(A*dt)，Bd=integral_0^dt exp(A*tau)B d_tau
- 可控矩阵[B AB ... A^(n-1)B]；可观测矩阵[C;CA;...;CA^(n-1)]

- 无固定优化目标；稳定性按连续实部/离散模数核验


### 求解和实现

- 定义状态/输入/测量及单位
- 确认连续或采样模型
- 核查维数/秩与极点
- 开环解析/数值与数据核验

Python - apis - scipy.signal.StateSpace
- cont2discrete
- lsim
- dlsim
- dependencies - SciPy
- implementation_notes - 实现方向；本卡未有完整运行验证。

MATLAB - apis - ss
- c2d
- lsim
- ctrb
- obsv
- dependencies - Control System Toolbox
- implementation_notes - 实现方向；本卡未有完整运行验证。


### 验证和回退

Baseline 标量x'=-a*x+b*u的常输入解析解

- - check 维数和单位
- method 逐矩阵核查
- expected 状态/输出定义一致
- - check 采样一致
- method 解析标量或矩阵指数与小dt比较
- expected 对应输入保持语义
- - check 可辨识/可控观测
- method 秩/奇异值而非仅rank布尔
- expected 说明不可观测状态

- 不恰当线性化
- 采样混叠/延迟遗漏
- 状态不能被数据识别

- 低阶输入输出模型
- 缩小操作域


### 来源边界

- - title SciPy StateSpace 官方本机文档（1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.StateSpace.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机StateSpace文档；URL网页未读取，见local_primary_source_checks.json
