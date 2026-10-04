---
name: mcm-final-auditor
description: "整合 MCM A–C 同一冻结版本的结果、英文论文及逐页 PDF 复核，判定本地交付状态并核对提交条件；适用于最终交付或正式上传前。"
---

# MCM 终审与交付

先读[交接合同](../mcm-suite/references/contracts.md)和[年度规则](../mcm-suite/references/official-rules.md)。这是内部终审，不是 COMAP 接收或获奖判定。只审 MCM A–C，训练/复现模式不虚构 Control Number、赛时截止或接收凭证。

使用 [$mcm-modeling-paper-writing](../mcm-modeling-paper-writing/SKILL.md) 的[论证协议](../mcm-modeling-paper-writing/references/narrative-protocol.md)审查同版本论文的意思与证据。历史获奖身份、结构完整、文字流畅或语言静态预检均不判定本稿数学通过。

## 同版本链

- 正式比赛先核对已现场验证的当年 `rules.json` 和实际题面；未确认的专项输出或规则冲突不得默认为满足。核对 `context.json` 真实题号、Control Number 和 live 时间窗。
- 用[冻结工具](../mcm-suite/scripts/freeze_artifacts.py)执行 `verify --root PROJECT --manifest results/run_manifest.json`，核对文件哈希；字节相同不证明结果正确。`verification/result_review.json` 必须 PASS，引用当前冻结 ID/清单哈希，覆盖任务与关键数字的实际验证。
- 核对 `paper/paper_manifest.json` 绑定同一结果清单、复核哈希，源稿/图/PDF 文件存在且哈希一致；论文数字 ID、引用 ID、任务覆盖、实际 AI 使用均可追溯。至少有用户选定的 Word 或 LaTeX 可编辑源与真实最终 PDF，不强制双源。
- `verification/layout_review.json` 必须 PASS，绑定当前 PDF 的 SHA-256，全部必需检查有真实证据，最终 PDF 所有页已经视觉复核。缺证据不能靠补写 true 获得通过。
- 核查布局交接中的语义证据：标题、摘要、图表、结论与专项材料对同一结果的对象、单位、比较、方向和条件一致；主要主张能追到真实任务、模型、结果与实际验证。参数来源、公式名称、指标定义、区间种类、最优性与因果强度不能互相冒充。局限与失败结果必须影响相关建议，而非只存在末尾。

## 最终判断

执行[静态检查](../mcm-suite/scripts/audit_delivery.py)：

```sh
python <mcm-suite>/scripts/audit_delivery.py --root PROJECT --pdf paper/NUMBER.pdf --review verification/layout_review.json --output verification/static_audit.json
```

把 `<mcm-suite>` 替换为入口技能目录真实路径。PRECHECK_PASS 只完成静态预检；人工整合结果/论文/排版同版本链，复核年度页数边界、Summary Sheet、英文、匿名、字号、Control Number、专项材料、AI 披露与文件大小后，才可写 `verification/final_audit.json`。

在 `checks` 单列当前 PDF 的主张—证据与跨段一致性审阅，记录页码、证据文件/位置和实际判断。没有结果或验证时不能补造摘要优点；训练拟合、参数扫描、启发式候选或预测解释不能升级为样本外、随机仿真、全局最优或因果结论。语义上未解决的实质冲突为未完成或失败，并回传相应上游；静态语言/声明链接检查不解除它，也不替代独立数学结果复核。

使用合同状态：已确认违反要求为 FAIL，缺少结果/文件/证据或规则未决为 INCOMPLETE；完整本地证据链成立才为 LOCAL_DELIVERY_PASS。记录 `pdf_sha256`、结果 `manifest_sha256`、每项证据及 `unresolved`，默认 `official_submission:"NOT_SUBMITTED"`。任何相关变化使受影响结论失效，PDF 任意字节改变须重新逐页复核。

## 冻结、交付与上传

`mode=live` 在 `stop_work_at` 后不得修改解答、引用、版式、AI 报告或重新改善提交 PDF；之后的窗口只用于上传已冻结文件。发现缺陷做只读记录并报告，不借“排版修复”继续工作。

交付分成内部复现包（原始副本、合同、源码、结果、日志和审计）与正式上传文件（单一 `ControlNumber.pdf`）。报告准确的本地状态、路径和剩余缺项。只本地保存或生成 PDF 不代表官方已接收。

实际上传须用户明确授权；已有授权有效，不重复询问。先完成可审阅文件和检查，再按当年官方入口提交，核对编号、题号、Advisor ID、AI 声明与 PDF。上传前终审快照保持 NOT_SUBMITTED；实际尝试和后续接收状态另存真实记录与时间。只有网站回执或可核验接收状态才能记录接收结论；若已尝试却未确认，明确报告“上传结果未知”，不能声称已接收或把尝试掩盖为未上传。
