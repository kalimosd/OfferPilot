---
name: offerpilot-claude-code-adapter
description: Use the OfferPilot skill pack for resume optimization, China-first JD fit diagnosis, targeted resumes, and cover letters in Claude Code style repository agents. Trigger on short intents like "按照 offerpilot 优化简历", "用 offerpilot 做 JD 匹配", or "/offerpilot ...".
---

# Claude Code Adapter

This adapter provides the minimum platform-specific bridge to the shared OfferPilot workflow.

## Read Order

1. `../../README.md`
2. `../../WORKFLOW.md`
3. if the task is China-first JD matching, read `../../JD_MATCHING.md`
4. `../../INPUTS.md`
5. `../../PROMPTS.md`
6. `../../OUTPUTS.md`

## Agent Behavior

- start from the original resume source
- keep outputs compact and factual
- ask for missing job descriptions only when task type requires them
- if a `.pdf` or `.docx` source cannot be read reliably, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` first
- use validation scripts only when the extra check adds value

## Short Triggers

Treat these as direct triggers for this skill:

- `按照 offerpilot 优化简历`
- `用 offerpilot 做 JD 匹配`
- `/offerpilot 优化简历`
- `/offerpilot 根据我简历推荐岗位`

When these short triggers appear, do not ask for a long setup prompt first. Start from the read order, then request only missing required inputs.
