---
name: offerpilot-codex-adapter
description: Use the OfferPilot skill pack for resume optimization, China-first JD fit diagnosis, job-targeted rewrites, and cover-letter workflows in Codex-style repository agents. Trigger on short intents like "按照 offerpilot 优化简历", "用 offerpilot 做 JD 匹配", or "/offerpilot ...".
---

# Codex Adapter

This adapter points Codex-style agents to the shared OfferPilot workflow.

## Read Order

1. `../../README.md`
2. `../../WORKFLOW.md`
3. if the task is China-first JD matching, read `../../JD_MATCHING.md`
4. `../../INPUTS.md`
5. `../../PROMPTS.md`
6. `../../OUTPUTS.md`

## Operating Rules

- use the original resume when available
- do not invent facts or metrics
- treat private source files as sensitive
- verify English name ordering for Chinese resumes when needed
- if a `.pdf` or `.docx` source cannot be read natively, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` and continue from the extracted text

## Short Triggers

Treat these as direct triggers for this skill:

- `按照 offerpilot 优化简历`
- `用 offerpilot 做 JD 匹配`
- `/offerpilot 优化简历`
- `/offerpilot 根据我简历推荐岗位`

When these short triggers appear, do not ask for a long setup prompt first. Start from the read order, then request only missing required inputs.

## Optional Scripts

- `python3 skill-pack/scripts/extract_text.py "path/to/file"` is required when native `.pdf` or `.docx` reading is unavailable
- use files under `../../scripts/` for validation when extra checks add value
