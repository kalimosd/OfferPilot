"""OfferPilot agent tools."""

from __future__ import annotations

import csv
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
        "--config", config, "--days", str(days), "--top-n", str(top_n),
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
