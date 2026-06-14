# OfferPilot AI Skill Pack

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot Skill Pack 是一套面向求职场景的 AI 工作流规则层，用来帮助候选人基于真实经历完成简历诊断、简历优化、JD 匹配、定向改写、结构化评估、面试准备、产品研究、申请追踪和外联消息生成。

它的底线很简单：**只使用你的真实经历，不编项目、不编数据、不编联系方式。**

[English](./README_en.md)

## 当前分支定位

这个分支是 [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill)。主入口是 `skill-pack/`，适合在 Cursor、Claude Code、Codex 等 AI 编程工具中作为 repo-local skill 或工作流文档使用。

这个分支不是可运行 Agent 产品分支：

- 没有 `offerpilot-agent` 自然语言入口。
- 没有 LangGraph runtime。
- 没有 FastAPI/Next.js Web UI。
- 保留了 `offerpilot` helper CLI，用来直接调用 `skill-pack/scripts/` 下的确定性脚本。

如果你想运行 LangGraph Agent、Web UI 或自然语言 CLI，请切换到 [`offerpilot-agent`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) 分支。

可以这样理解：

```text
skill-pack = 规则层 / 方法论 / 可移植工作流
agent      = skill-pack + runtime + tools + UI
```

## 核心原则

- 原始简历和 `profile_store.yaml` 是事实来源。
- 生成内容只能重写、筛选、组织真实经历，不能编造项目、公司、指标、学历或联系方式。
- Markdown 内容应先人工 review，再导出 PDF 或用于投递。
- 所有本地隐私数据默认不提交到 git。

## 能做什么

| 能力 | Skill Pack 中的来源 |
|---|---|
| 简历诊断 | `skill-pack/RESUME_DIAGNOSIS.md` |
| 简历优化和定向改写 | `skill-pack/WORKFLOW.md`、`skill-pack/PROMPTS.md`、`skill-pack/DATASTORE.md` |
| JD 匹配分析 | `skill-pack/JD_MATCHING.md` |
| 结构化评估和批量评估 | `skill-pack/EVALUATION.md` |
| 求职信 | `skill-pack/PROMPTS.md` |
| LinkedIn 外联 | `skill-pack/OUTREACH.md` |
| 模拟面试 | `skill-pack/MOCK_INTERVIEW.md` |
| 产品研究 | `skill-pack/PRODUCT_RESEARCH.md` |
| 申请追踪和 follow-up | `skill-pack/TRACKER.md` |
| 岗位扫描和推荐 | `skill-pack/scripts/scan_portals.py`、`skill-pack/scripts/run_pipeline.py` |
| PDF 辅助 | `skill-pack/scripts/render_pdf.py` |

注意：这个分支本身不提供 LLM 聊天 runtime。它定义规则和辅助脚本，由外部 agent 或 `offerpilot-agent` 分支负责执行复杂推理和对话。

## 快速开始

如果你要单独使用这个分支：

```bash
git clone -b offerpilot-skill https://github.com/kalimosd/OfferPilot.git offerpilot-skill
cd offerpilot-skill
```

如果你的 AI 编程工具支持 repo-local skills，优先打开对应 adapter：

- `skill-pack/adapters/codex/SKILL.md`
- `skill-pack/adapters/claude-code/SKILL.md`
- `skill-pack/adapters/cursor/SKILL.md`

否则按下面顺序阅读：

1. `skill-pack/README.md`
2. `skill-pack/WORKFLOW.md`
3. `skill-pack/INPUTS.md`
4. 简历诊断阅读 `skill-pack/RESUME_DIAGNOSIS.md`
5. 国内岗位匹配任务阅读 `skill-pack/JD_MATCHING.md`
6. 结构化评估阅读 `skill-pack/EVALUATION.md`
7. 模拟面试阅读 `skill-pack/MOCK_INTERVIEW.md`
8. 产品研究阅读 `skill-pack/PRODUCT_RESEARCH.md`
9. 申请追踪阅读 `skill-pack/TRACKER.md`
10. 外联消息阅读 `skill-pack/OUTREACH.md`
11. 需要本地脚本时阅读 `skill-pack/scripts/README.md`

## 可选脚本安装

只阅读和使用 Skill Pack 文档不需要安装依赖。需要提取文本、渲染 PDF、扫描岗位或运行校验脚本时，安装 Python helper：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m playwright install chromium
```

这个分支不需要 Node.js，也不需要 Web UI 依赖。

## Profile Datastore

推荐使用 `profile_store.yaml` 维护完整个人素材库。它不是简历成品，而是事实数据库。

可以从模板开始：

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

主要字段：

| 字段 | 说明 |
|---|---|
| `meta` | 姓名、英文名、出生年份、邮箱、电话、更新时间 |
| `experience` | 工作经历，每段经历包含多个 bullet |
| `projects` | 项目经历、开源、比赛、校园项目等 |
| `skills` | 技能、熟练度、使用年限、证据 |
| `education` | 教育背景 |
| `certifications` | 证书 |
| `achievements` | 奖项或荣誉 |

建议把经历写全，不要一开始就压缩。Skill Pack 会根据 JD 选择最相关的部分。

`profile_store.yaml`、`jds/`、`outputs/`、`data/` 都是本地私有数据，默认不应该提交到 git。

## Helper CLI

`offerpilot` 是可选 helper CLI，用来执行确定性脚本。它不是自然语言 Agent。

```bash
offerpilot --help
offerpilot extract sample_resume.docx --output sample_resume.txt
offerpilot pdf outputs/resumes/resume.md outputs/resumes/resume.pdf --style standard_cn
offerpilot validate-inputs profile_store.yaml jds/example.md
offerpilot validate-profile profile_store.yaml
offerpilot validate-aliases
offerpilot scan --cn-only --dry-run
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

也可以直接调用脚本：

```bash
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md
python skill-pack/scripts/extract_text.py resume.pdf
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md
python skill-pack/scripts/validate_profile_store.py profile_store.yaml
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
python skill-pack/scripts/run_pipeline.py --days 7 --top-n 10 --cn-focus
```

## 输出目录约定

所有输出放在 `outputs/` 下的对应子目录：

| 目录 | 内容 |
|---|---|
| `outputs/resumes/` | 简历诊断、简历优化、定向改写、JD 匹配、结构化评估、批量评估 |
| `outputs/research/` | 产品研究 |
| `outputs/interview/` | 面试题单、面试评估、面试准备 |
| `outputs/pipeline/` | 岗位扫描和推荐报告 |
| `outputs/misc/` | 外联消息、项目讲解、其他材料 |

不要直接把正式输出放在 `outputs/` 根目录。

## Skill Pack 结构

```text
skill-pack/
├── README.md              # Skill Pack 入口
├── WORKFLOW.md            # 通用任务流程
├── INPUTS.md              # 输入选择和隐私规则
├── OUTPUTS.md             # 输出格式和质量检查
├── PROMPTS.md             # 生成约束和可复用提示词
├── DATASTORE.md           # profile_store.yaml 数据结构说明
├── JD_MATCHING.md         # JD 匹配分析
├── RESUME_DIAGNOSIS.md    # 不依赖 JD 的简历诊断
├── EVALUATION.md          # 10 维结构化岗位评估
├── MOCK_INTERVIEW.md      # 模拟面试
├── PRODUCT_RESEARCH.md    # 产品研究
├── TRACKER.md             # 申请状态追踪
├── OUTREACH.md            # LinkedIn 外联
├── templates/             # 本地模板
├── data/                  # 技能别名等辅助数据
├── schemas/               # profile_store 和 skill aliases 的 JSON Schema
├── examples/              # 示例
├── scripts/               # 本地辅助脚本
└── adapters/              # Cursor / Claude Code / Codex 适配器
```

根目录还保留一个很小的 `offerpilot/` Python 包，只用于 helper CLI。它不是本分支的主要产品界面。

## 开发和验证

运行测试：

```bash
source .venv/bin/activate
python -m pytest
```

常用脚本校验：

```bash
python skill-pack/scripts/validate_inputs.py sample_resume.md sample_job.md
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
```

`skill-pack/templates/profile_store.yaml` 是空模板，直接运行 `validate_profile_store.py` 会提示必填字段缺失，这是预期行为。请复制成 `profile_store.yaml` 并填入真实内容后再校验。

## Troubleshooting

| 问题 | 处理 |
|---|---|
| `offerpilot-agent` 不存在 | 这是 skill 分支。需要自然语言 Agent 时切到 `offerpilot-agent` |
| Web UI 文件不完整或无法启动 | 这是预期行为。Web UI 只属于 `offerpilot-agent` |
| `ModuleNotFoundError` | 先执行 `source .venv/bin/activate`，再 `pip install -e .` |
| PDF 渲染失败 | 执行 `python -m playwright install chromium` |
| 模板校验报必填字段缺失 | 模板是空表单，不是有效个人数据；复制并填充后再校验 |
| 产品研究需要最新信息 | 这个分支不提供联网 runtime；请提供来源材料，或在有浏览能力的 agent 中使用 Skill Pack |

## 与 Agent 分支的关系

OfferPilot 有两种形态：

| 分支 | 定位 |
|---|---|
| [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) | Skill Pack，负责规则、流程、模板、脚本和方法论 |
| [`offerpilot-agent`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) | Runnable Agent，负责 LangGraph runtime、自然语言 CLI、Web UI 和自动化执行 |

维护建议：

- workflow 文档、输出规范、prompt 约束、schema、模板、skill alias、adapter 和脚本优先进入 `offerpilot-skill`。
- LangGraph runtime、Agent 工具、Web API、前端和用户可运行体验进入 `offerpilot-agent`。
- skill 分支改动同步到 agent 分支后，检查 `docs/AGENT_SYNC_CHECKLIST.md`，确认 `offerpilot/graph.py` 的 `SYSTEM_PROMPT` 是否需要同步。

## License

MIT
