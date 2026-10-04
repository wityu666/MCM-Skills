# numerical 模型和方法指南


以下内容按模型卡生成；知识等级与实际运行范围分别记录。完整来源和结构化字段见cards.json及编译catalog。


## 括区间二分求根


模型ID `num-bisection`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


连续函数在变号区间中定位零点


### 输入和适用条件

- 可有限求值f、a<b、端点变号/端点零点、x/f容差和预算
- f在区间连续；只变号不保证不连续函数有根


### 数学核心

- m=(a+b)/2
- r=f(m)

- 根据符号保留变号半区间；k轮区间宽=(b-a)/2^k

残差与横坐标误差停止标准分开


### 求解和实现

- 检查端点/有限值
- 二分并保留括区间
- 满足停止或预算/机器精度明确失败

Python - apis - assets/numerical_reference.py:bisect
- scipy.optimize.bisect（方向）
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - fzero([a,b])或原创二分
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline x²-2在[0,2]，根sqrt(2)

- - check 解析值
- method 与sqrt(2)而非另一份二分比较
- expected 误差符合横坐标容差
- - check 失败
- method 无变号、NaN、预算耗尽
- expected 拒绝/失败而非假收敛

- 不连续/域外
- 绝对精度低于浮点分辨率
- 只按迭代数称成功

- 改合法区间/连续模型或报告无法定位


### 来源边界

- - title SciPy bisect
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.bisect.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 余弦相似度


模型ID `num-cosine-similarity`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


比较非零向量方向，区别相似度和距离。


### 输入和适用条件

- 同特征空间的非零有限向量
- 方向而非幅度的任务解释
- 各维单位和尺度已定义
- 零向量没有定义方向，需明确处理而非默认高度相似
- 一般cosine距离不自动满足三角不等式


### 数学核心

- x,y∈R^d且范数非零

sim(x,y)=xᵀy/(||x||₂||y||₂)，cosine distance=1-sim；实向量相似度在[-1,1]，非负向量通常[0,1]。

依具体应用设定；此方法本身不自动定义预算、控制或因果目标。


### 求解和实现

- 确定特征和训练内尺度/文本表示
- 检查非零范数并在数值上稳健归一
- 计算内积与距离口径
- 与对象含义和其它距离对比

Python - apis - scipy.spatial.distance.cosine
- sklearn.metrics.pairwise.cosine_similarity
- dependencies - 按实际接口确认维护版本
- implementation_notes - 接口方向，不代表已运行当前问题；在训练/拟合范围内确定数据处理。

MATLAB - apis - 按定义点积和norm；必要时pdist接口
- dependencies - 按实际工具箱和版本确认
- implementation_notes - 本次未运行MATLAB；不把同名函数或外部工具箱视作已经可用。


### 验证和回退

Baseline 正交、同向和反向单位向量手算

- - check 范围
- method 单位向量手算
- expected 同向1、正交0、反向-1
- - check 尺度
- method 正倍数缩放复核
- expected 相似度不变
- - check 零值
- method 零向量边界
- expected 明确未定义，不偷偷给可比值

- 零范数、混合单位、把幅度差误作同一对象、余弦距离当万能度量

改为与任务相关的Euclidean/其它明确距离或报告不可比较


### 来源边界

- - title scipy.spatial.distance.cosine installed first-party documentation
- url https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.spatial.distance.cosine.html
- checked_at 2026-10-04
- evidence verified_primary
- version 1.15.3
- inspection_scope Local first-party documentation read; web page not represented as visited.
- doc_sha256 a3922f148cae770f572429ebddd391cef59aed83c1f5325fa21ed4ea9431acf7


## 特征/SVD分解与数值谱


模型ID `num-eigen`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


分析线性算子、秩与模式；不是自动赋予统计解释


### 输入和适用条件

- A、对称/复数属性、所需特征对与误差
- 对称矩阵可用eigh；一般非对称可能复谱或非正规


### 数学核心

- Av=λv
- A=UΣV^*

- 特征残差Av-λv；SVD为正交因子与非负奇异值

顺序、符号/相位、重特征空间不唯一


### 求解和实现

- 核结构选接口
- 分解并按任务排序
- 核残差/正交与解析谱

Python - apis - numpy.linalg.eig/eigh/svd
- scipy.sparse.linalg.eigs
- dependencies - SciPy
- NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - eig/eigs/svd
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline A=[[2,1],[1,2]]谱1,3

- - check 解析谱
- method 手算2×2
- expected 特征值1/3，不能逐元素强比向量符号
- - check 分解
- method 残差/重构
- expected 按尺度预设容差

- eigenvectors未排序
- 重特征基向量误判
- 非正规谱不稳定

- SVD/子空间比较，保留数值限制


### 来源边界

- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 最小二乘的rank、singular values、residual与驱动方法。
- verification_origin shared primary_sources.json#ps-linalg
- - title NIST DLMF §3.2 Linear Algebra
- url https://dlmf.nist.gov/3.2
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 数值微分/有限差分


模型ID `num-finite-difference`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


无解析导数时估计局部变化/Jacobian


### 输入和适用条件

- 可有限求值f、尺度/域与步长
- 足够光滑；噪声/舍入会与截断误差竞争


### 数学核心

- h为与x同单位步长

- f′≈[f(x+h)-f(x)]/h（O(h)）
- 中心f′≈[f(x+h)-f(x-h)]/(2h)（O(h²)，适当光滑）

无优化目标；域边界使用单边式而非非法求值


### 求解和实现

- 按尺度选h
- 计算一系列h
- 与解析特例/梯度检查对照

Python - apis - 原创差分
- scipy.differentiate（方向）
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - gradient/原创差分
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline f=x²的解析导数2x

- - check 误差
- method 一系列h与解析值
- expected 展示截断/舍入区间
- - check 边界
- method 域[0,∞)在0
- expected 不得向负域求值

- h太小取消误差
- 非光滑点
- 带噪函数

- 解析/自动微分或平滑后声明信息损失


### 来源边界

- - title NIST DLMF §3.4 Differentiation
- url https://dlmf.nist.gov/3.4
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 规则网格/散点多维插值


模型ID `num-grid-interpolation`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在空间/参数网格上评价场值


### 输入和适用条件

- 网格轴与排列、场数组/散点坐标、单位/查询域
- 规则网格与散点方法不同；凸包外不是已知场


### 数学核心

- z(x,y)为场
- t/u为单元内局部坐标

- 双线性z=(1-t)(1-u)z00+t(1-u)z10+(1-t)u z01+tu z11
- 散点分片线性需明确三角剖分/邻域

轴顺序、递增/递减轴与值矩阵匹配


### 求解和实现

- 确认网格类型
- 使用匹配接口
- 常数/仿射场与原节点独立核验

Python - apis - scipy.interpolate.RegularGridInterpolator
- LinearNDInterpolator/griddata
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - griddedInterpolant
- scatteredInterpolant
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 仿射场z=2x+3y+1

- - check 轴
- method 非正方形网格手例
- expected 不把x/y转置混同
- - check 节点/域
- method 全部节点与凸包外
- expected 原值一致、域外策略明确

- interp2d旧API
- 矩阵转置错
- 凸包外NaN被隐藏

- 低阶局部插值或限制域


### 来源边界

- - title SciPy interp2d removal/transition
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp2d.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 本次会话已核对1.14移除与规则/散点替代方向。


## Lagrange/重心多项式插值


模型ID `num-lagrange`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


以节点基函数或稳定重心形式插值


### 输入和适用条件

- 不同节点/值与查询
- 重复节点不适用；噪声数据更适合拟合而非强穿点


### 数学核心

- ℓ_i(x)=∏_(j≠i)(x-x_j)/(x_i-x_j)

- p=Σ_i y_iℓ_i；重心权w_i=1/∏_(j≠i)(x_i-x_j)
- p=Σ_i[w_i y_i/(x-x_i)]/Σ_i[w_i/(x-x_i)]；节点处直接y_i

外推风险与误差范围明确


### 求解和实现

- 处理节点/权
- 在节点精确返回值
- 对比解析函数与Newton小例

Python - apis - scipy.interpolate.BarycentricInterpolator
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创重心形式或低阶polyfit（不同拟合语义）
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 两点线性插值

- - check 基函数
- method 逐节点手核
- expected ℓ_i(x_j)=δ_ij
- - check 稳定性
- method 节点缩放/高阶扰动
- expected 报告振荡/舍入而非无限加阶

- 节点除零
- 高阶振荡
- 把最小二乘polyfit当穿点

- 分段/样条


### 来源边界

- - title NIST DLMF §3.3 Interpolation
- url https://dlmf.nist.gov/3.3
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读不同节点、Lagrange/重心公式与误差表达；Newton目录与差商配套，未做数值库运行。


## Laplace与逆Laplace变换


模型ID `num-laplace`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


将线性时域问题转到复频域并带入初值


### 输入和适用条件

- f(t)、t≥0、增长/收敛条件、初值
- 线性系统与收敛域匹配；逆变换需正确因果/分支


### 数学核心

- F(s)=∫0∞ e^(-st)f(t)dt

- L[f′]=sF-f(0)；高阶含各初值
- 解频域代数关系后逆变换

不把连续Laplace与离散Z变换混同


### 求解和实现

- 写收敛/初值
- 变换并解代数式
- 逆变换代回时域方程

Python - apis - sympy.laplace_transform/inverse_laplace_transform
- dependencies - SymPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - laplace/ilaplace（Symbolic Math Toolbox）
- dependencies - MATLAB基础功能
- Symbolic Math Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline f=e^(-at),F=1/(s+a)

- - check 逆变换
- method 解析指数对照
- expected 初值和原ODE一致
- - check 条件
- method 记录ROC与极点
- expected 不能删掉稳定性条件

- 初值项漏
- 收敛域未知
- 非线性问题错误线性化

- 直接ODE求解/数值对照


### 来源边界

- - title NIST DLMF Laplace transform
- url https://dlmf.nist.gov/1.14.iii
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 线性系统/最小二乘/广义逆数值计算


模型ID `num-linear-systems`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


求Ax=b或最小残差解并诊断秩/病态


### 输入和适用条件

- A,b、尺寸/尺度、是否精确方程或带噪最小二乘
- 不把小残差当参数可识别；矩阵秩与条件数重要


### 数学核心

- r=b-Ax
- A^+为Moore–Penrose广义逆

- 精确兼容时Ax=b；不兼容时min ||Ax-b||²
- QR/SVD比显式(A^TA)^-1更稳健；欠定最小范数需声明

rank不足意味着多解/不可识别；正则化改变问题


### 求解和实现

- 缩放与维度核对
- 分解/求解并留rank/奇异值
- 独立残差与解析小例

Python - apis - numpy.linalg.solve/lstsq/pinv
- scipy.linalg.lstsq
- dependencies - SciPy
- NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - mldivide（A\b）/lsqminnorm/pinv
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 2×2解析方程与过定简单直线

- - check 残差
- method 独立重乘A x
- expected 与精确/LS目标一致
- - check 病态
- method 扰动b比较x
- expected 参数不稳定不能由残差小否认

- 直接逆正规方程
- 秩亏
- 单位量级差

- SVD/正则化并声明改变的解语义


### 来源边界

- - title SciPy lstsq
- url https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 最小二乘的rank、singular values、residual与驱动方法。
- verification_origin shared primary_sources.json#ps-linalg


## Newton差商插值


模型ID `num-newton-interpolation`　类别 `method`　知识等级 `REFERENCE_IMPL_TESTED`


通过全部不同节点构造次数≤n-1的插值多项式


### 输入和适用条件

- n≥1不同x_i及有限y_i、查询x
- 重复节点需Hermite另模型；高阶/近节点有病态风险


### 数学核心

- c_k=f[x_0,…,x_k]为差商

- f[x_i,…,x_j]=(f[x_(i+1),…,x_j]-f[x_i,…,x_(j-1)])/(x_j-x_i)
- p(x)=c_0+Σ_(k=1)^(n-1)c_k∏_(j=0)^(k-1)(x-x_j)

所有阶到n-1；不能遗漏最后项


### 求解和实现

- 校验节点与长度
- 差商表/倒序更新
- 嵌套乘法评价并核全部节点

Python - apis - assets/numerical_reference.py:newton_coefficients/newton_evaluate
- dependencies - Python标准库；大数组可另选NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - 原创差商+嵌套评价
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 两点线性函数/三点二次

- - check 节点一致
- method 原节点逐项评价
- expected p(x_i)=y_i在数值误差范围
- - check 解析多项式
- method 不规则节点三次函数
- expected 任意查询与解析值一致

- 近重节点
- 遗漏最高阶
- 高阶Runge振荡

- 分段线性/样条；不把外推当观测


### 来源边界

- - title NIST DLMF §3.3 Interpolation
- url https://dlmf.nist.gov/3.3
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读不同节点、Lagrange/重心公式与误差表达；Newton目录与差商配套，未做数值库运行。


## Newton/割线求根


模型ID `num-newton-root`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在可微/局部适当初值下加速求零点


### 输入和适用条件

- f、导数或两初点、域、容差/预算
- Newton需导数非零且局部条件；不自动全局收敛


### 数学核心

- x_k为迭代
- f′为同单位导数

- x_(k+1)=x_k-f(x_k)/f′(x_k)
- 割线以两点斜率替导数

保护域与步长；小步不等于残差小


### 求解和实现

- 验证导数/初值
- 更新并检有限值、域与残差
- 不稳定时保留括区间保护

Python - apis - scipy.optimize.root_scalar/newton
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - fzero或原创保护Newton
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 有括区间时二分

- - check 解析例
- method x²-2
- expected 正初值收敛正根；导数/残差独立检查
- - check 奇异
- method f′=0或平坦函数
- expected 不能除零或仅步小假成功

- 导数零
- 越域
- 循环/发散

- 二分/Brent括区间法


### 来源边界

- - title NIST DLMF §3.4 Differentiation
- url https://dlmf.nist.gov/3.4
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行


## 分段线性插值


模型ID `num-piecewise-linear`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


局部连接相邻有序节点


### 输入和适用条件

- 有序不同x和y、查询域/外推规则
- 每段线性是近似假设；离散类别不能连成折线


### 数学核心

- t=(x-x_i)/(x_(i+1)-x_i)

- p(x)=(1-t)y_i+t y_(i+1)，x在该段

外域拒绝/固定外推策略，不能静默延伸


### 求解和实现

- 排序并检查重复
- 定位区间
- 局部插值并核节点/线性函数

Python - apis - numpy.interp
- scipy.interpolate.interp1d（兼容路线）
- dependencies - SciPy
- NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - interp1(...,"linear")
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 线性函数精确

- - check 节点
- method 全部原节点
- expected 返回原值
- - check 域
- method 端点/域外测试
- expected 符合声明外推政策

- 重复节点
- 极稀疏数据
- 不可解释外推

- 返回缺失/限制域并说明


### 来源边界

- - title NIST DLMF §3.3 Interpolation
- url https://dlmf.nist.gov/3.3
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读不同节点、Lagrange/重心公式与误差表达；Newton目录与差商配套，未做数值库运行。


## 梯形/Simpson/自适应数值求积


模型ID `num-quadrature`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


求有限/多重积分并解释误差


### 输入和适用条件

- 函数/样本节点、积分域、奇点/不连续与误差目标
- 复合Simpson等距且子区间偶数；阶数误差需相应光滑性


### 数学核心

- h=(b-a)/n

- 梯形h[y0/2+Σy_i+yn/2]
- Simpson h/3[y0+4Σ奇i yi+2Σ偶i yi+yn]
- Romberg由步长递减梯形作Richardson外推；自适应按局部误差分配子区间

多重积分域/次序与单位显式，误差估计不是绝对保证


### 求解和实现

- 定位奇点/区间
- 选样本或函数积分路线
- 解析特例与加密比较

Python - apis - numpy.trapezoid
- scipy.integrate.simpson/quad/dblquad/tplquad
- dependencies - SciPy
- NumPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - trapz/integral/integral2/integral3
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 常数/线性函数梯形，三次多项式Simpson

- - check 解析
- method ∫0^1 x³ dx
- expected 1/4；合规Simpson准确到舍入
- - check 收敛
- method 网格加密/解析参考
- expected 误差趋势与光滑条件相符

- Simpson样本不合条件
- 遗漏域Jacobian
- 奇点误差估计失效

- 分段积分/变量替换/更低阶并报告误差


### 来源边界

- - title NIST DLMF §3.5 Quadrature
- url https://dlmf.nist.gov/3.5
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读梯形、Simpson与误差条件；Romberg段落。


## 三次样条插值


模型ID `num-spline`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


在分段三次与连续导数条件下平滑插值


### 输入和适用条件

- 有序不同节点/值及自然/夹持/周期等边界条件
- 边界条件有依据；平滑不等于机理真实


### 数学核心

- S_i为分段三次
- M_i=S″(x_i)

- S(x_i)=y_i，内部S/S′/S″连续；各段三次
- 边界条件决定剩余自由度

单调数据若必须保形可改PCHIP；样条可能过冲


### 求解和实现

- 确认边界
- 解相应三对角系统或库接口
- 核节点/导数连接和域外行为

Python - apis - scipy.interpolate.CubicSpline/PchipInterpolator
- dependencies - SciPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - spline/interp1(...,"pchip")
- dependencies - MATLAB基础功能
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 分段线性

- - check 光滑
- method 内部左右导数比较
- expected 与边界/连续阶一致
- - check 保形
- method 单调/非负约束数据
- expected 过冲必须报告，不把负值静默裁剪

- 错误边界
- 稀节点过冲
- 外推失真

- PCHIP/线性并明确光滑损失


### 来源边界

- - title NIST DLMF §3.3 Interpolation
- url https://dlmf.nist.gov/3.3
- checked_at 2026-10-04
- evidence verified_primary
- verified_scope 已读不同节点、Lagrange/重心公式与误差表达；Newton目录与差商配套，未做数值库运行。


## 符号代数与微积分


模型ID `num-symbolic`　类别 `method`　知识等级 `THEORY_GUIDE_REVIEWED`


推导导数、积分、方程解并保持符号域


### 输入和适用条件

- 表达式、变量/假设、域与常数条件
- 符号分支/条件不应在数值化时丢失


### 数学核心

- 符号x的实/复、正性假设

- 按代数恒等/导数积分关系求变换；求解集需要代回原方程
- 不把化简所得表达式的值域自动扩展

无统一优化目标；解分支/常数由原条件决定


### 求解和实现

- 输入变量域
- 推导并保留条件
- 代回/数值点检查与量纲核验

Python - apis - sympy.diff/integrate/solve/simplify
- dependencies - SymPy
- implementation_notes - 接口是实现方向；依赖未因此声明已安装，未运行者不写运行成功。

MATLAB - apis - syms/diff/int/solve/simplify（Symbolic Math Toolbox）
- dependencies - MATLAB基础功能
- Symbolic Math Toolbox
- implementation_notes - 本轮未运行MATLAB；核对实际工具箱与许可，不把Python参考测试当作MATLAB验收。


### 验证和回退

Baseline 手算多项式导数/积分

- - check 恒等
- method 原域随机合法点和代回
- expected 表达式相等但不越过奇点
- - check 分支
- method sqrt(x²)实数域
- expected 不是任意实数恒等于x

- 域假设丢失
- 只留一个根
- 浮点常数污染精确推导

- 手工低阶/数值求解并保留条件


### 来源边界

- - title SymPy calculus documentation
- url https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html
- checked_at None
- evidence reference_only
- verified_scope 链接尚未核对全文；不声称原文复核或运行
