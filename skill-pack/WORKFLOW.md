# Workflow

Use this workflow for all OfferPilot tasks.

## 1. Classify the Task

Choose one of:

- profile datastore building (`PROFILE_BUILDER.md`)
- resume diagnosis (`RESUME_DIAGNOSIS.md`)
- general resume optimization (`PROMPTS.md` + `OUTPUTS.md`)
- job-targeted resume rewrite (`DATASTORE.md` + `PROMPTS.md` + `OUTPUTS.md`)
- jd-fit diagnosis (`JD_MATCHING.md`)
- structured evaluation (`EVALUATION.md`)
- batch evaluation (`EVALUATION.md`)
- offer evaluation and negotiation (`OFFER_EVALUATION.md`)
- cover letter generation (`PROMPTS.md`)
- job discovery and recommendation (`scan_portals.py` / `run_pipeline.py`)
- mock interview, post-interview debrief, or behavioral prep (`MOCK_INTERVIEW.md`)
- product research (`PRODUCT_RESEARCH.md`)
- application tracking (`TRACKER.md`)
- multi-channel outreach (`OUTREACH.md`)

## 2. Minimal Read Graph (按任务按需读取)

To avoid context bloating, read ONLY the documents required for the active task:

| Task Type | Required Documents to Read |
|---|---|
| **Profile Datastore Building** | `PROMPTS.md` → `DATASTORE.md` → `PROFILE_BUILDER.md` |
| **Resume Optimization / Targeted Rewrite** | `PROMPTS.md` → `OUTPUTS.md` → `DATASTORE.md` (if datastore used) |
| **Resume Diagnosis** | `PROMPTS.md` → `RESUME_DIAGNOSIS.md` |
| **JD-Fit Diagnosis** | `PROMPTS.md` → `JD_MATCHING.md` |
| **Structured / Batch Evaluation** | `PROMPTS.md` → `EVALUATION.md` |
| **Offer Evaluation & Negotiation** | `PROMPTS.md` → `OFFER_EVALUATION.md` |
| **Mock Interview / Debrief / Behavioral** | `PROMPTS.md` → `MOCK_INTERVIEW.md` |
| **Product Research** | `PROMPTS.md` → `PRODUCT_RESEARCH.md` |
| **Application Tracking** | `TRACKER.md` |
| **Outreach (Boss直聘 / 内推 / LinkedIn / Email)** | `PROMPTS.md` → `OUTREACH.md` |

## 3. Collect Inputs

Minimum inputs:

- original resume source or `profile_store.yaml`
- target language: `same`, `zh`, or `en`

Additional inputs when needed:

- job description for targeted resumes
- job description for jd-fit diagnosis
- job description for cover letters
- user-provided preferred romanization of the candidate name
- profile datastore (`profile_store.yaml`) for selection-based assembly (see `DATASTORE.md`)
- discovery constraints (city, role direction, seniority, remote/on-site preference) for job recommendation tasks
- for mock interview: job description + profile datastore (both required for Phase 1/2; interview questions/transcript required for Phase 3 debrief)
- for product research: job description (required) + profile datastore (optional)
- for structured evaluation: job description + profile datastore
- for offer evaluation: offer terms (base, months, bonus, equity, benefits, city) + optional competing offers
- for outreach: target company/role + profile datastore + optional channel (`boss` / `referral` / `linkedin` / `email`)

Input handling rules:

- if the source is `.txt`, `.md`, or `.yaml`/`.yml`, read it directly when possible
- if the source is `.pdf` or `.docx` and the agent cannot read it reliably, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` first
- use the extracted text as the working input after extraction succeeds

## 4. Normalize the Source of Truth

- Prefer the original resume or `profile_store.yaml` over any previously generated output
- If older generated drafts exist, treat them as reference only
- If the original file is private, avoid adding it to version control
- If the source content is sparse, improve clarity (or use `PROFILE_BUILDER.md` to ask follow-up questions) but do not invent facts
- If the source resume includes real contact details, keep them in the final deliverable unless the user explicitly asks for anonymization or redaction
- If the source resume does not include a contact detail, do not guess it, infer it, or add a placeholder as if it were real

## 5. Generate the Draft

**⚠ 生成简历类内容前必须确认以下规则：**

1. 读取 `OUTPUTS.md` — 确认 section 顺序、一页纸篇幅预算（14–18 条 bullets，800–1100 字）、输出目录、PDF style、文件命名
2. 读取 `PROMPTS.md` — 确认 Bullet 黄金公式、Few-shot 正反例、反模式黑名单和联系方式处理规则
3. 如果使用 profile datastore，读取 `DATASTORE.md` — 确认选取、组装与超标裁剪逻辑

> 格式和约束规则以 `OUTPUTS.md` 和 `PROMPTS.md` 为唯一依据，此处不再重复。以下 task 专属规则仅补充文档未覆盖的执行细节。

For profile datastore building:

- read `PROFILE_BUILDER.md` before extracting or updating `profile_store.yaml`

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
- tighten phrasing using the Golden Bullet Formula in `PROMPTS.md`
- remove filler and blacklisted buzzwords
- emphasize measurable impact only when the source supports it

For targeted resumes:

- if a profile datastore is provided, use the selection-based assembly path:
  1. parse the JD to extract requirements and keywords
  2. normalize keywords using `data/skill_aliases.zh-en.json`
  3. match keywords against bullet tags in the datastore
  4. rank matched bullets by relevance and impact level (`quantified` > `qualitative` > `context-only`)
  5. select the best variant for each bullet when available
  6. enforce the 1-page budget (14–18 bullets total), dropping low-relevance `context-only` items
  7. assemble selected bullets into resume sections and polish per `PROMPTS.md`
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

For mock interview, post-interview debrief, or behavioral prep:
- read `MOCK_INTERVIEW.md` before generating any content

For product research:
- read `PRODUCT_RESEARCH.md` before generating any content

For structured evaluation:
- read `EVALUATION.md` before scoring

For offer evaluation and negotiation:
- read `OFFER_EVALUATION.md` before calculating total compensation or writing negotiation scripts

For application tracking:
- read `TRACKER.md`

For multi-channel outreach:
- read `OUTREACH.md`

## 6. Review the Draft

Check:

- names
- phone numbers
- email addresses
- dates
- role titles
- company names
- section ordering and 1-page length budget
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

## 6b. Iterating on Feedback

用户 review 后提出修改意见时：

- **优先局部修改** — 只改用户指出的部分，不要重新生成整个文档
- **保持未修改内容** — 用户未提及的 section 保持原样（包括措辞和顺序）
- **版本号递增** — 修改后文件名版本号 +1（v1 → v2），保留旧版本文件不覆盖
- **重新触发条件** — 仅当用户明确说「重新生成」或「推翻重来」时，才走完整生成流程
- **迭代后验证** — 修改完成后重新运行 Section 7（Finalize），包括 PDF 重新导出与页数检查

## 7. Finalize the Deliverable

Preferred order:

1. review Markdown-like content first
2. revise content if needed
3. save the final Markdown file to the correct `outputs/` subdirectory
4. export PDF from the saved Markdown (for resume and cover letter tasks)

**输出目录规则（不可跳过）：**

- `outputs/resumes/` — 简历诊断、简历优化、定向改写、JD 匹配度分析、结构化评估、批量评估、Offer 评估与谈薪方案
- `outputs/research/` — 产品研究
- `outputs/interview/` — 面试题单、面试评估、真实面经复盘、行为面准备
- `outputs/pipeline/` — 扫描推荐、pipeline 报告
- `outputs/misc/` — Boss直聘打招呼、内推私信、LinkedIn 外联、其他

**交付规则（不可跳过）：**

- 简历类任务必须同时输出 Markdown 和 PDF 两个文件
- PDF 使用 `render_pdf.py` 生成，中文默认 style 为 `standard_cn`，英文默认 style 为 `classic`
- 若 `render_pdf.py` 提示页数超过 1 页（`WARNING: Rendered resume has X pages`），提示用户是否精简条目或切换 `--style compact`
- 两个文件的文件名必须一致（仅扩展名不同）

## Task Checklist

- [ ] correct task type selected and Minimal Read Graph followed
- [ ] original resume or `profile_store.yaml` used when available
- [ ] profile datastore used for selection when provided
- [ ] job description included for `jd-fit diagnosis`
- [ ] no fake achievements or fake metrics introduced
- [ ] source contact details are preserved in the final deliverable unless anonymization was requested
- [ ] missing contact details were not guessed, fabricated, or filled in without source support
- [ ] no placeholder fields like `<name>` or `<email>` remain unless the user explicitly asked for them
- [ ] private files kept out of git unless explicitly requested
- [ ] English name ordering checked when relevant
- [ ] final output matches the user's requested language and purpose
- [ ] for resume tasks, both Markdown and PDF files are saved and checked against the 1-page budget
- [ ] PDF uses `standard_cn` for Chinese resumes and `classic` for English resumes unless the user specified another style
- [ ] Markdown and PDF filenames are aligned (only extension differs)
- [ ] for recommendation tasks, shortlist includes actionable links and concise reasons
- [ ] for mock interview, question sheet saved before starting simulation
- [ ] for mock interview, evaluation report or debrief report and review checklist saved
- [ ] for product research, output saved as Markdown only (no PDF)
- [ ] for product research, profile_store sections included/skipped correctly based on availability
- [ ] for structured evaluation, scores follow `EVALUATION.md` weights and adaptive normalization
- [ ] for offer evaluation, total compensation breakdown and negotiation scripts saved to `outputs/resumes/`
- [ ] for outreach, message is saved to `outputs/misc/` and follows channel-specific length limits
