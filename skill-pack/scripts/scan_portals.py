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


class ConfigError(ValueError):
    """Raised when a portal config file is missing, malformed, or not a mapping."""


class BossScanError(RuntimeError):
    """Raised when the Boss scanner cannot start (missing browser, locked profile)."""


def _as_text(value) -> str:
    """Normalize an API/JSON field to a stripped string without raising."""
    if value is None:
        return ""
    return str(value).strip()


def _as_str_list(value) -> list[str]:
    """Normalize a scalar/list field to a clean list of non-empty strings."""
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def _ensure_playwright_browsers_path() -> None:
    """Ensure PLAYWRIGHT_BROWSERS_PATH points to an existing Chromium installation."""
    env_key = "PLAYWRIGHT_BROWSERS_PATH"
    current = os.environ.get(env_key, "")
    default_cache = Path.home() / "Library" / "Caches" / "ms-playwright"

    def _has_chromium(base: Path) -> bool:
        return base.exists() and any(base.glob("chromium-*/chrome-*"))

    if current and _has_chromium(Path(current)):
        return
    if _has_chromium(default_cache):
        if current:
            os.environ[env_key] = str(default_cache)
        return

    os.environ.pop(env_key, None)
    import subprocess
    print("  Chromium not found in current environment, installing via playwright...", file=sys.stderr)
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
    )


def load_config(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in config file {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"config file {path} must contain a YAML mapping")
    return data


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
        _ensure_playwright_browsers_path()
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
    jobs = []
    page = 1
    while True:
        try:
            req = urllib.request.Request(
                f"{api_url}?page={page}&recruitType=1&size=16",
                headers={
                    "Referer": "https://talent.didiglobal.com/social",
                    "User-Agent": "Mozilla/5.0",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
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
                job_ts = datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
                if job_ts < cutoff:
                    continue
            except Exception:
                pass
        loc = job.get("location", {}).get("name", "")
        job_url = job.get("absolute_url", "")
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

        links = re.findall(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html
        )
        company = name.split("—")[0].strip() if "—" in name else name

        _SKIP_DOMAINS = {
            "zhihu.com", "csdn.net", "toutiao.com", "sohu.com",
            "bilibili.com/video", "weixin.qq.com", "mp.weixin.qq.com",
            "cloud.tencent.com", "51cto.com", "jianshu.com",
            "betteryeah.com", "aihub.cn", "learnku.com", "github.com",
            "medium.com", "time.com", "163.com/dy", "news.163.com",
            "new.qq.com", "leiphone.com", "36kr.com", "sspai.com",
        }
        _SKIP_TITLE = [
            "排名", "排行", "盘点", "早报", "官宣", "启动", "发布",
            "首次公开", "密集招", "校招计划", "招聘计划",
            "前景", "趋势", "对比", "综合", "Empire", "Transform",
        ]

        for href, title in links:
            title = title.strip()
            if not title or len(title) < 4:
                continue
            if "uddg=" in href:
                href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
            if not href.startswith("http"):
                continue
            if any(d in href for d in _SKIP_DOMAINS):
                continue
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
        _ensure_playwright_browsers_path()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(careers_url, timeout=20000, wait_until="networkidle")
            page.wait_for_timeout(3000)

            links = page.query_selector_all("a")
            for link in links:
                text = (link.inner_text() or "").strip()
                href = link.get_attribute("href") or ""
                if not text or len(text) < 4 or len(text) > 200:
                    continue
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
# 猎聘 scanner — Playwright intercepts API responses
# ---------------------------------------------------------------------------

LIEPIN_CITY_CODES = {
    "上海": "020", "南京": "070", "苏州": "110", "杭州": "090",
    "北京": "010", "深圳": "050", "广州": "040", "成都": "140",
    "武汉": "170", "合肥": "130", "西安": "220",
}


def scan_liepin(queries: list[dict]) -> list[dict]:
    """Search 猎聘 by conditions. Uses Playwright to intercept the search API
    (api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠ 猎聘: playwright not installed, skipping", file=sys.stderr)
        return []

    jobs = []
    try:
        _ensure_playwright_browsers_path()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                locale="zh-CN",
            )
            page = context.new_page()

            for q in queries:
                if not isinstance(q, dict) or not q.get("enabled", True):
                    continue
                keywords = _as_str_list(q.get("keywords"))
                cities = _as_str_list(q.get("cities"))
                name = _as_text(q.get("name")) or ",".join(keywords)
                work_years = _as_str_list(q.get("work_year_codes"))
                for keyword in keywords:
                    for city in cities:
                        city_code = LIEPIN_CITY_CODES.get(city, "")
                        if not city_code:
                            print(f"  ⚠ 猎聘: unknown city code {city}", file=sys.stderr)
                            continue

                        search_url = (
                            f"https://www.liepin.com/zhaopin/"
                            f"?key={urllib.parse.quote(keyword)}"
                            f"&dqs={city_code}"
                        )
                        if work_years:
                            search_url += "&workYearCode=" + ",".join(work_years)

                        print(f"  猎聘: {keyword} @ {city}...")

                        captured: list[dict] = []

                        def _on_response(resp):
                            if "pc-search-job" in resp.url and "cond-init" not in resp.url:
                                try:
                                    captured.append(resp.json())
                                except Exception:
                                    pass

                        page.on("response", _on_response)

                        try:
                            page.goto(search_url, timeout=25000, wait_until="domcontentloaded")
                            page.wait_for_timeout(3000)
                        except Exception as e:
                            print(f"    ⚠ load failed — {e}", file=sys.stderr)
                            page.remove_listener("response", _on_response)
                            continue

                        page.remove_listener("response", _on_response)

                        if not captured:
                            print("    No API responses captured (possible block)")
                            continue

                        for data in captured:
                            if data.get("flag") != 1:
                                continue
                            inner = (data.get("data") or {}).get("data") or {}
                            job_cards = inner.get("jobCardList") or []
                            total = inner.get("total", 0)
                            for j in job_cards:
                                job = j.get("job") or {}
                                comp = j.get("comp") or {}
                                comp_name = comp.get("compName", "")
                                if comp_name.startswith("某"):
                                    continue
                                job_id = job.get("jobId", "")
                                liepin_url = (
                                    f"https://www.liepin.com/job/{job_id}.shtml"
                                    if job_id else ""
                                )
                                jobs.append({
                                    "title": job.get("title", ""),
                                    "url": liepin_url,
                                    "company": comp.get("compName", ""),
                                    "location": job.get("dq", ""),
                                    "source": f"liepin:{name}",
                                    "department": "",
                                    "category": job.get("jobKind", ""),
                                    "jd": f"{job.get('requireWorkYears','')} / {job.get('requireEduLevel','')} / {job.get('salary','')}",
                                    "highlight": f"规模: {comp.get('compScale','')} / 行业: {comp.get('compIndustry','')}",
                                })
                            print(f"    Found {len(job_cards)} listings (total: {total})")

            browser.close()
    except Exception as e:
        print(f"  ⚠ 猎聘 scan failed — {e}", file=sys.stderr)
    return jobs


# ---------------------------------------------------------------------------
# Boss直聘 scanner — Persistent headful context + API interception & DOM fallback
# ---------------------------------------------------------------------------

BOSS_CITY_CODES = {
    "全国": "100010000",
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280100",
    "深圳": "101280600",
    "杭州": "101210100",
    "南京": "101190100",
    "苏州": "101190400",
    "成都": "101270100",
    "武汉": "101200100",
    "合肥": "101220100",
    "西安": "101110100",
}

BOSS_PROFILE_DIR = "data/boss_browser_profile"


def _parse_boss_api_job(j: dict, query_name: str) -> dict | None:
    """Convert a Boss直聘 /wapi/zpgeek/search/joblist.json item into OfferPilot job dict."""
    if not isinstance(j, dict):
        return None
    encrypt_id = _as_text(j.get("encryptJobId"))
    title = _as_text(j.get("jobName"))
    if not encrypt_id or not title:
        return None

    city = _as_text(j.get("cityName"))
    district = _as_text(j.get("areaDistrict"))
    loc = f"{city} {district}".strip()
    salary = _as_text(j.get("salaryDesc"))
    exp = _as_text(j.get("jobExperience"))
    degree = _as_text(j.get("jobDegree"))
    all_tags = [*_as_str_list(j.get("skills")), *_as_str_list(j.get("jobLabels"))]

    jd_lines = [f"基本要求: {exp} / {degree} / {salary}"]
    if all_tags:
        jd_lines.append("技能标签: " + " / ".join(dict.fromkeys(all_tags)))

    highlight_parts = []
    scale = _as_text(j.get("brandScaleName"))
    industry = _as_text(j.get("brandIndustry"))
    stage = _as_text(j.get("brandStageName"))
    if scale:
        highlight_parts.append(f"规模: {scale}")
    if industry:
        highlight_parts.append(f"行业: {industry}")
    if stage:
        highlight_parts.append(f"阶段: {stage}")

    return {
        "title": title,
        "url": f"https://www.zhipin.com/job_detail/{encrypt_id}.html",
        "company": _as_text(j.get("brandName")),
        "location": loc,
        "source": f"api:boss:{query_name}",
        "department": "",
        "category": "",
        "jd": "\n".join(jd_lines),
        "highlight": " / ".join(highlight_parts),
    }


def _parse_boss_dom_card(card: dict, query_name: str, fallback_city: str) -> dict | None:
    """Convert a DOM-extracted Boss card into an OfferPilot job dict."""
    if not isinstance(card, dict):
        return None
    title = _as_text(card.get("title"))
    url = _as_text(card.get("url"))
    if not title or not url.startswith(("http://", "https://")):
        return None
    skills = _as_str_list(card.get("skills"))
    salary = _as_text(card.get("salary"))
    jd_lines = []
    if salary:
        jd_lines.append(f"薪资: {salary}")
    if skills:
        jd_lines.append("技能标签: " + " / ".join(skills))
    return {
        "title": title,
        "url": url,
        "company": _as_text(card.get("company")) or "Boss直聘企业",
        "location": _as_text(card.get("location")) or fallback_city,
        "source": f"dom:boss:{query_name}",
        "department": "",
        "category": "",
        "jd": "\n".join(jd_lines),
        "highlight": "",
    }


def _is_success_boss_payload(payload) -> bool:
    return isinstance(payload, dict) and payload.get("code") == 0


def _boss_error_summary(payload) -> str:
    if not isinstance(payload, dict):
        return "非 JSON 对象响应"
    code = payload.get("code")
    message = _as_text(payload.get("message")) or _as_text(payload.get("msg"))
    return f"code={code}" + (f" {message}" if message else "")


def _extract_boss_jobs(payload, query_name: str) -> list[dict]:
    """Safely extract jobs from one Boss joblist payload."""
    if not _is_success_boss_payload(payload):
        return []
    zp_data = payload.get("zpData")
    if not isinstance(zp_data, dict):
        return []
    job_list = zp_data.get("jobList")
    if not isinstance(job_list, list):
        return []
    jobs = []
    for item in job_list:
        parsed = _parse_boss_api_job(item, query_name)
        if parsed is not None:
            jobs.append(parsed)
    return jobs


def _build_boss_search_url(keyword: str, city_code: str, experience: str = "") -> str:
    url = (
        "https://www.zhipin.com/web/geek/job"
        f"?query={urllib.parse.quote(keyword)}&city={city_code}"
    )
    if experience:
        url += f"&experience={experience}"
    return url


def _boss_needs_interaction(url: str) -> bool:
    return "verify-slider" in url or "safe/" in url or "login" in url


def _launch_boss_context(p, profile_dir: Path, headless: bool):
    try:
        return p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            viewport={"width": 1366, "height": 860},
        )
    except Exception as exc:
        raise BossScanError(
            f"Boss 浏览器启动失败（{profile_dir} 可能被占用；请关闭残留 Chromium 后重试）: {exc}"
        ) from exc


def scan_boss(queries: list[dict], headless: bool = False) -> list[dict]:
    """Search Boss直聘 using a persistent Chromium profile (`data/boss_browser_profile`).

    Why this works where standard headless scrapers fail:
    1. Reuses persistent cookies/session in `data/boss_browser_profile` so you only scan QR once.
    2. Disables `AutomationControlled` blink feature and masks `navigator.webdriver`.
    3. Intercepts `/wapi/zpgeek/search/joblist.json` AND falls back to live DOM extraction.
    4. If slider verification (`verify-slider`) or login appears, pauses up to 45s for user interaction.
    """
    if not queries:
        return []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BossScanError(
            "playwright 未安装，无法扫描 Boss直聘；请先运行 pip install playwright"
        ) from exc

    profile_dir = Path(BOSS_PROFILE_DIR)
    profile_dir.mkdir(parents=True, exist_ok=True)
    jobs: list[dict] = []

    try:
        _ensure_playwright_browsers_path()
    except Exception as exc:
        raise BossScanError(f"Playwright 浏览器准备失败: {exc}") from exc

    try:
        with sync_playwright() as p:
            context = _launch_boss_context(p, profile_dir, headless)
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            page = context.pages[0] if context.pages else context.new_page()

            for q in queries:
                if not isinstance(q, dict) or not q.get("enabled", True):
                    continue
                keywords = _as_str_list(q.get("keywords"))
                cities = _as_str_list(q.get("cities"))
                name = _as_text(q.get("name")) or ",".join(keywords)
                experience_code = _as_text(q.get("experience"))  # "104"=1-3年, "105"=3-5年
                for keyword in keywords:
                    for city in cities:
                        city_code = BOSS_CITY_CODES.get(city)
                        if not city_code:
                            print(f"  ⚠ Boss直聘: unknown city {city}, skipping", file=sys.stderr)
                            continue
                        search_url = _build_boss_search_url(keyword, city_code, experience_code)

                        print(f"  Boss直聘: {keyword} @ {city}...")
                        captured: list[dict] = []
                        errors: list[dict] = []

                        def _on_boss_resp(resp):
                            if "zpgeek/search/joblist.json" not in resp.url:
                                return
                            try:
                                payload = resp.json()
                            except Exception:
                                return
                            if _is_success_boss_payload(payload):
                                captured.append(payload)
                            elif isinstance(payload, dict):
                                errors.append(payload)

                        page.on("response", _on_boss_resp)
                        needs_retry = False
                        try:
                            page.goto(search_url, timeout=25000, wait_until="domcontentloaded")
                            page.wait_for_timeout(4000)

                            # Check if redirected to slider verification or login
                            if _boss_needs_interaction(page.url):
                                print(
                                    "    ⏸ 检测到 Boss直聘安全验证或登录提示，请在弹出的浏览器窗口中完成扫码/验证（等待最多 45 秒）..."
                                )
                                needs_retry = True
                                for _ in range(15):
                                    page.wait_for_timeout(3000)
                                    if captured or not _boss_needs_interaction(page.url):
                                        break

                            # Completing login/verification often lands on a non-search
                            # page, so re-issue the search once the user is through.
                            if needs_retry and not captured:
                                print("    ↻ 验证结束，重新发起搜索...")
                                page.goto(search_url, timeout=25000, wait_until="domcontentloaded")
                                page.wait_for_timeout(4000)
                        except Exception as e:
                            print(f"    ⚠ load failed — {e}", file=sys.stderr)
                            page.remove_listener("response", _on_boss_resp)
                            continue

                        page.remove_listener("response", _on_boss_resp)

                        batch_count = 0
                        for payload in captured:
                            payload_jobs = _extract_boss_jobs(payload, name)
                            jobs.extend(payload_jobs)
                            batch_count += len(payload_jobs)
                        if batch_count == 0 and errors:
                            print(
                                f"    ⚠ Boss直聘 API 未返回岗位（{_boss_error_summary(errors[-1])}）；"
                                f"可能是登录态失效，请在浏览器中重新扫码，或删除 {BOSS_PROFILE_DIR} 后重试",
                                file=sys.stderr,
                            )

                        # DOM fallback if API response wasn't captured (e.g. SSR or cached state)
                        if batch_count == 0:
                            try:
                                dom_cards = page.evaluate(
                                    """() => {
                                        const cards = document.querySelectorAll('.job-card-wrapper, .job-card-body, li.job-card-box');
                                        return Array.from(cards).map(c => {
                                            const linkEl = c.querySelector('a.job-card-left, a[href*="/job_detail/"]');
                                            const titleEl = c.querySelector('.job-name, .job-title');
                                            const compEl = c.querySelector('.company-name a, .company-name');
                                            const salEl = c.querySelector('.salary');
                                            const areaEl = c.querySelector('.job-area');
                                            const tags = Array.from(c.querySelectorAll('.tag-list li, .job-card-footer li')).map(e => e.innerText.trim()).filter(Boolean);
                                            return {
                                                title: titleEl ? titleEl.innerText.trim() : '',
                                                url: linkEl ? linkEl.href.split('?')[0] : '',
                                                company: compEl ? compEl.innerText.trim() : '',
                                                location: areaEl ? areaEl.innerText.trim() : '',
                                                salary: salEl ? salEl.innerText.trim() : '',
                                                skills: tags
                                            };
                                        }).filter(x => x.title && x.url);
                                    }"""
                                )
                                for card in dom_cards or []:
                                    parsed = _parse_boss_dom_card(card, name, city)
                                    if parsed is not None:
                                        jobs.append(parsed)
                                        batch_count += 1
                            except Exception:
                                pass

                        print(f"    Found {batch_count} listings")
                        page.wait_for_timeout(3000)

            context.close()
    except BossScanError:
        raise
    except Exception as e:
        print(f"  ⚠ Boss直聘 scan failed — {e}", file=sys.stderr)
    return jobs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan career portals for job listings")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Portal config YAML")
    parser.add_argument("--greenhouse-only", action="store_true", help="Only scan Greenhouse API")
    parser.add_argument("--playwright-only", action="store_true", help="Only scan Playwright companies")
    parser.add_argument("--cn-only", action="store_true", help="Only scan Chinese company APIs")
    parser.add_argument("--search-only", action="store_true", help="Only run web search queries")
    parser.add_argument("--liepin-only", action="store_true", help="Only scan 猎聘")
    parser.add_argument("--boss-only", action="store_true", help="Only scan Boss直聘 (persistent browser)")
    parser.add_argument("--dry-run", action="store_true", help="Show results without writing files")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except (OSError, ConfigError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    tf = cfg.get("title_filter", {})
    loc_filter = cfg.get("location_filter", [])
    seen = load_history(HISTORY_FILE)
    today = datetime.now().strftime("%Y-%m-%d")

    all_jobs: list[dict] = []
    boss_failed = False
    only = (args.greenhouse_only or args.playwright_only or args.cn_only or
            args.search_only or args.liepin_only or args.boss_only)

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

    # --- 猎聘 (条件搜索) ---
    if not only or args.liepin_only:
        print("\n=== 猎聘 ===")
        liepin_jobs = scan_liepin(cfg.get("liepin_queries", []))
        print(f"  Total results: {len(liepin_jobs)}")
        all_jobs.extend(liepin_jobs)

    # --- Boss直聘 (默认仅在指定 --boss-only 或配置开启时运行，弹出持久化有头窗口) ---
    if args.boss_only or (not only and cfg.get("boss_auto_scan", False)):
        print("\n=== Boss直聘 (Persistent Browser) ===")
        try:
            boss_jobs = scan_boss(cfg.get("boss_queries", []))
        except BossScanError as exc:
            print(f"  ⚠ {exc}", file=sys.stderr)
            boss_jobs = []
            boss_failed = True
        print(f"  Total results: {len(boss_jobs)}")
        all_jobs.extend(boss_jobs)

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

        # Skip anonymous company listings (某XX公司)
        company = job.get("company") or ""
        if company.startswith("某"):
            stats["skipped_title"] += 1
            continue

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

    if boss_failed and args.boss_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
