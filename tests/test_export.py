import tempfile
import unittest
import warnings
import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent / "skill-pack" / "scripts" / "render_pdf.py"
)
MODULE_SPEC = importlib.util.spec_from_file_location("offerpilot_render_pdf", MODULE_PATH)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
render_pdf = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = render_pdf
MODULE_SPEC.loader.exec_module(render_pdf)


def _write_fake_pdf(path: Path, marker: bytes = b"%PDF-1.4\n") -> None:
    path.write_bytes(marker + b"fake pdf body\n")


class ExportTests(unittest.TestCase):
    def test_extract_heading_text_supports_level_three_headings(self) -> None:
        self.assertEqual(render_pdf._extract_heading_text("### **Education**"), "Education")

    def test_strip_markdown_inline_removes_emphasis_markers(self) -> None:
        text = "**Company** | *Role* | 2024-07 - Present"

        cleaned = render_pdf._strip_markdown_inline(text)

        self.assertEqual(cleaned, "Company | Role | 2024-07 - Present")

    def test_sanitize_pdf_text_replaces_unsupported_unicode_punctuation(self) -> None:
        text = "content‑side data – time‑series"

        sanitized = render_pdf._sanitize_pdf_text(text)

        self.assertEqual(sanitized, "content-side data - time-series")

    def test_parse_markdown_blocks_captures_resume_structure(self) -> None:
        markdown = "# Candidate Example\nPhone: 123\n\n## Experience\n- Built tooling\n**Key Project**\n"

        blocks = render_pdf._parse_markdown_blocks(markdown)

        self.assertEqual(
            [(block.kind, block.level, block.text) for block in blocks],
            [
                ("heading", 1, "Candidate Example"),
                ("meta", 0, "Phone: 123"),
                ("blank", 0, ""),
                ("heading", 2, "Experience"),
                ("bullet", 0, "Built tooling"),
                ("emphasis", 0, "Key Project"),
            ],
        )

    def test_render_blocks_to_html_builds_browser_friendly_markup(self) -> None:
        markdown = (
            "# 候选人示例\n"
            "Phone: 123\n"
            "## Experience\n"
            "- 使用 **Perfetto** / *Systrace* 分析\n"
        )
        blocks = render_pdf._parse_markdown_blocks(markdown)

        html = render_pdf._render_blocks_to_html(
            blocks,
            style_config=render_pdf._get_style_config("classic", "resume"),
            document_type="resume",
            style="classic",
        )

        self.assertIn('class="document style-classic type-resume"', html)
        self.assertIn("<h1 class=\"name\">候选人示例</h1>", html)
        self.assertIn("<p class=\"meta\">Phone: 123</p>", html)
        self.assertIn("<ul class=\"bullet-list\">", html)
        self.assertIn("<strong>Perfetto</strong>", html)
        self.assertIn("<em>Systrace</em>", html)
        self.assertIn("font-kerning: normal;", html)
        self.assertIn("PingFang SC", html)

    def test_render_markdown_to_pdf_prefers_browser_renderer(self) -> None:
        markdown = "# Candidate Example\nPhone: 123\n\n## Experience\n- Built tooling\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "resume.pdf"

            def fake_browser_renderer(html: str, path: Path) -> None:
                self.assertIn("OfferPilot PDF Export", html)
                _write_fake_pdf(path, marker=b"%PDF-browser\n")

            with patch(
                "offerpilot_render_pdf._render_html_to_pdf_with_playwright",
                side_effect=fake_browser_renderer,
            ) as browser_renderer, patch(
                "offerpilot_render_pdf._render_markdown_to_pdf_with_reportlab"
            ) as fallback_renderer:
                saved_path = render_pdf.render_markdown_to_pdf(markdown, str(output_path))

            self.assertTrue(saved_path.exists())
            self.assertIn(b"%PDF-browser", saved_path.read_bytes())
            browser_renderer.assert_called_once()
            fallback_renderer.assert_not_called()

    def test_render_markdown_to_pdf_raises_when_browser_render_fails(self) -> None:
        markdown = "# Candidate Example\nPhone: 123\n\n## Experience\n- Built tooling\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "resume.pdf"

            with patch(
                "offerpilot_render_pdf._render_html_to_pdf_with_playwright",
                side_effect=RuntimeError("Chromium missing"),
            ) as browser_renderer, patch(
                "offerpilot_render_pdf._render_markdown_to_pdf_with_reportlab"
            ) as fallback_renderer:
                with self.assertRaises(RuntimeError) as ctx:
                    render_pdf.render_markdown_to_pdf(
                        markdown,
                        str(output_path),
                        document_type="cover_letter",
                        style="ats",
                    )

            self.assertIn("Chromium missing", str(ctx.exception))
            browser_renderer.assert_called_once()
            fallback_renderer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
