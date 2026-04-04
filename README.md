# OfferPilot

OfferPilot 是一个开源的 AI skill pack，用于简历诊断、简历优化、面向岗位的简历改写，以及求职信工作流。

这个仓库围绕可复用的工作流文档、提示词规则、agent 适配器和少量辅助脚本组织，方便其他人下载后，在不同的仓库型 AI agent 中复用同一套技能。

## 适合谁用

OfferPilot 适合下面这几类使用场景：

- 想把本地简历和岗位描述交给 AI agent 做定向改写的人
- 想把“简历诊断 / 简历优化 / 定向简历 / 求职信”能力封装成 repository-local skill 的人
- 想在本地保留原始材料、只把结构化文本交给模型处理的人

它更偏向“本地文件 + agent 工作流 + 可复用规则”的使用方式，而不是在线 SaaS 或复杂模板编辑器。

## 仓库提供的内容

- 位于 `skill-pack/` 下的平台无关 skill pack
- 面向简历诊断、简历优化、定向简历改写和求职信生成的工作流指导
- 面向多语言求职材料的提示词规则
- 适配 Cursor、Codex 风格 agent 和 Claude Code 风格 agent 的适配器
- 用于文本提取、输入校验和输出检查的辅助脚本
- 暂时保留、仅作为兼容层存在的旧版 Python CLI

## 快速上手

如果你想把 OfferPilot 当作通用 skill pack 使用，最短路径是：

1. 准备原始简历文件，以及可选的岗位描述文件
2. 阅读 `skill-pack/README.md`
3. 按照 `skill-pack/WORKFLOW.md` 执行
4. 查看 `skill-pack/INPUTS.md`、`skill-pack/OUTPUTS.md` 和 `skill-pack/PROMPTS.md`
5. 在 `skill-pack/adapters/` 下选择适合你所用 AI agent 的适配器
6. 如果 agent 不能可靠读取 `.pdf` 或 `.docx`，先运行 `python3 skill-pack/scripts/extract_text.py "path/to/file"`
7. 仅在确实需要校验时，再运行 `skill-pack/scripts/` 下的可选脚本

## 从这里开始

更完整的读取顺序如下：

1. 阅读 `skill-pack/README.md`
2. 按照 `skill-pack/WORKFLOW.md` 执行
3. 查看 `skill-pack/INPUTS.md`、`skill-pack/OUTPUTS.md` 和 `skill-pack/PROMPTS.md`
4. 在 `skill-pack/adapters/` 下选择适合你所用 AI agent 的适配器
5. 如果 agent 不能可靠读取 `.pdf` 或 `.docx`，先运行 `python3 skill-pack/scripts/extract_text.py "path/to/file"`
6. 仅在确实需要校验时，再运行 `skill-pack/scripts/` 下的可选脚本

## 典型工作流

一个典型的“定向简历改写”流程如下：

1. 准备原始简历，例如 `resume.pdf`、`resume.docx` 或 `resume.md`
2. 准备岗位描述，例如 `job.md` 或直接粘贴 JD 文本
3. 如果输入是 `.pdf` 或 `.docx` 且 agent 不能稳定读取，运行 `python3 skill-pack/scripts/extract_text.py "resume.pdf"`
4. 使用 `skill-pack/WORKFLOW.md` 分类任务为 `job-targeted resume rewrite`
5. 按 `skill-pack/PROMPTS.md` 的约束生成 Markdown 版定向简历
6. 按 `skill-pack/OUTPUTS.md` 检查名称、日期、职位、语言和事实一致性
7. 如需最终交付，再导出为 PDF

你也可以只停留在 Markdown 这一步。对很多求职场景来说，先人工 review Markdown，再决定是否导出 PDF，通常更稳妥。

如果你还不确定要不要直接改写，可以先做“简历诊断”：

1. 用原始简历生成一份诊断报告
2. 查看当前优势、缺口、风险和建议修改项
3. 再决定是做通用优化还是针对某个 JD 改写

## 仓库结构

```text
.
├── README.md
├── LICENSE
├── pyproject.toml
├── sample_resume.md
├── sample_resume.docx
├── sample_job.md
├── sample_job.docx
├── docs/
│   └── migration.md
├── skill-pack/
│   ├── README.md
│   ├── WORKFLOW.md
│   ├── INPUTS.md
│   ├── OUTPUTS.md
│   ├── PROMPTS.md
│   ├── adapters/
│   │   ├── claude-code/
│   │   ├── codex/
│   │   └── cursor/
│   ├── examples/
│   │   ├── cover-letter.md
│   │   ├── resume-optimization.md
│   │   └── targeted-resume.md
│   └── scripts/
│       ├── extract_text.py
│       ├── validate_inputs.py
│       └── validate_outputs.py
├── offerpilot/
│   ├── cli.py
│   ├── config.py
│   ├── cover.py
│   ├── export.py
│   ├── io.py
│   ├── llm.py
│   └── resume.py
└── tests/
    ├── test_cover.py
    ├── test_export.py
    ├── test_io.py
    ├── test_llm.py
    └── test_resume.py
```

## 核心原则

- 原始简历是事实来源
- 生成结果是草稿，不是事实本身
- 不要编造经历、指标或证书
- 默认不要把私密简历文件加入版本控制
- 中文姓名在英文场景下应采用 `Given Name + Family Name`

私有文件处理建议：

- 对个人简历、职位描述或导出结果，优先使用本地 `.git/info/exclude` 做忽略
- 不要把带有真实姓名或其他敏感信息的具体文件名写入版本化的 `.gitignore`

示例：

- `中文名` -> `<Given Name> <Family Name>`

## 支持的输入类型

- `.txt`
- `.md`
- `.pdf`
- `.docx`

不支持旧式 `.doc` 文件。

## 兼容的 Agent

OfferPilot 主要面向仓库本地运行的 AI agent，包括：

- Cursor
- Codex 风格的本地仓库 agent
- Claude Code 风格的本地仓库 agent

核心工作流文档按“即使 agent 不能执行本地脚本也仍然可用”的原则编写。

## PDF 导出说明

当前仓库中的 PDF 导出优先使用 `HTML/CSS + Chromium` 浏览器渲染，而不是只依赖传统的 ReportLab 文本绘制。

这样做的主要原因是：

- 改善中文、英文、数字混排时的字体 fallback
- 改善英文和数字在简历中的 kerning 与可读性
- 让标题、列表、段落和不同 style 变体更容易通过 CSS 调整

如果你需要在本地使用这条 PDF 导出链路：

1. 安装项目依赖
2. 运行 `playwright install chromium`

在 Chromium 不可用时，仓库中仍暂时保留 ReportLab fallback 作为兼容兜底。

## 旧版 CLI

`offerpilot/` 下的 Python 包和 `offerpilot` 命令目前仍然保留，用作从 CLI-first 形态迁移过程中的兼容层。

如果你需要旧的执行路径，可以查看：

- `offerpilot/cli.py`
- `pyproject.toml`

这个旧版兼容层已经不再是项目的主要产品入口。

## 项目状态

这个仓库当前的主入口是 `skill-pack/`。

- 如果你想直接复用能力，优先从 `skill-pack/` 开始
- 如果你想看兼容层实现或本地 CLI 入口，再看 `offerpilot/`
- `offerpilot/` 和 `tests/` 目前仍保留，主要用于兼容与验证，不再代表项目的核心产品形态

## 示例文件

- `sample_resume.md`
- `sample_job.md`

## 项目范围

OfferPilot 聚焦于求职材料相关场景：

- 简历诊断
- 通用简历优化
- 面向岗位的简历改写
- 求职信生成
- 多语言输出指导
- 面向 agent 的可复用工作流封装
