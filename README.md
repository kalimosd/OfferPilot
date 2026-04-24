<div align="center">

# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

**AI 求职助手，把弱申请变成面试敲门砖。**

丢进简历和 JD，拿回一份更强的简历、一份定向改写、一份匹配度分析、或一封求职信 — 基于你的真实经历，不编不造。

[功能](#功能) · [快速开始](#快速开始) · [Agent 模式](#agent-模式) · [效果示例](#效果示例) · [项目结构](#项目结构) · [路线图](#路线图)

[English](./README_en.md)

</div>

---

## 功能

| 功能 | 说明 |
|------|------|
| **简历优化** | 精炼措辞、去除水分、强化 bullet point — 不编造事实 |
| **定向简历改写** | 围绕目标 JD 重写和重排内容 |
| **JD 匹配度分析** | 识别匹配信号、差距和改写优先级 |
| **结构化评估** | 10 维度打分 + A-F 等级，量化岗位匹配度 |
| **求职信生成** | 基于真实经历生成简洁、有针对性的求职信 |
| **Profile 素材库** | 从结构化 YAML 素材库中选取最相关的经历组装简历 |
| **职位发现** | 自动扫描招聘网站（美团/快手/滴滴 + Greenhouse + DuckDuckGo），发现匹配岗位 |
| **申请追踪** | 管理申请状态（discovered → applied → interviewing → offer/rejected），自动提醒跟进 |
| **批量评估** | 一次评估多个 JD，快速筛选值得投递的岗位 |
| **模拟面试** | 基于 JD 和个人经历生成面试题单，对话模拟并输出评估报告 |
| **产品研究** | 调研目标产品，输出产品介绍、竞品分析、面试预测和准备清单 |
| **LinkedIn 外联** | 生成针对目标公司的 LinkedIn outreach 消息 |
| **PDF 导出** | Markdown → 带样式 PDF，支持嵌入照片 |

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/kalimosd/offerpilot-ai.git
cd offerpilot-ai
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. 配置 LLM（支持 DeepSeek / Claude / Gemini / OpenAI）
cp .env.example .env
# 编辑 .env，填入 API key

# 3. 运行 Agent
python -m offerpilot.agent "帮我优化简历，简历在 profile_store.yaml"
```

## Agent 模式

OfferPilot Agent 基于 **LangGraph** 构建，支持自然语言输入，自动分类任务、调用工具、生成输出。

### 支持的 LLM

通过环境变量切换，无需改代码：

```bash
# DeepSeek（默认）
OFFERPILOT_MODEL=deepseek-chat
OFFERPILOT_API_KEY=your-key
OFFERPILOT_BASE_URL=https://api.deepseek.com

# Claude
OFFERPILOT_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=your-key

# Gemini
OFFERPILOT_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-key

# OpenAI
OFFERPILOT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-key
```

### 使用示例

```bash
# 单次模式 — 跑完即退出
python -m offerpilot.agent "帮我分析 jds/美团-AI_Agent工程师.md 和 profile_store.yaml 的匹配度"
python -m offerpilot.agent "批量评估 jds 目录下所有美团的 JD"
python -m offerpilot.agent "运行 pipeline，扫描最近 7 天的岗位，推荐 Top 10"
python -m offerpilot.agent "查看我的申请状态，有哪些需要跟进"
python -m offerpilot.agent "帮我写一封给 Anthropic 的 LinkedIn 外联消息"

# 多轮交互模式
python -m offerpilot.agent
> 帮我优化简历
> 再针对这个 JD 做定向改写
> 导出 PDF
> exit
```

### Agent 工具链（12 个工具）

| 工具 | 说明 |
|------|------|
| `read_file` / `write_file` | 读写文件 |
| `extract_text` | 从 PDF/DOCX 提取文本 |
| `render_pdf` | Markdown → PDF |
| `list_files` | 列出目录 |
| `scan_portals` | 扫描招聘网站 |
| `run_pipeline` | 端到端 pipeline（扫描→排序→推荐） |
| `tracker_add` / `tracker_update` / `tracker_query` | 申请状态追踪 |
| `check_followups` | 跟进提醒（applied>7天 / interviewing>5天） |
| `batch_evaluate` | 批量评估多个 JD |

Agent 通过 LangGraph ReAct 循环自动调度这些工具，不需要手动指定。

## Skill Pack 模式

除了独立 Agent，OfferPilot 也可以作为 AI 编辑器的 skill pack 使用：

1. 打开 `skill-pack/README.md` 按 read order 执行
2. 在 Claude Code / Cursor / Codex / Kiro 中使用触发语：
   - `按照 offerpilot 优化简历`
   - `用 offerpilot 做 JD 匹配`
   - `用 offerpilot 模拟面试这个岗位`

## 效果示例

**优化前**

```text
- 负责 Android 开发，和不同团队合作。
- 帮忙修 bug，提升 app 性能。
```

**优化后**

```text
- 使用 Perfetto 和 Systrace 诊断渲染、内存和 ANR 问题，推动跨平台团队修复，
  提升 Android 系统稳定性和性能。
- 负责最近任务功能的交付，协调工程干系人按期上线，加速跨团队问题闭环。
```

## 技术栈

- **Agent 框架**：LangGraph（状态图 + ReAct）+ LangChain（tool calling、多 provider 适配）
- **LLM**：DeepSeek / Claude / Gemini / OpenAI（环境变量切换）
- **PDF 导出 & 网页扫描**：Playwright
- **数据格式**：YAML（profile 素材库）、TSV（tracker、扫描历史）
- **Skill Pack**：模块化 Markdown 文档，适配多种 AI 编辑器

## 项目结构

```text
.
├── offerpilot/
│   ├── agent.py            # CLI 入口（单次 + 多轮交互）
│   ├── graph.py            # LangGraph 图定义 + system prompt
│   ├── tools.py            # 12 个 agent 工具
│   ├── llm.py              # 多 provider LLM 初始化
│   ├── state.py            # 图状态定义
│   └── cli.py              # 可选 CLI 辅助命令
├── skill-pack/
│   ├── WORKFLOW.md          # 任务流程和检查点
│   ├── DATASTORE.md         # 素材库规范
│   ├── JD_MATCHING.md       # JD 匹配分析规范
│   ├── MOCK_INTERVIEW.md    # 模拟面试流程
│   ├── PRODUCT_RESEARCH.md  # 产品研究流程
│   ├── OUTPUTS.md / PROMPTS.md / INPUTS.md
│   ├── scripts/             # 提取、渲染、扫描、校验脚本
│   └── adapters/            # Claude Code / Codex / Cursor 适配器
├── outputs/
│   ├── resumes/             # 简历、定向改写、JD 匹配分析
│   ├── research/            # 产品研究
│   ├── interview/           # 面试题单、面试评估
│   ├── pipeline/            # 扫描推荐报告
│   └── misc/                # 其他
├── profile_store.yaml       # 个人素材库（不入 git）
├── jds/                     # 扫描保存的 JD（不入 git）
├── data/                    # 扫描历史、tracker（不入 git）
└── tests/
```

## 路线图

- [ ] 基于 RAG 的简历知识系统
- [ ] Agent 驱动的自动投递工作流
- [ ] 简历版本管理和 A/B 测试
- [ ] Web UI

## 参与贡献

欢迎反馈、提 issue 和 PR。

## 写在最后

工作很重要。离开学校以后，它不声不响地占据了你醒着的大部分时间，这没什么好争的。

但工作又没那么重要。人不是为了优化 bullet point 而来到这个世界上的。

你做过真实的事。你解决过真实的问题。你加过班、赶过 deadline、替别人擦过屁股，但没人好好写下来 — 你自己也没有。

这个项目改变不了你的人生。但如果它能帮一个人不再低估自己，不再把同一份万能简历投进黑洞，真正拿到一个配得上的面试机会 —

那就够了。

去拿 offer 吧。然后合上电脑，好好生活。
