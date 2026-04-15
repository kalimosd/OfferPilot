# Workflow

Use this workflow for all OfferPilot tasks.

## 1. Classify the Task

Choose one of:

- general resume optimization
- job-targeted resume rewrite
- jd-fit diagnosis
- cover letter generation
- job discovery and recommendation
- mock interview

## 2. Collect Inputs

Minimum inputs:

- original resume source
- target language: `same`, `zh`, or `en`

Additional inputs when needed:

- job description for targeted resumes
- job description for jd-fit diagnosis
- job description for cover letters
- user-provided preferred romanization of the candidate name
- profile datastore (`profile_store.yaml`) for selection-based assembly (see `DATASTORE.md`)
- discovery constraints (city, role direction, seniority, remote/on-site preference) for job recommendation tasks
- for mock interview: job description + profile datastore (both required)

Input handling rules:

- if the source is `.txt` or `.md`, read it directly when possible
- if the source is `.pdf` or `.docx` and the agent cannot read it reliably, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` first
- use the extracted text as the working input after extraction succeeds

## 3. Normalize the Source of Truth

- Prefer the original resume over any previously generated output
- If older generated drafts exist, treat them as reference only
- If the original file is private, avoid adding it to version control
- If the source content is sparse, improve clarity but do not invent facts
- If the source resume includes real contact details, keep them in the final deliverable unless the user explicitly asks for anonymization or redaction
- If the source resume does not include a contact detail, do not guess it, infer it, or add a placeholder as if it were real

## 4. Generate the Draft

**⚠ 必须在生成任何内容之前完成以下读取，不可跳过：**

1. 读取 `OUTPUTS.md` — 确认 section 顺序、分离规则、PDF style
2. 读取 `PROMPTS.md` — 确认写作约束和联系方式处理规则
3. 如果使用 profile datastore，读取 `DATASTORE.md` — 确认选取和组装逻辑

**关键规则速查（不可违反）：**

- section 顺序：教育背景 → 工作经历 → 强相关项目 → 实习经历 → 其他项目 → 技能
- 实习经历和工作经历**必须分开**，不能合并
- 实习经历和项目经历**必须分开**，不能合并
- PDF 中文简历默认使用 `--style standard_cn`
- 文件命名：`姓名_公司_岗位_v1`

For jd-fit diagnosis:

- extract the core requirements from the JD
- identify direct evidence from the resume
- separate matched, partial, and missing signals
- explain the biggest fit gaps in practical language
- prioritize concrete rewrite suggestions

For resume optimization:

- preserve the candidate's actual experience
- tighten phrasing
- remove filler
- emphasize measurable impact only when the source supports it

For targeted resumes:

- if a profile datastore is provided, use the selection-based assembly path:
  1. parse the JD to extract requirements and keywords
  2. normalize keywords using `data/skill_aliases.zh-en.json`
  3. match keywords against bullet tags in the datastore
  4. rank matched bullets by relevance and impact level
  5. select the best variant for each bullet when available
  6. assemble selected bullets into resume sections
  7. polish phrasing per `PROMPTS.md` rules
- if no datastore is provided, fall back to direct rewrite:
  - align with the job description
  - surface matching keywords naturally
  - prioritize the most relevant experience

For cover letters:

- connect the resume to the job description
- stay specific
- keep the tone concise and credible

For job discovery and recommendation:

- discover jobs using `python3 skill-pack/scripts/scan_portals.py` when fresh listings are needed
- prioritize China-first relevance when user preference indicates domestic targeting
- rank opportunities by role fit signal, level signal, and source reliability
- return a compact shortlist (for example top 10) with clear reasons and links
- if results are too sparse, relax non-critical filters first (location > title strictness) and report what changed

For mock interview:

- read `MOCK_INTERVIEW.md` before generating any content
- follow the two-phase workflow: question generation then live simulation
- both JD and profile datastore are required inputs

## 5. Review the Draft

Check:

- names
- phone numbers
- email addresses
- dates
- role titles
- company names
- section ordering
- factual consistency
- language consistency
- whether the fit conclusion is supported by evidence from both the JD and the resume
- whether rewrite suggestions are specific enough to act on
- for recommendation tasks, whether ranking reasons are explicit and auditable

If the draft is in English and the source name is Chinese:

- verify `Given Name + Family Name`
- if the user already supplied the preferred spelling, use that exact spelling

Example:

- `中文名` -> `<Given Name> <Family Name>`

## 6. Finalize the Deliverable

Preferred order:

1. review Markdown-like content first
2. revise content if needed
3. save the final Markdown file
4. export PDF from the saved Markdown

**交付规则（不可跳过）：**

- 简历类任务必须同时输出 Markdown 和 PDF 两个文件
- PDF 使用 `render_pdf.py` 生成，默认 style 为 `standard_cn`
- 仅当用户明确指定其他 style 或输出语言为英文时，才使用其他 style
- 两个文件的文件名必须一致（仅扩展名不同）

## Task Checklist

- [ ] correct task type selected
- [ ] original resume used when available
- [ ] profile datastore used for selection when provided
- [ ] job description included for `jd-fit diagnosis`
- [ ] no fake achievements or fake metrics introduced
- [ ] source contact details are preserved in the final deliverable unless anonymization was requested
- [ ] missing contact details were not guessed, fabricated, or filled in without source support
- [ ] no placeholder fields like `<name>` or `<email>` remain unless the user explicitly asked for them
- [ ] private files kept out of git unless explicitly requested
- [ ] English name ordering checked when relevant
- [ ] final output matches the user's requested language and purpose
- [ ] for resume tasks, both Markdown and PDF files are saved
- [ ] PDF uses `standard_cn` style unless user specified otherwise or output is English
- [ ] Markdown and PDF filenames are aligned (only extension differs)
- [ ] for recommendation tasks, shortlist includes actionable links and concise reasons
- [ ] for mock interview, question sheet saved before starting simulation
- [ ] for mock interview, evaluation report and review checklist saved after simulation
