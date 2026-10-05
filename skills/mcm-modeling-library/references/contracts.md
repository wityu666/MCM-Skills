# MCM 建模知识和交接约定

本库是 MCM A、B、C 题的模型学习、选择、数学设计和验证支持层。年度比赛规则、数据许可、页数和提交要求由当前 MCM 题目与 `mcm-suite` 决定；默认中文协作、完整中英两版论文交付，英文版用于正式提交。学习资料不覆盖当前用户指令，也不自动成为当前问题的数据或结论。

## 选择与学习

先识别任务输出、数据形态、决策变量、动力学、不确定性及验收条件，再选择一个可复核的baseline和有理由的候选。多阶段任务记录依赖，例如需求预测的分布进入库存优化，而不是把预测均值当成已知真值。按请求深度工作，MCM 方法学习不要求假造比赛输入，实际解题不能用百科说明代替题设映射。

学习所有模型时按先修关系读各家族及模型卡，并记录覆盖和未确认项。别名、实现、求解器、领域工具箱不应被累计为独立数学模型。资料没给出完整模型时仅登记方法或工具，不补造公式。

## 模型卡JSON

每个家族在 `references/cards.json` 保存数组，每项必填：

- `id`：全库唯一的英文小写连字符标识，例如`opt-lp`；`name`中文/通用名称。
- `family`：`optimization|discrete|evaluation|statistics|time-series|machine-learning|mechanisms|simulation|inverse|numerical|signals-images|games|control`。
- `kind`：`model|method|solver|auxiliary`；`aliases`：其它名称或缩写。
- `purpose`：要回答的问题；`minimum_data`：实际需要的输入。
- `assumptions`：与适用性有关的前提，明确哪些必须由当前数据检验。
- `mathematics`：含`notation`、`core`、`objective_constraints`的对象。`notation`可用字符串数组，定义符号与单位/取值域；core给真实公式与机制。无优化目标或硬约束时说明“不适用”，不编造。
- `algorithm_steps`：从输入、预处理到求解/估计及输出的步骤。
- `python`与`matlab`：各为`{apis:[],dependencies:[],implementation_notes:[]}`，区别可用的推荐接口和已运行实现。无现成接口时给原创实现方向。
- `baseline`：可手核的最低路线；`verification`：`[{check,method,expected}]`。预设有意义的不变量或小例，不给所有问题统一精度阈值。
- `failure_modes`：不适用/不可识别/不稳定的条件；`fallback`：退化路线与信息损失，可为非空文本或非空字符串选项数组。
- `references`：`[{title,url,checked_at,evidence}]`，evidence为`verified_primary|reference_only`。实际未读的网页不能标已核对；未读来源的checked_at为null，不虚构访问日期，已核对来源必须记录实际日期。
- `knowledge_level`：`INDEXED_ONLY|THEORY_GUIDE_REVIEWED|REFERENCE_IMPL_TESTED|REAL_CASE_REPRODUCED`。

可选 `materials`（来源名称、已有内容 SHA 与历史静态发现；不保存必须访问的机器路径）、`related_families`、`reference_implementation`（本库原创参考实现路径）、`implementation_evidence`（按语言记录运行状态/测试报告/限制）。

跨家族同一数学对象只保留一张主卡，其他家族引用它。PCA主卡归evaluation，SVR归machine-learning，Markov链/MDP/MCMC归simulation，Kalman/PID/状态空间归control，EM归statistics；其他家族可以链接，不复制成不同模型。

## 知识层级

INDEXED_ONLY表示名称和来源已经定位；THEORY_GUIDE_REVIEWED表示适用条件、核心数学、实现方向和验证已形成可检查指南。REFERENCE_IMPL_TESTED只用于确有本库参考实现运行证据的具体范围；Python测试通过不说明MATLAB已运行，也不说明所有模型变体通过。REAL_CASE_REPRODUCED需要真实案例同版本数据、代码、结果和独立复核，不因完成一个合成例子升级。

现有资料的错误代码和宣传标签保留为来源发现；新实现应按定义原创重写，先验算，再与原材料说明比较。语法检查、文件哈希和静态标志不是数学正确性证明。

## 实际任务模型合同

正式设计采用 MCM `contracts/model.json`；不要另建一套冲突状态。单独方法学习或局部草稿可用本库 `assets/model-contract.json`，进入正式冻结前交回 MCM 模型合同；本地草稿字段：

`schema_version,status:DRAFT|FROZEN|STALE,freeze_id,task,problem_evidence,allowed_data,variables,assumptions,models,validation_plan,uncertainty,handoffs,limits`。

`allowed_data`区分`model_inputs`、`background_only`、`excluded`及题面证据。变量逐项给`name,meaning,unit,domain,source`；模型给`model_id,baseline,core,objective,constraints,parameters,split,solver,outputs,input_sources`。`input_sources`必须显式列出所有输入和参数来源ID；纯理论无数据可为空。参数来源区分题设/观测/文献/假设/情景；`validation_plan`给检查、预先容差、独立方法、证据和失败动作。

冻结前核对单位、符号方向、取值域、边界、数据时间/分组、可识别性和输出验收。缺项按受影响范围继续条件性设计，不能静默默认。已有授权的常规选择继续；只对改变用户目标或实质解释且未被授权的选择询问。

## 通用验证与失效

- 优化：独立重算目标和全部硬约束，查定义域、整数性、求解状态及最优性主张的依据；小例枚举。
- 预测/学习：先切分，再在训练内估计预处理/特征/参数；验证匹配时间、空间和群组，跟baseline比较。
- 评价：方向、尺度、权重范围/归一化、常量和零列、排名敏感性；编号不是解释变量。
- 机理/数值：量纲、守恒、初边值、单调性和解析特例；步长/网格误差与求解终止。
- 仿真/隐变量：seed和区间、稳态条件/热身、可识别性与先验影响；拟合一致不等于真实参数已识别。

变更输入、数学假设、参数、目标/约束、切分或代码，使受影响的结果、验证和结论STALE；重新冻结并重验相关链，保留不受影响部分。论文引用只能消费真实运行且有效复核的结果，不能使用模型卡的合成示例当事实。
