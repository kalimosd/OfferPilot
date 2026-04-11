# Workflow

Use this workflow for all OfferPilot tasks.

## 1. Classify the Task

Choose one of:

- general resume optimization
- job-targeted resume rewrite
- jd-fit diagnosis
- cover letter generation
- job discovery and recommendation

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
3. produce final export-ready formatting or PDF

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
- [ ] for recommendation tasks, shortlist includes actionable links and concise reasons
