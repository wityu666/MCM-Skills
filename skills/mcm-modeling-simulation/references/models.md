# simulation 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 主体/场景仿真结构


模型ID `sim-agent`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


表达多主体交互与行为规则的系统结果


### 输入和适用条件

- 主体状态/决策/交互图、时间/事件方式、随机机制与校准数据
- 主体类名不等于已给出行为模型；微观规则有依据且观察数据独立


### 数学核心

- a_i为主体状态
- F_i为更新/交互规则

- a_i(t+1)=F_i(a_i(t),neighbors,environment,ξ_i)；宏观量由明确聚合生成

不是仅写class Player就构成已审清ABM


### 求解和实现

- 画规则与因果输入
- 手核少主体场景
- 校准/验证分开、敏感性及反事实限制

Python - apis - 原创主体/事件循环
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创结构体/对象循环
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 无交互聚合/确定性场景

- - check 规则
- method 2主体一步手核
- expected 更新与资源守恒一致
- - check 证据
- method 独立观测/场景敏感性
- expected 拟合相同宏观均值不证明微观参数唯一

- 规则臆造
- 参数不可识别
- 结果宣传当实测

- 简化机制/场景区间


### 来源边界

- - title MathWorks SimEvents statistical analysis
- url https://www.mathworks.com/help/simevents/ug/statistics-for-data-analysis.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 区分暂态/稳态、样本量、独立重复次数与事件统计量。
- verification_origin shared primary_sources.json#ps-simstats


## Brownian/Wiener过程与SDE离散化


模型ID `sim-brownian`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


连续随机扰动的标准基础模型/离散近似


### 输入和适用条件

- 漂移a、扩散b、初态、时间单位/步长与噪声假设
- 独立高斯增量是明确建模假设；噪声并非任意randn点拼接


### 数学核心

- ΔW~N(0,Δt)
- X为状态，b单位X/√time

- W0=0,E[Wt]=0,Cov(Ws,Wt)=min(s,t)
- dX=a(X,t)dt+b(X,t)dW；EM步X′=X+aΔt+b√ΔtZ

非线性SDE需步长稳定/强弱误差条件；与统计EM算法不同


### 求解和实现

- 检查扩散量纲与增量
- 生成并保存路径/seed
- 对照可解析过程与步长/重复分布

Python - apis - 原创RNG路径/EM步
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创randn路径/EM步
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline Brownian均值0方差t；常系数X=x0+at+bWt

- - check 尺度
- method 不同Δt同一终点分布
- expected 方差b²t而非b²×步数
- - check 误差
- method 步长减半解析特例
- expected 不把绘图平滑当误差证明

- 漏√Δt
- 重尾/相关噪声假设不符
- 数值爆炸

- 离散Markov/经验扰动场景并说明信息损失


### 来源边界

- - title Kloeden and Platen Numerical Solution of SDEs
- url https://doi.org/10.1007/978-3-662-12616-5
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 元胞自动机


模型ID `sim-cellular`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


局部规则产生时空离散动力学


### 输入和适用条件

- 网格/状态集、邻域、更新规则、边界与初态
- 同步/异步更新不同；局部规则需题设/机制依据


### 数学核心

- s_i(t)为元胞状态
- N(i)为邻域

- s_i(t+1)=F({s_j(t):j∈N(i)})；随机CA另声明转移概率

边界/同步方式不可从代码默认推成物理事实


### 求解和实现

- 冻结规则/单位
- 双缓冲同步或明确异步
- 手核小网格、边界与守恒/稳定性

Python - apis - 原创网格更新
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创矩阵/双缓冲
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 一维3–5格逐步手算

- - check 时序
- method 同步小例与原位逐格比较
- expected 不把异步更新误当同步
- - check 边界
- method 周期/固定边界手例
- expected 行为与声明一致

- 更新顺序隐含
- 网格依赖
- 规则仅拟合现象

- 更简单状态递推/明确情景模型


### 来源边界

- - title Wolfram Statistical mechanics of cellular automata
- url https://doi.org/10.1103/RevModPhys.55.601
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 离散事件仿真


模型ID `sim-events`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按事件时刻更新排队/库存/资源状态


### 输入和适用条件

- 状态、事件类型/时间、转移、到达/服务/故障机制与时域
- 事件规则可解释；同刻事件优先级与资源守恒明确


### 数学核心

- 时钟t
- 未来事件表

- t推进到下一最早事件；按转移更新状态并安排后续事件
- 时间均值=Σ状态值×持续时间/总时长，不等于事件样本均值

事件排序与统计量定义是模型一部分


### 求解和实现

- 手写少量事件轨迹
- 事件队列执行与守恒检查
- 热身/重复/解析特例

Python - apis - 原创heapq事件表
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - SimEvents（若许可）或原创事件表
- dependencies - MATLAB基础功能
- SimEvents/Simulink
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 2–3到达服务事件手算

- - check 轨迹
- method 人工日历对照
- expected 时序与资源计数正确
- - check 平均
- method 时间加权手算
- expected 不把频繁事件偏置均值

- 同刻顺序不定
- 零时间事件无限循环
- 暂态当稳态

- 有限事件手算/确定性场景


### 来源边界

- - title MathWorks SimEvents statistical analysis
- url https://www.mathworks.com/help/simevents/ug/statistics-for-data-analysis.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 区分暂态/稳态、样本量、独立重复次数与事件统计量。
- verification_origin shared primary_sources.json#ps-simstats


## 开放有限容量M/M/c/K


模型ID `sim-finite-capacity`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


外来总到达率固定但满员阻塞的队列


### 输入和适用条件

- 总到达率λ≥0、服务μ>0、正整数服务器c、整数总容量K≥c
- 到达源开放；容量K包含服务与排队；满员拒绝


### 数学核心

- λ_n=λ(n<K),λ_K=0
- μ_n=min(n,c)μ

- 用生灭积比归一p_n；阻塞概率p_K；λ_eff=λ(1-p_K)
- L=Σn p_n；W=L/λ_eff

有限状态可有稳态；不能套无限容量λ<cμ作为必要稳定条件


### 求解和实现

- 确认容量/阻塞政策
- 归一有限状态分布
- 核吞吐/阻塞/Little关系

Python - apis - 原创递推/事件表
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创递推/SimEvents
- dependencies - MATLAB基础功能
- SimEvents/Simulink
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline c=K=1时p1=λ/(λ+μ)

- - check 语义
- method 与有限源对照
- expected λ_n常数而非(N-n)λ
- - check 流量
- method 接受到达率 vs离开率
- expected 稳态守恒

- K是排队长度还是总容量不明
- 误套无限容量式
- 把丢客当等待

- 明确阻塞规则后DES


### 来源边界

- - title MathWorks M/M/1 Queuing System
- url https://uk.mathworks.com/help/simevents/ug/m-m-1-queuing-system.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope Poisson到达、指数服务、单服务器、无限容量、等待时间理论对照。
- verification_origin shared primary_sources.json#ps-queue
- - title MathWorks dtmc asymptotics
- url https://www.mathworks.com/help/econ/dtmc.asymptotics.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope pi P=pi，多个常返类、周期性与遍历链的平稳/极限分布差异。
- verification_origin shared primary_sources.json#ps-markov


## 有限源多服务器生灭队列


模型ID `sim-finite-source`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


当闲置源数量影响到达率时估计系统占据


### 输入和适用条件

- 正整数源人口N、正整数服务器c、每闲置源激发率λ≥0、每忙服务器服务率μ>0
- N有限且每源最多一项；指数/独立假设；不是常总率开放到达


### 数学核心

- n=0,…,N
- λ_n=(N-n)λ
- μ_n=min(n,c)μ

- p_n=p_0∏_(k=0)^(n-1)(λ_k/μ_(k+1))，按Σp=1归一
- λ_eff=Σp_n λ_n；L=Σn p_n，W=L/λ_eff（若>0）

N是源总数，不是系统容量K的同义字母


### 求解和实现

- 先确认有限源语义
- 递推归一，不写死m-5阶乘
- 核概率/流平衡与事件模拟

Python - apis - 原创生灭递推（log域可选）
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创生灭递推
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline N=c=1,p1=λ/(λ+μ)

- - check 特例
- method 两状态独立解
- expected 概率比λ/μ
- - check 流平衡
- method p_nλ_n=p_(n+1)μ_(n+1)
- expected 各相邻状态相等

- 误用恒定λ
- 阶乘负参数/硬列公式
- λeff=0时除零

- 直接有限状态Markov/事件模拟


### 来源边界

- - title MathWorks M/M/1 Queuing System
- url https://uk.mathworks.com/help/simevents/ug/m-m-1-queuing-system.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope Poisson到达、指数服务、单服务器、无限容量、等待时间理论对照。
- verification_origin shared primary_sources.json#ps-queue
- - title MathWorks dtmc asymptotics
- url https://www.mathworks.com/help/econ/dtmc.asymptotics.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope pi P=pi，多个常返类、周期性与遍历链的平稳/极限分布差异。
- verification_origin shared primary_sources.json#ps-markov


## Gibbs条件采样


模型ID `sim-gibbs`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


利用可采样的完整条件分布构造后验链


### 输入和适用条件

- 每个p(x_j|x_-j)和相容联合模型
- 完整条件分布确实来自同一联合分布；顺序/块方案明确


### 数学核心

- x_j为条件更新坐标

- 按p(x_j|x_-j)更新各坐标；不是把边缘分布独立相乘

随机/系统扫描核与边界条件需一致


### 求解和实现

- 推导完整条件
- 初始化并固定扫描/块
- 多链/已知联合分布核验

Python - apis - 原创条件采样
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创条件采样
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 二维独立正态；或小联合概率表

- - check 条件
- method 从联合表独立重算
- expected 与采样条件一致
- - check 相关
- method 已知相关正态小例
- expected 不把条件替成边缘而抹掉相关

- 条件不相容
- 强相关混合慢
- 截断域遗漏

- 块采样/MH或直接小例积分


### 来源边界

- - title Geman and Geman Stochastic Relaxation (1984)
- url https://doi.org/10.1109/TPAMI.1984.4767596
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 重要性采样与方差缩减


模型ID `sim-importance`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


改善随机估计而保持正确目标


### 输入和适用条件

- 目标p、提议q/可求密度比，或已知均值控制量
- q覆盖p·g支持；权重矩有限；控制均值真实已知


### 数学核心

- w=p/q
- c为控制量且E[c]已知

- μhat=mean[g(X) p(X)/q(X)],X~q
- 控制变量g-β(c-E[c])；对偶变量利用负相关

自归一化权重是不同有限样本估计，有偏性需说明


### 求解和实现

- 核支持与权重
- 设计提议/控制变量
- 独立与朴素MC比较偏差与方差

Python - apis - 原创RNG/密度比
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创抽样/权重
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 朴素MC+解析期望

- - check 支持
- method p>0而q=0反例
- expected 拒绝错误提议
- - check 权重
- method 已知积分与有效样本诊断
- expected 不能只看加权样本数

- 支持缺口
- 权重爆炸
- 错控制均值

- 朴素MC或混合提议并报告尾部限制


### 来源边界

- - title Owen Monte Carlo theory, methods and examples
- url https://artowen.su.domains/mc/
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 有限状态可观测Markov链


模型ID `sim-markov`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


描述已观测状态的一步转移/占据分布


### 输入和适用条件

- 状态定义、转移P或连续观测序列、初分布与步长
- 一阶/齐次性由任务检验；不同P估计窗口不能混同


### 数学核心

- P_ij=P(S_(t+1)=j|S_t=i)
- 行向量π_t

- π_(t+1)=π_t P；P≥0,Σ_jP_ij=1
- stationary πP=π；遍历性才保证一般初分布收敛

不含HMM发射模型；零频行需明确未知/吸收假设


### 求解和实现

- 定义状态与采样步长
- 估计/给定P并核行
- 区分平稳分布、周期与多常返类

Python - apis - 原创矩阵转移
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - dtmc/asymptotics方向
- dependencies - MATLAB基础功能
- Econometrics Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 两状态P=[[.8,.2],[.4,.6]]的平稳(2/3,1/3)

- - check 概率
- method 行/非负与πP
- expected 约束满足，手核stationary
- - check 周期
- method 交替链P=[[0,1],[1,0]]
- expected stationary存在但起点分布不收敛

- 伪齐次
- 把stationary当limit
- 状态/单位未定义

- 分时P或经验频率；说明失去Markov预测


### 来源边界

- - title MathWorks dtmc asymptotics
- url https://www.mathworks.com/help/econ/dtmc.asymptotics.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope pi P=pi，多个常返类、周期性与遍历链的平稳/极限分布差异。
- verification_origin shared primary_sources.json#ps-markov


## Markov链Monte Carlo


模型ID `sim-mcmc`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


构造以目标后验/分布为平稳分布的采样链


### 输入和适用条件

- 非负可计算未归一π、状态域、转移核与初值/预算
- 核须保持π并有适当可达性/遍历；独立MC不是MCMC


### 数学核心

- X_t为链
- K为转移核

- 不变分布条件πK=π；可用详细平衡π(x)K(x,y)=π(y)K(y,x)
- 依赖样本估计需要自相关/有效样本而非N独立SE

无优化目标；收敛到分布不等于找到唯一最优点


### 求解和实现

- 定义目标与核
- 多起点记录轨迹/接受率
- 诊断混合/有效样本与已知目标

Python - apis - 原创核；ArviZ仅诊断方向
- dependencies - ArviZ
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创采样核+诊断
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 独立可解析目标或有限状态完整概率表

- - check 不变性
- method 有限小核直接πK比较
- expected 保持目标分布
- - check 混合
- method 多链/自相关与已知均值
- expected 诊断不替绝对收敛证明

- 支持不可达
- 多模态困住
- 未固定适应规则

- 直接抽样/数值积分或区间说明


### 来源边界

- - title Metropolis et al. Equation of State Calculations
- url https://doi.org/10.1063/1.1699114
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Markov决策过程


模型ID `sim-mdp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在状态/动作/随机转移下选择长期策略


### 输入和适用条件

- S、可行动作A(s)、P(s′|s,a)、奖励/成本、折扣γ或有限时域
- 状态充分；无限折扣版本0≤γ<1且奖励有界


### 数学核心

- V(s)为累计期望奖励
- π(s)为策略

- V*(s)=max_a[r(s,a)+γΣP(s′|s,a)V*(s′)]
- 值迭代应用Bellman算子；策略迭代交替评估/改进

奖励最大化与成本最小化不能混用；γ=1长期平均需另一合同


### 求解和实现

- 核动作/P/奖励语义
- 先固定策略评估baseline
- 值/策略迭代并核Bellman残差

Python - apis - 原创矩阵Bellman迭代
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创矩阵Bellman迭代
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 一状态奖励0/1,γ=.5，选1价值2

- - check 解析
- method 几何级数计算
- expected 最优价值2
- - check 收敛
- method Bellman残差与1/(1-γ)界
- expected 仅在折扣收缩条件内使用界

- 状态漏历史
- 未知转移编造
- γ=1误用收缩性

- 固定策略仿真或有限时域DP，失去无限策略主张


### 来源边界

- - title Sutton and Barto Reinforcement Learning
- url http://incompleteideas.net/book/the-book-2nd.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Metropolis–Hastings


模型ID `sim-mh`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


通过接受/拒绝提议保持目标π


### 输入和适用条件

- π(x)未归一密度、q(y|x)、log值与预算
- 提议支持覆盖目标；反向q必须可求


### 数学核心

- α(x,y)为接受率

- α=min(1, π(y)q(x|y)/(π(x)q(y|x)))
- logα=min(0,logπ(y)-logπ(x)+logq(x|y)-logq(y|x))

拒绝时保留原状态，不删除拒绝样本


### 求解和实现

- 检查支持/初值
- 提议并在log域接受
- 保留完整轨迹并做混合诊断

Python - apis - 原创MH核
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创MH核
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 有限2状态直接计算转移矩阵

- - check 详细平衡
- method 手算πxKxy=πyKyx
- expected 两侧相等
- - check 不对称提议
- method 人为不对称q
- expected 不得漏q比

- 溢出
- 漏反向提议
- 只保接受样本

- 独立采样/更合适提议


### 来源边界

- - title Hastings Monte Carlo sampling methods (1970)
- url https://doi.org/10.1093/biomet/57.1.97
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 开放无限容量M/M/1


模型ID `sim-mm1`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


求稳态队长/等待并核仿真


### 输入和适用条件

- 系统总到达率λ≥0、每服务器服务率μ>0和单位
- 独立Poisson到达、指数服务、无限源/容量；稳态λ<μ


### 数学核心

- ρ=λ/μ
- L/W为系统人数/逗留时间

- p_n=(1-ρ)ρ^n；L=ρ/(1-ρ)；W=1/(μ-λ)
- Lq=ρ²/(1-ρ),Wq=ρ/(μ-λ)

λ≥μ时无该稳态；不可拿此式替有限源队列


### 求解和实现

- 验证到达/服务分布和稳定性
- 算解析指标
- DES独立重复对照与Little定律

Python - apis - 原创生灭/事件仿真
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - SimEvents M/M/1或原创
- dependencies - MATLAB基础功能
- SimEvents/Simulink
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline λ=1,μ=2时L=W=1,Lq=Wq=.5

- - check 解析
- method 手核ρ=.5
- expected 对应指标正确
- - check Little
- method L=λW与Lq=λWq
- expected 同一计数/时间定义

- λ≥μ
- 服务非指数
- 有限源误套开放率

- 暂态DES/更合适G队列


### 来源边界

- - title MathWorks M/M/1 Queuing System
- url https://uk.mathworks.com/help/simevents/ug/m-m-1-queuing-system.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope Poisson到达、指数服务、单服务器、无限容量、等待时间理论对照。
- verification_origin shared primary_sources.json#ps-queue


## Monte Carlo估计/场景仿真


模型ID `sim-monte-carlo`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


从声明的随机输入估计期望/概率/输出分布


### 输入和适用条件

- 分布/情景生成机制、统计量g、样本量/seed与预算
- i.i.d.及有限方差仅在对应SE公式中使用；情景不是实测


### 数学核心

- μ=E[g(X)]
- μhat=N^-1Σg(X_i)

- i.i.d.有限方差SE≈s/√N；概率用指示量均值
- 依赖样本须批均值/有效样本方法，不能沿用独立SE

无统一优化目标；定义目标分布与损失/事件


### 求解和实现

- 先核采样分布/单位
- 保存seed与输出样本
- 重复、收敛与解析特例对照

Python - apis - random/NumPy RNG+原创仿真
- dependencies - NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - rng/rand/randn+原创仿真
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 解析Bernoulli概率/积分小例

- - check 分布
- method 已知均值方差小例
- expected 估计与误差区间相容
- - check 随机性
- method 独立重复/样本量扫描
- expected 不只报告一次最好结果

- 分布假造
- 重尾方差无限
- seed筛选

- 区间/情景范围或确定性界


### 来源边界

- - title MathWorks SimEvents statistical analysis
- url https://www.mathworks.com/help/simevents/ug/statistics-for-data-analysis.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 区分暂态/稳态、样本量、独立重复次数与事件统计量。
- verification_origin shared primary_sources.json#ps-simstats
- - title SciPy binomtest
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope Bernoulli成功数检验和exact比例区间。
- verification_origin shared primary_sources.json#ps-binomial
