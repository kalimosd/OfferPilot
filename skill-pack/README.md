# OfferPilot Skill Pack

This directory contains the portable, platform-agnostic version of OfferPilot.

Use it when you want to diagnose resumes, analyze JD fit, optimize resumes, tailor resumes to job descriptions, or draft cover letters with an AI agent. This directory is the primary product surface of the repository.

## Start Order

1. Read `WORKFLOW.md`
2. Check `INPUTS.md`
3. If the task is China-first JD matching, read `JD_MATCHING.md`
4. If the task is mock interview, read `MOCK_INTERVIEW.md`
5. If the task is product research, read `PRODUCT_RESEARCH.md`
6. If the task is structured evaluation, read `EVALUATION.md`
7. If the task is application tracking, read `TRACKER.md`
8. If the task is LinkedIn outreach, read `OUTREACH.md`
9. Use `PROMPTS.md` for generation guidance
10. Validate against `OUTPUTS.md`
11. Pick an adapter from `adapters/` if your agent supports repository-local skills
12. Check `scripts/README.md` when local helper scripts are needed

## What Is Inside

- `WORKFLOW.md`: task flow and checkpoints
- `JD_MATCHING.md`: China-first JD matching method and output expectations
- `MOCK_INTERVIEW.md`: mock interview question generation and live simulation
- `PRODUCT_RESEARCH.md`: pre-interview product research workflow
- `EVALUATION.md`: 10-dimension structured job fit evaluation (A-F grading)
- `TRACKER.md`: application status tracking and follow-up reminders
- `OUTREACH.md`: LinkedIn outreach message generation
- `INPUTS.md`: source selection and privacy rules
- `OUTPUTS.md`: expected output shapes and quality checks
- `PROMPTS.md`: reusable prompt patterns and constraints
- `data/`: reusable supporting data such as China-first skill alias mappings
- `examples/`: example usage for different job-application tasks; keep example names and filenames anonymized by default
- `scripts/`: text extraction, PDF rendering, and optional validation helpers
- `adapters/`: thin platform-specific wrappers

## Design Rules

- The original resume is the source of truth
- Generated outputs are drafts, not facts
- Private source files stay local unless the user explicitly wants to publish them
- English rendering of Chinese names should use `Given Name + Family Name`
- Markdown review should happen before any final export-ready formatting step

## Script Rules

- If the source is `.txt` or `.md` and the agent can read it directly, use the file as-is
- If the source is `.pdf` or `.docx` and the agent cannot reliably read it natively, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` before drafting
- Use the extracted text as the working source for prompting, review, and validation
- Use `python3 skill-pack/scripts/render_pdf.py "input.md" "output.pdf"` when a local PDF export step is needed
- Use `data/skill_aliases.zh-en.json` as a small China-first seed mapping for bilingual skill normalization
- `validate_inputs.py` and `validate_outputs.py` remain optional checks; `extract_text.py` is the required helper when native file reading is unavailable

## Recommended Flow

- Use diagnosis first when the user is unsure whether the resume should be rewritten or merely tightened
- Use jd-fit diagnosis first when a China-first user wants to know whether the resume matches a specific JD and what to change
- Use optimization when the user wants a stronger general-purpose resume
- Use targeted rewriting when a specific job description is available
- Use cover letter generation only after the resume and target role are clear
