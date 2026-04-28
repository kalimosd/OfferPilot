<div align="center">

# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

**AI career assistant that turns weak applications into interview-ready ones.**

Feed it your resume and a JD — get back a stronger resume, a targeted rewrite, a fit analysis, or a cover letter. Based on your real experience, no fabrication.

[Features](#features) · [Quick Start](#quick-start) · [Agent Mode](#agent-mode) · [Web UI](#web-ui) · [Project Structure](#project-structure)

[中文](./README_zh.md)

</div>

---

## Features

| Feature | Description |
|---------|-------------|
| **Resume Optimization** | Tighten phrasing, remove filler, strengthen bullet points — no fabrication |
| **Targeted Rewrite** | Rewrite and reorder content around a target JD |
| **JD Fit Analysis** | Identify match signals, gaps, and rewrite priorities |
| **Structured Evaluation** | 10-dimension scoring + A-F grade for quantified job fit |
| **Cover Letter** | Generate concise, targeted cover letters from real experience |
| **Profile Datastore** | Select the most relevant experience from a structured YAML library |
| **Job Discovery** | Auto-scan career sites (Meituan/Kuaishou/Didi + Greenhouse + DuckDuckGo) |
| **Application Tracker** | Track status (discovered → applied → interviewing → offer/rejected), auto follow-up reminders |
| **Batch Evaluation** | Evaluate multiple JDs at once, quickly filter worth-applying positions |
| **Mock Interview** | Generate interview questions based on JD and profile, simulate and evaluate |
| **Product Research** | Research target products with competitor analysis and interview predictions |
| **LinkedIn Outreach** | Generate targeted LinkedIn outreach messages |
| **PDF Export** | Markdown → styled PDF with photo embedding support |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/kalimosd/offerpilot-ai.git
cd offerpilot-ai
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure LLM (supports DeepSeek / Claude / Gemini / OpenAI)
cp .env.example .env
# Edit .env with your API key

# 3. Run Agent
python -m offerpilot.agent "optimize my resume from profile_store.yaml"
```

## Agent Mode

OfferPilot Agent is built on **LangGraph** with automatic task classification, tool calling, and output generation.

### Supported LLMs

Switch via environment variables:

```bash
# DeepSeek (default)
OFFERPILOT_MODEL=deepseek-chat
OFFERPILOT_API_KEY=your-key
OFFERPILOT_BASE_URL=https://api.deepseek.com

# Claude
OFFERPILOT_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=your-key

# Gemini
OFFERPILOT_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-key
```

### Usage Examples

```bash
# Single-shot mode
python -m offerpilot.agent "analyze the fit between jds/xxx.md and profile_store.yaml"
python -m offerpilot.agent "batch evaluate all JDs in jds/ directory"
python -m offerpilot.agent "run pipeline, scan last 7 days, recommend Top 10"
python -m offerpilot.agent "check which applications need follow-up"

# Interactive mode
python -m offerpilot.agent
> optimize my resume
> target rewrite for this JD
> export PDF
> exit
```

## Web UI

Next.js frontend + FastAPI backend with three pages: Chat, Tracker, Outputs.

```bash
# One command to start both
./start.sh

# Or manually:
# Terminal 1: uvicorn web.api.main:app --port 8000
# Terminal 2: cd web/frontend && npm run dev
```

Open http://localhost:3000

## Tech Stack

- **Agent Framework**: LangGraph (state graph + ReAct) + LangChain (tool calling, multi-provider)
- **LLM**: DeepSeek / Claude / Gemini / OpenAI (env var switch)
- **Web UI**: Next.js + shadcn/ui (frontend), FastAPI + SSE (backend)
- **PDF & Scraping**: Playwright
- **Data**: YAML (profile), TSV (tracker, scan history)

## Project Structure

```text
.
├── offerpilot/
│   ├── agent.py            # CLI entry (single-shot + interactive)
│   ├── graph.py            # LangGraph graph + system prompt
│   ├── tools.py            # 12 agent tools
│   ├── llm.py              # Multi-provider LLM init
│   ├── state.py            # Graph state definition
│   └── cli.py              # Optional CLI helper
├── web/
│   ├── api/                # FastAPI backend
│   └── frontend/           # Next.js frontend
├── skill-pack/             # Modular skill documents + scripts
├── outputs/
│   ├── resumes/            # Resumes, rewrites, fit analysis
│   ├── research/           # Product research
│   ├── interview/          # Interview prep
│   ├── pipeline/           # Scan recommendations
│   └── misc/               # Other
├── profile_store.yaml      # Personal material library (not in git)
├── jds/                    # Scanned JDs (not in git)
└── start.sh                # One-command web UI launcher
```

## License

MIT
