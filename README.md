# MCM Skills

面向 **MCM A、B、C** 的数学建模技能集：中文协作、英文论文，支持 Python 和 MATLAB。模型知识、选型规则、论文行文、模板、原创参考代码与测试均编入本仓库，克隆后不需要作者的原资料目录或工作区。

包含 11 个解题核心技能和 15 个模型、行文支持技能。198 张模型卡覆盖 13 个数学方法家族，逐卡给出适用任务、最低数据、假设、数学定义、算法步骤、Python/MATLAB 实现方向、验证和降级条件。目前 188 张为理论指南，10 张具有限定的参考实现测试证据；这些等级不等于所有变体或真实赛题均已复现。

## 安装

需要 Python 3.11 或更高版本。安装 skill 文件本身仅用 Python 标准库。

```sh
git clone https://github.com/wityu666/MCM-Skills.git
cd MCM-Skills
python3 scripts/install.py --check
python3 scripts/install.py
```

默认安装到 `$CODEX_HOME/skills`，未设置 `CODEX_HOME` 时使用 `~/.codex/skills`。指定其他位置：

```sh
python3 scripts/install.py --destination /path/to/skills
```

安装器一次安装完整 26 模块，复用字节相同的版本，保留已有不同版本和其他技能。安装后在下一轮对话使用 `$mcm-suite`。应整套安装，以保持兄弟技能调用和资源链接完整。

如果要运行本包 Python 参考实现和验证工具：

```sh
python3 -m pip install -r requirements.txt
```

各模型卡另列出相应方法的可选依赖；MATLAB 需要用户自己的运行环境及模型所需工具箱。

## 使用

```text
使用 $mcm-suite 分析这道 MCM C 题，先拆解任务、数据许可和输入输出，
给出 baseline 与候选模型，再落实代码、验证和英文论文。

使用 $mcm-modeling-library 比较季节朴素预测、ARIMA 和灰色预测，
根据我的数据长度与预测目标排除不适用的方法。

使用 $mcm-modeling-paper-writing 改写英文摘要；
只使用我已经提供并复核的模型、数字和结论。
```

检索模型卡也可直接运行：

```sh
python3 skills/mcm-modeling-library/scripts/query_models.py --query "整数规划"
python3 skills/mcm-modeling-library/scripts/query_models.py --id ts-gm1n --full
```

| 阶段 | 技能 |
|---|---|
| 入口、任务与规则 | `mcm-suite`、`mcm-problem-analyst` |
| 方法、数据与模型合同 | `mcm-method-retriever`、`mcm-data-researcher`、`mcm-model-designer` |
| 实现与独立复核 | `mcm-python-coder`、`mcm-matlab-coder`、`mcm-result-verifier` |
| 英文论文与交付 | `mcm-paper-writer`、`mcm-layout-verifier`、`mcm-final-auditor` |
| 模型与行文支持 | `mcm-modeling-library`、13 个 `mcm-modeling-*` 方法家族、`mcm-modeling-paper-writing` |

具体模型定义保存在各家族的 `references/cards.json` 和补充卡中；完整检索目录位于 `skills/mcm-modeling-library/assets/catalog.json`。所有引用使用仓库内相对路径或公开科学来源 URL。

## 验证

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
python3 scripts/run_tests.py
python3 scripts/check_fresh_install.py
```

本轮 Python 3.13 环境实际通过 183 项测试，并完成全新 `CODEX_HOME` 下的安装与全部文件回读。CI 配置覆盖 Python 3.11 和 3.13；远程 CI 的状态以 GitHub Actions 实际运行记录为准。MATLAB 源码保留静态审查范围，本轮未重新运行 MATLAB。

来源记录是资料名称、内容哈希和静态发现的摘要，不是必需外部文件。历史测试摘要明确保留其历史范围；当前发布验证使用本仓库的实际命令和相对资源。仓库不附第三方教材、原始优秀论文、商业源码包或个人机器目录。

当届规则、题面数据许可、AI 披露和提交要求仍由当前 MCM 任务核验。模型卡与合成例子提供方法知识，实际论文结论使用本题数据及有效复核结果。

## 许可

本仓库原创代码和技能说明采用 MIT License。引用的论文、官方文档和其他外部来源保留各自权利，来源摘要不授予其全文或第三方程序的再分发权。
