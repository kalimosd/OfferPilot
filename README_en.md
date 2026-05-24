# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot is a local-first AI career assistant for resume rewriting, JD evaluation, targeted applications, job discovery, application tracking, and interview preparation.

Its core rule is simple: **use the candidate's real experience only. No invented projects, fake metrics, or made-up contact details.**

[中文](./README.md)

![OfferPilot Web UI](docs/web-ui-screenshot.png)

## What This Project Is

OfferPilot is a complete project with three ways to use it:

- **Agent CLI**: the main interface. Ask in natural language and the LangGraph agent routes the task.
- **Web UI**: a local chat, tracker, and outputs dashboard.
- **Skill Pack**: a portable rule layer for Cursor, Claude Code, Codex, and similar coding agents.

```text
skill-pack = rule layer / methodology / portable workflow
agent      = skill-pack + runtime + tools + UI
```

The current agent uses explicit intent routing:

- General career tasks go through the ReAct tool loop.
- Pipeline requests run a deterministic scan, rank, and report workflow.
- Batch evaluation requests use a dedicated batch flow with low-temperature LLM scoring.

## What It Can Do

| Capability | Description |
|---|---|
| Resume optimization | Tighten phrasing and strengthen bullet points |
| Targeted rewrite | Reorder and rewrite experience around a specific JD |
| JD fit analysis | Identify match signals, gaps, keywords, and rewrite priorities |
| Structured evaluation | Score a role across 10 dimensions with an A-F recommendation |
| Batch evaluation | Rank multiple JDs to find roles worth applying to |
| Job discovery | Scan job portals and generate ranked recommendations |
| Application tracking | Manage application statuses and follow-up reminders |
| Cover letter | Generate targeted cover letters from real experience |
| LinkedIn outreach | Generate concise, personalized outreach messages |
| Mock interview | Generate question sheets and evaluation reports |
| Product research | Prepare company and product research before interviews |
| PDF export | Render Markdown outputs to styled PDFs |

## Requirements

- Python 3.10+
- Node.js 18+ for the Web UI
- An LLM API key, such as DeepSeek, Claude, Gemini, or OpenAI
- Recommended: Playwright Chromium for PDF rendering and browser-based scraping

## Installation

```bash
git clone https://github.com/kalimosd/offerpilot-ai.git
cd offerpilot-ai

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
python -m playwright install chromium
```

If you only want the Agent without tests, `pip install -e .` is enough.

## LLM Configuration

Create a local `.env` file in the repository root:

```bash
touch .env
```

Then choose one provider.

### DeepSeek

```bash
OFFERPILOT_MODEL=deepseek-chat
OFFERPILOT_API_KEY=your-deepseek-key
OFFERPILOT_BASE_URL=https://api.deepseek.com
```

### Claude

```bash
OFFERPILOT_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=your-anthropic-key
```

### Gemini

```bash
OFFERPILOT_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-google-key
```

### OpenAI

```bash
OFFERPILOT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-key
```

Optional temperature override:

```bash
OFFERPILOT_TEMPERATURE=0.3
```

OfferPilot also has task defaults in code: `0.3` for general agent work, `0.1` for precise evaluation, and `0.7` for creative writing.

## Prepare Your Data

Create a personal profile store:

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

`profile_store.yaml` is not the final resume. It is your fact database.

Main fields:

| Field | Description |
|---|---|
| `meta` | Name, email, phone, update date |
| `experience` | Work experience with multiple bullets per role |
| `projects` | Side projects, open-source, competitions, school projects |
| `skills` | Skills, level, years, and evidence |
| `education` | Education background |
| `certifications` | Certifications |
| `achievements` | Awards or recognition |

Put job descriptions under `jds/`:

```bash
mkdir -p jds outputs/resumes outputs/pipeline outputs/interview outputs/research outputs/misc
```

Private local files such as `profile_store.yaml`, `jds/`, `outputs/`, and `data/` are intended to stay out of git.

## Run The Agent

Single-shot mode:

```bash
python -m offerpilot.agent "analyze the fit between jds/anthropic-ai-agent-engineer.md and profile_store.yaml"
python -m offerpilot.agent "batch evaluate all JDs in jds/"
python -m offerpilot.agent "run pipeline, scan last 7 days, recommend top 10"
python -m offerpilot.agent "check which applications need follow-up"
```

Interactive mode:

```bash
python -m offerpilot.agent
```

You can also use the installed console script:

```bash
offerpilot-agent "batch evaluate all JDs in jds/"
```

## Web UI

Install backend and frontend dependencies:

```bash
source .venv/bin/activate
pip install -r web/api/requirements.txt

cd web/frontend
npm install
cd ../..
```

Start both services:

```bash
./start.sh
```

Open `http://localhost:3000`.

## Pipeline Workflow

The pipeline is for job discovery and recommendation:

1. Scan configured job portals.
2. Load recent entries from `data/scan-history.tsv`.
3. Score jobs using portal config, profile tags, and bilingual skill aliases.
4. Deduplicate and rank candidates.
5. Write a Markdown report to `outputs/pipeline/pipeline_recommendations.md`.

## Skill Pack Mode

Use `skill-pack/` when you want a portable workflow for an AI coding agent rather than the built-in OfferPilot agent.

If you only want the standalone Skill Pack rule layer, switch to the [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) branch.

Recommended reading order:

1. `skill-pack/WORKFLOW.md`
2. `skill-pack/INPUTS.md`
3. `skill-pack/JD_MATCHING.md` for China-first JD matching
4. `skill-pack/EVALUATION.md` for structured scoring
5. `skill-pack/TRACKER.md` for application tracking
6. `skill-pack/OUTREACH.md` for outreach messages
7. `skill-pack/scripts/README.md` when local helpers are needed
8. `skill-pack/adapters/` for Cursor, Claude Code, or Codex wrappers

Useful helper scripts:

```bash
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md
python skill-pack/scripts/extract_text.py resume.pdf
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md
```

## Output Directories

| Directory | Content |
|---|---|
| `outputs/resumes/` | Resume optimization, targeted rewrites, JD fit, structured evaluation |
| `outputs/research/` | Product research |
| `outputs/interview/` | Interview question sheets and evaluation reports |
| `outputs/pipeline/` | Job discovery and recommendation reports |
| `outputs/misc/` | Outreach messages, project explanations, other materials |

Do not place final deliverables directly under the `outputs/` root.

## Development

Run tests:

```bash
source .venv/bin/activate
python -m pytest
```

Quick graph compile smoke test:

```bash
python - <<'PY'
from unittest.mock import Mock, patch
from offerpilot.graph import build_graph

with patch("offerpilot.graph.get_llm") as get_llm:
    llm = Mock()
    llm.bind_tools.return_value.invoke.return_value = "ok"
    get_llm.return_value = llm
    print(type(build_graph()).__name__)
PY
```

Expected output:

```text
CompiledStateGraph
```

## Project Structure

```text
.
├── offerpilot/
│   ├── agent.py            # CLI entry
│   ├── graph.py            # LangGraph routing and workflows
│   ├── intent.py           # Intent classification
│   ├── llm.py              # Multi-provider LLM initialization
│   ├── script_loader.py    # Legacy script module loader
│   ├── state.py            # Graph state
│   └── tools.py            # Agent tools
├── skill-pack/             # Portable workflow docs, adapters, scripts, data
├── web/
│   ├── api/                # FastAPI backend
│   └── frontend/           # Next.js frontend
├── tests/                  # Unit and integration tests
├── outputs/                # Generated local outputs
├── jds/                    # Local job descriptions
├── data/                   # Tracker and scan history
└── profile_store.yaml      # Local personal profile store
```

## License

MIT
