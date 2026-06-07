# JD Matching

Use this document for the China-first `jd-fit diagnosis` task.

The goal is not to estimate whether a resume can pass a western ATS. The goal is to judge how well a resume matches a target job description, explain the biggest fit gaps, and suggest the highest-value revisions.

## Positioning

- external name in Chinese: `JD 匹配度分析`
- internal task name: `jd-fit diagnosis`
- primary audience: Chinese job seekers targeting domestic roles
- preferred output language: Simplified Chinese unless the user requests otherwise

## Experience Level Matching

When matching a candidate to job listings, use **actual work experience + 1 year** as the matching experience level.

- Calculate actual experience from the earliest full-time start date (exclude internships) to today
- Add 1 year to get the matching level
- Example: a candidate who started full-time in 2024.07 has ~2 years actual experience → match as 3 years
- If the JD requires more than the matching level, flag it as a gap but do not auto-disqualify
- If the JD does not specify experience requirements, skip this check

## Analysis Goals

- identify the core requirements in the JD
- find supporting evidence already present in the resume
- distinguish between matched, partially matched, and missing signals
- explain why the resume may fail to win interviews even if the background is broadly relevant
- produce concrete rewrite guidance instead of only giving an abstract score

## Scoring Dimensions

Use these default weights for the first China-first version:

1. `核心技能与 JD 关键词命中`: 35%
2. `经历相关性`: 30%
3. `学历 / 专业 / 证书匹配`: 15%
4. `信息密度与表达质量`: 15%
5. `基础格式合规`: 5%

The score is a prioritization aid, not the final conclusion. The explanation matters more than the number.

## Dimension Guidance

### 1. 核心技能与 JD 关键词命中

- extract explicit hard skills from the JD
- include common English and Chinese variants when the meaning is clearly the same
- separate matched keywords from missing keywords
- prefer evidence-backed matching over vague semantic guessing
- use `data/skill_aliases.zh-en.json` as a starter alias seed when bilingual normalization helps

Output expectations:

- matched keywords
- missing keywords
- estimated keyword coverage
- notes on the most important missing requirements

### 2. 经历相关性

- compare target role focus with the candidate's prior role titles, projects, and responsibilities
- check whether the resume demonstrates similar business problems, execution scope, and outcomes
- reward adjacent relevance, but label it as partial rather than full alignment when needed

Output expectations:

- strongest matching experiences
- partial matches
- major relevance gaps

### 3. 学历 / 专业 / 证书匹配

- compare JD degree requirements with the resume
- note relevant majors, certifications, or domain credentials
- for China-first outputs, mention school tier or background signal only when the source supports it and it is relevant to the target role

Output expectations:

- education match or mismatch
- relevant certifications if present
- whether this area is a risk, neutral factor, or advantage

### 4. 信息密度与表达质量

- check whether bullets show clear actions, context, and outcomes
- prefer quantified impact when the source supports it
- call out vague, repetitive, or low-signal phrasing
- check whether the most relevant information is surfaced early enough

Output expectations:

- high-value strengths already expressed well
- bullets that are too generic
- rewrite priorities

### 5. 基础格式合规

- verify that major sections are recognizable
- avoid over-weighting ATS-specific parser issues in the China-first flow
- only flag format issues that materially hurt readability or extraction

Output expectations:

- obvious structure risks
- inconsistent dates or headings
- severe readability problems only

## Recommended Output Shape

Use this structure by default:

1. `岗位匹配结论`
2. `综合匹配度`
3. `核心要求命中情况`
4. `经历相关性分析`
5. `学历 / 背景匹配`
6. `信息密度与表达问题`
7. `Top 3 修改建议`
8. `可直接替换的简历表达`

## Output Writing Rules

- write in clear Simplified Chinese unless another language is requested
- do not use the term `ATS score` in China-first outputs
- start with the fit conclusion, then explain the evidence
- avoid fake certainty when the source is sparse
- do not invent missing experience, metrics, schools, or certificates
- make rewrite suggestions concrete enough to act on immediately

## Rating Labels

Use labels like:

- `高匹配`
- `中高匹配`
- `中等匹配`
- `低匹配`

Use the numeric score as supporting context only when it improves prioritization.

## Error Recovery

- **JD 无法解析**（加密 PDF、图片扫描件、格式损坏）：提示用户用 `extract_text.py` 尝试提取；如仍失败，建议用户提供纯文本 JD
- **提取的关键词太少**（JD 过于简短或模糊）：用岗位名称和公司信息补充搜索，在报告中标注「JD 信息有限，分析仅供参考」
- **experience level 无法计算**（没有 profile_store 或缺乏日期信息）：跳过 experience+1 规则，仅对比 JD 要求年限与简历中可识别的全职工作年份
- **简历完全不匹配 JD**：如实输出低匹配结论，不要为了「好看」而编造匹配点。给出明确的转方向建议或需要补充的能力清单
