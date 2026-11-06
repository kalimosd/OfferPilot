#!/usr/bin/env python3
"""Zero-risk Boss直聘 (zhipin.com) job importer from Browser Console JSON or clipboard."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Reuse filtering, history, and JD saving helpers from scan_portals.py
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import scan_portals  # noqa: E402

CONSOLE_JS_SNIPPET = r"""// === 在 Boss直聘 搜索列表页或岗位详情页打开 Chrome 控制台 (F12 -> Console) 粘贴运行 ===
(() => {
  const cards = document.querySelectorAll('.job-card-wrapper, .job-card-body, li.job-card-box');
  const jobs = [];
  if (cards.length > 0) {
    cards.forEach(c => {
      const linkEl = c.querySelector('a.job-card-left, a[href*="/job_detail/"]');
      const titleEl = c.querySelector('.job-name, .job-title');
      const compEl = c.querySelector('.company-name a, .company-name, .boss-name');
      const salEl = c.querySelector('.salary, .job-limit .red');
      const areaEl = c.querySelector('.job-area, .company-location');
      const tags = Array.from(c.querySelectorAll('.tag-list li, .job-card-footer li, .labels-tag')).map(el => el.innerText.trim()).filter(Boolean);
      if (linkEl && titleEl) {
        jobs.push({
          title: titleEl.innerText.trim(),
          url: linkEl.href.split('?')[0],
          company: compEl ? compEl.innerText.trim() : '',
          location: areaEl ? areaEl.innerText.trim() : '',
          salary: salEl ? salEl.innerText.trim() : '',
          skills: tags,
          jd: (salEl ? '薪资: ' + salEl.innerText.trim() + '\n' : '') + '标签: ' + tags.join(' / ')
        });
      }
    });
  } else {
    // 单个岗位详情页提取
    const titleEl = document.querySelector('.job-banner .name h1, .info-primary .name h1');
    const compEl = document.querySelector('.sider-company .company-info a[ka*="company"], .company-info-box .name');
    const salEl = document.querySelector('.job-banner .salary, .info-primary .salary');
    const secEl = document.querySelector('.job-sec-text');
    if (titleEl) {
      jobs.push({
        title: titleEl.innerText.trim(),
        url: location.href.split('?')[0],
        company: compEl ? compEl.innerText.trim() : '',
        location: document.querySelector('.text-city')?.innerText.trim() || '',
        salary: salEl ? salEl.innerText.trim() : '',
        skills: Array.from(document.querySelectorAll('.job-keyword-list li')).map(e => e.innerText.trim()),
        jd: secEl ? secEl.innerText.trim() : ''
      });
    }
  }
  copy(JSON.stringify(jobs, null, 2));
  console.log(`✅ 已提取 ${jobs.length} 个 Boss直聘岗位并复制到剪贴板！现在可回终端运行: offerpilot import-boss --from-clipboard`);
})();"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import Boss直聘 jobs from browser console JSON file or macOS clipboard."
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default=None,
        help="Path to exported Boss直聘 JSON file.",
    )
    parser.add_argument(
        "--from-clipboard",
        action="store_true",
        help="Read exported JSON directly from macOS clipboard (pbpaste).",
    )
    parser.add_argument(
        "--print-js",
        action="store_true",
        help="Print the Chrome DevTools Console JS snippet for 1-click extraction.",
    )
    parser.add_argument(
        "--config",
        default=scan_portals.DEFAULT_CONFIG,
        help="Portal config YAML used for title/location filtering.",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Import all items in the JSON without title/location filtering.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview imported items without writing to disk.",
    )
    return parser


def normalize_raw_item(raw: dict) -> dict | None:
    """Convert either Console JS format or Boss API zpData.jobList item into OfferPilot job dict."""
    if not isinstance(raw, dict):
        return None

    as_text = scan_portals._as_text
    as_tags = scan_portals._as_str_list

    title = as_text(raw.get("title")) or as_text(raw.get("jobName"))
    company = as_text(raw.get("company")) or as_text(raw.get("brandName"))
    url = as_text(raw.get("url"))
    encrypt_id = as_text(raw.get("encryptJobId"))
    if not url and encrypt_id:
        url = f"https://www.zhipin.com/job_detail/{encrypt_id}.html"

    if not title or not url:
        return None

    location = as_text(raw.get("location"))
    if not location:
        city = as_text(raw.get("cityName"))
        district = as_text(raw.get("areaDistrict"))
        location = f"{city} {district}".strip()

    salary = as_text(raw.get("salary")) or as_text(raw.get("salaryDesc"))
    exp = as_text(raw.get("jobExperience"))
    degree = as_text(raw.get("jobDegree"))
    all_tags = [*as_tags(raw.get("skills")), *as_tags(raw.get("jobLabels"))]

    jd_text = as_text(raw.get("jd"))
    meta_parts = [p for p in (salary, exp, degree) if p]
    if not jd_text:
        lines = []
        if meta_parts:
            lines.append("基本要求: " + " / ".join(meta_parts))
        if all_tags:
            lines.append("技能标签: " + " / ".join(dict.fromkeys(all_tags)))
        jd_text = "\n".join(lines)

    scale = as_text(raw.get("brandScaleName"))
    industry = as_text(raw.get("brandIndustry"))
    stage = as_text(raw.get("brandStageName"))
    highlight_parts = []
    if scale:
        highlight_parts.append(f"规模: {scale}")
    if industry:
        highlight_parts.append(f"行业: {industry}")
    if stage:
        highlight_parts.append(f"阶段: {stage}")
    highlight = as_text(raw.get("highlight")) or " / ".join(highlight_parts)

    return {
        "title": title,
        "url": url,
        "company": company or "Boss直聘企业",
        "location": location,
        "source": "manual:boss",
        "department": "",
        "category": "",
        "jd": jd_text,
        "highlight": highlight,
    }


def parse_json_payload(raw_text: str) -> list[dict]:
    """Parse either a JSON list of jobs or a full /wapi/zpgeek/search/joblist.json payload."""
    data = json.loads(raw_text)
    if isinstance(data, dict):
        zp_data = data.get("zpData")
        if isinstance(zp_data, dict):
            items = zp_data.get("jobList") or []
        else:
            items = data.get("jobs") or []
    elif isinstance(data, list):
        items = data
    else:
        items = []

    if not isinstance(items, list):
        items = []

    normalized = []
    for item in items:
        try:
            job = normalize_raw_item(item)
        except Exception as exc:
            print(f"WARNING: skipped malformed Boss item: {exc}", file=sys.stderr)
            continue
        if job is not None:
            normalized.append(job)
    return normalized


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.print_js:
        print(CONSOLE_JS_SNIPPET)
        return 0

    raw_text = ""
    if args.from_clipboard:
        try:
            res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
            raw_text = res.stdout.strip()
        except Exception as exc:
            print(f"ERROR: Could not read from macOS clipboard via pbpaste: {exc}", file=sys.stderr)
            return 1
    elif args.json_path:
        path = Path(args.json_path)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 1
        raw_text = path.read_text(encoding="utf-8").strip()
    else:
        print(
            "Usage: provide a JSON file, '--from-clipboard', or '--print-js' to get the Console script.",
            file=sys.stderr,
        )
        return 1

    try:
        jobs = parse_json_payload(raw_text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON payload: {exc}", file=sys.stderr)
        return 1

    if not jobs:
        print("No valid Boss直聘 job items found in input.")
        return 0

    if args.no_filter:
        cfg = {}
    else:
        try:
            cfg = scan_portals.load_config(args.config)
        except (OSError, scan_portals.ConfigError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    tf = cfg.get("title_filter", {})
    loc_filter = cfg.get("location_filter", [])
    seen = scan_portals.load_history(scan_portals.HISTORY_FILE)
    today = datetime.now().strftime("%Y-%m-%d")

    added_jobs: list[dict] = []
    history_rows: list[dict] = []
    skipped_dup = 0
    skipped_filter = 0

    for job in jobs:
        url = job["url"]
        if url in seen:
            skipped_dup += 1
            continue
        seen.add(url)

        if not args.no_filter:
            if loc_filter and job.get("location"):
                if not any(loc in job["location"] for loc in loc_filter):
                    skipped_filter += 1
                    continue
            if scan_portals.matches_job(job, tf) is None:
                skipped_filter += 1
                continue

        added_jobs.append(job)
        if not args.dry_run and job.get("jd"):
            scan_portals.save_jd(scan_portals.JDS_DIR, job)
        history_rows.append(
            {
                "url": url,
                "date": today,
                "source": job["source"],
                "title": job["title"],
                "company": job["company"],
                "status": "added",
            }
        )

    print(
        f"Boss直聘 import summary: {len(jobs)} parsed, "
        f"{len(added_jobs)} added, {skipped_dup} duplicates, {skipped_filter} filtered out."
    )
    for job in added_jobs:
        print(f"  + {job['company']} | {job['title']} ({job['location']})")

    if not args.dry_run and history_rows:
        scan_portals.append_history(scan_portals.HISTORY_FILE, history_rows)
        scan_portals.append_pipeline(scan_portals.PIPELINE_FILE, added_jobs)
        print(f"Saved {len(added_jobs)} jobs to {scan_portals.JDS_DIR}/ and {scan_portals.HISTORY_FILE}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
