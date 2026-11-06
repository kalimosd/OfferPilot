#!/usr/bin/env python3
"""Check and summarize OfferPilot job application tracker (data/tracker.tsv)."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

DEFAULT_TRACKER_PATH = Path("data/tracker.tsv")
TRACKER_FIELDS = ["url", "company", "title", "status", "applied_date", "last_update", "notes"]
VALID_STATUSES = {
    "discovered",
    "applied",
    "interviewing",
    "offer",
    "offer_evaluating",
    "accepted",
    "declined",
    "rejected",
    "ghosted",
}
FOLLOWUP_THRESHOLDS = {
    "applied": (7, "投递已超 7 天未更新，建议发送礼貌跟进或打招呼消息"),
    "interviewing": (5, "面试状态已超 5 天未更新，建议联系 HR 询问面试结果"),
    "offer": (3, "Offer 评估已超 3 天未更新，建议确认谈薪进展与签署截止日"),
    "offer_evaluating": (3, "Offer 评估已超 3 天未更新，建议确认谈薪进展与签署截止日"),
}


@dataclass(frozen=True)
class FollowUpItem:
    company: str
    title: str
    status: str
    days_elapsed: int
    url: str
    advice: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect data/tracker.tsv and report status summary and follow-up reminders."
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_TRACKER_PATH),
        help="Path to tracker.tsv (default: data/tracker.tsv).",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize an empty tracker.tsv with header if it does not exist.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Optional reference date in YYYY-MM-DD format (for deterministic checks).",
    )
    return parser


def ensure_tracker_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(TRACKER_FIELDS)


def _parse_date(raw: str) -> date | None:
    text = (raw or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def analyze_tracker(
    path: Path, today: date | None = None
) -> tuple[Counter[str], list[FollowUpItem], int]:
    """Return (status_counts, followups, skipped_malformed_rows)."""
    ref_date = today or date.today()
    counts: Counter[str] = Counter()
    followups: list[FollowUpItem] = []
    skipped = 0

    if not path.exists():
        return counts, followups, skipped

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header:
            return counts, followups, skipped

        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            if len(row) < 6:
                skipped += 1
                continue

            url, company, title, status, applied_date, last_update = (
                row[0].strip(),
                row[1].strip(),
                row[2].strip(),
                row[3].strip().lower(),
                row[4].strip(),
                row[5].strip(),
            )
            if not company or not title or status not in VALID_STATUSES:
                skipped += 1
                continue

            ref_dt = _parse_date(last_update) or _parse_date(applied_date)
            if (last_update or applied_date) and ref_dt is None:
                skipped += 1
                continue

            counts[status] += 1
            if status in FOLLOWUP_THRESHOLDS and ref_dt is not None:
                threshold_days, advice = FOLLOWUP_THRESHOLDS[status]
                elapsed = (ref_date - ref_dt).days
                if elapsed > threshold_days:
                    followups.append(
                        FollowUpItem(
                            company=company,
                            title=title,
                            status=status,
                            days_elapsed=elapsed,
                            url=url,
                            advice=advice,
                        )
                    )

    return counts, followups, skipped


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracker_path = Path(args.path)

    ref_date = _parse_date(args.today) if args.today else date.today()
    if args.today and ref_date is None:
        print(f"ERROR: Invalid --today date format: {args.today} (expected YYYY-MM-DD)")
        return 1

    if args.init or not tracker_path.exists():
        ensure_tracker_file(tracker_path)
        if args.init:
            print(f"OK: initialized tracker file at {tracker_path}")

    counts, followups, skipped = analyze_tracker(tracker_path, today=ref_date)
    total = sum(counts.values())
    print(f"Tracker summary ({tracker_path}): {total} active records")
    for status_name in sorted(counts):
        print(f"  - {status_name}: {counts[status_name]}")

    if followups:
        print(f"\nFollow-up reminders ({len(followups)}):")
        for item in followups:
            print(
                f"  ! [{item.status}] {item.company} | {item.title} "
                f"({item.days_elapsed} days) -> {item.advice} ({item.url})"
            )
    else:
        print("\nNo overdue follow-up items.")

    if skipped > 0:
        print(f"\nWARNING: 跳过了 {skipped} 条格式异常记录")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
