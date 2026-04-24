"""LangGraph agent graph definition."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
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


def build_graph():
    """Build and compile the agent graph."""
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
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
