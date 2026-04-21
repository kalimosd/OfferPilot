"""OfferPilot Agent — LLM-powered CLI agent for career workflows."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skill-pack" / "scripts"

SYSTEM_PROMPT = """你是 OfferPilot Agent，一个求职材料助手。你可以调用工具完成任务。

你支持以下任务类型：
1. jd-fit — JD 匹配度分析
2. resume-optimize — 简历优化
3. resume-target — 针对 JD 的定向简历改写
4. cover-letter — 求职信生成
5. extract — 从 PDF/DOCX 提取文本
6. export-pdf — 将 Markdown 导出为 PDF

工作规则：
- 不编造事实、不猜测信息
- 保留候选人真实经历
- 输出保存到 outputs/ 目录
- 中文 PDF 使用 standard_cn 样式
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "文件路径"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_text",
            "description": "从 PDF 或 DOCX 文件提取纯文本",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "PDF/DOCX 文件路径"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_pdf",
            "description": "将 Markdown 文件渲染为 PDF",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Markdown 文件路径"},
                    "output_path": {"type": "string", "description": "PDF 输出路径"},
                    "style": {
                        "type": "string",
                        "enum": ["classic", "ats", "compact", "standard_cn"],
                        "description": "PDF 样式，中文默认 standard_cn",
                    },
                },
                "required": ["input_path", "output_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录下的文件",
            "parameters": {
                "type": "object",
                "properties": {"directory": {"type": "string", "description": "目录路径"}},
                "required": ["directory"],
            },
        },
    },
]


def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if name == "read_file":
            p = Path(args["path"])
            if not p.exists():
                return f"错误：文件不存在 {p}"
            return p.read_text(encoding="utf-8")[:50000]

        if name == "write_file":
            p = Path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"已写入 {p} ({len(args['content'])} 字符)"

        if name == "extract_text":
            script = SCRIPTS_DIR / "extract_text.py"
            result = subprocess.run(
                [sys.executable, str(script), args["path"]],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            return result.stdout if result.returncode == 0 else f"错误：{result.stderr}"

        if name == "render_pdf":
            script = SCRIPTS_DIR / "render_pdf.py"
            style = args.get("style", "standard_cn")
            result = subprocess.run(
                [sys.executable, str(script), args["input_path"], args["output_path"],
                 "--style", style],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            return f"PDF 已生成：{args['output_path']}" if result.returncode == 0 else f"错误：{result.stderr}"

        if name == "list_files":
            d = Path(args["directory"])
            if not d.is_dir():
                return f"错误：目录不存在 {d}"
            files = sorted(d.iterdir())
            return "\n".join(f.name for f in files if not f.name.startswith("."))

        return f"未知工具：{name}"
    except Exception as e:
        return f"工具执行错误：{e}"


def _create_client() -> OpenAI:
    """Create OpenAI-compatible client for DeepSeek."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("错误：请设置 DEEPSEEK_API_KEY", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def run_agent(user_input: str, max_turns: int = 15) -> None:
    """Run the OfferPilot agent with a ReAct loop."""
    client = _create_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        # No tool calls — final answer
        if not msg.tool_calls:
            print(f"\n{msg.content}")
            return

        # Execute tool calls
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            print(f"  🔧 {fn_name}({', '.join(f'{k}={v!r}' for k, v in fn_args.items() if k != 'content')})")
            result = _execute_tool(fn_name, fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    print("⚠️ 达到最大轮次限制")


def main() -> None:
    """CLI entry point for the agent."""
    if len(sys.argv) < 2:
        print("用法: offerpilot-agent <指令>")
        print('示例: offerpilot-agent "帮我分析这个JD和我简历的匹配度，JD在jds/xxx.md，简历在profile_store.yaml"')
        return
    user_input = " ".join(sys.argv[1:])
    print(f"🚀 OfferPilot Agent 启动\n📝 任务: {user_input}\n")
    run_agent(user_input)


if __name__ == "__main__":
    main()
