# Prompts

Use these prompt rules regardless of the AI platform.

## Shared Constraints

- preserve the candidate's real experience and intent
- preserve real contact details from the source resume in the final deliverable unless the user explicitly requests anonymization
- do not invent fake jobs, fake metrics, or fake credentials
- do not guess, infer, or fabricate missing names, phone numbers, or email addresses
- improve clarity, structure, and credibility
- keep outputs concise and usable for applications
- avoid commentary such as `Improved Version`
- do not replace real names, phone numbers, or email addresses with placeholders like `<name>` or `<email>` in local output files unless the user explicitly asks for redaction

## Resume Optimization Prompt Shape

Use a prompt that asks the model to:

- rewrite the resume for job applications
- improve bullet quality
- preserve facts
- remove filler
- keep the output clean and sectioned

## Targeted Resume Prompt Shape

Use a prompt that asks the model to:

- tailor the resume toward the provided job description
- surface matching skills and responsibilities
- emphasize the most relevant experience first
- stay truthful to the source

## JD-Fit Diagnosis Prompt Shape

Use a prompt that asks the model to:

- extract the JD's core requirements first
- identify direct evidence from the resume for each requirement
- label each requirement as matched, partially matched, or missing
- explain the fit in practical hiring language instead of abstract theory
- prioritize the top rewrite actions that would most improve alignment
- avoid using the term `ATS score` for China-first outputs unless the user explicitly requests it

For China-first outputs, prefer a structure like:

- `岗位匹配结论`
- `综合匹配度`
- `核心要求命中情况`
- `经历相关性分析`
- `学历 / 背景匹配`
- `信息密度与表达问题`
- `Top 3 修改建议`
- `可直接替换的简历表达`

## Cover Letter Prompt Shape

Use a prompt that asks the model to:

- connect the resume to the job description
- explain relevant fit using real experiences
- keep the letter concise
- avoid generic enthusiasm without evidence

## Name Handling Prompt Rules

For English outputs:

- preserve the candidate name accurately
- if the source name is Chinese, use pinyin unless the user gave a preferred spelling
- format the English name as `Given Name + Family Name`
- do not create a western nickname

## Contact Detail Handling Rules

- keep source phone numbers and email addresses in the final resume when they are present and the document is intended for actual job applications
- if privacy is a concern, avoid repeating sensitive contact details in chat summaries, but keep them in the generated local deliverable
- only use placeholders or redaction when the user explicitly requests anonymization
- if the source does not provide a phone number or email address, leave it absent rather than guessing or inventing one

## Suggested Validation Questions

After generation, ask:

- does every bullet map back to a real source fact?
- is the name correct?
- are phone number and email preserved when present in the source?
- were missing contact details left absent instead of being guessed or fabricated?
- did the output keep the requested language?
- did the model overstate impact beyond the source?
- does each match or gap cite evidence from the JD or the resume?
- are the rewrite suggestions concrete enough to use immediately?
