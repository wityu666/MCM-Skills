# 完整中文与英文两版交付

用户要求正式 MCM 比赛论文交付两份完整版本：中文版供阅读与复核，英文版用于正式提交。两版采用同一[用户结构](user-preferred-structure.md)、实际任务映射和冻结结果；中文版不是摘要、解释附件或逐段夹排在英文中的译文。后续明确指定的交付范围优先。

## 文件与提交边界

默认分别保存 `paper/zh/report.*` 与 `paper/en/report.*`；各版沿用用户选定的 Word 或 LaTeX 路线，保留一份可编辑源并导出一份 PDF，不要求同一语言同时生成 Word 和 LaTeX。中文 PDF 使用易区分的名称，例如 `report-zh.pdf`；正式上传仅选择已核验的英文 `ControlNumber.pdf`。

`context.json` 的 `paper_language:"en"` 继续表示正式上传语言，不表示给用户只交英文。中文版的页数可以与英文不同，中文排版检查可读性和完整性；当届官方页数、英文与提交文件规则在英文上传版上核验。不得为了让中文与英文同页数而删去中文关键内容或挤压英文版式。

## 同一内容的两种表达

- 两版完整覆盖摘要、正文、模型、验证、结论、必要附录以及题设 memo/letter。英文和中文标题可以自然表述，但保持对应的章节层级和论证功能。
- 模型、目标、约束、假设、变量、参数和公式一致。逐项保持数字、正负方向、单位、时间范围、精度、样本和比较基准；不因翻译更改结果或结论强度。
- 图表来自同一数据与生成代码。语言相关标题、轴标签、图例和图注可以翻译，数据、单位、坐标尺度、排序和误差口径一致；允许为排版调整尺寸与位置。
- 保留局限、失败结果、不确定性和条件。中文不增加英文没有依据的优势，英文不遗漏中文已说明的重要限制。参考文献保持可核验的原始作者、题名、年份及 DOI/URL，不造一份看似对译的新来源。
- 建立稳定的术语、章节、公式、图表及任务对应关系。选一版或内容提纲先成稿都可以；另一版必须与同一事实/结果母版对应，不能独立改写模型。翻译可自然表达，不要求句序或分页逐字相同。
- 若确实使用 AI 翻译或改写，记录实际活动并依当届政策披露；双语要求不自动证明使用过 AI，也不代替原始日志。

## 复核与交接

英文最终 PDF 继续使用 `verification/layout_review.json` 和原英文提交终审。中文 PDF 另做全部页面视觉复核，记录中文源稿/PDF 哈希、页数、中文字体与图表可读性以及未决问题；不能把中文稿的 `english_verified` 填为 true，或用英文提交静态检查器宣称中文合规。

使用[双语复核模板](../assets/bilingual-review.json)记录两版当前源稿与 PDF 哈希、结果冻结/清单、任务/章节、公式/符号、数字/单位、图表数据、引用、结论条件及实际中文逐页证据。各项默认未检查；通过必须有真实审阅位置与依据，哈希本身不证明翻译等价。

项目初始化会创建 `paper/zh/`、`paper/en/` 和未检查的 `verification/bilingual_review.json`。中文记录填实际 `zh_page_count`，在 `zh_page_evidence` 为每个物理页分别登记一项，例如 `{"page":1,"evidence":["渲染图路径与逐页实际检查发现"]}`；空记录、重复页码或只有 `zh_visual_all_pages_verified:true` 均不能证明逐页检查已做。

导出后复用[冻结工具](../../mcm-suite/scripts/freeze_artifacts.py)建立 `paper/content_manifest.json` 文件字节清单，纳入两份源稿和两份 PDF，以及实际使用的共享图表、TeX `input/include`、参考文献、非标准样式和其他项目输入。这是论文资源的字节冻结，不是第二套模型/结果状态。多文件 TeX 不能只登记 `main.tex`；项目外的自定义资源先复制入工作区并更新引用，编译器与系统标准包版本记录在运行环境。清单排除自身、所有 review 文件和 `paper/paper_manifest.json`，避免复核记录与清单互相包含哈希。下例使用 TeX 路线；按实际路线、资源和真实 Control Number 替换路径，不能保留不存在的示例文件：

命令中的 `MCM_SKILLS` 替换为整套 MCM 模块的安装根目录；在仓库中直接运行时它是 `skills/`，`PROJECT` 替换为实际项目根目录。

```sh
python3 MCM_SKILLS/mcm-suite/scripts/freeze_artifacts.py create \
  --root PROJECT --manifest paper/content_manifest.json --freeze-id PAPER-001 \
  --files paper/zh/report.tex paper/en/report.tex \
  paper/zh/report-zh.pdf paper/en/ControlNumber.pdf \
  paper/shared/methods.tex paper/shared/figures/results.png
```

在双语记录的 `paper_content_manifest` 中登记该清单的项目相对路径与真实 SHA-256。人工核对全部源稿依赖已列入清单后才设 `source_dependencies_verified:true`；此声明不能由文件数量或脚本运行代填。中文与英文主源/PDF分别绑定，中文逐页记录和两版对应检查填真实依据。未决事项仍在 `unresolved`，不能为运行成功清空。

然后运行[双语静态预检](../../mcm-suite/scripts/audit_bilingual_delivery.py)：

```sh
python3 MCM_SKILLS/mcm-suite/scripts/audit_bilingual_delivery.py \
  --root PROJECT --review verification/bilingual_review.json \
  --result-manifest results/run_manifest.json \
  --output verification/bilingual_preflight.json
```

该工具验证两版源稿/PDF、结果与论文资源清单字节、中文实际页数与逐页记录，并调用原英文预检；路径名称可调整。输出最多是 `PRECHECK_PASS`，只说明字节与给定审阅记录满足检查，不证明语言等价、视觉质量、TeX 依赖完备或模型正确，不代替人工复核、结果 PASS 和英文终审。真实可编辑源限当前支持的 `.docx` 或 UTF-8 `.tex`；PDF 本身或改扩展名的 PDF 不能冒充源稿。

`paper/paper_manifest.json` 的既有字段与英文状态保持；在 `files` 中列入两版实际文件，可增加 `language_versions` 分别登记 zh/en 文件与哈希，并登记双语复核文件。`LOCAL_DELIVERY_PASS` 继续说明英文提交链；只有两份完整源稿/PDF、中文页面复核与双语对应检查全部完成，才能向用户报告“中英两版交付完成”。一版缺失或未复核时明确报告该版未完成，不能用英文通过代替整体交付。

## 修改与冻结

中文纯表达/排版修改使中文页面复核和双语对应检查失效；英文相应修改使英文页面复核、双语检查及受影响英文终审失效。未变字节的另一版页面复核无需作废，但一致性需要重新核对变化。模型意义、数字、公式或共同结果变化按影响回到上游，并同步更新两版。

TeX 分文件、共享图表或其他已登记源资源改变会使论文内容清单核验失败；不能因为主源和旧 PDF 未变就沿用完成状态。按影响重新编译/导出、复核相应版本，重新冻结清单并更新对应审阅绑定。即使论文文件字节未变，重新生成内容清单也改变了清单字节，旧双语记录不能自动覆盖新清单；复核后重新绑定。共同资源变化同时核对两版。

正式比赛的两版写作与翻译纳入同一停止工作时间安排。到 `stop_work_at` 后不借“补中文版/翻译”继续改善解答；若中文版尚未完成，按实际缺项交付已冻结产物，保留对整体交付状态的准确说明。

停止时间检查覆盖两版主源、PDF和内容清单内全部源依赖/图资源；停止后改动分文件再重冻清单也不能恢复合规。字节清单及复核报告作为只读核验的记录可在之后生成，不借此重写论文资源。
