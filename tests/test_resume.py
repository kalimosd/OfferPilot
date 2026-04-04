import unittest

from offerpilot.resume import (
    build_resume_diagnosis_prompt,
    build_resume_optimization_prompt,
)


class ResumePromptTests(unittest.TestCase):
    def test_english_prompt_mentions_english_output(self) -> None:
        prompt = build_resume_optimization_prompt("sample", target_language="en")

        self.assertIn("polished English", prompt)
        self.assertIn("Given Name + Family Name order", prompt)

    def test_prompt_requires_preserving_name_accuracy(self) -> None:
        prompt = build_resume_optimization_prompt("sample", target_language="en")

        self.assertIn("Preserve the candidate's legal name exactly", prompt)
        self.assertIn("transliterate to pinyin", prompt)
        self.assertIn("first character as the family name", prompt)
        self.assertIn("surname usually comes first in Chinese but should appear last in English", prompt)

    def test_same_language_prompt_mentions_source_language(self) -> None:
        prompt = build_resume_optimization_prompt("sample", target_language="same")

        self.assertIn("same language as the source content", prompt)

    def test_ats_prompt_mentions_ats_friendly_style(self) -> None:
        prompt = build_resume_optimization_prompt("sample", style="ats")

        self.assertIn("ATS-friendly formatting", prompt)

    def test_job_targeting_prompt_mentions_job_alignment(self) -> None:
        prompt = build_resume_optimization_prompt(
            "sample",
            job_text="Need Android development and performance optimization experience.",
        )

        self.assertIn("Tailor the resume toward the provided job description", prompt)
        self.assertIn("Target Job Description:", prompt)

    def test_job_targeting_prompt_mentions_job_alignment(self) -> None:
        prompt = build_resume_optimization_prompt(
            "sample",
            job_text="Need Android development and performance optimization experience.",
        )

        self.assertIn("Tailor the resume toward the provided job description", prompt)
        self.assertIn("Target Job Description:", prompt)

    def test_diagnosis_prompt_requests_structured_sections(self) -> None:
        prompt = build_resume_diagnosis_prompt("sample", target_language="zh")

        self.assertIn("Analyze the resume below and produce a structured diagnosis", prompt)
        self.assertIn("## Summary", prompt)
        self.assertIn("## Strengths", prompt)
        self.assertIn("## Gaps", prompt)
        self.assertIn("## Risks", prompt)
        self.assertIn("## Recommended Fixes", prompt)

    def test_diagnosis_prompt_mentions_job_fit_when_job_provided(self) -> None:
        prompt = build_resume_diagnosis_prompt(
            "sample",
            job_text="Need AI solution design and cross-functional delivery experience.",
        )

        self.assertIn("Assess fit against the provided job description", prompt)
        self.assertIn("Target Job Description:", prompt)

    def test_diagnosis_prompt_mentions_chinese_output_when_requested(self) -> None:
        prompt = build_resume_diagnosis_prompt("sample", target_language="zh")

        self.assertIn("concise, professional Simplified Chinese", prompt)


if __name__ == "__main__":
    unittest.main()
