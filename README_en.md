# OfferPilot AI Skill Pack

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot Skill Pack is an AI career workflow rule layer for resume diagnosis, resume optimization, JD matching, targeted rewrites, structured evaluation, interview preparation, product research, application tracking, and outreach message generation.

Its core rule is simple: **use the candidate's real experience only. No invented projects, fake metrics, or made-up contact details.**

[中文](./README.md)

## Branch Role

This is the [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) branch. The primary entry point is `skill-pack/`, designed for AI coding agents such as Cursor, Claude Code, and Codex as a repo-local skill or workflow reference.

This is not the runnable Agent product branch:

- It does not provide the `offerpilot-agent` natural-language entry point.
- It does not include the LangGraph runtime.
- It does not include the FastAPI/Next.js Web UI.
- It keeps the `offerpilot` helper CLI for deterministic scripts under `skill-pack/scripts/`.

If you want the runnable LangGraph Agent, Web UI, or natural-language CLI, use the [`offerpilot-agent`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) branch.

```text
skill-pack = rule layer / methodology / portable workflow
agent      = skill-pack + runtime + tools + UI
```

## Core Principles

- The original resume and `profile_store.yaml` are the source of truth.
- Generated content may rewrite, select, and organize real experience, but must not invent projects, companies, metrics, education, or contact details.
- Markdown should be reviewed before PDF export or job submission.
- Local private data should stay out of git by default.

## What It Can Do

| Capability | Skill Pack source |
|---|---|
| Resume diagnosis | `skill-pack/RESUME_DIAGNOSIS.md` |
| Resume optimization and targeted rewrites | `skill-pack/WORKFLOW.md`, `skill-pack/PROMPTS.md`, `skill-pack/DATASTORE.md` |
| JD fit analysis | `skill-pack/JD_MATCHING.md` |
| Structured and batch evaluation | `skill-pack/EVALUATION.md` |
| Cover letters | `skill-pack/PROMPTS.md` |
| LinkedIn outreach | `skill-pack/OUTREACH.md` |
| Mock interviews | `skill-pack/MOCK_INTERVIEW.md` |
| Product research | `skill-pack/PRODUCT_RESEARCH.md` |
| Application tracking and follow-up | `skill-pack/TRACKER.md` |
| Job scanning and recommendations | `skill-pack/scripts/scan_portals.py`, `skill-pack/scripts/run_pipeline.py` |
| PDF helpers | `skill-pack/scripts/render_pdf.py` |

This branch does not provide an LLM chat runtime by itself. It defines rules and helper scripts; an external agent or the `offerpilot-agent` branch performs complex reasoning and conversation.

## Quick Start

Clone this branch directly:

```bash
git clone -b offerpilot-skill https://github.com/kalimosd/OfferPilot.git offerpilot-skill
cd offerpilot-skill
```

If your AI coding tool supports repo-local skills, start from the matching adapter:

- `skill-pack/adapters/codex/SKILL.md`
- `skill-pack/adapters/claude-code/SKILL.md`
- `skill-pack/adapters/cursor/SKILL.md`

Otherwise read in this order:

1. `skill-pack/README.md`
2. `skill-pack/WORKFLOW.md`
3. `skill-pack/INPUTS.md`
4. `skill-pack/RESUME_DIAGNOSIS.md` for resume diagnosis
5. `skill-pack/JD_MATCHING.md` for China-first JD matching
6. `skill-pack/EVALUATION.md` for structured evaluation
7. `skill-pack/MOCK_INTERVIEW.md` for mock interviews
8. `skill-pack/PRODUCT_RESEARCH.md` for product research
9. `skill-pack/TRACKER.md` for application tracking
10. `skill-pack/OUTREACH.md` for outreach messages
11. `skill-pack/scripts/README.md` when local helpers are useful

## Optional Script Setup

Reading and using the Skill Pack documents does not require installing dependencies. Install the Python helper only when you need text extraction, PDF rendering, job scanning, or validation scripts:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m playwright install chromium
```

This branch does not need Node.js or Web UI dependencies.

## Profile Datastore

Use `profile_store.yaml` as your complete personal evidence library. It is not the final resume; it is the fact database.

Start from the template:

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

Main fields:

| Field | Description |
|---|---|
| `meta` | Name, English name, birth year, email, phone, update date |
| `experience` | Work experience with multiple bullets per role |
| `projects` | Side projects, open-source, competitions, school projects |
| `skills` | Skills, level, years, and evidence |
| `education` | Education background |
| `certifications` | Certifications |
| `achievements` | Awards or recognition |

Write more than you think you need. The Skill Pack should select the most relevant pieces for each JD.

Private local files such as `profile_store.yaml`, `jds/`, `outputs/`, and `data/` are intended to stay out of git.

## Helper CLI

`offerpilot` is an optional helper CLI for deterministic scripts. It is not a natural-language Agent.

```bash
offerpilot --help
offerpilot extract sample_resume.docx --output sample_resume.txt
offerpilot pdf outputs/resumes/resume.md outputs/resumes/resume.pdf --style standard_cn
offerpilot validate-inputs profile_store.yaml jds/example.md
offerpilot validate-profile profile_store.yaml
offerpilot validate-aliases
offerpilot scan --cn-only --dry-run
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

You can also call scripts directly:

```bash
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md
python skill-pack/scripts/extract_text.py resume.pdf
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md
python skill-pack/scripts/validate_profile_store.py profile_store.yaml
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
python skill-pack/scripts/run_pipeline.py --days 7 --top-n 10 --cn-focus
```

## Output Directories

All outputs should be saved under `outputs/`:

| Directory | Content |
|---|---|
| `outputs/resumes/` | Resume diagnosis, optimization, targeted rewrites, JD fit, structured evaluation, batch evaluation |
| `outputs/research/` | Product research |
| `outputs/interview/` | Interview question sheets, evaluation reports, preparation notes |
| `outputs/pipeline/` | Job scanning and recommendation reports |
| `outputs/misc/` | Outreach messages, project explanations, other materials |

Do not place final deliverables directly under the `outputs/` root.

## Skill Pack Structure

```text
skill-pack/
├── README.md              # Skill Pack entry
├── WORKFLOW.md            # General workflow
├── INPUTS.md              # Input selection and privacy rules
├── OUTPUTS.md             # Output formats and quality checks
├── PROMPTS.md             # Prompt constraints and reusable patterns
├── DATASTORE.md           # profile_store.yaml data model
├── JD_MATCHING.md         # JD fit analysis
├── RESUME_DIAGNOSIS.md    # Resume diagnosis without a JD
├── EVALUATION.md          # 10-dimension structured evaluation
├── MOCK_INTERVIEW.md      # Mock interview workflow
├── PRODUCT_RESEARCH.md    # Product research workflow
├── TRACKER.md             # Application tracking
├── OUTREACH.md            # LinkedIn outreach
├── templates/             # Local templates
├── data/                  # Skill aliases and supporting data
├── schemas/               # JSON Schemas for profile store and aliases
├── examples/              # Examples
├── scripts/               # Local helper scripts
└── adapters/              # Cursor / Claude Code / Codex wrappers
```

The root also keeps a small `offerpilot/` Python package for the helper CLI. It is not the primary product surface of this branch.

## Development

Run tests:

```bash
source .venv/bin/activate
python -m pytest
```

Useful script checks:

```bash
python skill-pack/scripts/validate_inputs.py sample_resume.md sample_job.md
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
```

`skill-pack/templates/profile_store.yaml` is an empty template. Running `validate_profile_store.py` against it will report missing required fields, which is expected. Copy it to `profile_store.yaml`, fill in real data, then validate that file.

## Troubleshooting

| Problem | Fix |
|---|---|
| `offerpilot-agent` does not exist | This is the skill branch. Switch to `offerpilot-agent` for the natural-language Agent |
| Web UI files are incomplete or cannot start | Expected. The Web UI belongs to `offerpilot-agent` |
| `ModuleNotFoundError` | Run `source .venv/bin/activate`, then `pip install -e .` |
| PDF rendering fails | Run `python -m playwright install chromium` |
| Template validation reports missing fields | The template is an empty form, not valid candidate data. Fill a copied `profile_store.yaml` first |
| Product research needs fresh facts | This branch has no browsing runtime. Provide source material or use the Skill Pack inside an agent with browsing capability |

## Relationship To The Agent Branch

OfferPilot ships in two forms:

| Branch | Role |
|---|---|
| [`offerpilot-skill`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) | Skill Pack: rules, workflows, templates, scripts, and methodology |
| [`offerpilot-agent`](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) | Runnable Agent: LangGraph runtime, natural-language CLI, Web UI, and automation |

Maintenance guidance:

- Workflow docs, output rules, prompt constraints, schemas, templates, skill aliases, adapters, and scripts should generally start in `offerpilot-skill`.
- LangGraph runtime, Agent tools, Web API, frontend work, and runnable UX belong in `offerpilot-agent`.
- After syncing skill branch changes into the agent branch, check `docs/AGENT_SYNC_CHECKLIST.md` to decide whether `offerpilot/graph.py` `SYSTEM_PROMPT` needs updates.

## License

MIT
