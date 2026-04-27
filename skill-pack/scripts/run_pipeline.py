#!/usr/bin/env python3
"""End-to-end OfferPilot job pipeline: scan -> rank -> recommend."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_CONFIG = "portals_cn.yml"
HISTORY_FILE = "data/scan-history.tsv"
DEFAULT_OUTPUT = "outputs/pipeline/pipeline_recommendations.md"
DEFAULT_PROFILE = "profile_store.yaml"
ALIASES_FILE = "skill-pack/data/skill_aliases.zh-en.json"
JDS_DIR = "jds"


# ---------------------------------------------------------------------------
# Profile & alias loading
# ---------------------------------------------------------------------------

def load_profile_tags(path: Path) -> set[str]:
    """Extract all unique tags from profile_store.yaml."""
    if not path.exists():
        return set()
    try:
        import yaml
    except ImportError:
        return set()
    with path.open(encoding="utf-8") as f:
        store = yaml.safe_load(f) or {}
    tags: set[str] = set()
    for section in ("experience", "projects"):
        for entry in store.get(section, []):
            for bullet in entry.get("bullets", []):
                tags.update(t.lower() for t in bullet.get("tags", []))
    for skill in store.get("skills", []):
        tags.add(skill.get("name", "").lower())
    return tags


def load_aliases(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def expand_profile_tags(tags: set[str], aliases: dict[str, list[str]]) -> set[str]:
    """Expand profile tags with their aliases for broader matching."""
    expanded = set(tags)
    for canonical, alias_list in aliases.items():
        if canonical.lower() in tags:
            expanded.update(a.lower() for a in alias_list)
        for alias in alias_list:
            if alias.lower() in tags:
                expanded.add(canonical.lower())
                expanded.update(a.lower() for a in alias_list)
                break
    return expanded


# ---------------------------------------------------------------------------
# JD content loading
# ---------------------------------------------------------------------------

def load_jd_content(title: str, company: str) -> str:
    """Try to load saved JD content from jds/ directory."""
    jds_path = Path(JDS_DIR)
    if not jds_path.exists():
        return ""
    slug = re.sub(r"[^\w\u4e00-\u9fff-]", "_", f"{company}-{title}")
    slug = re.sub(r"_+", "_", slug).strip("_")[:80]
    jd_file = jds_path / f"{slug}.md"
    if jd_file.exists():
        return jd_file.read_text(encoding="utf-8").lower()
    return ""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    url: str
    date: str
    source: str
    title: str
    company: str
    score: float
    reasons: list[str] = field(default_factory=list)
    skill_hits: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end pipeline: optional scan + shortlist recommendations."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Portal config YAML.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="Profile datastore YAML.")
    parser.add_argument("--no-scan", action="store_true", help="Skip scan step and rank from history only.")
    parser.add_argument("--days", type=int, default=7, help="Include jobs from the last N days.")
    parser.add_argument("--top-n", type=int, default=10, help="Number of recommendations to output.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Markdown output path.")
    parser.add_argument("--cn-focus", action="store_true", help="Boost Chinese companies and CN API sources.")
    parser.add_argument("--max-per-company", type=int, default=0, help="Max jobs per company (0=unlimited).")
    return parser.parse_args()


def run_scan(config_path: str) -> int:
    script_path = Path(__file__).resolve().parent / "scan_portals.py"
    cmd = [sys.executable, str(script_path), "--config", config_path]
    return subprocess.call(cmd, cwd=str(Path(__file__).resolve().parents[2]))


def load_config(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("WARNING: PyYAML not installed, ranking will run with default scoring only.")
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_recent_added(path: Path, days: int) -> list[dict]:
    if not path.exists():
        return []
    cutoff = datetime.now() - timedelta(days=max(days, 1))
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") != "added":
                continue
            raw_date = row.get("date", "")
            try:
                row_date = datetime.strptime(raw_date, "%Y-%m-%d")
            except ValueError:
                continue
            if row_date < cutoff:
                continue
            rows.append(row)
    return rows


def is_cn_company(name: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in name)


def score_row(row: dict, cfg: dict, cn_focus: bool, profile_tags: set[str]) -> Candidate:
    title = row.get("title", "")
    company = row.get("company", "")
    source = row.get("source", "")
    title_lower = title.lower()
    score = 0.0
    reasons: list[str] = []

    # --- Source reliability (existing) ---
    if source.startswith("api:"):
        score += 3.0
        reasons.append("结构化来源")
    elif source.startswith("greenhouse:"):
        score += 2.0
        reasons.append("官方招聘API")
    elif source.startswith("search:"):
        score += 1.0
        reasons.append("搜索发现")

    # --- Seniority boost (existing) ---
    boosts = cfg.get("title_filter", {}).get("seniority_boost", [])
    if any(word.lower() in title_lower for word in boosts):
        score += 1.5
        reasons.append("资深级别匹配")

    # --- Title keyword match (existing) ---
    positives = cfg.get("title_filter", {}).get("positive", [])
    positive_hits = sum(1 for word in positives if word.lower() in title_lower)
    if positive_hits:
        score += min(2.0, 0.5 * positive_hits)
        reasons.append(f"关键词匹配x{positive_hits}")

    # --- CN focus (existing) ---
    if cn_focus and (source.startswith("api:") or is_cn_company(company)):
        score += 1.0
        reasons.append("国内岗位优先")

    # --- JD content loading (shared by new dimensions) ---
    jd_text = load_jd_content(title, company)
    blob = title_lower + " " + jd_text

    # --- Skill matching (new, max 4.0) ---
    skill_hits = 0
    if profile_tags:
        for tag in profile_tags:
            if tag in blob:
                skill_hits += 1
        if skill_hits > 0:
            score += min(4.0, skill_hits * 0.5)
            reasons.append(f"技能匹配x{skill_hits}")

    # --- Location preference (new, 0.5) ---
    loc_prefs = cfg.get("location_filter", [])
    if loc_prefs and any(loc.lower() in blob for loc in loc_prefs):
        score += 0.5
        reasons.append("目标城市")

    # --- JD content quality (new, 0.5) ---
    if jd_text:
        score += 0.5
        reasons.append("JD内容完整")

    return Candidate(
        url=row.get("url", ""),
        date=row.get("date", ""),
        source=source,
        title=title,
        company=company,
        score=round(score, 1),
        reasons=reasons or ["基础匹配"],
        skill_hits=skill_hits,
    )


def dedup_keep_best(candidates: list[Candidate]) -> list[Candidate]:
    best: dict[str, Candidate] = {}
    for c in candidates:
        existing = best.get(c.url)
        if existing is None or (c.score, c.date) > (existing.score, existing.date):
            best[c.url] = c
    return list(best.values())


def write_report(path: Path, top: list[Candidate], days: int, top_n: int,
                 profile_loaded: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# OfferPilot Pipeline Recommendations",
        "",
        f"- 生成时间: {now}",
        f"- 时间窗口: 最近 {days} 天",
        f"- 推荐数量: Top {top_n}",
        f"- 技能匹配: {'✅ 已加载 profile_store' if profile_loaded else '⚠️ 未加载（仅基础排序）'}",
        "",
        "| Rank | Score | Skills | Company | Title | Source | Reason | Link |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for idx, c in enumerate(top, start=1):
        reason = " / ".join(c.reasons)
        lines.append(
            f"| {idx} | {c.score:.1f} | {c.skill_hits} | {c.company} | {c.title} "
            f"| {c.source} | {reason} | [查看岗位]({c.url}) |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.no_scan:
        code = run_scan(args.config)
        if code != 0:
            print("ERROR: scan step failed", file=sys.stderr)
            return code

    cfg = load_config(args.config)

    # Load profile for skill-based scoring
    profile_path = Path(args.profile)
    raw_tags = load_profile_tags(profile_path)
    aliases = load_aliases(Path(ALIASES_FILE))
    profile_tags = expand_profile_tags(raw_tags, aliases) if raw_tags else set()
    if profile_tags:
        print(f"Profile loaded: {len(raw_tags)} tags, {len(profile_tags)} after alias expansion.")
    else:
        print("WARNING: No profile loaded, skill matching disabled.")

    history_rows = load_recent_added(Path(HISTORY_FILE), args.days)
    if not history_rows:
        print("No recent added jobs found. Try increasing --days or run without --no-scan.")
        return 0

    candidates = [score_row(row, cfg, args.cn_focus, profile_tags) for row in history_rows]
    unique = dedup_keep_best(candidates)
    ranked = sorted(unique, key=lambda x: (x.score, x.date), reverse=True)
    if args.max_per_company > 0:
        capped: list[Candidate] = []
        counts: dict[str, int] = {}
        for c in ranked:
            n = counts.get(c.company, 0)
            if n < args.max_per_company:
                capped.append(c)
                counts[c.company] = n + 1
        ranked = capped
    top = ranked[: max(args.top_n, 1)]

    output_path = Path(args.output)
    write_report(output_path, top, args.days, args.top_n, bool(profile_tags))

    print(f"Pipeline completed: {len(history_rows)} recent jobs, {len(top)} recommended.")
    print(f"Recommendation report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
