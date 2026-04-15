# Mock Interview

Use this workflow for technical mock interview tasks.

## Overview

Mock interview has two phases:

1. **Question generation** — analyze JD + profile, produce a question sheet
2. **Live simulation** — agent plays interviewer, user answers, then agent produces evaluation report

## Phase 1: Question Generation

### Inputs

Required:

- job description (JD file or inline text)
- profile datastore (`profile_store.yaml`)

Optional:

- specific topics the user wants to focus on
- preferred number of questions (default: 8-12)

### Gap Analysis

Before generating questions, perform a JD vs profile gap analysis:

1. Extract core technical requirements from the JD
2. Match requirements against profile bullet tags (reuse `data/skill_aliases.zh-en.json` for normalization)
3. Classify each requirement as: strong match, partial match, or gap
4. Use this classification to drive question selection

### Question Strategy

- **Strong-point deep-dive (约 60%)**: questions rooted in the candidate's actual experience. Ask how, why, what tradeoffs, what went wrong, what would you do differently. Tag as `[强项深挖]`.
- **Weakness probing (约 40%)**: questions targeting JD requirements where the profile is thin. Start from fundamentals, then escalate to design and application. Tag as `[弱点考察]`.

### Question Requirements

Each question must include:

- tag: `[强项深挖]` or `[弱点考察]`
- difficulty: `[基础]`, `[中等]`, or `[进阶]`
- topic label (e.g. "Android 性能优化")
- question text
- examination points (考察点): what the interviewer is looking for
- reference answer key points (参考答案要点): concise bullet points, not a full answer

### Question Sheet Output

Save to `outputs/` as Markdown:

```
姓名_公司_岗位_面试题单_v1.md
```

Structure:

```markdown
# 技术面试题单 — {公司} {岗位}

- 候选人: {姓名}
- 目标岗位: {公司} - {岗位}
- 生成时间: {时间}
- 题目数量: {N} 题（深挖 {X} + 弱点 {Y}）

## 匹配概览

（list strong areas and weak areas identified from gap analysis）

## 题目

### Q1 [强项深挖] [中等] {topic}
**题目：** ...
**考察点：** ...
**参考答案要点：** ...

### Q2 [弱点考察] [基础] {topic}
**题目：** ...
**考察点：** ...
**参考答案要点：** ...
```

### Transition to Phase 2

After saving the question sheet, ask the user:

> "题单已生成并保存。你可以先看看准备一下，准备好了说「开始模拟」进入面试。"

Only proceed to Phase 2 when the user explicitly says to start.

## Phase 2: Live Simulation

### Interviewer Behavior

- Ask one question at a time, following the question sheet order
- After the user answers, ask 1-2 follow-up questions (dig into details, edge cases, alternative approaches)
- Give brief feedback after each question concludes ("这个点答得很清楚" or "XX 方面可以再深入"), do not break the interview rhythm
- Do not reveal reference answers unless the user explicitly asks
- Tone: professional, not adversarial — simulate a real technical interview

### Flow Control

- User can say "跳过" to skip to the next question
- User can say "结束" to end early and go directly to evaluation
- Agent proactively checks in every 3-4 questions: "继续还是先到这里？"

### Evaluation Report

After the simulation ends (all questions done or user says "结束"), generate an evaluation report.

Save to `outputs/` as Markdown:

```
姓名_公司_岗位_面试评估_v1.md
```

Structure:

```markdown
# 模拟面试评估 — {公司} {岗位}

- 候选人: {姓名}
- 面试时间: {时间}
- 完成题数: {N}/{总数}

## 总体评价

（2-3 sentences summarizing overall performance）

## 逐题评估

### Q1 {topic} — ⭐⭐⭐⭐ (4/5)
- **亮点：** ...
- **不足：** ...
- **改进建议：** ...

### Q2 {topic} — ⭐⭐ (2/5)
- **亮点：** ...
- **不足：** ...
- **改进建议：** ...

## 复习清单

| 优先级 | 知识点 | 原因 | 建议学习方式 |
|--------|--------|------|-------------|
| 🔴 高 | ... | ... | ... |
| 🟡 中 | ... | ... | ... |
| 🟢 低 | ... | ... | ... |
```

### Scoring Rubric

Per question, score 1-5:

- **5**: accurate, deep, mentions tradeoffs and edge cases proactively
- **4**: correct with good detail, minor gaps
- **3**: fundamentally correct but shallow or missing key aspects
- **2**: partially correct, significant gaps or misconceptions
- **1**: unable to answer or fundamentally wrong

## Task Checklist

- [ ] JD and profile_store both loaded before generating questions
- [ ] gap analysis performed before question selection
- [ ] question mix follows ~60% deep-dive / ~40% weakness ratio
- [ ] each question has tag, difficulty, topic, examination points, and reference answer key points
- [ ] question sheet saved to outputs/ with correct naming
- [ ] user confirmed readiness before starting simulation
- [ ] follow-up questions asked after each answer
- [ ] evaluation report includes per-question scoring and improvement suggestions
- [ ] review checklist generated with priority levels and learning recommendations
- [ ] no fabricated technical claims in reference answers
