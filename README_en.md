# OfferPilot AI Skill Pack

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot is an AI career workflow Skill Pack for resume optimization, JD matching, targeted rewrites, structured evaluation, interview preparation, product research, application tracking, and outreach message generation.

This branch is [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill). The primary entry point is `skill-pack/`, designed for AI coding agents such as Cursor, Claude Code, and Codex.

If you want the runnable LangGraph Agent, CLI, or Web UI, use the [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) branch instead.

[中文](./README.md)

## Core Principles

- The original resume and `profile_store.yaml` are the source of truth.
- Generated content may rewrite, select, and organize real experience, but must not invent projects, companies, metrics, education, or contact details.
- Markdown should be reviewed before PDF export or job submission.
- Local private data should stay out of git by default.

## What It Can Do

| Capability | Description |
|---|---|
| Resume diagnosis | Identify resume gaps, weak phrasing, and missing evidence |
| Resume optimization | Tighten wording and strengthen bullet points |
| Targeted rewrite | Reorder and rewrite experience around a specific JD |
| JD fit analysis | Find match signals, gaps, keywords, and rewrite priorities |
| Structured evaluation | Score a job across 10 dimensions with an A-F recommendation |
| Batch evaluation | Rank multiple JDs to find roles worth applying to |
| Cover letter | Generate targeted cover letters from real experience |
| LinkedIn outreach | Generate concise, personalized outreach messages |
| Mock interview | Generate question sheets and evaluation reports |
| Product research | Prepare product and company research before interviews |
| Application tracking | Define tracker status flow and follow-up rules |
| PDF helpers | Provide local Markdown-to-PDF scripts |

## Quick Start

1. Open `skill-pack/README.md`
2. Read the workflow document for your task:
   - JD matching: `skill-pack/JD_MATCHING.md`
   - Structured evaluation: `skill-pack/EVALUATION.md`
   - Resume optimization / targeted rewrite: `skill-pack/WORKFLOW.md` + `skill-pack/PROMPTS.md`
   - Mock interview: `skill-pack/MOCK_INTERVIEW.md`
   - Product research: `skill-pack/PRODUCT_RESEARCH.md`
   - Application tracking: `skill-pack/TRACKER.md`
   - Outreach: `skill-pack/OUTREACH.md`
3. Prepare source files:
   - original resume or `profile_store.yaml`
   - target JD
   - optional company, role direction, or application tracker data
4. Check output expectations in `skill-pack/OUTPUTS.md`
5. Use local scripts from `skill-pack/scripts/README.md` when needed

## Profile Datastore

Use `profile_store.yaml` as your complete personal evidence library. It is not the final resume; it is the fact database.

Start from the template:

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

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

Write more than you think you need. The Skill Pack should select the most relevant pieces for each JD.

## Output Directories

All outputs should be saved under `outputs/`:

| Directory | Content |
|---|---|
| `outputs/resumes/` | Resume optimization, targeted rewrites, JD fit, structured evaluation |
| `outputs/research/` | Product research |
| `outputs/interview/` | Interview question sheets and evaluation reports |
| `outputs/pipeline/` | Job discovery and recommendation reports |
| `outputs/misc/` | Outreach messages, project explanations, other materials |

Do not place final deliverables directly under the `outputs/` root.

## Local Helper Scripts

These scripts are optional helpers. They do not require the runnable Agent.

```bash
# Validate source files
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md

# Extract text from PDF / DOCX / TXT / MD
python skill-pack/scripts/extract_text.py resume.pdf

# Render Markdown to PDF
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf

# Validate output naming and format
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md
```

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
├── EVALUATION.md          # 10-dimension structured evaluation
├── MOCK_INTERVIEW.md      # Mock interview workflow
├── PRODUCT_RESEARCH.md    # Product research workflow
├── TRACKER.md             # Application tracking
├── OUTREACH.md            # LinkedIn outreach
├── templates/             # Local templates
├── data/                  # Skill aliases and supporting data
├── examples/              # Examples
├── scripts/               # Local helper scripts
└── adapters/              # Cursor / Claude Code / Codex wrappers
```

## Adapters

`skill-pack/adapters/` provides entry instructions for different AI coding environments:

- `skill-pack/adapters/cursor/SKILL.md`
- `skill-pack/adapters/claude-code/SKILL.md`
- `skill-pack/adapters/codex/SKILL.md`

If your tool supports repo-local skills, prefer the matching adapter.

## Relationship To The Agent Branch

OfferPilot ships in two forms:

| Branch | Role |
|---|---|
| [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) | Skill Pack: rules, workflows, templates, scripts, and methodology |
| [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) | Runnable Agent: LangGraph runtime, CLI, Web UI, and automation |

Think of it as:

```text
skill-pack = rule layer / methodology / portable workflow
agent      = skill-pack + runtime + tools + UI
```

The Skill Pack is OfferPilot's rule layer. The Agent branch adds an executor and user interface around it.

This branch may still contain some historical runtime files, but they are not the primary entry point.

## Maintenance Notes

Changes to the Skill Pack should generally start in [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill):

- workflow documents
- output rules
- prompt constraints
- skill alias data
- templates
- scripts
- adapters

Agent runtime, Web UI, API, and LangGraph state changes belong in [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent).

## License

MIT
