---
name: offerpilot-cursor-adapter
description: Use the OfferPilot skill pack for resume optimization, China-first JD fit diagnosis, targeted rewrites, structured evaluation, mock interview prep, product research, application tracking, outreach, and cover letters in Cursor or other repository-local coding agents. Trigger on short intents like "按照 offerpilot 优化简历", "用 offerpilot 做 JD 匹配", or "/offerpilot ...".
---

# Cursor Adapter

This adapter is a thin wrapper over the platform-agnostic OfferPilot skill pack.

## Read Order

1. `../../README.md`
2. `../../WORKFLOW.md`
3. `../../INPUTS.md`
4. `../../OUTPUTS.md`
5. `../../PROMPTS.md`
6. task-specific document:
   - China-first JD matching: `../../JD_MATCHING.md`
   - profile datastore assembly: `../../DATASTORE.md`
   - structured or batch evaluation: `../../EVALUATION.md`
   - mock interview: `../../MOCK_INTERVIEW.md`
   - product research: `../../PRODUCT_RESEARCH.md`
   - application tracking: `../../TRACKER.md`
   - LinkedIn outreach: `../../OUTREACH.md`
7. `../../scripts/README.md` when local helper scripts are useful

## When To Use

- resume optimization
- China-first JD fit diagnosis
- targeted resume rewriting
- structured and batch job evaluation
- job discovery and recommendation
- mock interview question generation and evaluation
- product research for interview preparation
- application tracking and follow-up review
- LinkedIn outreach message generation
- cover letter generation
- multilingual application material cleanup

## Short Triggers

Treat these as direct triggers for this skill:

- `按照 offerpilot 优化简历`
- `用 offerpilot 做 JD 匹配`
- `/offerpilot 优化简历`
- `/offerpilot 根据我简历推荐岗位`
- `/offerpilot 结构化评估`
- `/offerpilot 模拟面试`
- `/offerpilot 产品研究`
- `/offerpilot 外联消息`

When these short triggers appear, do not ask for a long setup prompt first. Start from the read order, then request only missing required inputs.

## Cursor-Specific Notes

- prefer local repository files as inputs
- use the rules in `../../README.md`, `../../INPUTS.md`, and `../../OUTPUTS.md` as the source of truth instead of repeating platform-local variants
- run `python3 skill-pack/scripts/extract_text.py "path/to/file"` when a `.pdf` or `.docx` source cannot be read reliably
- use validation scripts when they reduce risk: `validate_inputs.py`, `validate_outputs.py`, `validate_profile_store.py`, and `validate_aliases.py`
