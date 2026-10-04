# evaluation 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 层次分析法AHP


模型ID `eval-ahp`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


从可说明的成对判断建立偏好权重


### 输入和适用条件

- 正互反判断矩阵、层级/判断者、RI表来源
- A_ij>0,A_ji=1/A_ij,A_ii=1；偏好能解释
- 一致性是结构检查，不证明偏好正确/客观


### 数学核心

- A∈R^(n×n)；w>=0,sum w=1；lambda_max；RI_n

- A*w=lambda_max*w，取正主向量并归一
- CI=(lambda_max-n)/(n-1), CR=CI/RI_n（n>2）
- n=1/2的互反有效矩阵按其一致性特例处理，不做0/0

- 权重范围/层级加权；CR接受阈值由选定依据声明


### 求解和实现

- 核对正互反和层级
- 冻结RI/判断来源
- 求主特征对和权重
- 一致性/判断扰动与等权对照

Python - apis - numpy.linalg.eig
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - eig
- 原创一致性检验
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline A_ij=w_i/w_j，w=(.5,.3,.2)时lambda=3、CI=0

- - check 精确一致
- method 用比值矩阵独立手核
- expected 恢复w且CI=0
- - check 结构
- method 检查互反/正性/维数
- expected 不让abs(eigenvector)掩盖非法矩阵
- - check 稳定
- method 判断者/权重扰动
- expected 报告排名/决策敏感性

- RI表混用
- 矩阵非互反
- 把主观权重包装客观

- 等权/分项判断
- 回到用户偏好而非自动填矩阵


### 来源边界

- - title Kułakowski 作者AHP综述/方法论文
- url https://arxiv.org/abs/1605.05777
- checked_at None
- evidence reference_only
- checked_scope 父任务定位，全文链接本次未读取
- metadata_recorded_at 2026-10-04


## DEA效率前沿（CCR/BCC）


模型ID `eval-dea`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


比较相似对象投入与产出的相对效率


### 输入和适用条件

- 同技术DMU、非负投入X和产出Y、方向/规模报酬政策
- DMU具有可比较生产技术，零/缺失与噪声处理明示
- 相对包络效率不等于因果或绝对质量


### 数学核心

- X∈R^(m×n)、Y∈R^(s×n)；x0/y0当前DMU；lambda>=0；theta

- CCR投入导向：min theta, s.t. X lambda<=theta x0, Y lambda>=y0, lambda>=0
- BCC另加sum lambda=1；这改变规模报酬假设

- theta>=0；包含本DMU时theta=1可行；输入/输出非退化


### 求解和实现

- 核对可比性和单位
- 选择投入/产出方向及CCR/BCC
- LP求解保存状态/松弛
- 独立可行/自比较与异常DMU敏感性

Python - apis - scipy.optimize.linprog
- dependencies - SciPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - linprog
- 原创DEA约束
- dependencies - Optimization Toolbox
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 单投入单产出CCR效率=(y0/x0)/max_j(yj/xj)，正输入

- - check 比率小例
- method 与1输入1产出手算对照
- expected 效率与LP一致
- - check 可行与界
- method 独立重算投入/产出约束，核对自身theta1
- expected 主张与方向一致
- - check 敏感
- method 删除异常前沿点/改规模假设
- expected 报告相对样本依赖

- 异质DMU
- 产出/投入定义错
- 噪声支配前沿
- 维数过多全有效

- 简单生产率比值
- 更同质对象或减少指标


### 来源边界

- - title Charnes/Cooper/Rhodes 1981作者论文
- url https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.27.6.668
- checked_at None
- evidence reference_only
- checked_scope 父任务定位，全文读取失败
- metadata_recorded_at 2026-10-04


## 熵权（数据差异赋权）


模型ID `eval-entropy-weights`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


按声明数据变换的样本差异定义指标权重


### 输入和适用条件

- 至少2对象、方向化非负z、零/常量政策
- 此权重测样本差异，不是用户偏好/因果重要性
- 对象集合/变换改变会改变权重


### 数学核心

- p_ij列概率；n对象；e_j归一熵；d_j=1-e_j

- p_ij=z_ij/sum_i z_ij（有效非恒定列）
- e_j=-sum_i p_ij ln p_ij/ln n，0 ln0=0
- w_j=(1-e_j)/sum_j(1-e_j)
- 常量列本参考约定p=1/n,e=1,w=0；全部无差异输出NO_DISCRIMINATION

- 0<=p,e,w<=1，列p和1；有信息时w和1


### 求解和实现

- 声明方向化/缩放
- 算概率/熵且处理零项
- 排除无差异列
- 比较等权、异常值/集合敏感性

Python - apis - scripts/entropy_topsis.py:entropy_profile
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - 原创概率/熵矩阵
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 列p=(.5,.5)熵1；p=(1,0)熵0

- - check 概率/熵手核
- method 两点分布独立计算
- expected 范围和极限正确
- - check 常量/零
- method 全常量及含零列
- expected 无信息不给排名
- - check 敏感
- method 对象与异常值变化
- expected 说明客观差异不等于价值

- n=1
- 负值未经合理变换
- 熵权被称真偏好

- 等权/分项报告
- 获取明确价值判断


### 来源边界

- - title Shannon 1948 原论文
- url https://www.princeton.edu/~wbialek/rome/refs/shannon_48.pdf
- checked_at None
- evidence reference_only
- checked_scope 父任务已定位；原文链接未读取；熵权方案是另行定义，非Shannon决策权重定理
- metadata_recorded_at 2026-10-04


## Gaussian因子分析


模型ID `eval-factor-analysis`　类别 `model`　知识等级 `THEORY_GUIDE_REVIEWED`


用潜在因子及特征特异噪声解释协方差


### 输入和适用条件

- 样本-特征、因子数、尺度、缺失与噪声政策
- z~N(0,I)，独立epsilon~N(0,Psi)且Psi对角
- 旋转/载荷不唯一，不能只凭载荷赋真实因果标签


### 数学核心

- x=mu+Lambda z+epsilon；Sigma=Lambda Lambda'+Psi

- MLE最小化logdet Sigma+tr(S Sigma^-1)，S=训练Xc'Xc/n
- Lambda Q的正交旋转保持Lambda Lambda'，所以需要识别/解释约束

- Psi正对角；因子数/识别/旋转政策由任务声明


### 求解和实现

- 训练内处理尺度
- 选因子数与识别/旋转政策
- 用审阅MLE/SVD等方法估计，EM引用统计家族
- 核对协方差与留出似然

Python - apis - sklearn.decomposition.FactorAnalysis
- dependencies - scikit-learn
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - factoran
- dependencies - Statistics and Machine Learning Toolbox
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 一因子Lambda=(1,2)'、Psi=diag(.5,.5)给Sigma=[[1.5,2],[2,4.5]]

- - check 协方差
- method 独立重建Lambda Lambda'+Psi
- expected 符合模型/样本误差
- - check 旋转
- method 正交Q前后协方差比较
- expected 保持同一观测分布
- - check 泛化
- method 留出/阶数敏感
- expected 避免纯训练拟合选复杂模型

- 因子不可识别
- 噪声结构不合
- 载荷因果化

- PCA主卡/分项统计
- 减少因子与解释主张


### 来源边界

- - title scikit-learn FactorAnalysis 官方本机文档
- url https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机官方包文档，网页未读；版本/hash见local_primary_source_checks.json


## 模糊综合评价与合成算子


模型ID `eval-fuzzy-comprehensive`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


用明确隶属与评价规则合成多指标结果


### 输入和适用条件

- 隶属矩阵R、等级含义、权重/算子与边界
- 隶属度是程度不是概率；数据/专家规则须有依据
- 加权均值与max-min不能混用解释


### 数学核心

- R_ij∈[0,1]；w_i>=0；b_j合成隶属

- 加权均值b_j=sum_i w_i R_ij，sum w=1
- max-min合成b_j=max_i min(w_i,R_ij)（指定模糊关系语义）
- 均值法仅当每行R和1才自然使b和1；max-min不要求/保证和1

- 无统一优化目标；隶属函数/权重/去模糊政策需定义


### 求解和实现

- 确定等级与隶属定义
- 声明合成算子
- 计算并保存每指标贡献
- 小矩阵/隶属与敏感性检验

Python - apis - 原创NumPy均值/max-min
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - 原创矩阵合成
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 两个指标、两等级的2×2均值和max-min可枚举

- - check 范围
- method 独立小矩阵计算
- expected 隶属在[0,1]
- - check 归一条件
- method 分别检验两种算子而非强迫全部和1
- expected 与声明语义一致
- - check 敏感
- method 权重/隶属/阈值变化
- expected 报告边界而非伪精确概率

- 概率误解
- 算子名不明
- 专家分数伪观测

- 分项隶属/等权均值
- 保留多个等级而非硬标签


### 来源边界

- - title Zadeh 1965 Fuzzy sets
- url https://doi.org/10.1016/S0019-9958(65)90241-X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## max-min模糊关系闭包


模型ID `eval-fuzzy-relation-closure`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在明确关系语义下补足模糊可达/等价关系


### 输入和适用条件

- [0,1]关系矩阵、方向/对称/自反要求
- 有向可达不自动对称；相似等价需求才预先对称/自反
- 隶属并非转移概率


### 数学核心

- R_ij关系强度；(R o R)_ij=max_k min(R_ik,R_kj)

- R+=R max (R o R) max ...直到固定点
- max-min Floyd更新R_ij=max(R_ij,min(R_ik,R_kj))
- 对等价相似先满足自反/对称，再求传递闭包；alpha-cut按对应关系解释

- 无优化目标；保留[0,1]与题设关系性质


### 求解和实现

- 核对关系来源/方向
- 仅按任务补自反/对称
- max-min闭包
- 小路径、固定点与alpha-cut验算

Python - apis - 原创NumPy max-min
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - 原创max-min循环
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 1→2=.7,2→3=.5,1→3=.1时闭包1→3=.5

- - check 路径枚举
- method 独立枚举小图路径瓶颈max-min
- expected 与闭包一致
- - check 固定点
- method 再次闭包/传递不等式
- expected 不再改变且未减小原关系
- - check 语义
- method 对称/方向/alpha-cut分别核对
- expected 不把可达误为概率

- 模糊概率混用
- 静默对称化改变任务
- 算子换成矩阵乘法

- 原关系/小图枚举
- 明确阈值后普通图解释


### 来源边界

- - title Zadeh 1965 Fuzzy sets（关系定义来源定位）
- url https://doi.org/10.1016/S0019-9958(65)90241-X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 经典绝对差灰色关联


模型ID `eval-grey-relation`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


按参考序列和尺度定义比较序列的接近程度


### 输入和适用条件

- 同索引序列、参考z0、变换、区分系数rho与汇总权重
- 比较意义来自参考/尺度，关联不等于统计因果
- 经典绝对差与资料斜率/符号变体不自动同一方法


### 数学核心

- Delta_ij=|z0_i-z_ij|；Dmin/Dmax在声明比较域；0<rho<=1

- xi_ij=(Dmin+rho*Dmax)/(Delta_ij+rho*Dmax)
- Gamma_j=sum_i v_i xi_ij，v_i>=0,sum v=1
- Dmax=0时所有序列相同，定义关联1且并列

- 没有独立优化目标；参考选择/参数需冻结


### 求解和实现

- 对齐索引与来源
- 声明无量纲变换/参考
- 用全域标量min/max算系数
- 汇总与参考/参数敏感性

Python - apis - 原创NumPy标量全域极值
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - 原创逐元素系数
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 参考与比较全相同关联1；单差值可直接手算

- - check 手核差矩阵
- method 独立算Delta/Dmin/Dmax
- expected 无向量右除误用
- - check 边界
- method 全相同/零方差/负原量
- expected 按声明变换解释
- - check 敏感
- method 换参考/rho/索引
- expected 不能把稳定接近当因果

- 参考/方向不明
- min/max维数错误
- 伪因果解释

- 直接差距/分项图
- 报告不同参考情景


### 来源边界

- - title Deng 1982 Control problems of grey systems
- url https://doi.org/10.1016/S0167-6911(82)80025-X
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## 指标方向与尺度变换


模型ID `eval-indicator-transforms`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


把不同单位指标转换到可比较且有意义的尺度


### 输入和适用条件

- 对象-指标、单位、方向、目标/最优区间、缺失/零/常量政策
- 方向来自业务目标，不由数据大小猜
- 样本范围缩放会依赖当前对象集合，未来应用应冻结训练尺度


### 数学核心

- x_ij原指标；l_j/h_j参照下上界；z_ij无量纲效用

- 收益z=(x-l)/(h-l)；成本z=(h-x)/(h-l)，h>l
- 目标点t可用z=1-|x-t|/max_i|x_i-t|，全同目标时定义1
- z-score=(x-mu)/s用于统计尺度，不自动表示好坏；常量s=0必须处理

- 没有统一优化目标；范围/外推/截断与零常量政策必须声明


### 求解和实现

- 排除ID并核对方向/单位
- 区分固定界和样本界
- 明确变换及边界
- 比较原尺度/等权/扰动

Python - apis - 原创NumPy变换
- StandardScaler(统计用途)
- dependencies - NumPy
- scikit-learn(可选)
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - 原创矩阵变换
- normalize/zscore(统计用途)
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 单指标收益/成本下端点0/1可手核

- - check 方向
- method 用两个已知优劣值独立代入
- expected 单调方向正确
- - check 单位
- method 正比例单位变换与声明平移规则
- expected 解释不因单位改变
- - check 边界
- method 零/负/常量/新对象越界
- expected 不静默倒数或删除

- 编号入模
- 零值倒数
- 方向不明
- 混同统计标准化与效用

- 原单位分项报告
- 等权并披露可比性限制


### 来源边界

- - title OECD/JRC Handbook on Constructing Composite Indicators
- url https://doi.org/10.1787/9789264043466-en
- checked_at None
- evidence reference_only
- checked_scope 仅定位；具体变换/权重政策为本卡声明的数学方案，不声称原文已读
- metadata_recorded_at 2026-10-04


## PCA主成分降维


模型ID `eval-pca`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


以线性低维表示保留样本变异；排名须额外建模


### 输入和适用条件

- 非ID连续特征、中心化/尺度政策、维数k
- 线性方差方向对任务有意义；尺度影响方向
- 训练内估计均值/缩放；成分符号不唯一


### 数学核心

- Xc=X-mean；S=Xc'Xc/(n-1)；V_k'V_k=I；T=Xc V_k

- S v_j=lambda_j v_j，特征值降序
- Xhat=T V_k'+mean
- PCA解min_rank<=k ||Xc-Xhat_c||F²；或最大化tr(V_k'SV_k)

- 降维目标不是评价对象的效用；综合排名需另定权重/符号


### 求解和实现

- 剔除ID并核对尺度
- 训练内中心化/可选标准化
- SVD/eig同步排序并选k
- 重构、方差与下游验证

Python - apis - sklearn.decomposition.PCA
- numpy.linalg.svd
- dependencies - scikit-learn
- NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - pca
- svd
- dependencies - Statistics and Machine Learning Toolbox(pca)
- MATLAB(svd)
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline X=[[-1,-2],[0,0],[1,2]]：S=[[1,2],[2,4]]，特征值5/0、rank1重构精确

- - check 解析协方差
- method 手算小矩阵特征对
- expected 方差/重构一致
- - check 排序/符号
- method 直接SVD对照并匹配符号
- expected 不假定eig顺序
- - check 任务
- method 维数/缩放/样本扰动与留出
- expected 降维与排名主张分开

- ID进入特征
- 零方差/缺失
- 将方差最大等同价值最高

- 原特征/少量有解释指标
- 等权评价另建合同


### 来源边界

- - title scikit-learn PCA 官方本机文档
- url https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- checked_at 2026-10-04
- evidence verified_primary
- checked_scope 已读本机官方包文档，网页未读；版本/hash见local_primary_source_checks.json


## 秩和比RSR（声明的秩聚合）


模型ID `eval-rank-sum-ratio`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


用指标秩作尺度稳健的综合排序


### 输入和适用条件

- 方向、对象矩阵、并列秩政策及权重
- 秩变换丢失数值间距；权重依然需依据
- 本卡只给基础RSR，不把probit分组等扩展默认包含


### 数学核心

- R_ij∈[1,n]为越大越好的秩；n对象,m指标

- 等权RSR_i=sum_j R_ij/(n*m)
- 加权RSR_i=sum_j w_j R_ij/n，w>=0,sum w=1

- 无优化目标；基础得分范围[1/n,1]（平均并列秩）


### 求解和实现

- 核对方向并按政策排秩
- 以基础或权重RSR聚合
- 保留并列与原指标
- 手核及排序/权重敏感性

Python - apis - scipy.stats.rankdata
- 原创聚合
- dependencies - SciPy
- NumPy
- implementation_notes - 未有运行证据的实现保持未验证。

MATLAB - apis - tiedrank
- 原创聚合
- dependencies - Statistics and Machine Learning Toolbox(可选)
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 2对象2同向指标两列秩[1,2]，RSR=[.5,1]

- - check 并列与方向
- method 手算小矩阵秩
- expected 平均并列和成本方向正确
- - check 范围/单位
- method 单调单位变换不改秩
- expected 按基础定义成立
- - check 解释
- method 极大差距与轻微差距的秩比较
- expected 说明丢失间距

- 把秩权当客观价值
- 拟合probit却无分布依据

- 原指标/分项秩
- 等权排名与限制


### 来源边界

- - title SciPy rankdata 官方接口（未读取网页）
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04


## TOPSIS理想点排序


模型ID `eval-topsis`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


在声明指标方向、尺度和权重下比较方案接近理想点程度


### 输入和适用条件

- 对象矩阵、方向、权重及标准化约定
- 权重反映当前比较目标；有限方案集与理想点依赖样本
- 本参考实现先方向min-max，再列L2归一，不与别的TOPSIS convention混用


### 数学核心

- z方向化矩阵；r_ij=z_ij/sqrt(sum_i z_ij²)；w_j>=0

- v_ij=w_j*r_ij；a+_j=max_i v_ij，a-_j=min_i v_ij
- D+_i=||v_i-a+||2，D-_i=||v_i-a-||2
- C_i=D-_i/(D+_i+D-_i)；相同对象/无信息分母0时定义并列.5

- sum w=1；不是优化器或唯一客观排名
- 全常量/无区分信息的参考实现允许全零权并返回NO_DISCRIMINATION与并列.5；正常比较要求正总权重。


### 求解和实现

- 核对方向/常量/ID
- 冻结变换与权重
- 求理想点/距离/接近度
- 手核、扰动、对象增删核验

Python - apis - scripts/entropy_topsis.py:topsis
- dependencies - NumPy
- implementation_notes - 未有运行证据的实现保持未验证。
- 有限大权重先按max(w)缩放后归一，避免sum溢出

MATLAB - apis - 原创方向化/距离矩阵
- dependencies - MATLAB
- implementation_notes - 未有运行证据的实现保持未验证。


### 验证和回退

Baseline 两同向指标[0,.5,1]且等权，接近度[0,.5,1]

- - check 手核距离
- method 直接画/算小二维理想点
- expected 与接近度一致
- - check 等同对象
- method 相同矩阵/常量指标
- expected 不给虚构优劣
- - check 尺度/权重
- method 正单位变化、排列、巨大有限权重
- expected 对应声明不变量

- 变换不明
- 成本方向错
- 排名逆转/权重敏感
- 权重求和溢出

- 等权分项/等级区间
- 报告敏感而非唯一排名


### 来源边界

- - title OECD/JRC Handbook on Constructing Composite Indicators
- url https://doi.org/10.1787/9789264043466-en
- checked_at None
- evidence reference_only
- checked_scope 仅定位；具体变换/权重政策为本卡声明的数学方案，不声称原文已读
- metadata_recorded_at 2026-10-04
- - title Hwang & Yoon Multiple Attribute Decision Making
- url https://link.springer.com/book/10.1007/978-3-642-48318-9
- checked_at None
- evidence reference_only
- metadata_recorded_at 2026-10-04
