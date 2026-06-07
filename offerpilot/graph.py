"""LangGraph agent graph definition."""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from pathlib import Path

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .intent import classify_user_intent
from .llm import get_llm, PRECISE_TEMPERATURE
from .script_loader import load_script_module
from .state import AgentState
from .tools import ALL_TOOLS

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skill-pack" / "scripts"

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
15. resume-diagnosis — 纯简历诊断（不依赖 JD，分析简历结构、表达、量化度）

工作规则：
- 不编造事实、不猜测信息
- 保留候选人真实经历
- 中文 PDF 使用 standard_cn 样式
- 简历诊断不需要 JD；jd-fit 诊断才需要 JD
- 使用 profile datastore 时，按 impact 优先级选择 bullet：quantified > qualitative > context-only
- 当 bullet 有 variants 时，选择最匹配目标 JD 角度的 variant；无匹配则用原始 text
- JD 工作年限匹配：按候选人实际全职经验 +1 年计算（experience+1 规则）
- 用户 review 后提修改意见时，优先局部修改而非重新生成整个文档；版本号递增（v1 → v2）
- 仅当用户明确说「重新生成」或「推翻重来」时，才走完整生成流程

输出目录规则（必须遵守）：
- outputs/resumes/    — 简历诊断、简历优化、定向改写、JD 匹配度分析、结构化评估报告
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

简历格式规则（必须遵守）：
- section 顺序：教育背景 → 工作经历 → 强相关项目 → 实习经历 → 其他项目 → 技能
- 工作经历 section 只放全职工作，实习经历必须放在单独的「实习经历」section，绝对不能合并
- 实习经历和项目经历必须分开，不能合并为同一个 section
- 不要生成"工作亮点"等额外总结性 section，除非用户明确要求
- 联系信息行格式：电话（微信同） | 邮箱 | XX 岁（从 birth_year 计算：当前年份 - birth_year）
- 教育行格式：**学校名 | 专业 | 学位**（例：**墨尔本大学 | 数据科学 | 硕士**）
- 技能用分类列表格式，不要用表格。每行一个类别，冒号后列出该类别下的技能，用顿号分隔。示例：
  - Android 开发：Java / Kotlin、Launcher 架构、Dock 状态机
  - AI 工程：AI Agent 工作流设计与开发、Prompt Engineering
  - 语言能力：英语流畅办公（五年澳洲留学及实习经历）
- 中文简历 PDF 默认使用 --style standard_cn
- 文件命名：姓名_公司_岗位_v1（或 姓名_岗位_v1）
- 简历类任务必须同时输出 Markdown 和 PDF 两个文件
- 不编造事实、不猜测信息、不发明不存在的联系方式
- 源简历中有的联系方式必须保留，没有的不要猜测填充
"""

def _classify_intent(state: AgentState) -> dict:
    """Classify user intent from the last message: pipeline, batch_evaluate, or general."""
    last_msg = state["messages"][-1]
    content = last_msg.content if isinstance(last_msg, HumanMessage) else ""
    return classify_user_intent(content)


def _route_by_intent(state: AgentState) -> str:
    task = state.get("task_type", "general")
    if task == "pipeline":
        return "pipeline"
    if task == "batch_evaluate":
        return "batch_evaluate"
    return "agent"


# === Pipeline subgraph ===

def _build_pipeline_subgraph():
    """Deterministic pipeline subgraph: scan portals → rank candidates → write report.

    Replaces the previous approach of having the LLM reason through pipeline steps
    via tool calls. The subgraph runs the scan, ranking, and report writing as a
    fixed sequence without LLM planning overhead.
    """
    run_pipeline = load_script_module("offerpilot_run_pipeline", str(SCRIPTS_DIR / "run_pipeline.py"))

    graph = StateGraph(AgentState)

    def scan_step(state: AgentState) -> dict:
        """Run portal scanner to discover new jobs."""
        config_path = state.get("pipeline_config", "portals_cn.yml")
        result_code = run_pipeline.run_scan(config_path)
        if result_code != 0:
            return {"messages": [AIMessage(content=f"Pipeline scan failed with exit code {result_code}. Check portal config `{config_path}` and scanner logs.")]}
        stdout = f"Scan completed with config `{config_path}`."
        return {"messages": [AIMessage(content=f"Scan results:\n{stdout[:3000]}")]}

    def rank_and_report(state: AgentState) -> dict:
        """Score jobs from scan history, rank them, and write the recommendation report."""
        config_path = state.get("pipeline_config", "portals_cn.yml")
        days = state.get("pipeline_days", 7)
        top_n = state.get("pipeline_top_n", 10)
        cn_focus = state.get("pipeline_cn_focus", False)
        profile_path = state.get("batch_profile_path", "profile_store.yaml")

        cfg = run_pipeline.load_config(config_path)
        profile_tags_raw = run_pipeline.load_profile_tags(REPO_ROOT / profile_path)
        aliases = run_pipeline.load_aliases(REPO_ROOT / "skill-pack" / "data" / "skill_aliases.zh-en.json")
        profile_tags = run_pipeline.expand_profile_tags(profile_tags_raw, aliases) if profile_tags_raw else set()

        history_rows = run_pipeline.load_recent_added(REPO_ROOT / "data" / "scan-history.tsv", days)
        if not history_rows:
            return {"messages": [AIMessage(content="No recent jobs found in scan history. Try increasing the time window with e.g. \"run pipeline last 14 days\".")]}

        candidates = [run_pipeline.score_row(row, cfg, cn_focus, profile_tags) for row in history_rows]
        unique = run_pipeline.dedup_keep_best(candidates)
        ranked = sorted(unique, key=lambda x: (x.score, x.date), reverse=True)
        top = ranked[:top_n]

        output_path = REPO_ROOT / "outputs" / "pipeline" / "pipeline_recommendations.md"
        run_pipeline.write_report(output_path, top, days, top_n, bool(profile_tags))

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [f"## Pipeline Recommendations ({now})", ""]
        lines.append(f"Scored {len(history_rows)} recent jobs, top {len(top)} below:\n")
        for idx, c in enumerate(top, 1):
            reason = " / ".join(c.reasons)
            lines.append(f"{idx}. **{c.company}** | {c.title} | Score: {c.score:.1f}")
            lines.append(f"   {reason} | [View]({c.url})")
        lines.append(f"\nFull report: `{output_path}`")

        return {"messages": [AIMessage(content="\n".join(lines))]}

    graph.add_node("scan", scan_step)
    graph.add_node("rank", rank_and_report)
    graph.set_entry_point("scan")
    graph.add_edge("scan", "rank")
    graph.add_edge("rank", END)

    return graph.compile()


# === Batch evaluate subgraph ===

def _build_batch_evaluate_subgraph():
    """Batch JD evaluation subgraph: load JDs → evaluate each → aggregate.

    Each JD is evaluated independently with a low-temperature LLM call to ensure
    consistent scoring. Results are aggregated into a single ranked summary.
    """
    graph = StateGraph(AgentState)

    def load_and_evaluate(state: AgentState) -> dict:
        """Load JDs from the jds/ directory and evaluate each one against the profile."""
        jds_dir = REPO_ROOT / "jds"
        if not jds_dir.is_dir():
            return {"messages": [AIMessage(content="No `jds/` directory found. Upload JDs first.")]}

        jd_files = sorted([
            f for f in jds_dir.iterdir()
            if f.suffix == ".md" and not f.name.startswith(".")
        ])[:20]

        if not jd_files:
            return {"messages": [AIMessage(content="No JDs found in `jds/` directory.")]}

        profile_path = state.get("batch_profile_path", "profile_store.yaml")
        profile_p = REPO_ROOT / profile_path
        profile_text = profile_p.read_text(encoding="utf-8") if profile_p.exists() else ""

        llm = get_llm(temperature=PRECISE_TEMPERATURE)
        results = []

        for jd_file in jd_files:
            jd_text = jd_file.read_text(encoding="utf-8")[:6000]
            jd_name = jd_file.stem.replace("_", " ").replace("-", " ")

            prompt = f"""Evaluate this job description against the candidate profile. Score from 0-5 (0=no match, 5=perfect). Give a one-line reason.

Profile:
{profile_text[:3000]}

Job: {jd_name}
{jd_text[:5000]}

Reply in this exact format: SCORE|ONE-LINE REASON (example: "4.2|Strong overlap in AI agent engineering and LLM experience")"""

            response = llm.invoke([HumanMessage(content=prompt)])
            results.append((jd_name, response.content.strip()))

        results.sort(key=lambda x: _parse_score(x[1]), reverse=True)

        lines = [f"## Batch Evaluation ({len(results)} JDs)\n"]
        lines.append("| Rank | Score | Company / Role | Reason |")
        lines.append("|------|-------|----------------|--------|")
        for idx, (name, eval_line) in enumerate(results, 1):
            score, reason = _parse_score_and_reason(eval_line)
            lines.append(f"| {idx} | {score:.1f} | {name} | {reason} |")

        return {"messages": [AIMessage(content="\n".join(lines))]}

    graph.add_node("evaluate", load_and_evaluate)
    graph.set_entry_point("evaluate")
    graph.add_edge("evaluate", END)

    return graph.compile()


def _parse_score(eval_line: str) -> float:
    """Extract numeric score from an evaluation line like '4.2|reason'."""
    try:
        return float(eval_line.split("|")[0].strip())
    except (ValueError, IndexError):
        return 0.0


def _parse_score_and_reason(eval_line: str) -> tuple[float, str]:
    """Extract score and reason from evaluation output. Returns (score, reason)."""
    parts = eval_line.split("|", 1)
    try:
        score = float(parts[0].strip())
    except (ValueError, IndexError):
        score = 0.0
    reason = parts[1].strip() if len(parts) > 1 else eval_line
    return score, reason


# === Main graph ===

@lru_cache(maxsize=1)
def build_graph():
    """Build and compile the agent graph with intent routing and specialized subgraphs.

    Graph structure:
        classify_intent → pipeline subgraph → END
        classify_intent → batch_evaluate subgraph → END
        classify_intent → agent → tools → agent (ReAct loop for general tasks)
    """
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        return {"messages": [llm_with_tools.invoke(messages)]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", _classify_intent)
    graph.add_node("pipeline", _build_pipeline_subgraph())
    graph.add_node("batch_evaluate", _build_batch_evaluate_subgraph())
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges("classify_intent", _route_by_intent, {
        "pipeline": "pipeline",
        "batch_evaluate": "batch_evaluate",
        "agent": "agent",
    })
    graph.add_edge("pipeline", END)
    graph.add_edge("batch_evaluate", END)
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
