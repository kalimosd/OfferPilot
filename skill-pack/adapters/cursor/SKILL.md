---
name: offerpilot
description: Use the OfferPilot skill pack for profile datastore building, resume optimization, China-first JD fit diagnosis, targeted rewrites, structured evaluation, offer evaluation and negotiation, mock interview prep and debrief, product research, application tracking, multi-channel outreach, and cover letters in Cursor or other repository-local coding agents. Trigger on short intents like "按照 offerpilot 优化简历", "用 offerpilot 做 JD 匹配", or "/offerpilot ...".
---

# Cursor Adapter

This adapter is a thin wrapper over the platform-agnostic OfferPilot skill pack.

## Read Order (Minimal Read Graph)

To avoid loading unnecessary rules into context, follow the minimal read path for the active task:

1. Core baseline: `../../README.md`, `../../WORKFLOW.md`, `../../INPUTS.md`, `../../PROMPTS.md`
2. Resume & PDF deliverable formatting (read ONLY when generating/rewriting resumes or cover letters): `../../OUTPUTS.md`
3. Task-specific document (read ONLY the one matching the current task):
   - profile datastore building / cold-start extraction: `../../PROFILE_BUILDER.md` and `../../DATASTORE.md`
   - China-first JD matching: `../../JD_MATCHING.md`
   - resume diagnosis: `../../RESUME_DIAGNOSIS.md`
   - profile datastore assembly: `../../DATASTORE.md`
   - structured or batch evaluation: `../../EVALUATION.md`
   - offer evaluation and salary negotiation: `../../OFFER_EVALUATION.md`
   - mock interview, post-interview debrief, or behavioral prep: `../../MOCK_INTERVIEW.md`
   - product research: `../../PRODUCT_RESEARCH.md`
   - application tracking: `../../TRACKER.md`
   - multi-channel outreach (Boss直聘 / 内推 / LinkedIn / Email): `../../OUTREACH.md`
4. `../../scripts/README.md` when local helper scripts are useful

## When To Use

- profile datastore building and cold-start resume extraction
- resume diagnosis
- resume optimization
- China-first JD fit diagnosis
- targeted resume rewriting
- structured and batch job evaluation
- offer total compensation evaluation and negotiation scripts
- job discovery and recommendation
- mock interview question generation, live simulation, post-interview debrief, and behavioral STAR prep
- product research for interview preparation
- application tracking and follow-up review
- multi-channel outreach message generation (Boss直聘 / 脉脉内推 / LinkedIn / Email)
- cover letter generation
- multilingual application material cleanup

## Short Triggers

Treat these as direct triggers for this skill:

- `按照 offerpilot 优化简历`
- `用 offerpilot 做 JD 匹配`
- `/offerpilot 建素材库`
- `/offerpilot 优化简历`
- `/offerpilot 根据我简历推荐岗位`
- `/offerpilot 结构化评估`
- `/offerpilot 批量评估`
- `/offerpilot 模拟面试`
- `/offerpilot 面经复盘`
- `/offerpilot 行为面`
- `/offerpilot 产品研究`
- `/offerpilot 外联消息`
- `/offerpilot 简历诊断`
- `/offerpilot 求职信`
- `/offerpilot 申请追踪`
- `/offerpilot 谈薪决策`

When these short triggers appear, do not ask for a long setup prompt first. Start from the minimal read order for that task, then request only missing required inputs.

## Cursor-Specific Notes

- prefer local repository files as inputs
- use the rules in `../../README.md`, `../../INPUTS.md`, and `../../OUTPUTS.md` as the source of truth instead of repeating platform-local variants
- run `python3 skill-pack/scripts/extract_text.py "path/to/file"` when a `.pdf` or `.docx` source cannot be read reliably
- use validation scripts when they reduce risk: `validate_inputs.py`, `validate_outputs.py`, `validate_profile_store.py`, and `validate_aliases.py`
