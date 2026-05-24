"""OfferPilot agent tools."""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from langchain_core.tools import tool

from .script_loader import load_script_module

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
    extract_module = load_script_module("offerpilot_extract_text", str(SCRIPTS_DIR / "extract_text.py"))

    try:
        return extract_module.load_text_from_file(path)
    except Exception as e:
        return f"错误：{e}"


@tool
def render_pdf(input_path: str, output_path: str, style: str = "standard_cn") -> str:
    """将 Markdown 文件渲染为 PDF。style 可选: classic, ats, compact, standard_cn。"""
    render_module = load_script_module("offerpilot_render_pdf", str(SCRIPTS_DIR / "render_pdf.py"))

    input_p = Path(input_path)
    if not input_p.exists():
        return f"错误：文件不存在 {input_p}"

    markdown_text = input_p.read_text(encoding="utf-8")
    photo_path = None
    for ext in (".jpg", ".png"):
        candidate = REPO_ROOT / "assets" / f"photo{ext}"
        if candidate.exists():
            photo_path = str(candidate)
            break

    try:
        render_module.render_markdown_to_pdf(markdown_text, output_path, style=style, photo_path=photo_path)
        return f"PDF 已生成：{output_path}"
    except Exception as e:
        return f"错误：{e}"


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
        "--config", config, "--days", str(days), "--top-n", str(top_n),
    ]
    if cn_focus:
        cmd.append("--cn-focus")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    output = result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    if result.returncode != 0:
        details = output.strip() or "(no output)"
        return f"错误：pipeline 运行失败 (exit code {result.returncode})\n{details}"
    return output


@tool
def validate_inputs(paths: list[str]) -> str:
    """校验 OfferPilot 输入文件是否存在、格式是否支持。"""
    if not paths:
        return "错误：请提供至少一个输入文件路径"
    script = SCRIPTS_DIR / "validate_inputs.py"
    result = subprocess.run(
        [sys.executable, str(script), *paths],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    output = result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    if result.returncode != 0:
        return f"错误：输入校验失败 (exit code {result.returncode})\n{output.strip()}"
    return output


@tool
def validate_outputs(paths: list[str], english_name: str = "") -> str:
    """校验 OfferPilot 输出文件命名和可选英文名格式。"""
    if not paths:
        return "错误：请提供至少一个输出文件路径"
    script = SCRIPTS_DIR / "validate_outputs.py"
    cmd = [sys.executable, str(script), *paths]
    if english_name:
        cmd.extend(["--english-name", english_name])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    output = result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    if result.returncode != 0:
        return f"错误：输出校验失败 (exit code {result.returncode})\n{output.strip()}"
    return output


@tool
def validate_profile(path: str, aliases: str = "skill-pack/data/skill_aliases.zh-en.json") -> str:
    """校验 profile_store.yaml 的结构、bullet tags、impact、技能等级和别名覆盖。"""
    script = SCRIPTS_DIR / "validate_profile_store.py"
    result = subprocess.run(
        [sys.executable, str(script), path, "--aliases", aliases],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    output = result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    if result.returncode != 0:
        return f"错误：profile 校验失败 (exit code {result.returncode})\n{output.strip()}"
    return output


@tool
def validate_aliases(path: str = "skill-pack/data/skill_aliases.zh-en.json") -> str:
    """校验技能别名 JSON 映射，包括 key 格式、空值和重复 alias。"""
    script = SCRIPTS_DIR / "validate_aliases.py"
    result = subprocess.run(
        [sys.executable, str(script), path],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    output = result.stdout + (f"\n{result.stderr}" if result.stderr else "")
    if result.returncode != 0:
        return f"错误：alias 校验失败 (exit code {result.returncode})\n{output.strip()}"
    return output


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
            if row["url"].strip().rstrip("\r") == url.strip().rstrip("\r"):
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
    scan_portals, run_pipeline, validate_inputs, validate_outputs,
    validate_profile, validate_aliases,
    tracker_add, tracker_update, tracker_query, check_followups,
    batch_evaluate,
]
