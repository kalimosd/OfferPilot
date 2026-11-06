# Mock Interview

Use this workflow for technical mock interview, post-interview debrief, and behavioral/reverse interview preparation.

## Overview

This workflow supports four interview preparation modes:

1. **Phase 1: Question generation** — analyze JD + profile, produce a targeted question sheet
2. **Phase 2: Live simulation** — agent plays interviewer, user answers, then agent produces an evaluation report
3. **Phase 3: Post-interview debrief (真实面经复盘)** — analyze real interview questions/transcripts after an actual interview
4. **Phase 4: Behavioral & reverse interview (行为面 STAR 故事卡与反问清单)** — prepare for manager/HR rounds and reverse Q&A

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

Save to `outputs/interview/` as Markdown:

```
outputs/interview/姓名_公司_岗位_面试题单_v1.md
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

Save to `outputs/interview/` as Markdown:

```
outputs/interview/姓名_公司_岗位_面试评估_v1.md
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

---

## Phase 3: Post-Interview Debrief (真实面经复盘)

Use this mode when the candidate shares real questions or a transcript from a completed interview.

### Debrief Workflow
1. **考点拆解**：分析面试官每一问背后的真实考察意图（基础功底、架构权衡、故障排查思路还是跨团队推进）。
2. **回答诊断**：复盘候选人原回答中的得分点与失分点（如逻辑跳跃、缺少量化指标、只讲了表面现象未讲底层根因）。
3. **高分重构回答**：结合候选人 `profile_store.yaml` 中的真实项目背景，给出结构清晰（结论先行 + 原理拆解 + 落地收益）的示范回答。
4. **知识盲区归档**：生成按优先级排序的下一轮补强清单；若复盘中挖出了简历未写的新亮点，提示通过 `PROFILE_BUILDER.md` 回写到 `profile_store.yaml`。

### Output Naming
Save to `outputs/interview/姓名_公司_岗位_面经复盘_v1.md`.

---

## Phase 4: Behavioral & Reverse Interview (行为面与反问面试官)

Use this mode to prepare for主管面 (Hiring Manager)、交叉面或 HR 面：

### 1. STAR 行为面故事卡（基于 `profile_store.yaml` 真实经历提取）
针对高频行为面问题，提炼 3 张结构化 `STAR`（Situation / Task / Action / Result）故事卡：
- **最难的技术攻坚 / 线上故障排查**：突出定位工具链、假设验证过程与根因闭环。
- **跨团队分歧与推动落地**：突出如何对齐边界（如产品、BSP、多窗口团队）、化解阻力并按期交付。
- **主动创新与效率突破**：突出痛点识别与自发工具化/AI 工程化改造带来的效率跃升。

### 2. 高水平反问面试官清单（Reverse Interview）
结合目标公司业务与岗位 JD，准备 3 个高质量反问问题：
- **业务与技术挑战类**：“团队接下来半年在 [JD 核心方向] 上最优先攻克的技术瓶颈或核心指标是什么？”
- **工程落地与协作类**：“目前咱们组在 [相关模块/AI 工程] 上的技术栈演进和跨团队协作模式是怎样的？”
- **角色期望类**：“如果我有幸加入，您期望这个岗位在前 3 个月内交付什么样的核心成果？”

---

## Error Recovery

- **JD 或 profile_store 缺失**（Phase 1/2 必要输入）：不强行生成题单。明确列出缺失的输入，等待用户提供
- **JD 过于宽泛无法生成技术问题**（如仅有岗位名称无详细职责）：基于岗位名称推断常见技术栈和面试题，但在题单开头标注「JD 信息有限，问题基于岗位常见考察点生成」
- **gap analysis 发现 profile 与 JD 几乎完全匹配**：调整深挖/弱点比例为 80/20（极少弱点可挖），并将弱点题集中在行为面或系统设计等通用维度
- **用户提前结束模拟**：直接生成评估报告，标注「未完成题数」，仅对已完成的题目评分

## Task Checklist

- [ ] JD and profile_store both loaded before generating questions
- [ ] gap analysis performed before question selection
- [ ] question mix follows ~60% deep-dive / ~40% weakness ratio
- [ ] each question has tag, difficulty, topic, examination points, and reference answer key points
- [ ] question sheet saved to outputs/ with correct naming
- [ ] user confirmed readiness before starting simulation
- [ ] follow-up questions asked after each answer
- [ ] evaluation or debrief report includes per-question scoring and improvement suggestions
- [ ] review checklist generated with priority levels and learning recommendations
- [ ] no fabricated technical claims in reference answers or STAR story cards
