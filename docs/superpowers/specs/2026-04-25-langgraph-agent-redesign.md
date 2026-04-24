# OfferPilot Agent LangGraph 改造设计

## 目标

将 `agent.py` 从原生 OpenAI SDK 单文件 ReAct agent 迁移到 LangGraph 架构，同时新增 6 个 career-ops 启发的功能：结构化评估、Application Tracker、Follow-up 提醒、LinkedIn 外联消息、批量评估、全自动 pipeline。

## 文件结构

```
offerpilot/
├── agent.py      # CLI 入口（单次 + 多轮交互）
├── graph.py      # LangGraph 图定义
├── tools.py      # 所有 tool 定义
├── state.py      # 图状态 TypedDict
├── llm.py        # LLM 初始化（多 provider）
├── __init__.py
└── __main__.py
```

## 模块设计

### llm.py

- 使用 `langchain.chat_models.init_chat_model` 根据 model name 自动选 provider
- 环境变量：
  - `OFFERPILOT_MODEL` — 模型名（如 `deepseek-chat`、`claude-sonnet-4-20250514`、`gemini-2.0-flash`），默认 `deepseek-chat`
  - `OFFERPILOT_API_KEY` — 主 API key
  - `OFFERPILOT_BASE_URL` — 可选，自定义 base URL（DeepSeek 等）
  - 也支持 provider 原生环境变量（`ANTHROPIC_API_KEY`、`GOOGLE_API_KEY` 等）
- 导出 `get_llm()` 函数

### state.py

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
```

保持最简，只用 messages。任务类型由 LLM 从对话中推断，不需要额外状态字段。

### tools.py

现有工具（保留）：
- `read_file(path)` — 读取文件
- `write_file(path, content)` — 写入文件
- `extract_text(path)` — 从 PDF/DOCX 提取文本
- `render_pdf(input_path, output_path, style?)` — Markdown → PDF
- `list_files(directory)` — 列出目录

新增工具：
- `evaluate_jd(jd_path, profile_path?)` — 结构化 10 维评估，输出 A-F 等级报告到 `outputs/resumes/`
- `tracker_add(url, company, title, status?, notes?)` — 添加申请记录
- `tracker_update(url, status, notes?)` — 更新申请状态
- `tracker_query(status?, company?, days?)` — 查询/筛选记录
- `check_followups()` — 返回需要跟进的申请列表
- `batch_evaluate(jd_paths, profile_path?)` — 批量评估多个 JD
- `scan_portals(config?, cn_only?, greenhouse_only?, search_only?)` — 调用 scan_portals.py
- `run_pipeline(config?, days?, top_n?, cn_focus?)` — 调用 run_pipeline.py

LinkedIn 外联消息不需要专门的 tool，LLM 直接生成内容后用 `write_file` 保存。

### graph.py

标准 ReAct 图：

```
START → agent → (has tool calls?) → tools → agent → ... → END
```

- agent 节点：调用 LLM with tools
- tools 节点：执行 tool calls
- 条件边：有 tool_calls 则继续循环，否则结束

批量评估和全自动 pipeline 的确定性逻辑封装在 tool 内部，不需要图层面的特殊节点。

### agent.py

精简为 CLI 入口：
- 加载 .env
- 构建图
- 单次模式：`python -m offerpilot.agent "任务描述"`
- 多轮模式：`python -m offerpilot.agent`（进入交互循环）
- 保留 `offerpilot-agent` 命令行入口

## Tracker 数据格式

文件：`data/tracker.tsv`

| 字段 | 说明 |
|------|------|
| url | 岗位链接 |
| company | 公司名 |
| title | 岗位名 |
| status | discovered / applied / interviewing / offer / rejected / ghosted |
| applied_date | 投递日期 |
| last_update | 最后更新日期 |
| notes | 备注 |

## Follow-up 规则

- `applied` 超过 7 天无更新 → 提醒
- `interviewing` 超过 5 天无更新 → 提醒
- 其他状态不提醒

## 结构化评估维度

| # | 维度 | 权重 |
|---|------|------|
| 1 | 核心技能匹配 | 15% |
| 2 | 经历相关性 | 15% |
| 3 | 级别匹配 | 10% |
| 4 | 学历匹配 | 10% |
| 5 | 行业契合度 | 10% |
| 6 | 成长空间 | 10% |
| 7 | 薪资竞争力 | 10% |
| 8 | 地理位置 | 5% |
| 9 | 公司阶段/规模 | 10% |
| 10 | 文化契合度 | 5% |

等级映射：A(4.5+), B(3.5+), C(2.5+), D(1.5+), F(<1.5)

## System Prompt 更新

在现有 prompt 基础上新增任务类型：
- evaluate — 结构化评估
- tracker — 申请追踪管理
- followup — 跟进提醒
- outreach — LinkedIn 外联消息
- batch-evaluate — 批量评估
- auto-pipeline — 全自动 pipeline

## 依赖变化

pyproject.toml 新增：
```
langchain>=0.3
langgraph>=0.2
langchain-openai
langchain-anthropic
langchain-google-genai
```

## 迁移策略

1. 新建 `llm.py`, `state.py`, `tools.py`, `graph.py`
2. 重写 `agent.py` 为精简入口
3. 更新 `pyproject.toml` 依赖
4. 更新 system prompt
5. 验证现有功能 + 新功能
