# discrete 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## Bellman–Ford负权路径


模型ID `disc-bellman-ford`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


处理负边并检测源可达负环


### 输入和适用条件

- 有向边及权重、源、节点数
- 最短路径有限需源可达子图无负环


### 数学核心

- d源=0，其他∞

- 重复|V|-1轮逐边松弛；再可松弛表示可达负环

不可达源不参与∞松弛


### 求解和实现

- 初始化
- 松弛至无变化或|V|-1轮
- 检测额外一轮/重建路径

Python - apis - networkx.single_source_bellman_ford
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - shortestpath(Method="mixed")或原创
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 无负环小图手算

- - check 负边
- method 边1, -2与直达0
- expected 经两边代价-1
- - check 负环
- method 构造可达环总成本<0
- expected 显式失败，不伪报有限最短

- 不检环
- 溢出
- 大图O(VE)预算超限

- Dijkstra限非负；或只报告可达性


### 来源边界

- - title SciPy shortest_path
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 有向/无向图与Dijkstra/Bellman-Ford等路径接口及权重边界。
- verification_origin shared primary_sources.json#ps-graph


## 社区检测/模块度优化


模型ID `disc-community`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


寻找连接密集的社区结构


### 输入和适用条件

- 无向非负边权图、分辨率/目标定义
- 以下标准Q适用于声明的无向加权null model；不自动适用负权/有向


### 数学核心

- A_ij为权重
- k_i=Σ_j A_ij
- 2m=Σ_i k_i

- Q=(1/(2m))Σ_ij[A_ij-γ k_i k_j/(2m)]·1(c_i=c_j)

选择社区划分提高Q；启发式局部最优不保证唯一


### 求解和实现

- 检查图/null model与孤点
- 运行具体社区算法
- 跨seed/γ比较划分与Q

Python - apis - networkx.community.greedy_modularity_communities/louvain_communities
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创Q与社区搜索；外部CDTB仅索引
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 按连通组件与小图所有划分比较

- - check 小图
- method 枚举划分/重算Q
- expected Q与定义一致
- - check 稳定性
- method γ/seed扰动
- expected 报告分辨率依赖而非唯一真社区

- m=0
- 负权套公式
- 小社区分辨率限制

- 组件/领域规则分组并说明非优化


### 来源边界

- - title Newman and Girvan Community Structure
- url https://doi.org/10.1103/PhysRevE.69.026113
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Dijkstra单源最短路


模型ID `disc-dijkstra`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


非负加权图中找源点到可达节点的最小代价


### 输入和适用条件

- 有向/无向、节点集、显式边/非负权重与源点
- 所有边非负且有限；零权是合法边；不存在边不等于权重0


### 数学核心

- d(v)为目前上界
- pred(v)为合法路径前驱

- 松弛d(v)←min(d(v),d(u)+w_uv)；每次取最小未定d

负边必须换方法；不可达d=∞且无路径


### 求解和实现

- 用边表/邻接映射保存零边
- 优先队列松弛并跳过过期记录
- 重建路径并逐边重算成本

Python - apis - assets/discrete_reference.py:dijkstra
- networkx.single_source_dijkstra
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - graph/digraph+shortestpath（边表保零权）
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 小图所有简单路径枚举/Bellman–Ford对照

- - check 零边/不可达
- method a→b=0,b→c=2,a→c=9+孤点
- expected d(c)=2；孤点无路径
- - check 负边
- method 含未可达负边输入
- expected 参考实现拒绝，不删成缺边

- 0转成Inf删边
- 不可达伪路径
- 浮点累计溢出

- Bellman–Ford处理负边；保留孤点与缺边语义


### 来源边界

- - title SciPy shortest_path
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 有向/无向图与Dijkstra/Bellman-Ford等路径接口及权重边界。
- verification_origin shared primary_sources.json#ps-graph
- - title NetworkX single_source_dijkstra
- url https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.single_source_dijkstra.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读非负权/不可达/权重语义；未调用该库实现。


## 有限阶段动态规划


模型ID `disc-dp`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


有状态充分性与阶段依赖的决策


### 输入和适用条件

- 状态、可行动作、转移、阶段代价、终端值和有限时域
- 当前状态含未来所需历史；优化子结构成立


### 数学核心

- V_t(s)为t时状态s的后续最优值

- V_t(s)=min_a[c_t(s,a)+V_(t+1)(T_t(s,a))]

动作/状态的可行域属于递推本身


### 求解和实现

- 定义充分状态/终端
- 逆序递推并保存策略
- 用小树完整展开核验

Python - apis - 原创字典/数组DP
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创数组/容器DP
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 穷举短时域动作序列

- - check 最优子结构
- method 完整决策树比较
- expected 价值/策略与树枚举一致
- - check 状态压缩
- method 比较未压缩小例
- expected 不丢失影响未来的信息

- 状态爆炸
- 状态漏历史
- 错把贪心当DP

- 缩小状态/时域或MILP并说明近似


### 来源边界

- - title Boyd and Vandenberghe, Convex Optimization
- url https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 容量流/最大流


模型ID `disc-flow`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


给定源汇与容量最大化可运输量


### 输入和适用条件

- 有向边容量c_e≥0、源汇与单位
- 守恒、容量真实；源汇不混同中间节点


### 数学核心

- f_e≥0
- 流值F为源净流出

- max F；0≤f_e≤c_e；中间点流入=流出

残量网络含反向边以撤回先前流


### 求解和实现

- 构图与单位一致
- 求最大流
- 独立核容量/守恒与割容量

Python - apis - networkx.maximum_flow
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - digraph+maxflow
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 小网络所有源汇割枚举

- - check 最大流最小割
- method 比较流与独立割
- expected 小例流值=最小割容量
- - check 守恒
- method 逐节点求和
- expected 各中间点净流0

- 缺反向残量
- 双向容量混算
- 无源汇定义

- 网络LP或可行流下界


### 来源边界

- - title NetworkX maximum_flow
- url https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.maximum_flow.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## Floyd–Warshall全对最短路


模型ID `disc-floyd`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


中小图求所有点对路径长度


### 输入和适用条件

- 完整节点/边、∞缺边、0对角和方向
- 允许负边但不能有导致最短路无定义的负环


### 数学核心

- D^(k)_ij仅允许前k节点为内部节点

- D^(k)_ij=min(D^(k-1)_ij,D^(k-1)_ik+D^(k-1)_kj)

结束后负对角提示负环；∞计算需保护


### 求解和实现

- 初始化缺边/零边
- 三重递推并保存前驱
- 与枚举/逐源方法核验

Python - apis - networkx.floyd_warshall
- scipy.sparse.csgraph.shortest_path(method="FW")
- dependencies - SciPy
- NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - distances或原创Floyd
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 三节点手算

- - check 路径
- method 三点0→1=2,1→2=3,0→2=8
- expected d02=5
- - check 负环
- method 额外负环小例
- expected 报告无有限最短路而非普通距离

- 更新次序错
- 把有向强行对称
- 无负环检查

- 逐源Bellman–Ford/稀疏最短路


### 来源边界

- - title SciPy shortest_path
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 有向/无向图与Dijkstra/Bellman-Ford等路径接口及权重边界。
- verification_origin shared primary_sources.json#ps-graph


## 组合/多层图建模


模型ID `disc-graph-composition`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


合成网络或状态空间并保持对象身份


### 输入和适用条件

- 各图节点键、边属性、组合语义与跨层边
- 并合/不交并/乘积语义不同；同名节点是否合并必须规定


### 数学核心

- V_1,V_2为节点集

- 并合G1∪G2合并同身份节点；不交并保留层标签
- 笛卡尔积V=V1×V2：一次仅在一个坐标沿原边移动

成本/容量不因节点标签碰撞自动相加


### 求解和实现

- 选择组合算子并映射身份
- 构建边与属性
- 检查节点数/路径是否保留原约束

Python - apis - networkx.compose/disjoint_union/cartesian_product
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 带层标签的graph/digraph构图
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 两个2节点图手绘积图

- - check 结构
- method 手绘并合/积图
- expected 积节点数4；身份不误并
- - check 应用
- method 原状态合法动作核对
- expected 组合图路径不允许非法跨层跃迁

- 同名节点误合
- 乘积状态爆炸
- 混淆容量/距离语义

- 保留分图+显式耦合约束


### 来源边界

- - title NetworkX graph operators
- url https://networkx.org/documentation/stable/reference/algorithms/operators.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 0-1背包


模型ID `disc-knapsack`　类别 `model`　知识等级 `REFERENCE_IMPL_TESTED`


从不可分割项目中选择价值最高且总重量不超容量的集合


### 输入和适用条件

- 有限v_i、非负整数w_i、整数容量C
- 每项目至多一次；容量离散尺度真实；零重项目允许一次


### 数学核心

- z_i∈{0,1}
- D(i,c)为前i项容量c最优值

- max Σv_i z_i,s.t.Σw_i z_i≤C
- D(i,c)=max(D(i-1,c),D(i-1,c-w_i)+v_i)（可装时）

回溯从i=n到1；同值优先不选；不可从错误行判断第一项


### 求解和实现

- 校验整数容量与尺寸
- 从第0行零基底递推
- 回溯并独立重算选择价值/重量

Python - apis - assets/discrete_reference.py:knapsack01
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创二维DP或intlinprog
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline ≤20项目枚举全部子集

- - check 反例
- method v=(100,1),w=(3,1),C=2
- expected 仅第二项，价值1、重量1
- - check 独立最优
- method 不同的子集枚举
- expected 价值与枚举一致，集合无重复且容量合法

- 把0-1写成完全背包
- 负/非整数重量
- 回溯与DP表不一致

- MILP或稀疏DP；记录规模/精度信息损失


### 来源边界

- - title SciPy milp
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 线性目标/范围约束/整数变量，status、gap、dual bound、time limit。
- verification_origin shared primary_sources.json#ps-milp


## 匹配与二部指派


模型ID `disc-matching`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


不重复使用对象的配对/指派优化


### 输入和适用条件

- 可配边与收益/成本、二部性/一对一规则
- 一般图匹配与二部指派不同；缺边不能默作0成本


### 数学核心

- z_e∈{0,1}
- 每顶点最多一条被选边

- max Σw_e z_e,s.t.Σ_(e邻接v)z_e≤1；完整指派为行列等式

成本型需定义惩罚/不可配边和是否允许未配


### 求解和实现

- 明确一般图还是二部矩阵
- 选择匹配或指派方法
- 独立检查不重复与费用

Python - apis - networkx.max_weight_matching
- scipy.optimize.linear_sum_assignment（指派）
- dependencies - SciPy
- NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - matchpairs（指派方向）或MILP
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline ≤4对象全部合法配对/排列枚举

- - check 合法性
- method 集合/行列计数
- expected 没有重复对象或不可配边
- - check 最优
- method 小例全部配对枚举
- expected 权重一致

- 一般图套矩阵指派
- 把未配惩罚忽略
- 最大基数与最大权混同

- 明确目标后MILP/小例枚举


### 来源边界

- - title SciPy milp
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 线性目标/范围约束/整数变量，status、gap、dual bound、time limit。
- verification_origin shared primary_sources.json#ps-milp


## 最小费用流/最大流的最小费用


模型ID `disc-mincost-flow`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


容量和供需下最小化流费用


### 输入和适用条件

- 边容量/成本、节点供需；是否先最大化流值
- 先后目标必须明确；费用按同一流单位


### 数学核心

- f为边流
- b_v为净供需

- min Σc_e f_e；0≤f≤u，节点净流=b
- 最大流最小费用是先定最大流值再比成本

供应/需求和需守恒；不要混作任意最小流0


### 求解和实现

- 选择供需型或词典序型
- 求解并留流矩阵
- 逐边重算费用与守恒

Python - apis - networkx.min_cost_flow/max_flow_min_cost
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - linprog/intlinprog构造网络流
- dependencies - MATLAB基础功能
- Optimization Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 整数小流全枚举

- - check 费用
- method 从独立边表重算
- expected 不是复用solver cost_of_flow作为唯一检查
- - check 目标顺序
- method 允许零流的小例
- expected 不得把0费用0流当最大流方案

- 需求符号错
- 负费用循环
- 漏容量

- 可行流与成本界/LP


### 来源边界

- - title SciPy linprog
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 标准LP、返回可行残差、最优/不可行/无界/数值终止。
- verification_origin shared primary_sources.json#ps-lp


## 最小生成树/森林


模型ID `disc-mst`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


以最小总连接成本连通无向节点


### 输入和适用条件

- 无向权重边、节点集、是否要求全连通
- 边成本可加；图不连通只能生成森林


### 数学核心

- T为无环边集

- min Σ_(e∈T)w_e；连通n点时|T|=n-1

Kruskal按权排序并用并查集避环；Prim从切边扩展


### 求解和实现

- 核方向/连通性
- 选Kruskal或Prim
- 检无环/覆盖与小例最优

Python - apis - networkx.minimum_spanning_tree
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - graph+minspantree
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 小图枚举n-1边子集

- - check 结构
- method 独立DFS/连通组件
- expected 无环且覆盖；断连报森林
- - check 最优
- method 小图枚举树
- expected 总成本相同

- 有向图错误套MST
- 节点丢失
- 森林冒充全连通

- 按组件森林或重定义连接规则


### 来源边界

- - title NetworkX minimum_spanning_tree
- url https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.minimum_spanning_tree.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 图结构与复杂网络指标


模型ID `disc-network-metrics`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


描述连接结构而不是仅画节点图


### 输入和适用条件

- 图方向/权重语义、节点/边、组件
- 以下C用于简单无向无权图；加权/有向需匹配相应定义；断连需报告范围


### 数学核心

- k_i为邻接节点数
- t_i为邻居间边数
- σ_st为最短路径条数

- 简单无向局部聚类C_i=2t_i/[k_i(k_i-1)]（k_i<2约定0）
- 度中心性k_i/(n-1)；介数Σ_(s≠v≠t)σ_st(v)/σ_st需声明点对计数与归一化
- 平均距离对指定可达点对平均；直径max有限距离需说明组件

无优化目标；孤点/方向/权重不是可忽略缺项


### 求解和实现

- 规定指标与距离语义
- 按组件计算并对照小图
- 避免从相关图指标推出因果

Python - apis - networkx.clustering/diameter/centrality
- dependencies - NetworkX
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - degree/distances与原创指标
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 三角形C=1，链端C=0

- - check 定义
- method 手算三角形/链/孤点
- expected 组件处理不暗删孤点
- - check 单位
- method 重标度距离
- expected 路径长度按对应尺度变化

- 断连默认省略
- 边强度被当距离
- 编号数值被当特征

- 分组件指标+完整范围说明


### 来源边界

- - title SciPy shortest_path
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 有向/无向图与Dijkstra/Bellman-Ford等路径接口及权重边界。
- verification_origin shared primary_sources.json#ps-graph
