# OfferPilot Skill Pack

This directory contains the portable, platform-agnostic version of OfferPilot.

Use it when you want to build a personal material datastore, diagnose resumes, analyze JD fit, optimize resumes, tailor resumes to job descriptions, prepare for technical/behavioral interviews, evaluate offers, or draft multi-channel outreach and cover letters with an AI agent. This directory is the primary product surface of the repository.

## Start Order (Minimal Read Graph)

1. Read `WORKFLOW.md` and `PROMPTS.md` (and `INPUTS.md` when checking source inputs)
2. Read the task-specific document for the active task:
   - profile datastore cold-start extraction or update: `PROFILE_BUILDER.md` + `DATASTORE.md`
   - resume diagnosis (no JD): `RESUME_DIAGNOSIS.md`
   - China-first JD matching: `JD_MATCHING.md`
   - mock interview, post-interview debrief, or behavioral STAR prep: `MOCK_INTERVIEW.md`
   - product research: `PRODUCT_RESEARCH.md`
   - structured or batch evaluation: `EVALUATION.md`
   - offer evaluation and salary negotiation: `OFFER_EVALUATION.md`
   - application tracking: `TRACKER.md`
   - multi-channel outreach (Boss直聘 / 内推 / LinkedIn / Email): `OUTREACH.md`
3. When generating or rewriting resumes/cover letters, validate against `OUTPUTS.md` (including the 1-page length budget)
4. Pick an adapter from `adapters/` if your agent supports repository-local skills
5. Check `scripts/README.md` when local helper scripts are needed

> **Installable skill:** the repository-root `SKILL.md` is the canonical Claude Code / Codex skill entry. See `../INSTALL.md` for `./scripts/install_skill.sh` usage, invocation names, and manual installation.

## What Is Inside

- `WORKFLOW.md`: task flow, Minimal Read Graph, and checkpoints
- `PROFILE_BUILDER.md`: cold-start datastore extraction from resumes, elaboration prompting, and post-interview ingestion
- `DATASTORE.md`: `profile_store.yaml` schema, bullet tagging, and 1-page selection logic
- `JD_MATCHING.md`: China-first JD matching method and output expectations
- `RESUME_DIAGNOSIS.md`: resume quality diagnosis without a target JD
- `MOCK_INTERVIEW.md`: mock interview question generation, live simulation, post-interview debrief, and behavioral STAR prep
- `PRODUCT_RESEARCH.md`: pre-interview product research workflow
- `EVALUATION.md`: 10-dimension structured job fit evaluation (A-F grading with adaptive weight normalization)
- `OFFER_EVALUATION.md`: total compensation calculation, multi-offer comparison matrix, and salary negotiation scripts
- `TRACKER.md`: application status tracking and follow-up reminders
- `OUTREACH.md`: multi-channel outreach generation (Boss直聘打招呼, 脉脉/校友内推私信, LinkedIn, Cold Email)
- `INPUTS.md`: source selection and privacy rules
- `OUTPUTS.md`: expected output shapes, 1-page resume budget, and quality checks
- `PROMPTS.md`: Golden Bullet Formula, Few-Shot Before/After examples, anti-patterns blacklist, and constraints
- `data/`: reusable supporting data such as China-first skill alias mappings
- `examples/`: example usage for different job-application tasks; keep example names and filenames anonymized by default
- `scripts/`: text extraction, PDF rendering (with 1-page budget check), portal scanning, and validation helpers
- `adapters/`: thin platform-specific wrappers (`claude-code`, `cursor`, `codex`)

## Design Rules

- The original resume or `profile_store.yaml` is the source of truth
- Generated outputs are drafts, not facts
- Private source files stay local unless the user explicitly wants to publish them
- English rendering of Chinese names should use `Given Name + Family Name`
- Markdown review should happen before any final export-ready formatting step

## Script Rules

- If the source is `.txt`, `.md`, or `.yaml`/`.yml` and the agent can read it directly, use the file as-is
- If the source is `.pdf` or `.docx` and the agent cannot reliably read it natively, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` before drafting
- Use the extracted text as the working source for prompting, review, and validation
- Use `python3 skill-pack/scripts/render_pdf.py "input.md" "output.pdf"` when a local PDF export step is needed
- Use `data/skill_aliases.zh-en.json` as a small China-first seed mapping for bilingual skill normalization
- `validate_inputs.py`, `validate_outputs.py`, `validate_profile_store.py`, and `validate_aliases.py` remain optional checks; `extract_text.py` is the required helper when native file reading is unavailable

## Recommended Flow

- Use `PROFILE_BUILDER.md` first when initializing or enriching `profile_store.yaml` from an existing resume
- Use diagnosis first when the user is unsure whether the resume should be rewritten or merely tightened
- Use jd-fit diagnosis first when a China-first user wants to know whether the resume matches a specific JD and what to change
- Use optimization when the user wants a stronger general-purpose resume
- Use targeted rewriting when a specific job description is available
- Use `OFFER_EVALUATION.md` once an offer is received to break down total compensation and prepare negotiation scripts
