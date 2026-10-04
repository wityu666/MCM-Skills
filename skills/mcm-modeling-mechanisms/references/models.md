# mechanisms 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## SOC–RC Thevenin电池与简化热耦合


模型ID `mech-battery-soc-rc-thermal`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


解释电流负载下SOC、电压松弛与温度变化


### 输入和适用条件

- 电流/时间、电压、容量、OCV–SOC–T关系、R0/R1/C1与热参数；初值
- 正I为放电；参考参数在窗口固定，未建模老化/扩散机制
- 参考热式仅欧姆/RC耗散，熵热等若重要需加入并验证
- 本卡库仑计量baseline取eta=1；充放电效率扩展需分方向与数据依据，不采用无依据通用常数。


### 数学核心

- z∈[0,1] SOC；I[A]；Q[Ah]；Vp[V]；R[ohm]；C1[F]；Cth[J/K]；hA[W/K]

- z'=-eta*I/(3600*Q)
- Vp'=-Vp/(R1*C1)+I/C1；V=OCV(z,T)-I*R0-Vp
- Cth*T'=I²*R0+Vp²/R1-hA*(T-Ta)（声明的简化热模型）

- Q,R1,C1,Cth>0，R0,hA>=0；SOC到界时停止或切换，不能用剪裁掩盖不守恒


### 求解和实现

- 核对电流正号/容量单位和OCV来源
- 用静态内阻/库仑计量baseline
- 校准RC与热参数，分离时间验证
- 求解并核对电荷、松弛与热量级

Python - apis - solve_ivp
- pybamm.equivalent_circuit.Thevenin（版本核对）
- dependencies - SciPy
- PyBaMM(可选)
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。
- PyBaMM所读22.11默认热结构有cell/jig两个节点；本卡简化单节点热式不等同其默认热子模型，选库时需明确重建/匹配。

MATLAB - apis - 原创ODE
- Simulink等效电路（可选）
- dependencies - MATLAB
- Simulink(可选)
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline 恒流时z线性；I=0时Vp指数衰减；无热源时T→Ta

- - check 容量单位
- method 独立积分I*dt/3600
- expected 与Ah与SOC变化一致
- - check RC特例
- method I=0时Vp=Vp0 exp(-t/(R1*C1))
- expected 松弛时间常数一致
- - check 耗散与储能
- method 核对电阻热和RC储能，不把I(OCV-V)全部当电阻热
- expected 能量定义与热近似透明
- - check 外层验证
- method 用未参与校准的负载段对比V/T
- expected 说明参数和任务范围

- 用手机功率直接当实测电流
- R/C混淆或OCV不足
- 热/老化依赖显著

- SOC+静态R baseline
- 固定有依据参数区间、温度影响单列情景


### 来源边界

- - title thevenin维护者 Model Description
- url https://thevenin.readthedocs.io/stable/user_guide/model_description.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已打开维护者模型说明；本卡额外热耗散式由RC能量平衡独立推导，不代表文档全部变体
- - title PyBaMM Thevenin 22.11文档（已读版本）
- url https://docs.pybamm.org/en/v22.11/source/models/equivalent_circuit/thevenin.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读维护者文档的OCV/电阻/RC结构与热耦合说明；不声称当前版本接口已运行


## 离散Logistic映射


模型ID `mech-discrete-logistic`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


描述固有离散的非线性反馈/学习分岔


### 输入和适用条件

- x0、r、时间步意义；真实过程需映射
- 不能把离散映射与连续Logistic ODE的参数/稳定性混为一谈
- 比例解释用x0∈[0,1]和0≤r≤4


### 数学核心

- x_k比例；r无量纲，每步时间需说明

- x_(k+1)=r*x_k*(1-x_k)
- 固定点0及1-1/r（r!=0）；后者局部导数2-r

- 物理比例域0≤x≤1时限制0≤r≤4；无优化目标


### 求解和实现

- 定义每步含义和参数
- 逐步迭代保存状态
- 核对固定点/区间
- 按稳定或敏感区间选择验证

Python - apis - 原创NumPy迭代
- dependencies - NumPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - 原创for迭代
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline r=0时下一步为0；固定点轨迹

- - check 区间
- method 利用x(1-x)≤1/4独立检查
- expected 指定参数域内不离开[0,1]
- - check 固定点
- method 独立代入固定点
- expected 下一步等于当前
- - check 局部稳定
- method 核对|2-r|与扰动
- expected 对应局部而非全球声明

- 时间步/比例定义不当
- 长期逐点比较未考虑敏感性

- 固定点/短期分析
- 报告参数区间与统计性质


### 来源边界

- - title May 1976 Simple mathematical models with very complicated dynamics
- url https://doi.org/10.1038/261459a0
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 一维热扩散与Crank–Nicolson离散


模型ID `mech-heat-diffusion-cn`　类别 `model`　知识等级 `REFERENCE_IMPL_TESTED`


在给定材料/边界下预测温度或扩散场


### 输入和适用条件

- 扩散系数C、域长L、初值phi、边界及时间；具体物理量单位
- 参考实现C常量、无源、1D、零Dirichlet；变系数/源/通量边界须重推
- 网格和时间步需要精度检验


### 数学核心

- u场量；C[length²/time]；dx,dt；r=C*dt/dx²；T三对角[-2,1,1]

- u_t=C*u_xx
- (I-r*T/2)u^(k+1)=(I+r*T/2)u^k（内点，零边界）
- phi=sin(pi*x/L)时u=exp(-C*pi²*t/L²)sin(pi*x/L)

- 初/边值按任务；CN线性能量稳定不保证大r下无振荡/非负


### 求解和实现

- 核对初边值和量纲
- 推导离散算子并组带状矩阵
- 逐步求解记录r和状态
- 解析模态/能量/网格收敛核验

Python - apis - scripts/heat_cn.py
- scipy.linalg.solve_banded
- dependencies - NumPy
- SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。
- 本库原创Python已测；只覆盖上述参考范围

MATLAB - apis - scripts/heat_cn.m
- spdiags
- A\b
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。
- 原创对应文件静态未运行，不能继承Python运行通过


### 验证和回退

Baseline 正弦模态解析解与零场

- - check 解析模态
- method Nx20/40相应细化dt，对照正弦衰减
- expected 误差下降并接近二阶空间行为
- - check 能量
- method 独立计算sum(u_i²)
- expected 无源零边界时不增加
- - check 定义域
- method 拒绝非零边界/非有限输入
- expected 不静默更改模型

- 把r误写dt/dx
- 隐式可算却不检验精度
- 大步长振荡

- 细化时间/空间
- 简化1D解析特例，复杂边界另写合同


### 来源边界

- - title Crank & Nicolson 1947 原论文（未读取链接）
- url https://doi.org/10.1017/S0305004100023197
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04
- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本


## 线性分室守恒模型


模型ID `mech-linear-compartments`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


描述多个充分混合存量间的传输


### 输入和适用条件

- 初始存量、转移率、外部流入/流出、观察数据
- 各室充分混合；一级转移率适用于当前尺度
- 率非负；外部汇与源不能遗漏


### 数学核心

- m_i存量[mass]；q_ij从i到j率[1/time]；u_i流入[mass/time]；o_i外流率

- dm_i/dt=sum_{j!=i} q_ji*m_j - sum_{j!=i} q_ij*m_i + u_i - o_i*m_i
- 矩阵dm/dt=K*m+u；K非对角非负，列和=-o

- m_i>=0；封闭系统u=o=0时总量守恒


### 求解和实现

- 建立室/流图与单位
- 从逐室平衡组K
- 求解并记录外部累计流量
- 核对总量与观测

Python - apis - numpy
- scipy.linalg.expm
- solve_ivp
- dependencies - NumPy
- SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - expm
- ode45
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline 两个封闭室只由1流向2时m1=m10 exp(-q t)、m2=总量-m1

- - check 守恒
- method 独立核对d(sum m)/dt=sum u-sum o_i*m_i
- expected 闭合系统总量不变
- - check 非负性
- method 检查率/初值和负状态量级
- expected 物理域成立且数值误差可解释

- 混合不充分
- 转移率随状态变而仍用常率
- 观察不能分辨多个率

- 合并不可区分室
- 改非线性通量并重新验算


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本


## Logistic连续增长模型


模型ID `mech-logistic-growth`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


刻画受有限容量约束的单种群增长


### 输入和适用条件

- N0、时间与种群观测；r/K来源
- r,K在所研究窗口固定且K>0
- 同质单群体；无未建模捕食/迁移
- 本增长卡采用r>=0、K>0；N0=0为恒零特例，N0>0才使用给出的闭式分式。


### 数学核心

- N种群/存量；r[1/time]；K与N同单位

- dN/dt=r*N*(1-N/K)
- N(t)=K/[1+(K/N0-1)*exp(-r*t)]，N0>0

- N>=0；r,K估计约束来自当前问题


### 求解和实现

- 核对尺度和是否需容量机制
- 从训练窗口校准r,K或声明情景
- 解析或ODE求解
- 留出与参数剖面核验

Python - apis - solve_ivp
- scipy.optimize.least_squares
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - ode45
- lsqcurvefit
- dependencies - MATLAB
- Optimization Toolbox(校准时)
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline 初期指数增长或r=0的常量路线

- - check 解析一致
- method 数值轨迹与闭式解比较
- expected 一致于声明容差
- - check 平衡
- method 独立代入N=0,K
- expected 导数为0
- - check 识别与外推
- method 参数剖面/时间留出与指数baseline
- expected 说明r/K混淆和外推误差

- 观测只在初期导致K不可识别
- 容量或外部输入变化

- 报告K区间
- 短时指数/分段模型


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本
- - title Logistic连续增长：闭式解为本卡独立代入核验；SciPy文档仅支持ODE实现接口
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 本机官方接口文档已读；不以其作为Verhulst历史原文引用


## Lorenz三维动力系统


模型ID `mech-lorenz`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


学习非线性动力、平衡与初值敏感性


### 输入和适用条件

- 初值、sigma/rho/beta、时间尺度；真实应用另需测量映射
- 此低维系统是所研究过程的适当近似；不能只因轨迹相似认定机理
- 混沌参数区间不由名称自动保证
- 经典卡采用sigma>0、beta>0；rho范围须声明，rho>1时给出的非零平衡才在此参数域可用。


### 数学核心

- x,y,z状态（原非量纲化模型）；sigma,rho,beta参数

- x'=sigma*(y-x)；y'=x*(rho-z)-y；z'=x*y-beta*z
- rho>1时平衡为(±sqrt(beta*(rho-1)),±sqrt(beta*(rho-1)),rho-1)，同号

- 没有固定优化目标；参数/观察域由任务声明


### 求解和实现

- 定义无量纲尺度/参数来源
- 选平衡/短期数值baseline
- 记录容差与初值
- 区分短期轨迹与长期统计检验

Python - apis - solve_ivp
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - ode45
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline 各平衡点恒定轨迹

- - check 平衡
- method 代入方程独立重算
- expected 三个导数为0
- - check 敏感性
- method 相近初值与更细容差分开比较
- expected 不能以长期逐点不一致自动判实现错
- - check 长期量
- method 按任务比较分布/均值与置信范围
- expected 主张有对应统计口径

- 把数值敏感当参数已识别
- 任意参数均宣称混沌

- 短时/平衡分析
- 报告长期统计与适用边界


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本
- - title Lorenz 1963 Deterministic Nonperiodic Flow
- url https://doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## Lotka–Volterra捕食—被捕食模型


模型ID `mech-lotka-volterra`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


解释两类群体的相互作用动力


### 输入和适用条件

- 正初始种群、时间序列及作用率依据
- 充分混合、参数固定；没有自限/迁移/外部干预
- 物种相互作用符号与观察范围应检验
- 主捕食卡alpha,beta,gamma,delta>0；beta=delta=0仅作为无相互作用的退化baseline。


### 数学核心

- x猎物、y捕食者；alpha/gamma[1/time]；beta/delta分别与对应种群单位配平

- dx/dt=alpha*x-beta*x*y
- dy/dt=delta*x*y-gamma*y
- 正平衡x*=gamma/delta, y*=alpha/beta
- H=delta*x-gamma*ln(x/x_ref)+beta*y-alpha*ln(y/y_ref)（正值域，参考尺度同单位）

- x,y>=0；未规定优化目标


### 求解和实现

- 核对生态链中实际相互作用
- 采用两物种baseline；复杂链单独写通量
- 校准/情景并求解
- 核查平衡、H和留出

Python - apis - solve_ivp
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - ode45
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline 正平衡常量轨迹；无相互作用beta=delta=0时独立指数

- - check 平衡
- method 将正平衡代入两方程
- expected 两个导数为0
- - check 守恒特例
- method 固定参数无干预模型核对H随时间漂移
- expected 随积分精度改善而减小
- - check 物理域
- method 检验非负与时间留出
- expected 不把模型周期直接称真实生态规律

- 自限/空间/多种群机制缺失
- 参数不可识别
- 样本少却预测远期周期

- 独立增长baseline
- 增加有依据通量并重新冻结


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本
- - title Volterra 1926 物种丰度变化论文
- url https://doi.org/10.1038/118558a0
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 常微分方程初值建模


模型ID `mech-ode-ivp`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


从速率机制预测状态轨迹及事件


### 输入和适用条件

- f(t,x,theta)、初值x0、时间范围、参数/观察方程
- 初值完整；存在性/唯一性需核对局部连续/Lipschitz或对应理论
- 刚性、事件或不连续不能由默认步长掩盖


### 数学核心

- t时间；x状态向量，各分量单位由题设给；f单位x/time

- dx/dt=f(t,x,theta), x(t0)=x0
- 观测y_k=h(x(t_k),theta)+epsilon_k

- 不适用固定优化目标；定义域/事件来自模型


### 求解和实现

- 从通量/速率推导f并核对量纲
- 确定初值、域、观察与参数来源
- 选非刚性RK或适合刚性的隐式法并设置误差/事件
- 输出状态与独立检验

Python - apis - scipy.integrate.solve_ivp
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。
- 记录method/rtol/atol、status和事件；不要复制旧ODE45系统函数

MATLAB - apis - ode45
- ode15s
- odeset
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。
- 按刚性/维数选择；核对which-all与求解终止


### 验证和回退

Baseline 标量x'=-a*x的解析解x=x0 exp(-a(t-t0))

- - check 解析特例
- method 与标量指数解比较并收紧容差
- expected 误差随容差/步长改善
- - check 机理不变量
- method 独立计算单位、守恒或域残差
- expected 符合当前模型而非统一阈值

- 初值/机制未知
- 不可辨识参数
- 刚性或突变被忽略

- 简化状态或分段模型
- 保留无法识别参数区间


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本


## SEIR含潜伏期分室模型


模型ID `mech-seir`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在传播模型中显式表示尚未感染性/未转出暴露状态


### 输入和适用条件

- S/E/I/R初值、潜伏转移率、传播/移出率及观测定义
- 暴露期是否具有感染性由题设决定，本卡E不传播
- 封闭且充分混合、率固定；潜伏时间采用指数等待近似


### 数学核心

- S,E,I,R比例；beta,sigma,gamma[1/time]

- S'=-beta*S*I；E'=beta*S*I-sigma*E
- I'=sigma*E-gamma*I；R'=gamma*I

- 各分量非负，总和1；无固定优化目标


### 求解和实现

- 核验潜伏分室是否有必要/数据可识别
- 定义观察与估计窗口
- 求解并比较SIRbaseline
- 敏感性与守恒核验

Python - apis - solve_ivp
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - ode45
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline beta=0时E指数衰减；sigma很大时与适当SIR极限比较

- - check 守恒
- method 独立逐式相加
- expected 总导数为0
- - check 零传播
- method 解析E=E0 exp(-sigma t)
- expected 暴露衰减一致
- - check 识别
- method sigma/beta联合参数剖面
- expected 不可识别时报告集合

- 仅感染观测无法分辨潜伏/传播
- 指数等待与真实延迟不符

- SIR简模型
- 固定有依据的潜伏区间或延迟模型


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本
- - title Kermack–McKendrick SIR原论文定位；本卡SEIR是显式增加潜伏室的模型
- url https://doi.org/10.1098/rspa.1927.0118
- checked_at None
- evidence reference_only
- checked_scope 链接未读，不声称该1927文献核验了本卡全部SEIR扩展
- metadata_recorded_at 2026-10-04


## SIR分室传播模型


模型ID `mech-sir`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


描述封闭群体的易感、感染与移出变化


### 输入和适用条件

- 群体/时间边界、初始分量、传播与移出率及观测定义
- 本卡用比例S+I+R=1；充分混合、固定率、无人口流动
- 感染/移出观测不等于所有真实状态，识别需另检验


### 数学核心

- S,I,R无量纲比例；beta/gamma[1/time]

- S'=-beta*S*I；I'=beta*S*I-gamma*I；R'=gamma*I
- 使用人数时感染项必须为beta*S*I/N
- 初期有效增长率beta*S0-gamma，不仅看beta/gamma

- S,I,R>=0且总和1；无决策优化目标


### 求解和实现

- 确认观测与分室定义
- 确定率及时间范围
- 求解并映射观测
- 做总量、早期线性与留出检验

Python - apis - solve_ivp
- dependencies - SciPy
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。

MATLAB - apis - ode45
- dependencies - MATLAB
- implementation_notes - 接口为实现方向；未运行的语言/变体保持未验证。


### 验证和回退

Baseline beta=0时I=I0 exp(-gamma t)、S恒定

- - check 总量
- method 逐式相加并数值核对
- expected S+I+R恒定
- - check 早期符号
- method 独立检查beta*S0-gamma
- expected 感染增长方向与方程一致
- - check beta=0特例
- method 与解析衰减比较
- expected 一致于声明容差

- 流动/潜伏/干预机制显著
- 传播率与报送率混淆

- 使用短窗条件性情景
- 增加有依据分室，不把拟合用于临床决策


### 来源边界

- - title SciPy solve_ivp 官方本机文档（SciPy 1.15.3）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 读取本机函数文档；网页工具失败，URL网页本次未读取；local_primary_source_checks.json留源路径/版本
- - title Kermack–McKendrick 1927 原论文
- url https://doi.org/10.1098/rspa.1927.0118
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04
