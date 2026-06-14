# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot 是一个本地优先的 AI 求职助手，用来把真实经历整理成更强的简历、JD 匹配分析、定向改写、岗位推荐、申请追踪和面试准备材料。

它的底线很简单：**只使用你的真实经历，不编项目、不编数据、不编联系方式。**

[English](./README_en.md)

![OfferPilot Web UI](docs/web-ui-screenshot.png)

## 当前分支定位

这个分支是 `offerpilot-agent`。它是可运行产品分支，包含：

- **Agent CLI**：主入口。用自然语言描述任务，LangGraph Agent 自动判断流程并调用工具。
- **Web UI**：本地可视化界面，包含 Chat、Tracker、Outputs。
- **Skill Pack**：可移植规则层，给 Cursor、Claude Code、Codex 等 AI 编程工具使用。
- **Helper CLI**：`offerpilot` 命令，直接调用提取、渲染、校验、扫描和 pipeline 脚本。

可以这样理解：

```text
skill-pack = 规则层 / 方法论 / 可移植工作流
agent      = skill-pack + runtime + tools + UI
```

如果你只想使用纯 Skill Pack 规则层，请看 [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) 分支。两个分支共享规则和脚本，但职责不同：skill 分支维护方法论，agent 分支维护可运行体验。

## 能力和实现方式

| 能力 | 当前实现 |
|---|---|
| 简历诊断、简历优化、定向改写、JD 匹配、求职信 | 通用 Agent + Skill Pack 规则 + 文件/PDF 工具 |
| 结构化评估 | 通用 Agent 按 10 维评分规则生成；批量评估有专门流程 |
| 批量 JD 评估 | LangGraph 专门分支，低温度 LLM 逐个评分并排序 |
| 岗位扫描和推荐 | LangGraph pipeline 分支，调用 `skill-pack/scripts/run_pipeline.py` |
| 申请追踪和 follow-up | Agent 工具和 Web Tracker 读写 `data/tracker.tsv` |
| 外联消息、模拟面试、产品研究 | Skill Pack 规则驱动的通用 Agent 工作流 |
| PDF 导出 | Playwright Chromium 渲染 Markdown 到 PDF |

注意：当前 Agent 没有内置通用联网搜索工具。岗位扫描使用已有脚本；产品研究等任务如果需要最新网页信息，应提供来源材料，或在支持联网/浏览器能力的外部 agent 中使用 Skill Pack。

## 环境要求

- Python 3.10+
- Node.js 18+，仅 Web UI 需要
- 至少一个 LLM API key，例如 DeepSeek、Claude、Gemini 或 OpenAI
- Playwright Chromium，用于 PDF 渲染和部分网页扫描能力

## 安装

```bash
git clone -b offerpilot-agent https://github.com/kalimosd/OfferPilot.git offerpilot-ai
cd offerpilot-ai

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
python -m playwright install chromium
```

如果只跑 Agent，不跑测试，可以用：

```bash
pip install -e .
```

## 配置 LLM

在项目根目录创建 `.env`：

```bash
touch .env
```

然后按你使用的模型填写其中一种配置。

| 变量 | 说明 |
|---|---|
| `OFFERPILOT_MODEL` | 模型名，默认 `deepseek-chat` |
| `OFFERPILOT_API_KEY` | OpenAI-compatible provider 的 API key，例如 DeepSeek |
| `OFFERPILOT_BASE_URL` | OpenAI-compatible provider 的 base URL |
| `OFFERPILOT_TEMPERATURE` | 可选，覆盖默认温度 |
| `ANTHROPIC_API_KEY` | Claude 原生 provider 使用 |
| `GOOGLE_API_KEY` | Gemini 原生 provider 使用 |
| `OPENAI_API_KEY` | OpenAI 原生 provider 使用 |

### DeepSeek

```bash
OFFERPILOT_MODEL=deepseek-chat
OFFERPILOT_API_KEY=your-deepseek-key
OFFERPILOT_BASE_URL=https://api.deepseek.com
```

### Claude

```bash
OFFERPILOT_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=your-anthropic-key
```

### Gemini

```bash
OFFERPILOT_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-google-key
```

### OpenAI

```bash
OFFERPILOT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-key
```

当前 runtime 显式使用两档温度：普通 Agent 任务默认 `0.3`，批量 JD 评估使用 `0.1`。代码中保留了 `CREATIVE_TEMPERATURE = 0.7` 常量，但当前图不会按任务自动切换到这档温度。

## 准备个人资料和 JD

先创建个人素材库：

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

`profile_store.yaml` 不是最终简历，而是事实数据库。建议把经历写全，不要一开始就压缩。

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

把 JD 放到 `jds/`：

```bash
mkdir -p jds outputs/resumes outputs/pipeline outputs/interview outputs/research outputs/misc
```

示例结构：

```text
jds/
  anthropic-ai-agent-engineer.md
  meituan-algorithm-engineer.md
```

`profile_store.yaml`、`jds/`、`outputs/`、`data/` 都是本地私有数据，默认不应该提交到 git。

## 运行 Agent

单次模式：

```bash
python -m offerpilot.agent "分析 jds/anthropic-ai-agent-engineer.md 和 profile_store.yaml 的匹配度"
python -m offerpilot.agent "批量评估 jds/ 目录下所有 JD"
python -m offerpilot.agent "运行 pipeline，扫描最近 7 天的岗位，推荐 Top 10"
python -m offerpilot.agent "查看有哪些申请需要跟进"
```

多轮交互模式：

```bash
python -m offerpilot.agent
```

进入后可以输入：

```text
帮我优化 profile_store.yaml 里的简历素材
针对 jds/anthropic-ai-agent-engineer.md 做定向改写
把最新简历导出成 PDF
exit
```

也可以使用安装后的命令：

```bash
offerpilot-agent "批量评估 jds/ 目录下所有 JD"
```

## Helper CLI

`offerpilot-agent` 是自然语言 Agent；`offerpilot` 是脚本型 helper CLI。后者适合直接做确定性操作：

```bash
offerpilot --help
offerpilot extract sample_resume.docx --output sample_resume.txt
offerpilot pdf outputs/resumes/resume.md outputs/resumes/resume.pdf --style standard_cn
offerpilot validate-inputs profile_store.yaml jds/example.md
offerpilot validate-profile profile_store.yaml
offerpilot validate-aliases
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

`python -m offerpilot` 等价于 helper CLI；自然语言 Agent 请使用 `python -m offerpilot.agent` 或 `offerpilot-agent`。

## Web UI

Web UI 使用 FastAPI 后端和 Next.js 前端。

先安装 Web 依赖：

```bash
source .venv/bin/activate
pip install -r web/api/requirements.txt

cd web/frontend
npm install
cd ../..
```

一条命令启动：

```bash
./start.sh
```

打开：

```text
http://localhost:3000
```

手动启动方式：

```bash
# 终端 1
source .venv/bin/activate
uvicorn web.api.main:app --port 8000

# 终端 2
cd web/frontend
npm run dev -- --port 3000
```

## API 概览

Web 后端暴露这些本地 API：

| Endpoint | 说明 |
|---|---|
| `GET /api/health` | 健康检查 |
| `POST /api/chat` | SSE 形式流式返回 Agent 消息、工具调用和工具结果 |
| `POST /api/files/upload` | 上传文件到项目根目录或 `jds/` |
| `GET /api/files/outputs` | 列出 `outputs/` 或指定子目录 |
| `GET /api/files/outputs/{subdir}/{filename}` | 下载或预览输出文件 |
| `DELETE /api/files/outputs/{subdir}/{filename}` | 删除输出文件 |
| `GET /api/tracker` | 查询申请记录 |
| `POST /api/tracker` | 新增申请记录 |
| `PATCH /api/tracker` | 更新申请状态 |
| `PUT /api/tracker` | 编辑 tracker 行 |
| `GET /api/tracker/followups` | 查询需要跟进的申请 |

这些 API 默认只为本地 Web UI 使用，CORS 只允许 `http://localhost:3000`。

## Pipeline 是什么

这里的 pipeline 指岗位扫描和推荐流程，不是泛泛的数据管道。

它做五件事：

1. 根据配置扫描招聘网站。
2. 从 `data/scan-history.tsv` 读取最近新增岗位。
3. 根据职位配置、个人 profile 标签、中英技能别名打分。
4. 去重并排序。
5. 写出 `outputs/pipeline/pipeline_recommendations.md`。

示例：

```bash
python -m offerpilot.agent "运行 pipeline，扫描最近 14 天，推荐前 20 个国内岗位"
```

## Skill Pack 模式

如果你不是直接跑 OfferPilot Agent，而是想让 Cursor、Claude Code、Codex 这类工具按照一套文档流程工作，就使用 `skill-pack/`。

建议阅读顺序：

1. `skill-pack/WORKFLOW.md`
2. `skill-pack/INPUTS.md`
3. 简历诊断阅读 `skill-pack/RESUME_DIAGNOSIS.md`
4. 国内岗位匹配任务阅读 `skill-pack/JD_MATCHING.md`
5. 结构化评估阅读 `skill-pack/EVALUATION.md`
6. 模拟面试阅读 `skill-pack/MOCK_INTERVIEW.md`
7. 产品研究阅读 `skill-pack/PRODUCT_RESEARCH.md`
8. 申请追踪阅读 `skill-pack/TRACKER.md`
9. 外联消息阅读 `skill-pack/OUTREACH.md`
10. 需要本地脚本时阅读 `skill-pack/scripts/README.md`
11. 需要平台适配时阅读 `skill-pack/adapters/`

常用脚本：

```bash
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md
python skill-pack/scripts/extract_text.py resume.pdf
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md
python skill-pack/scripts/validate_profile_store.py profile_store.yaml
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
```

Agent 里也已经接入这些校验工具，可以在对话流程里自动调用。

## 输出目录约定

| 目录 | 内容 |
|---|---|
| `outputs/resumes/` | 简历诊断、简历优化、定向改写、JD 匹配、结构化评估、批量评估 |
| `outputs/research/` | 产品研究 |
| `outputs/interview/` | 面试题单、面试评估、面试准备 |
| `outputs/pipeline/` | 岗位扫描和推荐报告 |
| `outputs/misc/` | 外联消息、项目讲解、其他材料 |

不要直接把正式输出放在 `outputs/` 根目录。

## 开发和验证

运行测试：

```bash
source .venv/bin/activate
python -m pytest
```

检查 Agent 图是否能编译：

```bash
python - <<'PY'
from unittest.mock import Mock, patch
from offerpilot.graph import build_graph

with patch("offerpilot.graph.get_llm") as get_llm:
    llm = Mock()
    llm.bind_tools.return_value.invoke.return_value = "ok"
    get_llm.return_value = llm
    print(type(build_graph()).__name__)
PY
```

期望输出：

```text
CompiledStateGraph
```

## Troubleshooting

| 问题 | 处理 |
|---|---|
| `ModuleNotFoundError: langchain_core` | 先执行 `source .venv/bin/activate`，再 `pip install -e ".[dev]"` |
| `pytest` 找不到 | 确认已安装 dev 依赖：`pip install -e ".[dev]"` |
| `./start.sh` 找不到 `uvicorn` | `start.sh` 默认使用 `.venv/bin/uvicorn`，请先按安装步骤创建并安装 `.venv` |
| PDF 渲染失败 | 执行 `python -m playwright install chromium` |
| Agent 调用模型失败 | 检查 `.env` 中模型名、API key、base URL 是否匹配 |
| Web 前端无法连接后端 | 确认 API 在 `http://localhost:8000`，前端在 `http://localhost:3000` |
| 产品研究缺少事实来源 | 提供公司/产品材料、JD、网页摘录，或在支持联网能力的 agent 中使用 Skill Pack |

## 项目结构

```text
.
├── offerpilot/
│   ├── agent.py            # 自然语言 Agent CLI 入口
│   ├── cli.py              # helper CLI 入口
│   ├── graph.py            # LangGraph 路由和工作流
│   ├── intent.py           # 意图识别
│   ├── llm.py              # 多 provider LLM 初始化
│   ├── script_loader.py    # skill-pack 脚本加载器
│   ├── state.py            # 图状态
│   └── tools.py            # Agent tools
├── skill-pack/             # 工作流文档、适配器、脚本、schema 和数据
├── web/
│   ├── api/                # FastAPI 后端
│   └── frontend/           # Next.js 前端
├── tests/                  # 测试
├── outputs/                # 本地生成结果，不入 git
├── jds/                    # 本地 JD，不入 git
├── data/                   # tracker 和扫描历史，不入 git
└── profile_store.yaml      # 本地个人素材库，不入 git
```

## 分支维护建议

- 规则、prompt、输出格式、schema、模板、脚本和 adapter 优先进入 `offerpilot-skill`。
- LangGraph runtime、Agent 工具、Web API、前端和可运行体验进入 `offerpilot-agent`。
- 从 skill 分支同步到 agent 分支后，检查 `docs/AGENT_SYNC_CHECKLIST.md`，确认 `offerpilot/graph.py` 的 `SYSTEM_PROMPT` 是否需要更新。
- `docs/migration.md` 是历史迁移笔记，不能代表当前 agent 分支的产品形态。

## 写在最后

> **工作很重要。**
> 离开学校以后，它不声不响地占据了你醒着的大部分时间。
>
> 但工作又没那么重要。人不是为了优化 bullet point 而来到这个世界上的。
>
> 你做过真实的事。你解决过真实的问题。你加过班、赶过 deadline、替别人擦过屁股，但没人好好写下来，你自己也没有。
>
> 这个项目改变不了你的人生。但如果它能帮一个人不再低估自己，不再把同一份万能简历投进黑洞，真正拿到一个配得上的面试机会，那就够了。
>
> **去拿 offer 吧。然后合上电脑，好好生活。**

## License

MIT
