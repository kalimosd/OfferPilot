<div align="center">

# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

[![Claude Code](https://img.shields.io/badge/Claude_Code-000?style=flat&logo=anthropic&logoColor=white)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-000?style=flat&logo=cursor&logoColor=white)](https://cursor.com)
[![Codex](https://img.shields.io/badge/Codex-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![Kiro](https://img.shields.io/badge/Kiro-FF9900?style=flat&logo=amazon&logoColor=white)](https://kiro.dev)

**AI job assistant that turns weak applications into interview-ready ones.**

Your resume reads like a job description copy-paste?<br>
Your cover letter could belong to literally anyone?<br>
Your strongest projects are buried on page two?<br>
You did the work — but the paper doesn't show it?

Stop underselling yourself. Let AI sharpen what's already true.

Feed in your resume and a job description,<br>
get back a stronger resume, a tailored rewrite, a JD-fit analysis, or a cover letter —<br>
grounded in your real experience, not hallucinated fluff.

[Features](#features) · [Quick Start](#quick-start) · [Example](#example-output) · [Advanced Usage](#advanced-usage) · [Roadmap](#roadmap) · [Contributing](#contributing--feedback)

[中文](./README_zh.md)

</div>

---

## Why This Project

Many international students and early-career candidates do strong work but present it weakly. Their resumes are too generic, their cover letters feel interchangeable, and their most relevant experience gets buried.

OfferPilot focuses on outcomes: clearer positioning, stronger materials, and better odds of getting interviews.

## Features

| Feature | Description |
|---------|-------------|
| **Resume optimization** | Tightens wording, removes filler, strengthens bullet points — without inventing facts |
| **Job-targeted rewriting** | Rewrites and reorders content around a specific job description |
| **JD fit analysis** | Identifies match signals, gaps, and rewrite priorities |
| **Cover letter generation** | Produces concise, tailored letters grounded in real experience |
| **Profile datastore** | Pulls the most relevant experience from a structured YAML data source |
| **Job discovery** | Scans career portals and search engines to find relevant openings automatically |
| **PDF export** | Renders Markdown drafts to styled PDFs with photo embedding support |

## Quick Start

1. Prepare `resume.md` (or `resume.pdf`)
2. Prepare `job.md` for the target role
3. Open `skill-pack/README.md` and follow the read order
4. Use short triggers in your agent, e.g.:
   - `optimize my resume with offerpilot`
   - `run JD fit analysis with offerpilot`
   - `/offerpilot recommend 10 jobs based on my resume`
5. Review the generated Markdown output, then export when ready

## Example Output

**Before**

```text
- Responsible for Android development and worked with different teams.
- Helped fix bugs and improve app performance.
```

**After**

```text
- Improved Android system stability and performance by diagnosing rendering,
  memory, and ANR issues with Perfetto and Systrace, then driving fixes
  across platform teams.
- Owned delivery for recent-tasks features, coordinating engineering
  stakeholders to ship on schedule and close cross-team issues faster.
```

These outputs are meant to be directly usable with minimal editing.

## Tech Stack

- Python · LLM-powered rewriting and analysis
- Modular skill-pack architecture
- YAML-based profile datastore
- Playwright-based PDF export and portal scanning

## Project Structure

```text
.
├── README.md               # English (default)
├── README_zh.md            # 中文
├── profile_store.yaml      # your personal material library (gitignored)
├── portals_cn.yml
├── skill-pack/
│   ├── README.md           # skill pack entry point
│   ├── WORKFLOW.md         # task flow and checkpoints
│   ├── DATASTORE.md        # profile datastore spec
│   ├── JD_MATCHING.md      # China-first JD matching
│   ├── INPUTS.md / OUTPUTS.md / PROMPTS.md
│   ├── adapters/           # Claude Code, Codex, Cursor wrappers
│   ├── examples/           # sample outputs
│   ├── data/               # skill alias mappings
│   └── scripts/            # extract, render, scan, validate
├── jds/                    # (gitignored) saved JDs from scans
├── data/                   # (gitignored) scan history
└── tests/
```

## Advanced Usage

Optional CLI (skill-pack is the primary entry point):

```bash
# See all commands
offerpilot

# Extract source file text
offerpilot extract "resume.pdf" --output "resume.txt"

# Export PDF
offerpilot pdf "resume.md" "resume.pdf" --style classic

# Scan job portals
offerpilot scan --cn-only

# Minimal flow: validate input + export resume PDF
offerpilot run "resume.md" "outputs/resume.pdf" --style ats

# End-to-end pipeline: scan + rank + top-N recommendations
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

Direct script calls:

```bash
# Extract text from PDF or DOCX
python3 skill-pack/scripts/extract_text.py "resume.pdf" --output "resume.txt"

# Export reviewed draft to PDF
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --document-type resume --style classic

# Export with photo embedded in header
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --style standard_cn --photo "photo.jpg"

# Scan career portals
python3 skill-pack/scripts/scan_portals.py              # full scan
python3 skill-pack/scripts/scan_portals.py --cn-only     # CN APIs only
python3 skill-pack/scripts/scan_portals.py --greenhouse-only  # international
python3 skill-pack/scripts/scan_portals.py --search-only # web search only
python3 skill-pack/scripts/scan_portals.py --dry-run     # preview
```

Matched jobs are saved to `jds/` with full JD content and application links. Scan history is tracked in `data/scan-history.tsv` for deduplication.

## Roadmap

- RAG-based job search and resume knowledge system
- Interview simulation and feedback
- Better datastore retrieval and ranking
- Agent-driven application workflows
- Resume versioning and targeting automation

## Contributing / Feedback

Feedback, issues, and pull requests are welcome.

If you want to improve the workflow, test the output quality, or suggest product directions — open an issue or start a discussion.

---

<div align="center">

Work matters. After school ends, it quietly takes over most of your waking hours — that's just how it is.

But work isn't everything. You weren't put on this earth to optimize bullet points.

You did real things. You solved real problems. You stayed late, shipped on time, cleaned up someone else's mess, and nobody wrote it down properly — least of all you.

This project won't change your life. But if it helps one person stop underselling themselves, stop copy-pasting the same generic resume into the void, and actually land an interview they deserve —

that's enough.

Go get the offer. Then close the laptop and live.

</div>
