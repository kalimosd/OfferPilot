import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from offerpilot import cli


class CliTests(unittest.TestCase):
    def test_diagnose_command_saves_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / "resume.md"
            output_path = Path(temp_dir) / "diagnosis.md"
            resume_path.write_text("# Candidate\n- Built tooling\n", encoding="utf-8")

            with patch(
                "offerpilot.cli.call_llm",
                return_value="## Summary\n\nSolid technical baseline.\n",
            ) as mock_call:
                exit_code = cli.main(
                    [
                        "diagnose",
                        str(resume_path),
                        "--lang",
                        "zh",
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn("## Summary", output_path.read_text(encoding="utf-8"))
            mock_call.assert_called_once()

    def test_diagnose_command_loads_optional_job_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / "resume.md"
            job_path = Path(temp_dir) / "job.md"
            resume_path.write_text("# Candidate\n- Built tooling\n", encoding="utf-8")
            job_path.write_text("Need AI solution planning experience.\n", encoding="utf-8")

            captured_prompt: list[str] = []

            def fake_call(prompt: str, provider: str = "deepseek", model: str | None = None) -> str:
                captured_prompt.append(prompt)
                return "## Summary\n\nStrong fit.\n"

            with patch("offerpilot.cli.call_llm", side_effect=fake_call):
                exit_code = cli.main(
                    [
                        "diagnose",
                        str(resume_path),
                        "--job",
                        str(job_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(captured_prompt), 1)
            self.assertIn("Need AI solution planning experience.", captured_prompt[0])


if __name__ == "__main__":
    unittest.main()
