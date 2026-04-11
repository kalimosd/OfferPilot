<div align="center">

# OfferPilot AI

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

## Quick Start (Skills-First)

1. Prepare `resume.md` (or `resume.pdf`)
2. Prepare `job.md` for the target role
3. Open `skill-pack/README.md` and follow the read order
4. Trigger with a short intent in your agent, such as:
   - `按照 offerpilot 优化简历`
   - `用 offerpilot 做 JD 匹配`
   - `/offerpilot 根据我简历推荐10个岗位`
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
├── README.md
├── README_zh.md
├── profile_store.yaml        # your personal material library (gitignored)
├── portals_cn.yml
├── skill-pack/
│   ├── README.md             # skill pack entry point
│   ├── WORKFLOW.md           # task flow and checkpoints
│   ├── DATASTORE.md          # profile datastore spec
│   ├── JD_MATCHING.md        # China-first JD matching
│   ├── INPUTS.md / OUTPUTS.md / PROMPTS.md
│   ├── adapters/             # Claude Code, Codex, Cursor wrappers
│   ├── examples/             # sample outputs
│   ├── data/                 # skill alias mappings
│   └── scripts/              # extract, render, scan, validate
├── jds/                      # (gitignored) saved JDs from scans
├── data/                     # (gitignored) scan history
└── tests/
```

## Optional Helper Commands (CLI)

`skill-pack` is the primary product surface. CLI is an optional helper executor.

```bash
# Show all commands
offerpilot

# Extract source text
offerpilot extract "resume.pdf" --output "resume.txt"

# Render PDF
offerpilot pdf "resume.md" "resume.pdf" --style classic

# Scan job portals
offerpilot scan --cn-only

# Minimal pipeline: validate input + render resume PDF
offerpilot run "resume.md" "outputs/resume.pdf" --style ats

# End-to-end job pipeline: scan + rank + Top-N recommendations
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

Direct script usage (also optional):

Extract text from PDF or DOCX:

```bash
python3 skill-pack/scripts/extract_text.py "resume.pdf" --output "resume.txt"
```

Export a reviewed draft to PDF:

```bash
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --document-type resume --style classic
```

Export with a photo embedded in the header:

```bash
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --style standard_cn --photo "photo.jpg"
```

Scan career portals for matching job listings:

```bash
# Full scan (CN APIs + Greenhouse + web search)
python3 skill-pack/scripts/scan_portals.py

# Chinese company APIs only (Meituan, Kuaishou, Didi)
python3 skill-pack/scripts/scan_portals.py --cn-only

# Greenhouse API only (international companies)
python3 skill-pack/scripts/scan_portals.py --greenhouse-only

# Web search only (DuckDuckGo, covers 20+ companies)
python3 skill-pack/scripts/scan_portals.py --search-only

# Preview without writing files
python3 skill-pack/scripts/scan_portals.py --dry-run
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

## Last Words

Work matters. After school ends, it quietly takes over most of your waking hours — that's just how it is.

But work isn't everything. You weren't put on this earth to optimize bullet points.

You did real things. You solved real problems. You stayed late, shipped on time, cleaned up someone else's mess, and nobody wrote it down properly — least of all you.

This project won't change your life. But if it helps one person stop underselling themselves, stop copy-pasting the same generic resume into the void, and actually land an interview they deserve —

that's enough.

Go get the offer. Then close the laptop and live.
