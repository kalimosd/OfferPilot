def build_resume_optimization_prompt(
    resume_text: str,
    target_language: str = "same",
    style: str = "classic",
    job_text: str | None = None,
) -> str:
    language_instruction = _build_language_instruction(target_language)
    style_instruction = _build_style_instruction(style)
    job_instruction = _build_job_instruction(job_text)

    return f"""
You are an expert resume editor for international students and entry-level job seekers.

Rewrite the resume content below so it is stronger for job applications.

Requirements:
- Keep the output concise and professional
- Use strong action-oriented bullet points
- Emphasize measurable impact when possible
- Improve clarity, grammar, and phrasing
- Do not invent fake experience or fake metrics
- If a metric is missing, improve the wording without fabricating numbers
- Preserve the candidate's actual experience and intent
- Use clean Markdown formatting
- Prefer short sections and compact bullets
- If the source content is sparse, improve wording without adding new facts
- Remove filler, repetition, and weak phrasing
- Make each bullet sound interview-ready rather than generic
- Use "-" for bullet points
- Keep contact details plain and clean with no emoji
- Preserve the candidate's legal name exactly; do not invent, alter, or "improve" the spelling
- If the source name is Chinese and English output is requested, transliterate to pinyin and format as Given Name + Family Name
- For a standard Chinese full name, treat the first character as the family name and the remaining characters as the given name

Language:
- {language_instruction}

Style:
- {style_instruction}

Job targeting:
- {job_instruction}

Output format:
- Start with the candidate name as a heading if a name is present
- Group content into simple resume sections when appropriate
- Use bullet points for experience and projects
- Keep bullets to 1 line when possible
- Avoid long paragraphs
- Do not include commentary, notes, or labels like "Improved Version"
- Return only the improved resume text with no explanation

Resume:
{resume_text}

Target Job Description:
{job_text.strip() if job_text else "Not provided."}
""".strip()


def build_resume_diagnosis_prompt(
    resume_text: str,
    target_language: str = "same",
    job_text: str | None = None,
) -> str:
    language_instruction = _build_diagnosis_language_instruction(target_language)
    job_instruction = _build_diagnosis_job_instruction(job_text)

    return f"""
You are an expert resume reviewer for job applications.

Analyze the resume below and produce a structured diagnosis before any rewrite.

Requirements:
- Do not rewrite the resume
- Do not invent facts, missing experience, or missing metrics
- Identify strengths, weaknesses, risks, and missing signals
- Focus on what matters for hiring outcomes
- Be specific and practical rather than generic
- If a job description is provided, evaluate fit against that job
- If no job description is provided, evaluate general job-readiness
- Preserve the candidate's legal name exactly if you mention it
- Keep the output concise, readable, and decision-oriented

Language:
- {language_instruction}

Job targeting:
- {job_instruction}

Output format:
- Use Markdown
- Include these sections in order:
  1. `## Summary`
  2. `## Strengths`
  3. `## Gaps`
  4. `## Risks`
  5. `## Recommended Fixes`
- Under `## Strengths`, list 3-5 bullets
- Under `## Gaps`, list 3-5 bullets
- Under `## Risks`, list only real concerns that are supported by the resume
- Under `## Recommended Fixes`, list the highest-value improvements first
- Return only the diagnosis with no extra commentary

Resume:
{resume_text}

Target Job Description:
{job_text.strip() if job_text else "Not provided."}
""".strip()


def _build_language_instruction(target_language: str) -> str:
    if target_language == "en":
        return (
            "Write the entire resume in polished English for international job applications. "
            "Do not translate word-for-word. Use natural resume language. "
            "Keep person names accurate and use Given Name + Family Name order. "
            "For Chinese names, the surname usually comes first in Chinese but should appear last in English."
        )

    if target_language == "zh":
        return "Write the entire resume in concise, professional Simplified Chinese."

    return (
        "Keep the resume in the same language as the source content unless the source mixes languages."
    )


def _build_style_instruction(style: str) -> str:
    if style == "ats":
        return (
            "Use ATS-friendly formatting: plain headings, straightforward bullets, minimal decoration, "
            "and emphasize keywords and clarity."
        )

    if style == "compact":
        return (
            "Use a compact one-page-friendly style: tighter bullets, fewer filler words, and denser phrasing "
            "without losing clarity."
        )

    return (
        "Use a classic professional resume style with clean sectioning, balanced readability, and polished phrasing."
    )


def _build_job_instruction(job_text: str | None) -> str:
    if job_text and job_text.strip():
        return (
            "Tailor the resume toward the provided job description. Prioritize the most relevant experience, "
            "align wording with important responsibilities and skills, and surface matching keywords naturally "
            "without inventing facts."
        )

    return "No specific job description is provided, so optimize for general job-readiness."


def _build_diagnosis_language_instruction(target_language: str) -> str:
    if target_language == "en":
        return "Write the entire diagnosis in polished English."

    if target_language == "zh":
        return "Write the entire diagnosis in concise, professional Simplified Chinese."

    return "Keep the diagnosis in the same language as the source content unless the source mixes languages."


def _build_diagnosis_job_instruction(job_text: str | None) -> str:
    if job_text and job_text.strip():
        return (
            "Assess fit against the provided job description. Call out matching signals, missing requirements, "
            "keyword gaps, and places where the resume undersells relevant experience."
        )

    return "Assess the resume for general job-readiness, clarity, credibility, and interview potential."
