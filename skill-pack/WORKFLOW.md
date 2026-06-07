# Workflow

Use this workflow for all OfferPilot tasks.

## 1. Classify the Task

Choose one of:

- resume diagnosis
- general resume optimization
- job-targeted resume rewrite
- jd-fit diagnosis
- structured evaluation
- batch evaluation
- cover letter generation
- job discovery and recommendation
- mock interview
- product research
- application tracking
- LinkedIn outreach

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
- for product research: job description (required) + profile datastore (optional)
- for structured evaluation: job description + profile datastore
- for LinkedIn outreach: target company/role + profile datastore

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

1. 读取 `OUTPUTS.md` — 确认 section 顺序、分离规则、输出目录、PDF style、文件命名
2. 读取 `PROMPTS.md` — 确认写作约束和联系方式处理规则
3. 如果使用 profile datastore，读取 `DATASTORE.md` — 确认选取和组装逻辑

> 格式和约束规则以 `OUTPUTS.md` 和 `PROMPTS.md` 为唯一依据，此处不再重复。以下 task 专属规则仅补充文档未覆盖的执行细节。

For jd-fit diagnosis:

- extract the core requirements from the JD
- identify direct evidence from the resume
- separate matched, partial, and missing signals
- explain the biggest fit gaps in practical language
- prioritize concrete rewrite suggestions
- use the experience-level rule in `JD_MATCHING.md` when a JD specifies years of experience

For resume diagnosis:

- read `RESUME_DIAGNOSIS.md` before generating any content

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

For product research:
- read `PRODUCT_RESEARCH.md` before generating any content

For structured evaluation:
- read `EVALUATION.md` before scoring

For application tracking:
- read `TRACKER.md`

For LinkedIn outreach:
- read `OUTREACH.md`

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
- for product research, whether product information is sourced from search results (not fabricated)
- for product research, whether interview questions are specific and answerable

If the draft is in English and the source name is Chinese:

- verify `Given Name + Family Name`
- if the user already supplied the preferred spelling, use that exact spelling

Example:

- `中文名` -> `<Given Name> <Family Name>`

## 5b. Iterating on Feedback

用户 review 后提出修改意见时：

- **优先局部修改** — 只改用户指出的部分，不要重新生成整个文档
- **保持未修改内容** — 用户未提及的 section 保持原样（包括措辞和顺序）
- **版本号递增** — 修改后文件名版本号 +1（v1 → v2），保留旧版本文件不覆盖
- **重新触发条件** — 仅当用户明确说「重新生成」或「推翻重来」时，才走完整生成流程
- **迭代后验证** — 修改完成后重新运行 Section 6（Finalize），包括 PDF 重新导出

## 6. Finalize the Deliverable

Preferred order:

1. review Markdown-like content first
2. revise content if needed
3. save the final Markdown file to the correct `outputs/` subdirectory
4. export PDF from the saved Markdown

**输出目录规则（不可跳过）：**

- `outputs/resumes/` — 简历优化、定向改写、JD 匹配度分析、结构化评估、批量评估
- `outputs/research/` — 产品研究
- `outputs/interview/` — 面试题单、面试评估、面试准备
- `outputs/pipeline/` — 扫描推荐、pipeline 报告
- `outputs/misc/` — 其他

**交付规则（不可跳过）：**

- 简历类任务必须同时输出 Markdown 和 PDF 两个文件
- PDF 使用 `render_pdf.py` 生成，中文默认 style 为 `standard_cn`，英文默认 style 为 `classic`
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
- [ ] PDF uses `standard_cn` for Chinese resumes and `classic` for English resumes unless the user specified another style
- [ ] Markdown and PDF filenames are aligned (only extension differs)
- [ ] for recommendation tasks, shortlist includes actionable links and concise reasons
- [ ] for mock interview, question sheet saved before starting simulation
- [ ] for mock interview, evaluation report and review checklist saved after simulation
- [ ] for product research, output saved as Markdown only (no PDF)
- [ ] for product research, profile_store sections included/skipped correctly based on availability
- [ ] for structured evaluation, scores follow `EVALUATION.md` weights and grade mapping
- [ ] for LinkedIn outreach, message is saved to `outputs/misc/` and remains under 300 words
