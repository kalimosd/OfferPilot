#!/usr/bin/env python3
"""End-to-end OfferPilot job pipeline: scan -> rank -> recommend."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_CONFIG = "portals_cn.yml"
HISTORY_FILE = "data/scan-history.tsv"
DEFAULT_OUTPUT = "outputs/pipeline_recommendations.md"


@dataclass
class Candidate:
    url: str
    date: str
    source: str
    title: str
    company: str
    score: float
    reasons: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end pipeline: optional scan + shortlist recommendations."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Portal config YAML.")
    parser.add_argument("--no-scan", action="store_true", help="Skip scan step and rank from history only.")
    parser.add_argument("--days", type=int, default=7, help="Include jobs from the last N days.")
    parser.add_argument("--top-n", type=int, default=10, help="Number of recommendations to output.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Markdown output path.")
    parser.add_argument("--cn-focus", action="store_true", help="Boost Chinese companies and CN API sources.")
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


def score_row(row: dict, cfg: dict, cn_focus: bool) -> Candidate:
    title = row.get("title", "")
    company = row.get("company", "")
    source = row.get("source", "")
    title_lower = title.lower()
    score = 0.0
    reasons: list[str] = []

    if source.startswith("api:"):
        score += 3.0
        reasons.append("结构化来源")
    elif source.startswith("greenhouse:"):
        score += 2.0
        reasons.append("官方招聘API")
    elif source.startswith("search:"):
        score += 1.0
        reasons.append("搜索发现")

    boosts = cfg.get("title_filter", {}).get("seniority_boost", [])
    if any(word.lower() in title_lower for word in boosts):
        score += 1.5
        reasons.append("资深级别匹配")

    positives = cfg.get("title_filter", {}).get("positive", [])
    positive_hits = sum(1 for word in positives if word.lower() in title_lower)
    if positive_hits:
        plus = min(2.0, 0.5 * positive_hits)
        score += plus
        reasons.append(f"关键词匹配x{positive_hits}")

    if cn_focus and (source.startswith("api:") or is_cn_company(company)):
        score += 1.0
        reasons.append("国内岗位优先")

    return Candidate(
        url=row.get("url", ""),
        date=row.get("date", ""),
        source=source,
        title=title,
        company=company,
        score=score,
        reasons=reasons or ["基础匹配"],
    )


def dedup_keep_best(candidates: list[Candidate]) -> list[Candidate]:
    best: dict[str, Candidate] = {}
    for c in candidates:
        existing = best.get(c.url)
        if existing is None or (c.score, c.date) > (existing.score, existing.date):
            best[c.url] = c
    return list(best.values())


def write_report(path: Path, top: list[Candidate], days: int, top_n: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# OfferPilot Pipeline Recommendations",
        "",
        f"- 生成时间: {now}",
        f"- 时间窗口: 最近 {days} 天",
        f"- 推荐数量: Top {top_n}",
        "",
        "| Rank | Score | Company | Title | Source | Reason | Link |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for idx, c in enumerate(top, start=1):
        reason = " / ".join(c.reasons)
        lines.append(
            f"| {idx} | {c.score:.1f} | {c.company} | {c.title} | {c.source} | {reason} | [查看岗位]({c.url}) |"
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
    history_rows = load_recent_added(Path(HISTORY_FILE), args.days)
    if not history_rows:
        print("No recent added jobs found. Try increasing --days or run without --no-scan.")
        return 0

    candidates = [score_row(row, cfg, args.cn_focus) for row in history_rows]
    unique = dedup_keep_best(candidates)
    ranked = sorted(unique, key=lambda x: (x.score, x.date), reverse=True)
    top = ranked[: max(args.top_n, 1)]

    output_path = Path(args.output)
    write_report(output_path, top, args.days, args.top_n)

    print(f"Pipeline completed: {len(history_rows)} recent jobs, {len(top)} recommended.")
    print(f"Recommendation report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
