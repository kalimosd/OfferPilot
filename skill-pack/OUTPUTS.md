# Outputs

## Output Categories

OfferPilot supports three main output types:

- resume diagnosis
- optimized resume
- job-targeted resume
- jd-fit diagnosis
- cover letter
- mock interview question sheet
- mock interview evaluation report

## Age Display

- Display age on the contact information line, after email: `电话（微信同） | 邮箱 | XX 岁`
- Calculate age from the `birth_year` field in the profile datastore: `current_year - birth_year`
- Format: `XX 岁` for Chinese outputs, `Age XX` for English outputs
- If `birth_year` is not provided, omit the age line

## Education Line Format

- 学历 emphasis 行使用 `|` 分隔学校、专业和学位，格式为：`**学校名 | 专业 | 学位**`
- 示例：`**墨尔本大学 | 数据科学 | 硕士**`
- 英文示例：`**University of Melbourne | Data Science | Master**`

## Default Section Ordering

Use this order for resume outputs unless the user requests otherwise:

1. 教育背景
2. 工作经历
3. 与目标岗位强相关的项目经历（如投 AI 岗则优先展示 AI 项目）
4. 实习经历
5. 其他项目经历（科研、学术等）
6. 技能

Rules:

- 实习经历和项目经历必须分开，不能合并为同一个 section
- 当存在多类项目时，与目标岗位相关性更高的项目 section 排在实习之前，其余排在实习之后
- 如果没有明确的目标岗位，所有项目经历统一放在实习经历之后
- 不要生成"工作亮点"等额外总结性 section，除非用户明确要求

## Resume Diagnosis Expectations

- identifies strengths that are already supported by the source
- identifies gaps relative to either general job-readiness or a target job
- calls out risks without inventing problems
- suggests the highest-value rewrite priorities before generation

## JD-Fit Diagnosis Expectations

- explains how well the resume matches the target JD
- separates matched, partial, and missing signals
- prioritizes practical rewrite actions over abstract commentary
- uses a score only as supporting context, not as the sole conclusion
- avoids `ATS score` framing for China-first outputs unless explicitly requested

## Language Options

- `same`: keep the source language unless the source is mixed and the user asked for cleanup
- `zh`: produce professional Simplified Chinese
- `en`: produce polished English for job applications

## Resume Output Expectations

- clear sectioning
- concise bullet points
- stronger action-oriented phrasing
- no fabricated facts
- no inflated metrics
- compact, interview-ready tone
- preserves real source contact details in the final deliverable unless the user explicitly requested anonymization
- does not leave placeholder fields such as `<name>`, `<phone number>`, or `<email>` in application-ready outputs
- does not add guessed or fabricated contact details that are missing from the source

## PDF Style Options

The `render_pdf.py` script supports multiple styles via `--style`:

- `classic` — default, left-aligned, clean layout
- `ats` — optimized for ATS parsing, slightly smaller text
- `compact` — tighter margins and spacing for dense content
- `standard_cn` — centered name and contact info, section headings with solid underline, sub-headings with light dashed underline, dates right-aligned

**默认选择规则：**

- 中文简历 → `standard_cn`
- 英文简历 → `classic`
- 除非用户明确指定其他 style

## PDF Formatting Rules

- Project links (e.g. GitHub URLs) should be placed on a separate line below the project title in small text, not inline with the title
- Dates in headings are rendered right-aligned; all date columns start at the same horizontal position
- Section headings and their content are kept together across page breaks when possible

## Recommended File Naming

Use scheme `B` by default for locally saved resume deliverables:

- if only a target role is known: `姓名_岗位_v1`
- if both company and role are known: `姓名_公司_岗位_v1`
- keep the version suffix even for the first saved draft
- use `_` as the separator
- avoid spaces in filenames
- keep Markdown and PDF filenames aligned except for the file extension

Examples:

- `候选人A_安卓开发工程师_v1.md`
- `候选人A_小米_安卓开发工程师_v1.md`
- `候选人A_小米_安卓开发工程师_v2.pdf`

If the user explicitly requests anonymized sample files, replace `姓名` with an obvious example name rather than a real person.

## Targeted Resume Expectations

- emphasizes experience relevant to the target role
- incorporates job-description language naturally
- reorders emphasis without changing the underlying facts

## Cover Letter Expectations

- reflects the job description
- stays grounded in the candidate's real background
- avoids generic filler
- keeps the tone professional and direct

## Mock Interview Question Sheet Expectations

- 8-12 questions by default unless the user specifies otherwise
- ~60% strong-point deep-dive, ~40% weakness probing
- each question includes: tag, difficulty, topic, examination points, reference answer key points
- reference answers are concise key points, not full essays
- naming: `姓名_公司_岗位_面试题单_v1.md`

## Mock Interview Evaluation Report Expectations

- per-question scoring (1-5 stars) with highlights, gaps, and improvement suggestions
- overall summary in 2-3 sentences
- review checklist with priority levels (高/中/低) and concrete learning recommendations
- naming: `姓名_公司_岗位_面试评估_v1.md`

## English Name Check

When the source resume is Chinese and the output is English:

- verify the English name order
- default to `Given Name + Family Name`
- keep the user-provided spelling if one exists

Example:

- `中文名` -> `<Given Name> <Family Name>`

## Final Review Checklist

- [ ] name is correct
- [ ] phone number is correct when present in the source
- [ ] email address is correct when present in the source
- [ ] missing contact details were left absent unless the user explicitly provided them later
- [ ] dates are correct
- [ ] titles and employer names are correct
- [ ] content matches the intended task
- [ ] language matches the request
- [ ] fit conclusions are supported by resume and JD evidence
- [ ] rewrite suggestions are concrete and truthful
- [ ] no placeholder contact fields remain unless anonymization was explicitly requested
- [ ] saved filenames follow the default naming rule unless the user asked for a different scheme
- [ ] nothing confidential is accidentally included in publishable artifacts
