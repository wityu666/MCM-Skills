# games 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 有限矩阵博弈/Nash均衡


模型ID `game-nash`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


检查各方给定他方策略时是否仍有单方改进


### 输入和适用条件

- 行动集与A/B收益矩阵、信息/同时行动规则
- 收益和理性/信息规则是任务假设；总收益最大不等于Nash


### 数学核心

- x/y为混合策略，非负且各和1
- u1=x^TAy,u2=x^TBy

- x*是Ay*的最优回应，y*是x*^TB的最优回应
- 单方偏离收益不超过均衡收益

有限混合Nash存在性不意味着唯一或纯策略解


### 求解和实现

- 写收益而非把用户偏好隐藏到算法
- 找纯best responses或小支持枚举
- 核每方偏离/混合支持

Python - apis - Nashpy方向（未安装/未运行）
- 原创小支持枚举
- dependencies - Nashpy（方向，未安装/未运行）
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创best-response/support检查
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 2×2逐项最好回应

- - check 均衡
- method 匹配硬币A=[[1,-1],[-1,1]],B=-A
- expected 混合各.5，任何单方偏离不获利
- - check 目标
- method 协调/囚徒类对照
- expected 不以社会总收益最大代替Nash

- 收益无依据
- 多均衡未报告
- 非理性/不完全信息模型错位

- 最好回应/行为情景并降级均衡主张


### 来源边界

- - title Nashpy bimatrix games documentation
- url https://nashpy.readthedocs.io/en/stable/text-book/bimatrix-games.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Nash议价分配


模型ID `game-nash-bargaining`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在谈判失败基准上分配联合可行效用


### 输入和适用条件

- 可行效用集合U、disagreement d、协商权重（若加权）
- 可转移/可实现效用与正增益域；权重是偏好假设


### 数学核心

- u_i-d_i>0为谈判增益

- max Π_i(u_i-d_i)；等价max Σlog(u_i-d_i)
- 加权变体max Σw_i log(u_i-d_i)

保留U与u≥d；不可将任意收益乘积当议价


### 求解和实现

- 确定失败点/可行集
- 在正增益域求解
- 核对称与基准敏感性

Python - apis - scipy.optimize/CVXPY（凸域适配）
- dependencies - SciPy
- CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - fmincon
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 总剩余R与相同失败基准的2人对称问题，各得R/2

- - check 对称
- method 固定总增益小例
- expected 等权对称分配
- - check 基准
- method 扰动d/可行边界
- expected 解释分配变化

- 对数域不合法
- 失败基准臆造
- 非凸局部结果夸大

- 透明规则/可行分配范围


### 来源边界

- - title Nash The Bargaining Problem (1950)
- url https://doi.org/10.2307/1907266
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 演化博弈/复制动态


模型ID `game-replicator`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


考察策略份额在收益差异下如何演化


### 输入和适用条件

- 收益矩阵A、初始策略份额x、时间尺度与更新机制
- 大群体/复制规则是机制假设；稳态不自动等于Nash或真实演化


### 数学核心

- x_i≥0,Σx=1
- f_i=(Ax)_i,平均fbar=x^TAx

- dx_i/dt=x_i[(Ax)_i-x^TAx]

理论单纯形不变量；数值求解仍要查非负/质量守恒


### 求解和实现

- 明确收益与复制规则
- 解析边界/固定点
- ODE与步长/稳定性比较

Python - apis - scipy.integrate.solve_ivp
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - ode45
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 两策略份额的一维方程

- - check 不变量
- method 求和导数
- expected Σdx_i/dt=0，零份额面不产生负值
- - check 稳定
- method 线性化/扰动小例
- expected 固定点与稳定性分别报告

- 求解产生负份额
- 机制无依据
- 收敛图替均衡分析

- 静态收益/最好回应情景


### 来源边界

- - title SciPy solve_ivp
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 初值ODE、非刚性/刚性方法、容差、事件与终止状态。
- verification_origin shared primary_sources.json#ps-ode
- - title Taylor and Jonker Evolutionarily Stable Strategies
- url https://doi.org/10.1016/0025-5564(78)90077-9
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 合作博弈Shapley值


模型ID `game-shapley`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按所有联盟边际贡献分配总价值


### 输入和适用条件

- N个参与者、全部/可查询联盟worth v(S)，v(∅)=0及价值依据
- 可转移效用及worth定义；公平公理不等于现实因果贡献


### 数学核心

- φ_i为分配
- S不含i

- φ_i=Σ_(S⊆N且i∉S) |S|!(n-|S|-1)!/n!·[v(S∪{i})-v(S)]
- 等价于随机排列中i加入时的期望边际贡献

效率Σφ=v(N)；指数枚举成本需预算；SHAP特征应用归ML关联此核心


### 求解和实现

- 核worth和空集
- 小n精确联盟/排列
- 核效率/对称/虚设参与者

Python - apis - 原创联盟/排列枚举
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创枚举；MatTuGames仅在来源/依赖确认后
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 2人加性游戏v(S)=Σa_i

- - check 公理
- method 加性/对称/零贡献手例
- expected φ_i=a_i；sum守恒
- - check 语义
- method worth依据检查
- expected 不能由主观权重自动变因果贡献

- worth编造
- 遗漏空集/参与者映射
- n太大枚举

- 排列Monte Carlo+误差区间；或明确简单分配规则


### 来源边界

- - title Shapley, A Value for n-Person Games (1953)
- url https://doi.org/10.1515/9781400881970-018
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行
- - title Lundberg and Lee SHAP
- url https://arxiv.org/pdf/1705.07874
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 原论文物理p4–5：加性解释、local accuracy与特征依赖
- verification_origin shared primary_sources.json#ps-shap


## Stackelberg领导者–跟随者


模型ID `game-stackelberg`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


表达先行承诺与后行最好回应


### 输入和适用条件

- 行动顺序、领导/跟随收益与域、可观测承诺
- 最好回应可能多值；乐观/悲观择解必须明确


### 数学核心

- BR(x)=argmax_y uF(x,y)

- max_x uL(x,y),s.t.y∈BR(x)
- 内层KKT替换仅在内层相应前提成立时等价

不能把同时Nash或随意固定跟随反应当先后博弈


### 求解和实现

- 冻结顺序/择解
- 小例枚举内层响应
- 对照双层可行与偏离

Python - apis - 原创双层小例/优化接口
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创双层枚举/fmincon
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 有限2×2：逐领导行动计算跟随BR

- - check 响应
- method 内层完整枚举
- expected 跟随者确实不改善
- - check 歧义
- method 收益并列BR小例
- expected 报告乐观/悲观不同结果

- 多值响应被隐去
- 内层局部解
- KKT缺条件

- 有限行动枚举/情景范围


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行
- - title Stackelberg Market Structure and Equilibrium
- url https://doi.org/10.1007/978-3-642-12586-7
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 加权多数合作博弈/投票权力


模型ID `game-weighted-voting`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


区分票权与成为关键参与者的概率/次数


### 输入和适用条件

- 非负权w_i、quota q、参与者集；1≤q≤Σw的语义
- 投票联盟worth是0/1；排列与均匀联盟对应不同权力假设


### 数学核心

- v(S)=1(Σ_(i∈S)w_i≥q)
- 临界i：v(S∪i)-v(S)=1

- Shapley–Shubik为该简单游戏Shapley值
- Banzhaf原始数=Σ_(S⊆N且i∉S)[v(S∪i)-v(S)]；归一化按总数

权重比例不是权力指数；零临界总数不可除零


### 求解和实现

- 定义配额/联盟概率语义
- 小n枚举排列与联盟
- 分开核两类指数

Python - apis - 原创小n枚举
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创枚举，不运行Mathematica bridge/外发接口
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline w=(2,1,1),q=3

- - check 排列
- method 6排列关键者手核
- expected SS=(2/3,1/6,1/6)
- - check 联盟
- method 临界计数手核
- expected 归一Banzhaf=(3/5,1/5,1/5)；不同概念

- 把份额当权力
- quota退化
- 外部bridge冒充纯本地算法

- 透明计数/区间而不假公平证明


### 来源边界

- - title Shapley, A Value for n-Person Games (1953)
- url https://doi.org/10.1515/9781400881970-018
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 零和矩阵博弈/极小极大LP


模型ID `game-zero-sum`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


防最坏对手时选择混合策略


### 输入和适用条件

- 矩阵A；B=-A的零和依据
- 零和且对手可选混合；收益单位一致


### 数学核心

- x为行玩家
- v为保证收益（可负）

- max v,s.t.A^T x≥v1,x≥0,1^Tx=1
- 列玩家相应min上界；原/对偶值一致

v必须自由实数，不能承袭LP默认非负界


### 求解和实现

- 确认零和
- 构LP/对偶
- 核概率、偏离与对偶间隙

Python - apis - scipy.optimize.linprog（显式v free bounds）
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - linprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 2×2手算/纯策略保守值

- - check 值
- method 匹配硬币
- expected 值0，各方.5
- - check 负收益
- method 全部A=-1
- expected 值-1；v≥0会错误不可行

- 并非零和
- 默认界错
- 漏对偶核验

- 一般Nash/收益区间


### 来源边界

- - title SciPy linprog
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 标准LP、返回可行残差、最优/不可行/无界/数值终止。
- verification_origin shared primary_sources.json#ps-lp
- - title Nashpy bimatrix games documentation
- url https://nashpy.readthedocs.io/en/stable/text-book/bimatrix-games.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行
