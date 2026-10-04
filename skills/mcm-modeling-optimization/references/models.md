# optimization 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 人工蜂群优化


模型ID `opt-abc`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


雇佣/观察/侦察蜂的连续搜索


### 输入和适用条件

- f与Ω、食源数、试探/弃置规则、随机预算
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- 常见候选：v_ij=x_ij+φ_ij(x_ij-x_kj), φ∈[-1,1],k≠i
- 观察蜂按正适应度归一概率选食源；limit超限食源重新探索

适应度映射、边界规则、limit是算法变体参数，原工具箱未复现


### 求解和实现

- 选择可解释适应度映射
- 邻域比较并统计未改进计数
- 弃置/重新采样，核可行与多seed

Python - apis - 原创ABC（待指定变体）
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创MATLAB ABC
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 随机/网格搜索或标准NLP

- - check 变体
- method 核对原始公式和正适应度映射
- expected 不把最小化原值直接当选择概率
- - check 对照
- method 低维解析函数
- expected 与确定性baseline比较预算

- 变体未定
- 概率负值
- 频繁弃置丢最优记录

- 保留baseline；补核工具包变体后再采用


### 来源边界

- - title Karaboga ABC technical report
- url https://abc.erciyes.edu.tr/pub/tr06_2005.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 蚁群优化


模型ID `opt-aco`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


信息素引导的组合路径搜索


### 输入和适用条件

- 图/可行组件、启发值η、信息素τ、α/β/ρ与预算
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- p(i→j)=τ_ij^α η_ij^β / Σ_(可行k)τ_ik^α η_ik^β
- τ_ij←(1-ρ)τ_ij+Σ_ant Δτ_ij（如Q/L）

仅在明确可行邻域归一化；Q/L规则适用于相应最小化路径变体


### 求解和实现

- 定义状态/禁忌表
- 按概率构造可行路径
- 更新信息素，保留最佳并验路径

Python - apis - 原创ACO
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创MATLAB ACO
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline Dijkstra/最近邻或小路径枚举

- - check 概率
- method 逐节点重算p
- expected 非负且和1；无可选节点要退出
- - check 可行性
- method 路径逐边与访点计数
- expected 无重复/缺点或不许可边

- η=1/d遇零距离
- 概率分母零
- 信息素过早集中

- 精确最短路/可行贪心


### 来源边界

- - title Dorigo et al. Ant System
- url https://doi.org/10.1109/3477.484436
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Adam自适应梯度优化


模型ID `opt-adam`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


以动量与二阶矩缩放训练梯度步


### 输入和适用条件

- 梯度、学习率、β1/β2、ε、停止与训练切分
- 梯度有限；随机梯度噪声和尺度影响结果；Adam不保证任意非凸全局最优


### 数学核心

- m/v为一/二阶矩指数平均
- t为迭代

- m_t=β1 m_(t-1)+(1-β1)g_t；v_t=β2 v_(t-1)+(1-β2)g_t²
- m̂=m/(1-β1^t),v̂=v/(1-β2^t)
- θ←θ-α m̂/(sqrt(v̂)+ε)

若有硬约束需另外投影/参数化；减小损失不代替验证


### 求解和实现

- 记录超参数和seed
- 检查梯度/有限值
- 训练与验证分别监视

Python - apis - torch.optim.Adam
- 原创Adam（用于小例）
- dependencies - PyTorch
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - adamupdate（Deep Learning Toolbox方向）
- dependencies - MATLAB基础功能
- Deep Learning Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 普通梯度下降+解析凸二次对照

- - check 更新
- method 零梯度手核
- expected 参数保持不变
- - check 偏差修正
- method 首步手算
- expected m̂=g,v̂=g²

- ε/学习率不适合单位
- 梯度爆炸
- 训练过拟合

- 缩放+更简单优化器/小学习率


### 来源边界

- - title Kingma and Ba Adam
- url https://arxiv.org/abs/1412.6980
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 人工鱼群搜索与明确教学变体

模型ID `opt-afsa`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`

理解觅食、群聚、追尾和随机移动，并为连续盒域声明完整可实现搜索规则。

### 输入和适用条件

- 可评估目标f、连续盒域Ω、群规模M、Visual、Step、尝试次数T、拥挤因子δ、预算与随机种子。
- 声明最大化正食物浓度Y=φ(f)>0的映射φ；原最小化/最大化目标仍独立报告。
- 本卡给最大化食物浓度的自洽教学变体，行为基础来自primary论文；不是原商业工具箱或任一作者实验的复现。
- 随机搜索无通用全局最优保证；食物浓度映射影响拥挤比，必须冻结并做敏感性。
- 盒域坐标需按尺度归一；非凸/整数域不能只靠连续投影保持硬约束。

### 数学核心

**记号**

- x_i∈Ω；N_i={j≠i:||x_j-x_i||<Visual}，n_i=|N_i|；U∼Uniform(0,1)。
- 群心x_c=(1/n_i)Σ_N_i x_j；最优邻鱼x_b=argmax_N_i Y_j；δ>0。

**定义与更新**

- toward(x,y)=Π_Ω[x+Step*U*(y-x)/||y-x||]，y=x时保持x；Π_Ω仅指逐坐标盒域截断。
- 觅食：在Ω与Visual球交集中随机采至多T个y，发现Y(y)>Y(x)则生成toward；均失败时随机移动。采样分布要声明，不能将正向标量Rand当均匀球采样。
- 群聚/追尾：n_i>0且Y(target)>Y_i、Y(target)/n_i>δY_i时向x_c或x_b移动，否则走觅食。空邻域/零方向不除以0。
- 教学选择：产生各行为候选，评估原目标和可行性，选其中最大Y的候选替换当前鱼；同步由前一代群定义邻居，保留独立的历代最优可行公告牌。随机移动可劣于当前鱼，但不能丢失公告牌。
- 随机移动教学规则：先取单位方向v（零向量重采）和r∼Uniform(0,Step)，再Π_Ω(x+r v)；此分布是明确工程选择，不冒称任何源码的唯一AFSA公式。

**目标与边界**

- 优化原目标f于Ω；Y仅为声明搜索适应度。预算包括所有试探/候选评估；公告牌是best found，不标成已证明最优。

### 求解和实现

- 先建立可行baseline，归一坐标，冻结Y映射、参数、同步更新、预算和随机源。
- 初始化可行鱼群和最优公告牌；从前一代计算邻居、群心、最优邻鱼。
- 逐鱼生成行为候选、重新查硬约束，择最大Y候选；更新公告牌。
- 按预算/停滞停止，多随机种子报告best found分布并与同预算标准算法比较。

**PYTHON**

- apis: numpy.random.Generator
- apis: 原创邻域/行为与盒域检查；本包未提供已运行AFSA函数
- dependencies: Python标准库；大数组可另选NumPy
- implementation_notes: 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

**MATLAB**

- apis: rng/rand/randn与原创行为循环；未知工具箱/MEX不作为依赖
- dependencies: MATLAB基础功能
- implementation_notes: 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。

### 验证和回退

Baseline：低维网格或确定性NLP

- 方向和拥挤门：正Y的小鱼群手算n、群心、邻best；核对觅食更大Y、空邻域、重合鱼、δ门。 验收：最大化方向一致，空邻域/零距离不生成NaN。
- 可行性和记忆：独立核验每候选边界/硬约束；记录公告牌和真实评估次数。 验收：公告牌最佳原目标不退化，硬约束不被适应度惩罚替代。
- 搜索价值：低维已知函数与网格/确定性NLP、相同评估预算多种子对照；改变Y映射/尺度/参数。 验收：报告找到的解和敏感性，不把一次最好随机值宣称全局最优。

- 失败边界：原文/源码最大化最小化符号混用；fitness平移改变拥挤比；空邻域和重合鱼除零；同步/异步未声明；盒域截断误用于整数/非凸约束。

- 回退：低维网格、标准确定性NLP或已审清优化算法；必要时只采用明确的行为思想并标注变体。

### 来源边界

- 原资料鱼群算法工具箱（仅命名索引）：历史来源标签；Only a historical material label was known; no verified public source or implementation is claimed.
- [Zhang and Ma, Adaptive parameter-tuning stochastic resonance based on SVD... (2019), section 2.3](https://link.springer.com/article/10.1186/s13634-019-0617-5)；Targeted read of AFSA state/Visual/Step and four behavior definitions. The page prey inequality conflicts with its maximization swarm/follow convention; this guide explicitly selects a consistent maximization teaching convention instead of claiming exact reproduction.
- [Guo et al., 改进人工鱼群的移动机器人避障寻优算法 (2021)](https://html.rhhz.net/yykj/html/202101007.htm)；Targeted section 2.1 direction steps and best-behavior/bulletin update. Adaptations of boundaries, sampling and synchrony in this guide are declared implementation choices; original experiment not reproduced.

本卡补全日期：2026-10-04。新等级仅证明限定数学指南已核验；Python／MATLAB 实现及原场景未运行。

## 模糊规划


模型ID `opt-fuzzy`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在隶属度描述下折中模糊目标/约束


### 输入和适用条件

- 每个目标/约束的隶属函数μ_j(x)、阈值/偏好依据
- 隶属度不是概率；形状与聚合是明确假设


### 数学核心

- μ_j∈[0,1]
- λ为最低满意度

- max λ, s.t. μ_j(x)≥λ,0≤λ≤1
- 也可按明确规则聚合满意度

保留物理硬约束；不要把模糊化当取消硬约束


### 求解和实现

- 定义可解释μ函数
- 构造max-min或选择的聚合
- 阈值/形状敏感性和硬约束核验

Python - apis - 原创μ函数+scipy.optimize/CVXPY
- dependencies - SciPy
- CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创μ函数+fmincon/linprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 硬阈值可行性或等权满意度

- - check 语义
- method 核对概率与隶属解释
- expected 不写“μ=0.9代表90%概率”
- - check 敏感性
- method 改变阈值/斜率
- expected 方案变化被记录

- μ没有依据
- 误当随机规划
- 对不可违反规则模糊化

- 硬约束模型+情景说明


### 来源边界

- - title Zimmermann fuzzy programming (1978)
- url https://doi.org/10.1016/0165-0114(78)90031-3
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 遗传算法


模型ID `opt-ga`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


种群编码、选择、交叉、变异


### 输入和适用条件

- 候选x/编码、适应度、约束与预算
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- 子代crossover(x_i,x_j)，再按变异核产生x′；按明确适应度选下一代

基因与数组应复制；不自动保证可行或全局最优


### 求解和实现

- 编码真实变量域
- 独立复制父代并做交叉/变异
- 修复/拒绝不可行子代，记录种群多seed

Python - apis - scipy.optimize.differential_evolution（不同进化方法的baseline）
- 原创GA
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - ga
- dependencies - MATLAB基础功能
- Global Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 小整数枚举/局部确定性搜索

- - check 正确性
- method 用小例枚举并检验编码解码
- expected 目标、容量/逻辑正确
- - check 随机性
- method 多seed分布
- expected 不只给最好seed

- 别名共享破坏父代
- 种群不截断
- 无实际基因变异

- 枚举/MILP；或有状态的可行局部搜索


### 来源边界

- - title MathWorks gamultiobj
- url https://www.mathworks.com/help/gads/gamultiobj.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 约束多目标遗传搜索、Pareto返回与exitflag。
- verification_origin shared primary_sources.json#ps-multiobj


## 遗传规划/符号进化


模型ID `opt-gp`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


搜索符号表达式或程序结构


### 输入和适用条件

- 允许的语法树节点/函数、训练数据、损失和复杂度限制
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- min_T Σ_i ℓ(T(x_i),y_i)+λ·complexity(T)
- 交叉/变异作用于合法子树，不是固定长度数值向量

GP不是Gaussian Process；保护除零等操作，训练/验证分离


### 求解和实现

- 定义类型安全文法
- 树交叉/变异与深度预算
- 检查域、复杂度与样本外损失

Python - apis - 原创受限语法树搜索
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创MATLAB树结构搜索
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 低阶多项式/线性模型

- - check 结构
- method 手核树合法性与保护操作
- expected 不执行任意生成Python源码
- - check 泛化
- method 独立测试与复杂度曲线
- expected 不凭训练拟合选择无限大树

- 程序膨胀
- 训练过拟合
- eval任意字符串

- 固定基函数/更简单模型


### 来源边界

- - title Koza Genetic Programming
- url https://mitpress.mit.edu/9780262111706/genetic-programming/
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 目标/硬约束独立复核与有限盒枚举


模型ID `opt-independent-check`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


从候选决策变量重新计算模型定义，不依赖求解器自报值


### 输入和适用条件

- c,x,A/b,E/d,明确边界/整数索引与容差；枚举另需有限整数盒
- 验证公式独立于生产求解器；枚举只覆盖声明盒


### 数学核心

- 违反量max(g,0)
- 整数残差|x-round(x)|

- f=c^Tx；线性不等式/等式/界逐项计算
- 有限整数盒∏[l_i,u_i]逐点比较所有可行目标

未提供的非负约束不私自添加；整数性只用绝对容差


### 求解和实现

- 核查维度/有限数
- 独立重算每条约束与目标
- 预算允许时完整枚举并报告范围

Python - apis - assets/optimization_reference.py:check_linear_candidate
- assets/optimization_reference.py:enumerate_integer_box
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创标量/矩阵检查与小例ndgrid枚举
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 手算2变量目标/约束

- - check 枚举最优
- method c=(-4,-3),2x1+x2≤4,x∈{0,…,3}²
- expected x=(1,2),目标-10
- - check 约束域
- method 负变量无显式界、非法整数测试
- expected 不虚增非负约束，不相对放宽整数性

- 缺输入约束导致漏验
- 忽略舍入/单位
- 枚举超预算

- 只做可行/目标复核，最优性主张降级


### 来源边界

- - title SciPy linprog
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 标准LP、返回可行残差、最优/不可行/无界/数值终止。
- verification_origin shared primary_sources.json#ps-lp
- - title SciPy milp
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 线性目标/范围约束/整数变量，status、gap、dual bound、time limit。
- verification_origin shared primary_sources.json#ps-milp


## Lagrange对偶与KKT条件


模型ID `opt-kkt`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


分析约束解的必要/充分条件和影子价格


### 输入和适用条件

- 可微f/g/h，候选x与约束资格信息
- 必要性需约束资格；凸性+适当条件才给充分性


### 数学核心

- λ_i≥0为不等式乘子
- ν_j为等式乘子

- L=f+Σλ_i g_i+Σν_j h_j
- ∇_x L=0；g≤0,h=0,λ≥0；λ_i g_i=0

区分原始可行、对偶可行、驻点和互补松弛


### 求解和实现

- 明确不等式符号
- 求/核乘子
- 同时检验四类条件并判断凸性

Python - apis - 原创残差检查
- CVXPY dual_value（读取方向）
- dependencies - CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 求解器lambda输出+原创核算
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 一变量min x²,s.t.x≥1，最优x=1,乘子2（g=1-x）

- - check 符号
- method 手核上述约束
- expected λ=2且∇L=0
- - check 充分性
- method 检查凸性/资格
- expected 仅KKT残差小不能断言非凸全局最优

- 不等式符号混乱
- 资格失效
- 局部/充分混同

- 直接可行性与目标比较；不使用未满足前提的证书


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 梯度/拟Newton/SQP与无导数局部优化


模型ID `opt-local-methods`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按导数、域与约束选择局部算法，而非把minimize当模型


### 输入和适用条件

- 可求值f，必要导数/约束/界，初值与停止标准
- 平滑性/局部曲率等前提匹配算法；Brent标量区间最小值与求根不同


### 数学核心

- g=∇f
- H或逆H近似曲率
- s=x_(k+1)-x_k,y=g_(k+1)-g_k

- 梯度方向-∇f；拟Newton求曲率方向并线搜索
- BFGS维护满足割线条件Hs=y的曲率近似；L-BFGS保存有限(s,y)
- SQP解局部二次子问题；Nelder–Mead以单纯形反射/扩张/收缩；Brent结合括区间与插值

边界/非线性约束由算法正确支持；不是所有method都处理相同约束


### 求解和实现

- 匹配算法假设与输入
- 检查数值梯度或Jacobian
- 对照解析/网格/多起点

Python - apis - scipy.optimize.minimize
- scipy.optimize.fminbound
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - fminunc
- fmincon
- fminsearch
- fminbnd
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 解析二次函数或一维网格

- - check 导数
- method 有限差分/解析导数对照
- expected 方向和尺度正确
- - check 局部性
- method 不同初值对照
- expected 分歧按非凸局部结果报告

- Newton曲率不正定
- Brent假设不符
- 小步长假收敛

- 缩放/保护线搜索/更简单可行baseline


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 线性规划


模型ID `opt-lp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在资源与线性规则下最小化费用


### 输入和适用条件

- c∈R^n，A/b，等式E/d，逐变量上下界及单位
- 目标与约束为线性；系数对应相同时间/单位；检查可行域是否有界


### 数学核心

- x∈R^n为决策
- c^Tx为目标
- A x≤b，E x=d，l≤x≤u

- min c^T x；可行解是全部显式约束的交集

上述线性约束，不自动增加x≥0


### 求解和实现

- 核对方向/单位并显式给边界
- 求LP并保存status、残差/对偶
- 从x独立重算目标和全部约束

Python - apis - scipy.optimize.linprog(method="highs")
- assets/optimization_reference.py:check_linear_candidate
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - linprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 二维角点/可行点手核；零决策仅在确实可行时作为baseline

- - check 可行性
- method 用独立矩阵/标量重算残差
- expected 所有硬约束在预设容差内
- - check 目标
- method 手算小例c=[3,2],x=[1,1]
- expected 目标5；无界变量需明确free bounds

- 不可行/无界
- 数量级导致病态
- 把“有x”当最优

- 定位冲突约束；保留可行baseline或报告无界，不能捏造解


### 来源边界

- - title SciPy linprog
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 标准LP、返回可行残差、最优/不可行/无界/数值终止。
- verification_origin shared primary_sources.json#ps-lp


## 整数/混合整数规划


模型ID `opt-milp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


处理不可分割数量与逻辑选择


### 输入和适用条件

- LP数据与整数索引/二元变量、有限大M依据
- 整数性有实际意义；大M有紧界而非随意极大常数


### 数学核心

- x_I∈Z，二元x∈{0,1}
- 其余变量可连续

- min c^Tx；x_I为整数

线性约束+变量域


### 求解和实现

- 写出逻辑的线性化与界
- 求解并保存gap/bound/status
- 独立检查整数性和约束，枚举小实例

Python - apis - scipy.optimize.milp
- PuLP/CVXPY（选实际可用solver）
- assets/optimization_reference.py:enumerate_integer_box
- dependencies - SciPy
- CVXPY
- PuLP
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - intlinprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 有限小整数盒完整枚举或问题特定贪心可行解

- - check 最优性主张
- method 有限盒穷举
- expected 与完整枚举最优一致；大问题只按gap报告
- - check 整数性
- method 距最近整数的绝对差
- expected 按预声明整数容差，不放大为相对容差

- LP解四舍五入不可行
- M过大
- 超时且gap未闭合

- 可行启发式+界；不能说已证明最优


### 来源边界

- - title SciPy milp
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 线性目标/范围约束/整数变量，status、gap、dual bound、time limit。
- verification_origin shared primary_sources.json#ps-milp


## 多目标/Pareto决策


模型ID `opt-multiobjective`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


表达相互冲突的目标与可选方案


### 输入和适用条件

- 目标向量F(x)、可行域、方向、偏好/尺度
- 目标可比口径；权重是偏好而非观测事实


### 数学核心

- F=(f_1,…,f_m)
- 支配要求逐项不劣且至少一项严格优

- min F(x)；Pareto解不能被另一可行解支配
- 加权和min Σw_j f_j；ε约束固定其它目标界

可行性仍满足全部硬约束；加权和可能漏非凸前沿


### 求解和实现

- 统一方向/尺度
- 先生成确定性对照再扫描权重或ε
- 筛支配、保存原始目标和偏好敏感性

Python - apis - scipy.optimize/LP重复求解
- pymoo方向（未安装不宣称可用）
- dependencies - SciPy
- pymoo（方向，未运行）
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - gamultiobj
- 多次linprog/fmincon
- dependencies - MATLAB基础功能
- Optimization Toolbox
- Global Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 小例枚举整个目标表，找全部非支配点

- - check 前沿
- method 逐对支配检查
- expected 无被当前可行集支配的报告点
- - check 偏好
- method 权重/ε扰动
- expected 排序变化需报告；不是唯一客观最优

- 混用max/min方向
- 只看归一化值
- 启发式前沿当全局前沿

- 枚举/ε网格+明确缺失范围


### 来源边界

- - title MathWorks gamultiobj
- url https://www.mathworks.com/help/gads/gamultiobj.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 约束多目标遗传搜索、Pareto返回与exitflag。
- verification_origin shared primary_sources.json#ps-multiobj


## 约束非线性规划


模型ID `opt-nlp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


优化平滑/非线性目标与约束


### 输入和适用条件

- f、g_i≤0、h_j=0、界、可行初值及导数方向
- 导数与模型域一致；局部方法不保证全局


### 数学核心

- x为决策
- g/h为约束函数

- min f(x), g(x)≤0, h(x)=0

域/界不可因罚函数而丢失


### 求解和实现

- 验证域与初值
- 缩放并选导数/约束算法
- 多起点或解析小例对照、重算可行性

Python - apis - scipy.optimize.minimize(method="SLSQP"/"trust-constr")
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - fmincon
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 可行初值与低维网格对照

- - check 局部最优
- method 梯度/KKT与多起点
- expected 残差达预设标准；不把局部一致写全局证明
- - check 边界
- method 独立计算全部g/h
- expected 可行性必须满足原约束

- 域外函数NaN
- 初值不可行
- 只有fun没有状态

- 调整缩放/可行点；保留较简单可行模型


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## NSGA-II


模型ID `opt-nsga2`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在多目标种群中维持非支配与多样性


### 输入和适用条件

- F(x)、约束、编码、种群/预算
- 目标方向/尺度一致；小前沿不保证全局


### 数学核心

- rank为非支配层
- crowding distance为邻点间归一化目标间距

- 按非支配rank优先，再按拥挤距离选择；父子合并后截回固定种群数

可行性支配/约束处理须单独声明


### 求解和实现

- 先可行baseline
- 非支配排序与拥挤度
- 精英截断、重复seed并查支配

Python - apis - pymoo.algorithms.moo.nsga2.NSGA2（方向）
- dependencies - pymoo（方向，未运行）
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - gamultiobj（相关实现，不宣称同一算法逐行一致）
- dependencies - MATLAB基础功能
- Global Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 二维小可行域完全枚举前沿

- - check 前沿
- method 枚举非支配点
- expected 误差/覆盖明确
- - check 种群
- method 每代计数与越界检查
- expected 不会无意指数增长

- 尺度扭曲拥挤距离
- 重复解淹没前沿
- 漏检查硬约束

- ε约束/权重网格


### 来源边界

- - title MathWorks gamultiobj
- url https://www.mathworks.com/help/gads/gamultiobj.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 约束多目标遗传搜索、Pareto返回与exitflag。
- verification_origin shared primary_sources.json#ps-multiobj
- - title Deb et al. NSGA-II
- url https://doi.org/10.1109/4235.996017
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 粒子群优化


模型ID `opt-pso`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


个体/群体历史最优引导的连续群体搜索


### 输入和适用条件

- 变量域、f、种群/系数/seed预算
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- v_i←ωv_i+c1 r1⊙(pbest_i-x_i)+c2 r2⊙(gbest-x_i)
- x_i←投影_Ω(x_i+v_i)

这是含惯性常见变体；约束修复、速度界与系数必须定义


### 求解和实现

- 初始化可行粒子
- 更新速度/位置并独立保存最好态
- 多seed与低维网格对照

Python - apis - 原创向量PSO
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - particleswarm
- dependencies - MATLAB基础功能
- Global Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 均匀网格/可行局部搜索

- - check 状态
- method 检查pbest/gbest独立副本
- expected 最优记录不被原地数组更新污染
- - check 结果
- method 解析凸二次小例
- expected 接近已知解而非只说收敛图好看

- 群体坍缩
- 边界粘连
- 差单位变量同尺度速度

- 缩放+确定性baseline


### 来源边界

- - title Kennedy and Eberhart Particle Swarm Optimization
- url https://doi.org/10.1109/ICNN.1995.488968
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 二次规划


模型ID `opt-qp`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


线性约束下处理二次成本或方差


### 输入和适用条件

- 对称Q、c、线性约束和边界
- 凸版本要求Q半正定；非凸版本仅局部或需全局策略


### 数学核心

- Q∈R^(n×n)
- x∈R^n

- min 1/2 x^T Qx+c^Tx

线性可行域；对称化Q不代表修正错误模型


### 求解和实现

- 检查Q对称与谱
- 选择凸QP或明确非凸路线
- 重算目标/残差与小例最优

Python - apis - CVXPY:quad_form
- scipy.optimize.minimize（一般路线）
- dependencies - SciPy
- CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - quadprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline Q=2I,c=(-2,-4)的无约束解x=(1,2)

- - check 解析解
- method 配方/一阶条件
- expected 小例x=(1,2)
- - check 凸性
- method 特征值与模型假设
- expected 若有负特征值不得宣称凸全局最优

- 非PSD却用凸解释
- 错误1/2因子
- 协方差病态

- 正则化需记录；或切非凸NLP并报告局部性


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 鲁棒优化


模型ID `opt-robust`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在指定不确定集合内保守地保持可行


### 输入和适用条件

- f/g、集合U的范围/相关结构及依据
- U覆盖意图明确；鲁棒不是概率可靠度声明


### 数学核心

- u∈U为不确定量

- min_x max_(u∈U) f(x,u), s.t. g(x,u)≤0 ∀u∈U

线性盒不确定时用端点/对偶推导；一般集合不可盲枚举少数点代替∀


### 求解和实现

- 界定U与保守度
- 构造可证明等价对偶或最坏子问题
- 独立搜索/手核最坏点

Python - apis - CVXPY/SciPy+原创鲁棒对应
- dependencies - SciPy
- CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - linprog/quadprog+原创对应
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 盒集线性小例枚举所有角点

- - check 最坏情景
- method 角点/对偶上界
- expected 报告解在声明U内可行
- - check 集合敏感性
- method 扩缩U
- expected 说明保守性代价

- U随意
- 非线性极值不在角点
- 把抽样可行当∀证明

- 情景模型并降级为经验覆盖


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 模拟退火


模型ID `opt-sa`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


带温度的随机邻域接受


### 输入和适用条件

- 能量E(x)、可行邻域、温度表、预算
- 随机搜索必须与预算/可行baseline比较；无通用全局最优保证


### 数学核心

- x为可行候选；f为原目标
- 随机系数/迭代不带真实数据含义

- 接受改进；ΔE>0时以exp(-ΔE/T)接受；T>0按声明计划下降

有限运行是启发式，不引用无限慢降温的结论作当前证明


### 求解和实现

- 构造可行邻域
- 计算真实ΔE并接受/拒绝
- 保留历史最优可行解，结束时独立核验

Python - apis - scipy.optimize.dual_annealing（实现方向）
- 原创SA
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - simulannealbnd
- dependencies - MATLAB基础功能
- Global Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 可行局部爬山/小例枚举

- - check 温度
- method 手算ΔE=1,T=1
- expected 接受概率e^-1；T→0不接受劣化
- - check 解
- method 独立核目标约束
- expected 历史最优不被最后劣化态覆盖

- 温度/能量量纲不匹配
- 邻域不可达
- 只保存最后态

- 确定性局部搜索并报告局部性


### 来源边界

- - title Kirkpatrick et al. Optimization by Simulated Annealing
- url https://doi.org/10.1126/science.220.4598.671
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 随机规划/情景优化


模型ID `opt-stochastic`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


在概率性输入与补救决策下选择方案


### 输入和适用条件

- 随机量分布/独立情景及权重；先验决策/补救变量
- 情景代表部署分布；不能用预测均值代替全部随机量


### 数学核心

- ξ为随机输入
- p_s≥0,Σp_s=1
- x为事前、y_s为情景补救

- min c^Tx+E[Q(x,ξ)]≈c^Tx+Σp_s q_s^Ty_s
- 机会约束P(g(x,ξ)≤0)≥1-α

非预见性：同一事前x不能因已知未来ξ_s改变


### 求解和实现

- 区分决策时间与情景
- 求SAA并保存样本/seed
- 独立样本验证成本和违规概率

Python - apis - 原创情景LP/MILP
- SciPy/CVXPY
- dependencies - SciPy
- CVXPY
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创情景矩阵+linprog/intlinprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 确定性保守情景+简单补救规则

- - check 非预见性
- method 检查共享变量
- expected 事前变量跨情景一致
- - check 机会约束
- method 独立样本与二项区间
- expected 经验频率及不确定性；不由训练场景自证

- 未来信息泄漏
- 概率权重假造
- 尾部场景不足

- 保守鲁棒界或报告分布敏感性


### 来源边界

- - title SciPy binomtest
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope Bernoulli成功数检验和exact比例区间。
- verification_origin shared primary_sources.json#ps-binomial
- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行
