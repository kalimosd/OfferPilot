# OfferPilot Skill Pack

This directory contains the portable, platform-agnostic version of OfferPilot.

Use it when you want to diagnose resumes, optimize resumes, tailor resumes to job descriptions, or draft cover letters with an AI agent, without depending on the repository's legacy CLI.

## Start Order

1. Read `WORKFLOW.md`
2. Check `INPUTS.md`
3. Use `PROMPTS.md` for generation guidance
4. Validate against `OUTPUTS.md`
5. Pick an adapter from `adapters/` if your agent supports repository-local skills

## What Is Inside

- `WORKFLOW.md`: task flow and checkpoints
- `INPUTS.md`: source selection and privacy rules
- `OUTPUTS.md`: expected output shapes and quality checks
- `PROMPTS.md`: reusable prompt patterns and constraints
- `examples/`: example usage for different job-application tasks
- `scripts/`: text extraction and optional validation helpers
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
- `validate_inputs.py` and `validate_outputs.py` remain optional checks; `extract_text.py` is the required helper when native file reading is unavailable

## Recommended Flow

- Use diagnosis first when the user is unsure whether the resume should be rewritten or merely tightened
- Use optimization when the user wants a stronger general-purpose resume
- Use targeted rewriting when a specific job description is available
- Use cover letter generation only after the resume and target role are clear
