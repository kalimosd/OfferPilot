---
name: offerpilot
description: Use the OfferPilot skill pack for profile datastore building, resume optimization, China-first JD fit diagnosis, targeted resumes, structured evaluation, offer evaluation and negotiation, mock interview prep and debrief, product research, application tracking, multi-channel outreach, and cover letters. Trigger on short intents like "按照 offerpilot 优化简历", "用 offerpilot 做 JD 匹配", or /offerpilot, $offerpilot.
---

# OfferPilot

This is the canonical OfferPilot skill entry point. The documents under `skill-pack/` are the source of truth; do not duplicate their rules in answers.

## Read Order (Minimal Read Graph)

To avoid loading unnecessary rules into context, follow the minimal read path for the active task:

1. Core baseline: `skill-pack/README.md`, `skill-pack/WORKFLOW.md`, `skill-pack/INPUTS.md`, `skill-pack/PROMPTS.md`
2. Resume & PDF deliverable formatting (read ONLY when generating/rewriting resumes or cover letters): `skill-pack/OUTPUTS.md`
3. Task-specific document (read ONLY the one matching the active task):
   - profile datastore building / cold-start extraction: `skill-pack/PROFILE_BUILDER.md` and `skill-pack/DATASTORE.md`
   - China-first JD matching: `skill-pack/JD_MATCHING.md`
   - resume diagnosis: `skill-pack/RESUME_DIAGNOSIS.md`
   - structured or batch evaluation: `skill-pack/EVALUATION.md`
   - offer evaluation and salary negotiation: `skill-pack/OFFER_EVALUATION.md`
   - mock interview, post-interview debrief, or behavioral prep: `skill-pack/MOCK_INTERVIEW.md`
   - product research: `skill-pack/PRODUCT_RESEARCH.md`
   - application tracking: `skill-pack/TRACKER.md`
   - multi-channel outreach (Boss直聘 / 内推 / LinkedIn / Email): `skill-pack/OUTREACH.md`
4. `skill-pack/scripts/README.md` when local helper scripts are useful

## When To Use

- profile datastore building and cold-start resume extraction
- resume diagnosis and optimization
- China-first JD fit diagnosis and targeted resume rewriting
- structured and batch job evaluation
- offer total compensation evaluation and negotiation
- job discovery and recommendation
- mock interview question generation, live simulation, post-interview debrief, and behavioral STAR prep
- product research for interview preparation
- application tracking and follow-up review
- multi-channel outreach message generation
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

When these triggers appear, do not ask for a long setup prompt first. Start from the minimal read order for that task, then request only missing required inputs.

## Platform Notes

- **Claude Code**: invoke with `/offerpilot <task>`.
- **Codex**: invoke with `$offerpilot <task>` or the `/skills` picker; Codex does not document a `/offerpilot` slash command.
- **Helper scripts**: run from this skill's root, e.g. `python3 skill-pack/scripts/extract_text.py "path/to/file"`.
- Use the validation scripts when they reduce risk: `validate_inputs.py`, `validate_outputs.py`, `validate_profile_store.py`, and `validate_aliases.py`.
