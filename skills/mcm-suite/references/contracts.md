# MCM 项目交接合同 v1

以下是本套件内部约定，不是 COMAP 额外规则。小任务只产出相关文件。路径相对项目根；文件哈希为 SHA-256，同一事实保持一个来源。

## 目录与上下文

`inputs/`原始副本，`contracts/`问题/模型，`sources/`来源，`data/`派生数据，`code/`源码，`results/`冻结结果，`verification/`复核，`paper/`英文源稿/PDF，`logs/`决策/AI使用。

`context.json`：`schema_version:1,contest:"MCM",year`整数，`mode:live|practice|reproduce,problem:A|B|C|null,team_control_number`字符串或null，`working_language:"zh",paper_language:"en",implementation:python|matlab|undecided`。未选题保持null；正式终审需真实题号与 Control Number。

`rules.json`：`schema_version:1,contest:"MCM",year,checked_at`为ISO日期或带时区时间戳，`verification:reference_snapshot|verified|unresolved,sources:[{id,url,title,accessed_at}],claims:{key:{value,status:verified|unresolved,source_id,note}},conflicts:[],problem_specific_requirements_status:not_yet_published|verified|unresolved`。复制快照保持reference_snapshot；现场读取当年官方规则和题面后才能设verified。

关键规则键：`max_main_pages,ai_report_excluded,summary_first_page,english_required,anonymous_required,control_number_each_page,minimum_font_pt,pdf_only,max_file_mb_exclusive,ai_report_required_if_used,stop_work_at,submit_by,submission_url`。值为年度数据，脚本不得写死。训练无需虚构编号或提交凭证。

## 问题与模型

`contracts/problem.json`：`schema_version,status:DRAFT|FROZEN|STALE,freeze_id,statement_files:[{path,sha256}],tasks:[{id,request,deliverables,acceptance,dependencies}],problem_specific_requirements,unresolved,decisions`。题设memo/letter等专项输出也列任务。影响目标/解释的缺项先解决或明示假设；无关缺项不阻碍分析。

`contracts/model.json`：`schema_version,status:DRAFT|FROZEN|STALE,freeze_id,problem_sha256,assumptions:[{id,text,type,evidence,sensitivity}],models:[{task_id,baseline,variables,equations,constraints,objective,method,parameters,outputs}],verification_plan,decisions,fallback`。`type`区分事实/文献参数/建模假设/情景；约定单位、时间范围、目标方向、容差。problem_sha256引用实际问题合同字节。

## 来源与派生数据

`sources/sources.csv` 列：`id,url,title,accessed_at,usage,kind,local_path,sha256,license,limitations`。kind=`official_input|observation|method|parameter|image|scenario`；本地来源也有ID与哈希。网络来源记录机构、变量定义、覆盖范围和as-of；派生数据记录输入ID、转换代码和单位。情景不得标成观测，未知许可记unknown。

## 运行与数字

`results/run_manifest.json`由`scripts/freeze_artifacts.py create`生成：`schema_version,freeze_id,created_at,files:[{path,sha256,bytes}]`。纳入输入、合同、代码、依赖/配置和结果，排除清单自身；补充`command,environment,seed,solver,termination,roles`。字节冻结不证明模型正确。

`results/numeric_bindings.json`示例：

```json
{"schema_version":1,"bindings":[{"id":"RID-001","file":"results/metrics.csv","selector":{"row":0,"column":"mae"},"expected":1.2,"abs_tol":0.001,"rel_tol":0,"unit":"kWh"}]}
```

CSV row为从0开始的数据行；JSON selector=`{"keys":["metrics","mae"]}`。引用限项目内，数值与容差有限且容差非负，必填unit字符串（空字符串表示无量纲）。registry可带freeze_id/run_id。检查器记录registry与真实来源文件的SHA。论文显示取整另说明，不能用容差掩盖结论改变。图表绑定源ID和生成代码。

## 复核与论文

`verification/result_review.json`：`status:PASS|FAIL|INCOMPLETE|STALE,freeze_id,manifest_sha256,checks:[{id,method,evidence,expected,actual,tolerance,status}],task_coverage,unresolved`。关键量独立重算/小样本手核、约束不变量、边界与敏感性按风险选择；原程序重跑只证明重复性。

`paper/paper_manifest.json`：`freeze_id,result_manifest_sha256,result_review_sha256,files`（源稿/图/PDF真实哈希），`number_ids,citation_ids,task_coverage,ai_used`。结构可先起草，未复核数字不能冒充定稿。

`verification/layout_review.json`：`status:PASS|FAIL|INCOMPLETE|STALE,pdf_sha256,page_count,main_page_count,ai_report_start_page`（物理页从1开始或null），`ai_used`必须根据真实日志明确为true或false，模板为null；`main_pages_verified,summary_first_page_verified,english_verified,anonymous_verified,control_number_each_page_verified,minimum_font_verified,visual_all_pages_verified,ai_report_appropriate_verified,citations_verified,task_coverage_verified,unresolved,evidence`。模板检查布尔值全为false。英文、匿名、字体、任务覆盖必须实际检查；最终PDF逐页视觉复核，不能仅靠文本抽取。只有AI报告页可按确认规则排除。

`verification/final_audit.json`：`status:LOCAL_DELIVERY_PASS|FAIL|INCOMPLETE,pdf_sha256,manifest_sha256,checks,unresolved,official_submission:"NOT_SUBMITTED"`。自动静态检查最多给PRECHECK_PASS；真实接收凭证另存。

## 失效与AI记录

数据/模型/代码/参数变化→受影响运行/结果复核/论文失效。纯措辞与引用修订通常只重做论文和版面；改变模型解释回到模型阶段。PDF任何字节变化使旧layout哈希不匹配，须重新渲染检查。保留不受影响成果。

`logs/ai_usage.jsonl`每行：`time,tool,version,purpose,category,input_record,output_record,used_in,human_validation`。只记录实际使用，未知版本记unknown。敏感细节留私有日志，公开披露依当年官方政策；翻译/内嵌AI/代码补全与生成内容的披露形式分别处理。
