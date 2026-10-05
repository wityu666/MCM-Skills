---
name: mcm-layout-verifier
description: "复核 MCM A–C 最终英文 PDF 的实际渲染、页数、匿名、字体、引用和任务覆盖，把逐页证据绑定到该 PDF；适用于初次成稿和任何重新导出后。"
---

# MCM 最终 PDF 排版复核

先读[交接合同](../mcm-suite/references/contracts.md)和[年度规则](../mcm-suite/references/official-rules.md)。检查项目真实的 `rules.json`、题面、`paper/paper_manifest.json`、可编辑源与最终 `paper/NUMBER.pdf`，不能以源稿或旧预览替代最终文件。

英文与论证复核按 [$mcm-modeling-paper-writing](../mcm-modeling-paper-writing/SKILL.md) 的[论证协议](../mcm-modeling-paper-writing/references/narrative-protocol.md)。版面可读和语言流畅不证明数学正确；语义检查查当前 PDF 实际呈现的意思及其证据承接。

完整用户交付默认另有中文 PDF。依[双语约定](../mcm-paper-writer/references/bilingual-delivery.md)逐页检查中文版的完整性、中文字体/图表可读性，并审阅两版的结构、模型、数字、公式和结论对应；证据记录在独立双语复核中。下述 `layout_review.json`、`english_verified` 及官方页数检查继续用于英文提交版，不把中文稿伪标成英文通过；两版页数无需相同。

## 检查与证据

1. 计算最终 PDF 的 SHA-256，核对论文清单绑定的结果版本和 PDF 字节。复制[检查表模板](assets/layout-review.json)到 `verification/layout_review.json`；所有检查默认 false，只在实际证据成立后改为 true；`ai_used` 依真实日志与论文清单填写，不能把 null 默认为未使用。训练未分配 Control Number 时该页眉检查注明不适用，不虚构编号。
2. 使用可用 PDF 技能/渲染器将最终 PDF **全部页面**渲染为图像并逐页查看。记录渲染命令、时间、页数、图像路径和每页审阅结论，所有证据绑定 `pdf_sha256`。缩略图浏览和文本抽取可辅助，不能代替逐页检查。缺少渲染工具或未看完时为 INCOMPLETE。
3. 按年度规则核验总页数与主解答页数，记录 AI 报告第一物理页（从 1 开始，无报告为 null）。Summary Sheet 必须是第一页且只有一页；主解答包含目录、参考文献、附录、代码和题面专项材料。仅真实 AI 报告可排除，混入普通解答/图表时不能按 AI 页豁免。最多页数不要求写满。
4. 实查英文、最低字号、各页顶部 Control Number/页码、段落表格断裂、公式/图表截断、图注单位、可读性和空白页。字体核验结合 PDF 字体/文字信息与视觉；不能从源稿设置推断最终字号。
5. 匿名检查覆盖文字抽取、逐页图像、嵌图文字、超链接、源稿作者属性和 PDF 元数据。检查引用可定位、数字与图表和论文清单一致、题目 `tasks` 及专项输出覆盖；核查 AI 报告与实际日志、正文/参考文献披露相符。无法检查的部分保持 false 并写入 `unresolved`。
6. 对照标题、Summary Sheet、正文结果、图表、结论及 memo/letter 的对象、符号、单位、比较基准、数值方向与限定语。实读重要段落：方法选择有结构/数据理由，公式与模型名一致，图表正文解释所支持的判断，局限确实限制相关建议。保留训练/预测、可行/最优、关联/因果、敏感性/稳健性和各类区间的区别；分页、删图或缩写不能使条件丢失或结论变强。
7. 在 `evidence` 记录语义检查涉及的 PDF 页、段落/图表、上游证据位置、当前哈希及判断。语言识别、句长或关键词扫描只定位候选问题；缺支持不能通过删除措辞隐藏。数学含义或数字冲突交回模型/结果复核，纯表达或版面问题交回论文模块；不能把排版/语言检查写成结果 PASS。
8. 正式比赛对照[用户默认结构](../mcm-paper-writer/references/user-preferred-structure.md)检查章节顺序、实际题数、每个模型任务的四步功能，以及误差/敏感性、评价/推广和结论的分工。核对标题级别、连续编号、正文与自动目录页码一致；存在有理由的结构调整时检查交接映射。清除旧样例年份/控制号/页码和编辑提示。结构符合不代替数学与最终页面检查。

## 状态与交接

`layout_review.json` 使用合同字段：实际失败为 FAIL，证据不足为 INCOMPLETE，PDF 哈希或相关版本改变为 STALE。只有全部必需检查实际完成且无阻断项才写 PASS；`evidence` 含可复核的检查方法、证据路径、页码和结论，不能只写“已检查”。

运行[静态检查器](../mcm-suite/scripts/audit_delivery.py)：

```sh
python <mcm-suite>/scripts/audit_delivery.py --root PROJECT --pdf paper/NUMBER.pdf --review verification/layout_review.json --output verification/static_audit.json
```

其中 `<mcm-suite>` 替换为本套件入口技能目录的真实路径。脚本最多返回 PRECHECK_PASS，不能自动证明逐页视觉检查或最终可交付。把最终 PDF、论文清单、逐页证据、`layout_review.json` 和静态结果交给 `$mcm-final-auditor`。

修复交回论文模块，重新导出后所有旧 PDF 证据失效，须重做当前文件检查。`mode=live` 到停止工作时间后不修改文件以修复排版，只做只读审核并如实报告缺陷。
