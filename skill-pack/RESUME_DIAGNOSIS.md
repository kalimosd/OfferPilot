# Resume Diagnosis

Use this workflow for diagnosing resume quality without a specific JD (纯简历诊断).

## Positioning

- external name in Chinese: `简历诊断`
- internal task name: `resume-diagnosis`
- primary audience: job seekers who want to improve their resume before targeting specific roles
- difference from jd-fit diagnosis: **no JD required** — evaluates resume quality on its own merits
- preferred output language: same as source resume language

## When to Use

- user has a resume but no target JD yet
- user wants to know "is my resume good enough?"
- user wants to identify general weaknesses before starting job applications
- user has not updated their resume in a while and wants a health check

If the user provides a JD, use `JD_MATCHING.md` instead — jd-fit diagnosis is always preferred when a target role is available.

## Inputs

Required:
- original resume source (`.md`, `.txt`, `.pdf`, or `.docx`)
- target language preference

Optional:
- profile datastore (`profile_store.yaml`) — enriches analysis with fuller experience context
- target role direction (e.g. "AI 工程", "后端开发") — helps judge keyword and skill alignment without a specific JD

## Diagnosis Dimensions

| # | 维度 | 权重 | 评估要点 |
|---|------|------|---------|
| 1 | 结构与完整性 | 25% | section 是否齐全，顺序是否合理，是否有明显的 section 缺失 |
| 2 | 表达质量 | 25% | bullet 是否清晰、有行动/结果描述，是否过度使用套话或弱动词 |
| 3 | 量化程度 | 20% | 是否有数字、百分比、规模等可量化成果，量化是否可信 |
| 4 | 关键词密度 | 15% | 如果用户给了方向，检查该方向的核心技能关键词是否出现在简历中 |
| 5 | 格式与可读性 | 15% | 排版是否清晰，日期是否一致，是否有明显的格式错误 |

Scoring per dimension: 1-5. Weighted total maps to:
- A (4.5+): 高质量，可直接投递
- B (3.5+): 整体不错，建议针对性优化后投递
- C (2.5+): 有明显提升空间
- D (1.5+): 需要较大修改
- F (<1.5): 需要重写

## Output Structure

```markdown
# 简历诊断 — {姓名}

- 候选人: {姓名}
- 诊断时间: {时间}
- 目标方向: {方向或"未指定"}

## 诊断总览
- 总分: X.XX / 5
- 等级: X
- 综合结论: （1-2 句话）

## 逐维度分析

| 维度 | 权重 | 得分 | 评价 |
|------|------|------|------|
| ... | ... | ... | ... |

## 优势
（bullet list of strengths）

## 问题与风险
（bullet list of problems and risks）

## 优化建议（按优先级）
1. **高优先级**：...
2. **中优先级**：...
3. **低优先级**：...
```

## Rules

- 不要编造缺失的信息来填补简历空白
- 评分必须基于证据，不能凭感觉
- 优化建议必须具体可操作，不能只是「写得更专业」
- 如果用户没有指定目标方向，维度 4 标注「未评估（缺少目标方向）」，不计入总分

## Error Recovery

- **简历无法读取**（加密 PDF、格式损坏）：尝试 `extract_text.py`；失败则提示用户提供纯文本版本
- **简历极短**（< 200 字）：可能只有个人信息和简介。如实标注「信息量不足」，不强行编造诊断结果。建议用户补充经历细节后重新诊断
- **无方向且未提供 profile_store**：维度 4 跳过。提醒用户「如指定目标方向，可以给出更精准的关键词覆盖分析」

## Task Checklist

- [ ] 原始简历已读取
- [ ] 目标方向已确认（或标注为未指定）
- [ ] 每个维度有具体证据支撑评分
- [ ] 优势和建议都映射到具体简历内容
- [ ] 不编造缺失信息
- [ ] 文件已保存到 `outputs/resumes/`，命名 `姓名_简历诊断_v1.md`
