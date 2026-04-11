#!/usr/bin/env python3
"""Portal scanner for OfferPilot — discovers jobs from company career pages and Greenhouse API."""

import argparse
import csv
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = "portals_cn.yml"
HISTORY_FILE = "data/scan-history.tsv"
PIPELINE_FILE = "data/pipeline.md"
GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
JDS_DIR = "jds"
MAX_AGE_DAYS = 90


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Title filter
# ---------------------------------------------------------------------------

def matches_job(job: dict, tf: dict) -> str | None:
    """Return 'added' if a job passes title/content filters, or None."""
    title = (job.get("title") or "").lower()
    content_blob = " ".join(
        [
            job.get("title", ""),
            job.get("department", ""),
            job.get("category", ""),
            job.get("jd", ""),
            job.get("highlight", ""),
        ]
    ).lower()
    if any(neg.lower() in content_blob for neg in tf.get("negative", [])):
        return None
    positives = tf.get("positive", [])
    if not positives:
        return "added"
    if any(pos.lower() in title for pos in positives):
        return "added"
    if any(pos.lower() in content_blob for pos in positives):
        return "added"
    return None


# ---------------------------------------------------------------------------
# History / dedup
# ---------------------------------------------------------------------------

def load_history(path: str) -> set[str]:
    """Return set of URLs already seen."""
    seen: set[str] = set()
    if not os.path.exists(path):
        return seen
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            seen.add(row.get("url", ""))
    return seen


def append_history(path: str, rows: list[dict]):
    exists = os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["url", "date", "source", "title", "company", "status"],
            delimiter="\t",
        )
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def append_pipeline(path: str, entries: list[dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(f"- [ ] {e['url']} | {e['company']} | {e['title']}\n")


def save_jd(jds_dir: str, job: dict):
    """Save job description as a Markdown file in jds/ directory."""
    os.makedirs(jds_dir, exist_ok=True)
    # Sanitize filename
    slug = re.sub(r"[^\w\u4e00-\u9fff-]", "_", f"{job['company']}-{job['title']}")
    slug = re.sub(r"_+", "_", slug).strip("_")[:80]
    filepath = os.path.join(jds_dir, f"{slug}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {job['title']}\n\n")
        f.write(f"- 公司: {job['company']}\n")
        f.write(f"- 地点: {job.get('location', '')}\n")
        if job.get("department"):
            f.write(f"- 部门: {job['department']}\n")
        if job.get("category"):
            f.write(f"- 类别: {job['category']}\n")
        f.write(f"- 投递链接: {job['url']}\n")
        f.write(f"- 来源: {job.get('source', '')}\n")
        f.write(f"\n---\n\n")
        if job.get("jd"):
            f.write(f"## 岗位职责\n\n{job['jd']}\n")
        if job.get("highlight"):
            f.write(f"\n## 岗位亮点\n\n{job['highlight']}\n")
    return filepath


# ---------------------------------------------------------------------------
# Chinese company API scanners
# ---------------------------------------------------------------------------

def scan_meituan(api_url: str, keywords: str) -> list[dict]:
    """Fetch jobs from Meituan internal API."""
    import urllib.parse
    payload = json.dumps({
        "page": {"pageNo": 1, "pageSize": 100},
        "jobShareType": "1",
        "keywords": keywords,
        "cityList": [],
        "department": [],
        "jfJgList": [],
        "jobType": [{"code": "3", "subCode": []}],
        "typeCode": [],
        "specialCode": [],
    }).encode()

    req = urllib.request.Request(
        api_url, data=payload,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Referer": "https://zhaopin.meituan.com/social-recruitment",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠ 美团 API failed — {e}", file=sys.stderr)
        return []

    jobs = []
    now_ms = int(datetime.now().timestamp() * 1000)
    cutoff_ms = now_ms - MAX_AGE_DAYS * 86400 * 1000
    for j in data.get("data", {}).get("list", []):
        refresh = j.get("refreshTime") or 0
        if refresh < cutoff_ms:
            continue
        cities = ", ".join(c["name"] for c in j.get("cityList", []))
        job_id = j.get("jobUnionId", "")
        dept = ", ".join(d["name"] for d in j.get("department", []))
        jobs.append({
            "title": j.get("name", ""),
            "url": f"https://zhaopin.meituan.com/social-recruitment/detail?jobUnionId={job_id}",
            "company": "美团",
            "location": cities,
            "source": "api:meituan",
            "department": dept,
            "category": j.get("jobFamily", ""),
            "jd": j.get("jobDuty", "") or "",
            "highlight": j.get("highLight", "") or "",
        })
    return jobs


def scan_kuaishou(api_url: str, keywords: str) -> list[dict]:
    """Fetch jobs from Kuaishou via Playwright (requires browser session)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠ 快手: playwright not installed, skipping", file=sys.stderr)
        return []

    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            captured: list[dict] = []

            def on_resp(resp):
                if "positions/simple" in resp.url and resp.status == 200:
                    try:
                        captured.append(resp.json())
                    except Exception:
                        pass

            page.on("response", on_resp)
            page.goto(
                "https://zhaopin.kuaishou.cn/recruit/e/#/official/social/",
                timeout=15000, wait_until="domcontentloaded",
            )
            page.wait_for_timeout(6000)

            if not captured:
                browser.close()
                return []

            now_ms = int(datetime.now().timestamp() * 1000)
            cutoff_ms = now_ms - MAX_AGE_DAYS * 86400 * 1000
            for j in captured[-1].get("result", {}).get("list", []):
                desc = j.get("description", "") or ""
                demand = j.get("positionDemand", "") or ""
                loc_code = j.get("workLocationCode", "")
                job_id = j.get("id", "")
                jobs.append({
                    "title": j.get("name", ""),
                    "url": f"https://zhaopin.kuaishou.cn/recruit/e/#/official/social/{job_id}",
                    "company": "快手",
                    "location": loc_code,
                    "source": "api:kuaishou",
                    "department": "",
                    "category": j.get("positionCategoryCode", ""),
                    "jd": desc + ("\n\n## 任职要求\n\n" + demand if demand else ""),
                    "highlight": "",
                })
            browser.close()
    except Exception as e:
        print(f"  ⚠ 快手: scan failed — {e}", file=sys.stderr)
    return jobs


def scan_didi(api_url: str, keywords: str) -> list[dict]:
    """Fetch jobs from Didi internal API (paginated, max 16 per page)."""
    import subprocess
    jobs = []
    page = 1
    while True:
        try:
            result = subprocess.run(
                ["curl", "-s", f"{api_url}?page={page}&recruitType=1&size=16",
                 "-H", "Referer: https://talent.didiglobal.com/social",
                 "-H", "User-Agent: Mozilla/5.0"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
        except Exception as e:
            print(f"  ⚠ 滴滴 API page {page} failed — {e}", file=sys.stderr)
            break

        items = (data.get("data") or {}).get("items") or []
        if not items:
            break

        for j in items:
            refresh = j.get("refreshTime", "")
            if refresh:
                try:
                    rt = datetime.strptime(refresh, "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - rt).days > MAX_AGE_DAYS:
                        continue
                except Exception:
                    pass
            jd_id = j.get("jdId", "")
            jobs.append({
                "title": j.get("jobName", ""),
                "url": f"https://talent.didiglobal.com/social/position-detail/{jd_id}",
                "company": "滴滴",
                "location": j.get("workArea", ""),
                "source": "api:didi",
                "department": j.get("deptName", ""),
                "category": "",
                "jd": j.get("jobDuty", "") or "",
                "highlight": "",
            })

        total = (data.get("data") or {}).get("total", 0)
        if page * 16 >= total or page >= 10:  # cap at 10 pages
            break
        page += 1
    return jobs


CN_API_SCANNERS = {
    "meituan": scan_meituan,
    "kuaishou": scan_kuaishou,
    "didi": scan_didi,
}


# ---------------------------------------------------------------------------
# Greenhouse API scanner
# ---------------------------------------------------------------------------

def scan_greenhouse(slug: str, company: str) -> list[dict]:
    """Fetch jobs from Greenhouse boards API."""
    url = GREENHOUSE_API.format(slug=slug) + "?content=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠ {company}: Greenhouse API failed — {e}", file=sys.stderr)
        return []

    jobs = []
    cutoff = datetime.now().timestamp() - MAX_AGE_DAYS * 86400
    for job in data.get("jobs", []):
        updated = job.get("updated_at", "")
        if updated:
            try:
                from email.utils import parsedate_to_datetime
                job_ts = datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
                if job_ts < cutoff:
                    continue
            except Exception:
                pass
        loc = job.get("location", {}).get("name", "")
        job_url = job.get("absolute_url", "")
        # content is HTML, strip tags for plain text
        content = job.get("content", "")
        if content:
            content = re.sub(r"<[^>]+>", "", content)
            content = re.sub(r"\s+", " ", content).strip()
        dept_list = job.get("departments", [])
        dept = ", ".join(d.get("name", "") for d in dept_list) if dept_list else ""
        jobs.append({
            "title": job.get("title", ""),
            "url": job_url,
            "company": company,
            "location": loc,
            "source": f"greenhouse:{slug}",
            "department": dept,
            "category": "",
            "jd": content,
            "highlight": "",
        })
    return jobs


# ---------------------------------------------------------------------------
# Web search scanner (Layer 3)
# ---------------------------------------------------------------------------

def scan_web_search(queries: list[dict]) -> list[dict]:
    """Discover jobs via DuckDuckGo HTML search."""
    jobs = []
    for q in queries:
        if not q.get("enabled", True):
            continue
        name = q["name"]
        query = q["query"]
        print(f"  Searching: {name}...")

        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        })
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"    ⚠ failed — {e}", file=sys.stderr)
            continue

        # Extract results: href and title from result__a links
        links = re.findall(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html
        )
        company = name.split("—")[0].strip() if "—" in name else name

        # Noise domains to skip
        _SKIP_DOMAINS = {
            "zhihu.com", "csdn.net", "toutiao.com", "sohu.com",
            "bilibili.com/video", "weixin.qq.com", "mp.weixin.qq.com",
            "cloud.tencent.com", "51cto.com", "jianshu.com",
            "betteryeah.com", "aihub.cn", "learnku.com", "github.com",
            "medium.com", "time.com", "163.com/dy", "news.163.com",
            "new.qq.com", "leiphone.com", "36kr.com", "sspai.com",
        }
        # Noise title keywords (news/articles, not job listings)
        _SKIP_TITLE = [
            "排名", "排行", "盘点", "早报", "官宣", "启动", "发布",
            "首次公开", "密集招", "校招计划", "招聘计划",
            "前景", "趋势", "对比", "综合", "Empire", "Transform",
        ]

        for href, title in links:
            title = title.strip()
            if not title or len(title) < 4:
                continue
            # Unwrap DuckDuckGo redirect
            if "uddg=" in href:
                href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
            if not href.startswith("http"):
                continue
            # Skip noise domains
            if any(d in href for d in _SKIP_DOMAINS):
                continue
            # Skip news/article titles
            if any(k in title for k in _SKIP_TITLE):
                continue

            jobs.append({
                "title": title[:150],
                "url": href,
                "company": company,
                "location": "",
                "source": f"search:{name}",
                "department": "",
                "category": "",
                "jd": "",
                "highlight": "",
            })
        print(f"    Found {len(links)} results")
    return jobs


# ---------------------------------------------------------------------------
# Playwright scanner
# ---------------------------------------------------------------------------

def scan_playwright(company: str, careers_url: str) -> list[dict]:
    """Use Playwright to scrape SPA career pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"  ⚠ {company}: playwright not installed, skipping", file=sys.stderr)
        return []

    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(careers_url, timeout=20000, wait_until="networkidle")
            page.wait_for_timeout(3000)

            # Generic extraction: find all links that look like job listings
            links = page.query_selector_all("a")
            for link in links:
                text = (link.inner_text() or "").strip()
                href = link.get_attribute("href") or ""
                if not text or len(text) < 4 or len(text) > 200:
                    continue
                # Heuristic: job links usually contain keywords
                href_lower = href.lower()
                is_job_link = any(k in href_lower for k in [
                    "job", "position", "career", "recruit", "zhaopin",
                    "detail", "apply",
                ])
                if not is_job_link and not any(
                    k in text for k in ["工程师", "开发", "算法", "产品", "设计",
                                        "Engineer", "Developer", "Manager"]
                ):
                    continue
                # Normalize URL
                if href.startswith("/"):
                    from urllib.parse import urljoin
                    href = urljoin(careers_url, href)
                if not href.startswith("http"):
                    continue
                jobs.append({
                    "title": re.sub(r"\s+", " ", text)[:150],
                    "url": href,
                    "company": company,
                    "location": "",
                    "source": f"playwright:{company}",
                })
            browser.close()
    except Exception as e:
        print(f"  ⚠ {company}: Playwright scan failed — {e}", file=sys.stderr)
    return jobs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scan career portals for job listings")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Portal config YAML")
    parser.add_argument("--greenhouse-only", action="store_true", help="Only scan Greenhouse API")
    parser.add_argument("--playwright-only", action="store_true", help="Only scan Playwright companies")
    parser.add_argument("--cn-only", action="store_true", help="Only scan Chinese company APIs")
    parser.add_argument("--search-only", action="store_true", help="Only run web search queries")
    parser.add_argument("--dry-run", action="store_true", help="Show results without writing files")
    args = parser.parse_args()

    cfg = load_config(args.config)
    tf = cfg.get("title_filter", {})
    loc_filter = cfg.get("location_filter", [])
    seen = load_history(HISTORY_FILE)
    today = datetime.now().strftime("%Y-%m-%d")

    all_jobs: list[dict] = []
    only = args.greenhouse_only or args.playwright_only or args.cn_only or args.search_only

    # --- Chinese company APIs ---
    if not only or args.cn_only:
        print("=== Chinese Company APIs ===")
        for co in cfg.get("cn_api_companies", []):
            if not co.get("enabled", True):
                continue
            scanner = CN_API_SCANNERS.get(co.get("type"))
            if not scanner:
                print(f"  ⚠ Unknown type: {co.get('type')}", file=sys.stderr)
                continue
            print(f"  Scanning {co['name']}...")
            jobs = scanner(co["api_url"], co.get("keywords", ""))
            print(f"    Found {len(jobs)} listings")
            all_jobs.extend(jobs)

    # --- Greenhouse API ---
    if not only or args.greenhouse_only:
        print("=== Greenhouse API ===")
        for co in cfg.get("greenhouse_companies", []):
            if not co.get("enabled", True):
                continue
            print(f"  Scanning {co['name']}...")
            jobs = scan_greenhouse(co["slug"], co["name"])
            print(f"    Found {len(jobs)} listings")
            all_jobs.extend(jobs)

    # --- Playwright ---
    if not only or args.playwright_only:
        print("\n=== Playwright (SPA) ===")
        for co in cfg.get("playwright_companies", []):
            if not co.get("enabled", True):
                continue
            print(f"  Scanning {co['name']}...")
            jobs = scan_playwright(co["name"], co["careers_url"])
            print(f"    Found {len(jobs)} listings")
            all_jobs.extend(jobs)

    # --- Web search (Layer 3) ---
    if not only or args.search_only:
        print("\n=== Web Search ===")
        search_jobs = scan_web_search(cfg.get("search_queries", []))
        print(f"  Total results: {len(search_jobs)}")
        all_jobs.extend(search_jobs)

    # --- Filter & dedup ---
    print(f"\n=== Filtering ===")
    print(f"Total raw listings: {len(all_jobs)}")

    history_rows = []
    pipeline_entries = []
    stats = {"added": 0, "skipped_title": 0, "skipped_dup": 0, "skipped_location": 0}

    seen_urls_this_run: set[str] = set()
    for job in all_jobs:
        url = job["url"]

        # Dedup within this run
        if url in seen_urls_this_run:
            continue
        seen_urls_this_run.add(url)

        # Dedup against history
        if url in seen:
            stats["skipped_dup"] += 1
            continue

        # Location filter
        if loc_filter and job.get("location"):
            if not any(loc in job["location"] for loc in loc_filter):
                stats["skipped_location"] += 1
                history_rows.append({
                    "url": url, "date": today, "source": job["source"],
                    "title": job["title"], "company": job["company"],
                    "status": "skipped_location",
                })
                continue

        # Title filter
        result = matches_job(job, tf)
        if result is None:
            stats["skipped_title"] += 1
            history_rows.append({
                "url": url, "date": today, "source": job["source"],
                "title": job["title"], "company": job["company"],
                "status": "skipped_title",
            })
            continue

        # Pass
        stats["added"] += 1
        pipeline_entries.append(job)
        if job.get("jd"):
            save_jd(JDS_DIR, job)
        history_rows.append({
            "url": url, "date": today, "source": job["source"],
            "title": job["title"], "company": job["company"],
            "status": "added",
        })

    # --- Output ---
    print(f"\nResults:")
    print(f"  Added to pipeline: {stats['added']}")
    print(f"  Skipped (title):   {stats['skipped_title']}")
    print(f"  Skipped (dup):     {stats['skipped_dup']}")
    print(f"  Skipped (location):{stats['skipped_location']}")

    if pipeline_entries:
        print(f"\nNew listings:")
        for e in pipeline_entries:
            boost = ""
            for s in tf.get("seniority_boost", []):
                if s.lower() in e["title"].lower():
                    boost = " ⭐"
                    break
            print(f"  + {e['company']} | {e['title']}{boost}")

    if not args.dry_run:
        if history_rows:
            append_history(HISTORY_FILE, history_rows)
        if pipeline_entries:
            append_pipeline(PIPELINE_FILE, pipeline_entries)
        print(f"\nWritten to {HISTORY_FILE} and {PIPELINE_FILE}")
    else:
        print("\n(dry-run, nothing written)")


if __name__ == "__main__":
    main()
