# LangGraph Agent Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate OfferPilot agent from raw OpenAI SDK to LangGraph with multi-provider support, and add 6 new career-ops features (structured evaluation, tracker, follow-ups, outreach, batch evaluate, auto pipeline).

**Architecture:** Single LangGraph ReAct graph with tool-calling agent node. Deterministic logic (tracker CRUD, follow-up calculation, batch loops) lives inside tools. LLM handles reasoning and content generation. Split from 1 file into 5 focused modules.

**Tech Stack:** Python 3.12, LangGraph, LangChain (langchain-openai, langchain-anthropic, langchain-google-genai), existing Playwright/PyYAML/pypdf stack.

---

### Task 1: Install dependencies and update pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update pyproject.toml dependencies**

```toml
[project]
name = "offerpilot"
version = "0.2.0"
description = "Skill-first workflow pack for resume diagnosis, JD fit analysis, targeted rewrites, and cover letters."
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "langchain>=0.3",
    "langgraph>=0.2",
    "langchain-openai",
    "langchain-anthropic",
    "langchain-google-genai",
    "playwright",
    "pypdf",
    "PyYAML",
    "python-docx",
    "python-dotenv>=1.0.0",
]

[project.scripts]
offerpilot = "offerpilot.cli:main"
offerpilot-agent = "offerpilot.agent:main"

[project.optional-dependencies]
dev = ["pytest"]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 2: Install dependencies**

Run: `cd /Users/zhanchidong/code/offerpilot-ai && .venv/bin/pip install -e ".[dev]"`
Expected: All packages install successfully, including langchain, langgraph, langchain-openai, langchain-anthropic, langchain-google-genai.

- [ ] **Step 3: Verify imports work**

Run: `.venv/bin/python -c "from langgraph.graph import StateGraph; from langchain_openai import ChatOpenAI; from langchain_anthropic import ChatAnthropic; from langchain_google_genai import ChatGoogleGenerativeAI; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: add langchain and langgraph dependencies"
```

---

### Task 2: Create llm.py — multi-provider LLM initialization

**Files:**
- Create: `offerpilot/llm.py`

- [ ] **Step 1: Create llm.py**

```python
"""LLM initialization with multi-provider support."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@lru_cache(maxsize=1)
def get_llm():
    """Return a ChatModel instance based on environment config.

    Supports any provider via langchain's init_chat_model:
      - OFFERPILOT_MODEL=deepseek-chat  (needs OFFERPILOT_API_KEY + OFFERPILOT_BASE_URL)
      - OFFERPILOT_MODEL=claude-sonnet-4-20250514  (needs ANTHROPIC_API_KEY)
      - OFFERPILOT_MODEL=gemini-2.0-flash  (needs GOOGLE_API_KEY)
      - OFFERPILOT_MODEL=gpt-4o-mini  (needs OPENAI_API_KEY)
    """
    from langchain.chat_models import init_chat_model

    model = os.environ.get("OFFERPILOT_MODEL", "deepseek-chat")
    api_key = os.environ.get("OFFERPILOT_API_KEY", "")
    base_url = os.environ.get("OFFERPILOT_BASE_URL", "")

    # DeepSeek or other OpenAI-compatible APIs with custom base_url
    if base_url or _is_openai_compatible(model):
        if not base_url and model.startswith("deepseek"):
            base_url = "https://api.deepseek.com"
        kwargs = {"api_key": api_key, "base_url": base_url} if api_key else {}
        return init_chat_model(model, model_provider="openai", **kwargs)

    # Native providers — they read their own env vars (ANTHROPIC_API_KEY, etc.)
    return init_chat_model(model)


def _is_openai_compatible(model: str) -> bool:
    return any(model.startswith(p) for p in ("deepseek", "qwen", "yi-", "glm"))
```

- [ ] **Step 2: Verify it loads with current .env**

Run: `.venv/bin/python -c "from offerpilot.llm import get_llm; llm = get_llm(); print(type(llm).__name__)"`
Expected: `ChatOpenAI` (since current .env uses DeepSeek)

- [ ] **Step 3: Commit**

```bash
git add offerpilot/llm.py
git commit -m "feat: add multi-provider LLM initialization"
```

---

### Task 3: Create state.py — graph state definition

**Files:**
- Create: `offerpilot/state.py`

- [ ] **Step 1: Create state.py**

```python
"""LangGraph state definition."""

from __future__ import annotations

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
```

- [ ] **Step 2: Verify import**

Run: `.venv/bin/python -c "from offerpilot.state import AgentState; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add offerpilot/state.py
git commit -m "feat: add LangGraph agent state definition"
```

---

### Task 4: Create tools.py — all tool definitions

**Files:**
- Create: `offerpilot/tools.py`

- [ ] **Step 1: Create tools.py with existing tools migrated + new tools**

```python
"""OfferPilot agent tools."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from langchain_core.tools import tool

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skill-pack" / "scripts"
TRACKER_FILE = REPO_ROOT / "data" / "tracker.tsv"

TRACKER_FIELDS = ["url", "company", "title", "status", "applied_date", "last_update", "notes"]
VALID_STATUSES = {"discovered", "applied", "interviewing", "offer", "rejected", "ghosted"}


# === Existing tools (migrated) ===


@tool
def read_file(path: str) -> str:
    """读取文件内容。"""
    p = Path(path)
    if not p.exists():
        return f"错误：文件不存在 {p}"
    return p.read_text(encoding="utf-8")[:50000]


@tool
def write_file(path: str, content: str) -> str:
    """写入文件内容。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"已写入 {p} ({len(content)} 字符)"


@tool
def extract_text(path: str) -> str:
    """从 PDF 或 DOCX 文件提取纯文本。"""
    script = SCRIPTS_DIR / "extract_text.py"
    result = subprocess.run(
        [sys.executable, str(script), path],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    return result.stdout if result.returncode == 0 else f"错误：{result.stderr}"


@tool
def render_pdf(input_path: str, output_path: str, style: str = "standard_cn") -> str:
    """将 Markdown 文件渲染为 PDF。style 可选: classic, ats, compact, standard_cn。"""
    script = SCRIPTS_DIR / "render_pdf.py"
    result = subprocess.run(
        [sys.executable, str(script), input_path, output_path, "--style", style],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    return f"PDF 已生成：{output_path}" if result.returncode == 0 else f"错误：{result.stderr}"


@tool
def list_files(directory: str) -> str:
    """列出目录下的文件。"""
    d = Path(directory)
    if not d.is_dir():
        return f"错误：目录不存在 {d}"
    files = sorted(d.iterdir())
    return "\n".join(f.name for f in files if not f.name.startswith("."))


# === New tools ===


@tool
def scan_portals(config: str = "portals_cn.yml", cn_only: bool = False,
                 greenhouse_only: bool = False, search_only: bool = False) -> str:
    """扫描招聘网站发现新岗位。"""
    script = SCRIPTS_DIR / "scan_portals.py"
    cmd = [sys.executable, str(script), "--config", config]
    if cn_only:
        cmd.append("--cn-only")
    if greenhouse_only:
        cmd.append("--greenhouse-only")
    if search_only:
        cmd.append("--search-only")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    return result.stdout if result.returncode == 0 else f"错误：{result.stderr}"


@tool
def run_pipeline(config: str = "portals_cn.yml", days: int = 7,
                 top_n: int = 10, cn_focus: bool = False) -> str:
    """运行端到端岗位 pipeline：扫描 → 排序 → 推荐。"""
    script = SCRIPTS_DIR / "run_pipeline.py"
    cmd = [
        sys.executable, str(script),
        "--config", config, "--days", str(days),
        "--top-n", str(top_n),
    ]
    if cn_focus:
        cmd.append("--cn-focus")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    return result.stdout + (f"\n{result.stderr}" if result.stderr else "")


@tool
def tracker_add(url: str, company: str, title: str,
                status: str = "discovered", notes: str = "") -> str:
    """添加一条申请记录到 tracker。status: discovered/applied/interviewing/offer/rejected/ghosted。"""
    if status not in VALID_STATUSES:
        return f"错误：无效状态 '{status}'，可选: {', '.join(sorted(VALID_STATUSES))}"
    today = datetime.now().strftime("%Y-%m-%d")
    row = {
        "url": url, "company": company, "title": title,
        "status": status, "applied_date": today if status == "applied" else "",
        "last_update": today, "notes": notes,
    }
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    exists = TRACKER_FILE.exists()
    with open(TRACKER_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_FIELDS, delimiter="\t")
        if not exists:
            writer.writeheader()
        writer.writerow(row)
    return f"已添加: {company} - {title} [{status}]"


@tool
def tracker_update(url: str, status: str, notes: str = "") -> str:
    """更新申请记录的状态。"""
    if status not in VALID_STATUSES:
        return f"错误：无效状态 '{status}'，可选: {', '.join(sorted(VALID_STATUSES))}"
    if not TRACKER_FILE.exists():
        return "错误：tracker 文件不存在"
    rows = []
    updated = False
    with open(TRACKER_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["url"] == url:
                row["status"] = status
                row["last_update"] = datetime.now().strftime("%Y-%m-%d")
                if status == "applied" and not row.get("applied_date"):
                    row["applied_date"] = row["last_update"]
                if notes:
                    row["notes"] = notes
                updated = True
            rows.append(row)
    if not updated:
        return f"错误：未找到 URL {url}"
    with open(TRACKER_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return f"已更新: {url} → [{status}]"


@tool
def tracker_query(status: str = "", company: str = "", days: int = 0) -> str:
    """查询申请记录。可按 status、company 筛选，days>0 表示最近 N 天。"""
    if not TRACKER_FILE.exists():
        return "tracker 为空"
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d") if days > 0 else ""
    results = []
    with open(TRACKER_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if status and row.get("status") != status:
                continue
            if company and company.lower() not in row.get("company", "").lower():
                continue
            if cutoff and row.get("last_update", "") < cutoff:
                continue
            results.append(row)
    if not results:
        return "无匹配记录"
    lines = [f"共 {len(results)} 条记录：", ""]
    for r in results:
        lines.append(f"- [{r.get('status','')}] {r.get('company','')} | {r.get('title','')} | {r.get('last_update','')} | {r.get('url','')}")
    return "\n".join(lines)


@tool
def check_followups() -> str:
    """检查需要跟进的申请（applied>7天 或 interviewing>5天 未更新）。"""
    if not TRACKER_FILE.exists():
        return "tracker 为空"
    today = datetime.now()
    reminders = []
    with open(TRACKER_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            status = row.get("status", "")
            last = row.get("last_update", "")
            if not last:
                continue
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d")
            except ValueError:
                continue
            gap = (today - last_date).days
            if status == "applied" and gap > 7:
                reminders.append(f"⏰ {row['company']} | {row['title']} — 已投递 {gap} 天未更新")
            elif status == "interviewing" and gap > 5:
                reminders.append(f"⏰ {row['company']} | {row['title']} — 面试中 {gap} 天未更新")
    return "\n".join(reminders) if reminders else "✅ 暂无需要跟进的申请"


@tool
def batch_evaluate(jd_paths: list[str], profile_path: str = "profile_store.yaml") -> str:
    """批量评估多个 JD 文件，返回汇总结果。传入 JD 文件路径列表。"""
    results = []
    for jd_path in jd_paths:
        p = Path(jd_path)
        if not p.exists():
            results.append(f"❌ {jd_path}: 文件不存在")
            continue
        jd_content = p.read_text(encoding="utf-8")[:10000]
        title = p.stem.replace("_", " ").replace("-", " ")
        results.append(f"📄 {title}\n路径: {jd_path}\nJD 长度: {len(jd_content)} 字符\n---")
    summary = f"共 {len(jd_paths)} 个 JD 待评估：\n\n" + "\n".join(results)
    summary += "\n\n请逐个读取上述 JD 内容和 profile_store，对每个 JD 进行结构化评估。"
    return summary


ALL_TOOLS = [
    read_file, write_file, extract_text, render_pdf, list_files,
    scan_portals, run_pipeline,
    tracker_add, tracker_update, tracker_query, check_followups,
    batch_evaluate,
]
```

- [ ] **Step 2: Verify imports**

Run: `.venv/bin/python -c "from offerpilot.tools import ALL_TOOLS; print(f'{len(ALL_TOOLS)} tools loaded')"`
Expected: `12 tools loaded`

- [ ] **Step 3: Commit**

```bash
git add offerpilot/tools.py
git commit -m "feat: add all agent tools with tracker and batch support"
```

---

### Task 5: Create graph.py — LangGraph ReAct graph

**Files:**
- Create: `offerpilot/graph.py`

- [ ] **Step 1: Create graph.py**

```python
"""LangGraph agent graph definition."""

from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .llm import get_llm
from .state import AgentState
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """你是 OfferPilot Agent，一个 AI 求职助手。你可以调用工具完成任务。

你支持以下任务类型：
1. jd-fit — JD 匹配度分析
2. resume-optimize — 简历优化
3. resume-target — 针对 JD 的定向简历改写
4. cover-letter — 求职信生成
5. extract — 从 PDF/DOCX 提取文本
6. export-pdf — 将 Markdown 导出为 PDF
7. evaluate — 结构化多维度岗位评估（10 维打分 + A-F 等级）
8. tracker — 申请状态追踪（添加、更新、查询）
9. followup — 检查需要跟进的申请
10. outreach — 生成 LinkedIn 外联消息
11. batch-evaluate — 批量评估多个 JD
12. auto-pipeline — 全自动 pipeline（扫描→排序→推荐）
13. mock-interview — 模拟面试
14. product-research — 产品研究

工作规则：
- 不编造事实、不猜测信息
- 保留候选人真实经历
- 中文 PDF 使用 standard_cn 样式

输出目录规则（必须遵守）：
- outputs/resumes/    — 简历优化、定向改写、JD 匹配度分析、结构化评估报告
- outputs/research/   — 产品研究
- outputs/interview/  — 面试题单、面试评估、面试准备
- outputs/pipeline/   — 扫描推荐、pipeline 报告
- outputs/misc/       — 其他（项目讲解、设计方案、LinkedIn 外联消息等）

结构化评估维度（evaluate 任务使用）：
1. 核心技能匹配 (15%)  2. 经历相关性 (15%)  3. 级别匹配 (10%)
4. 学历匹配 (10%)      5. 行业契合度 (10%)  6. 成长空间 (10%)
7. 薪资竞争力 (10%)    8. 地理位置 (5%)     9. 公司阶段/规模 (10%)
10. 文化契合度 (5%)
总分 5 分制 → 等级: A(4.5+), B(3.5+), C(2.5+), D(1.5+), F(<1.5)
每个维度给出分数和一句话理由，最后给出总分、等级和综合结论。

Tracker 状态流转：discovered → applied → interviewing → offer / rejected / ghosted
"""


def build_graph() -> StateGraph:
    """Build and compile the agent graph."""
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        # Inject system prompt if not present
        if not messages or messages[0].type != "system":
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
```

- [ ] **Step 2: Verify graph builds**

Run: `.venv/bin/python -c "from offerpilot.graph import build_graph; g = build_graph(); print('Graph compiled OK')"`
Expected: `Graph compiled OK`

- [ ] **Step 3: Commit**

```bash
git add offerpilot/graph.py
git commit -m "feat: add LangGraph ReAct agent graph"
```

---

### Task 6: Rewrite agent.py — slim CLI entry point

**Files:**
- Modify: `offerpilot/agent.py` (full rewrite)

- [ ] **Step 1: Rewrite agent.py**

```python
"""OfferPilot Agent — LangGraph-powered CLI agent for career workflows."""

from __future__ import annotations

import sys

from langchain_core.messages import HumanMessage

from .graph import build_graph


def run_agent(user_input: str) -> None:
    """Run the agent with a single user input."""
    graph = build_graph()
    result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
    last = result["messages"][-1]
    print(f"\n{last.content}")


def run_interactive() -> None:
    """Run the agent in multi-turn interactive mode."""
    print("🚀 OfferPilot Agent（输入 exit 退出）\n")
    graph = build_graph()
    messages = []

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("👋 再见")
            break

        messages.append(HumanMessage(content=user_input))
        result = graph.invoke({"messages": messages})
        messages = result["messages"]
        last = messages[-1]
        print(f"\n{last.content}\n")


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) >= 2:
        user_input = " ".join(sys.argv[1:])
        print(f"🚀 OfferPilot Agent\n📝 任务: {user_input}\n")
        run_agent(user_input)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify CLI help works**

Run: `.venv/bin/python -m offerpilot.agent --help 2>&1 || echo "No --help, that's fine"`
Expected: Runs without import errors (may print usage or start interactive mode)

- [ ] **Step 3: Commit**

```bash
git add offerpilot/agent.py
git commit -m "feat: rewrite agent.py as slim LangGraph CLI entry"
```

---

### Task 7: Update pyproject.toml entry point and clean up

**Files:**
- Modify: `offerpilot/__init__.py`

- [ ] **Step 1: Update __init__.py to export version**

```python
"""OfferPilot package."""

__all__ = ["__version__"]

__version__ = "0.2.0"
```

- [ ] **Step 2: Verify full agent invocation (single-shot, dry run)**

Run: `.venv/bin/python -c "from offerpilot.graph import build_graph; from langchain_core.messages import HumanMessage; g = build_graph(); print('Ready to invoke')"`
Expected: `Ready to invoke`

- [ ] **Step 3: Verify tool count in compiled graph**

Run: `.venv/bin/python -c "from offerpilot.tools import ALL_TOOLS; print([t.name for t in ALL_TOOLS])"`
Expected: List of 12 tool names

- [ ] **Step 4: Commit all changes**

```bash
git add -A
git commit -m "feat: complete LangGraph agent migration with new career-ops tools"
```

---

### Task 8: End-to-end smoke test

- [ ] **Step 1: Test single-shot mode with a simple task**

Run: `.venv/bin/python -m offerpilot.agent "列出 jds 目录下的文件"`
Expected: Agent calls `list_files` tool and returns the file listing.

- [ ] **Step 2: Test tracker tool**

Run: `.venv/bin/python -c "from offerpilot.tools import tracker_add, tracker_query, check_followups; print(tracker_add.invoke({'url': 'https://example.com/job1', 'company': '测试公司', 'title': '测试岗位', 'status': 'applied'})); print(tracker_query.invoke({'status': 'applied'})); print(check_followups.invoke({}))"`
Expected: Record added, query returns it, followups shows no reminders (just added today).

- [ ] **Step 3: Clean up test data**

Run: `rm -f /Users/zhanchidong/code/offerpilot-ai/data/tracker.tsv`

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "test: verify LangGraph agent end-to-end"
```
