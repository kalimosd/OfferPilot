#!/usr/bin/env python3
"""Render OfferPilot markdown outputs to PDF."""

from __future__ import annotations

import argparse
import re
import warnings
from dataclasses import dataclass
from html import escape
from pathlib import Path

HEADER_ALIGNMENT_LEFT = 0

_DATE_TAIL_RE = re.compile(r'[\s\u3000]+([\d]{4}[\.\-/][\d]{2}\s*[–\-~]\s*(?:[\d]{4}[\.\-/][\d]{2}|至今|present|Present))\s*$')


def _split_date_tail(text: str) -> tuple[str, str | None]:
    """Split trailing date range from text. Returns (main_text, date_or_None)."""
    m = _DATE_TAIL_RE.search(text)
    if m:
        return text[:m.start()].rstrip(), m.group(1).strip()
    return text, None
LATIN_REGULAR_FONT = "Helvetica"
LATIN_BOLD_FONT = "Helvetica-Bold"
CJK_FONT = "STSong-Light"
DEFAULT_FONT_STACK = (
    '"Inter", "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", '
    '"Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif'
)
MONOSPACE_FONT_STACK = (
    '"SFMono-Regular", "Cascadia Mono", "Liberation Mono", Consolas, monospace'
)

UNICODE_PDF_SAFE_TRANSLATION = str.maketrans(
    {
        "\u00a0": " ",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
    }
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render OfferPilot markdown-like content to PDF."
    )
    parser.add_argument("input", help="Path to the markdown or text source file.")
    parser.add_argument("output", help="Path to the output PDF file.")
    parser.add_argument(
        "--document-type",
        choices=["resume", "cover_letter"],
        default="resume",
        help="Document type to render. Default: resume.",
    )
    parser.add_argument(
        "--style",
        choices=["classic", "ats", "compact", "wondercv"],
        default="classic",
        help="PDF style to use. Default: classic.",
    )
    return parser


def render_markdown_to_pdf(
    markdown_text: str,
    output_path: str,
    document_type: str = "resume",
    style: str = "classic",
) -> Path:
    """Render markdown-like resume text to a PDF file."""
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    style_config = _get_style_config(style, document_type)
    blocks = _parse_markdown_blocks(markdown_text)
    html = _render_blocks_to_html(
        blocks,
        style_config=style_config,
        document_type=document_type,
        style=style,
    )

    try:
        _render_html_to_pdf_with_playwright(html, target_path)
    except Exception as exc:
        warnings.warn(
            f"Browser PDF rendering failed; falling back to ReportLab. Reason: {exc}",
            stacklevel=2,
        )
        _render_markdown_to_pdf_with_reportlab(
            markdown_text,
            target_path,
            document_type=document_type,
            style=style,
        )

    return target_path


@dataclass(frozen=True)
class MarkdownBlock:
    kind: str
    text: str = ""
    level: int = 0


def _parse_markdown_blocks(markdown_text: str) -> list[MarkdownBlock]:
    blocks: list[MarkdownBlock] = []

    for line in markdown_text.splitlines():
        stripped = _sanitize_pdf_text(line).strip()

        if not stripped:
            blocks.append(MarkdownBlock("blank"))
            continue

        if stripped == "---":
            blocks.append(MarkdownBlock("divider"))
            continue

        heading_text = _extract_heading_text(stripped)
        if heading_text is not None:
            heading_level = 1 if stripped.startswith("# ") else (3 if stripped.startswith("### ") else 2)
            blocks.append(MarkdownBlock("heading", text=heading_text, level=heading_level))
            continue

        if stripped.startswith("- "):
            blocks.append(MarkdownBlock("bullet", text=stripped[2:].strip()))
            continue

        if stripped.startswith("Phone:") or stripped.startswith("Email:") or "@" in stripped and "|" in stripped:
            blocks.append(MarkdownBlock("meta", text=stripped))
            continue

        if stripped.startswith("**") and stripped.endswith("**"):
            blocks.append(MarkdownBlock("emphasis", text=_strip_markdown_inline(stripped[2:-2].strip())))
            continue

        if stripped.startswith("http://") or stripped.startswith("https://"):
            blocks.append(MarkdownBlock("link_line", text=stripped))
            continue

        blocks.append(MarkdownBlock("paragraph", text=stripped))

    return blocks


def _render_blocks_to_html(
    blocks: list[MarkdownBlock],
    *,
    style_config: dict,
    document_type: str,
    style: str,
) -> str:
    body_parts: list[str] = []
    list_is_open = False
    project_group_open = False

    for i, block in enumerate(blocks):
        if block.kind != "bullet" and list_is_open:
            body_parts.append("</ul>")
            list_is_open = False

        # Close project-group before a new emphasis, heading, or divider
        if project_group_open and block.kind in ("emphasis", "heading", "divider", "blank"):
            # Don't close on blank if next block is still part of the group
            if block.kind == "blank":
                next_b = blocks[i + 1] if i + 1 < len(blocks) else None
                if next_b and next_b.kind not in ("emphasis", "heading", "divider"):
                    continue  # skip blank inside project group
            body_parts.append("</div>")
            project_group_open = False

        if block.kind == "blank":
            # Skip blank lines between a heading and its content to prevent page breaks
            prev_b = blocks[i - 1] if i > 0 else None
            next_b = blocks[i + 1] if i + 1 < len(blocks) else None
            if prev_b and prev_b.kind == "heading" and next_b and next_b.kind in ("bullet", "link_line", "emphasis", "heading"):
                continue
            body_parts.append('<div class="blank-line" aria-hidden="true"></div>')
            continue

        if block.kind == "divider":
            body_parts.append('<div class="section-break" aria-hidden="true"></div>')
            continue

        if block.kind == "heading":
            if block.level == 1:
                tag_name, css_class = "h1", "name"
            elif block.level == 2:
                tag_name, css_class = "h2", "section-heading"
            else:
                tag_name, css_class = "h3", "sub-heading"
            main_text, date_text = _split_date_tail(block.text)
            if date_text and block.level != 1:
                body_parts.append(
                    f'<{tag_name} class="{css_class}">'
                    f'<span class="date-right">{escape(date_text)}</span>'
                    f'{escape(main_text)}</{tag_name}>'
                )
            else:
                body_parts.append(
                    f'<{tag_name} class="{css_class}">{escape(block.text)}</{tag_name}>'
                )
            continue

        if block.kind == "bullet":
            if not list_is_open:
                body_parts.append('<ul class="bullet-list">')
                list_is_open = True
            body_parts.append(f"<li>{_render_inline_html(block.text)}</li>")
            continue

        if block.kind == "meta":
            body_parts.append(f'<p class="meta">{_render_inline_html(block.text)}</p>')
            continue

        if block.kind == "emphasis":
            if project_group_open:
                body_parts.append("</div>")
            body_parts.append('<div class="project-group">')
            project_group_open = True
            body_parts.append(f'<p class="emphasis">{escape(block.text)}</p>')
            continue

        if block.kind == "link_line":
            url = block.text
            body_parts.append(f'<p class="link-line"><a href="{escape(url)}">{escape(url)}</a></p>')
            continue

        main_text, date_text = _split_date_tail(block.text)
        if date_text:
            body_parts.append(
                f'<p class="body">'
                f'<span class="date-right">{escape(date_text)}</span>'
                f'{_render_inline_html(main_text)}</p>'
            )
        else:
            body_parts.append(f'<p class="body">{_render_inline_html(block.text)}</p>')

    if list_is_open:
        body_parts.append("</ul>")
    if project_group_open:
        body_parts.append("</div>")

    css = _build_pdf_css(style_config, document_type=document_type, style=style)
    body_html = "\n".join(body_parts)
    document_class = f"document style-{style} type-{document_type}"

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>OfferPilot PDF Export</title>
    <style>
{css}
    </style>
  </head>
  <body>
    <main class="{document_class}">
{body_html}
    </main>
  </body>
</html>
"""


def _render_inline_html(text: str) -> str:
    html = escape(text)
    patterns = [
        (r"\*\*(.+?)\*\*", "strong"),
        (r"__(.+?)__", "strong"),
        (r"\*(.+?)\*", "em"),
        (r"_(.+?)_", "em"),
    ]

    for pattern, tag_name in patterns:
        html = re.sub(pattern, rf"<{tag_name}>\1</{tag_name}>", html)

    return html


def _build_pdf_css(style_config: dict, *, document_type: str, style: str) -> str:
    tokens = _style_config_to_css_tokens(style_config, document_type=document_type, style=style)
    return f"""
      @page {{
        size: A4;
        margin: 0;
      }}

      * {{
        box-sizing: border-box;
      }}

      html, body {{
        margin: 0;
        padding: 0;
        background: #ffffff;
        color: #111827;
      }}

      body {{
        font-family: {DEFAULT_FONT_STACK};
        font-size: {tokens["body_font_size"]};
        line-height: {tokens["body_line_height"]};
        text-rendering: geometricPrecision;
        font-kerning: normal;
        font-variant-ligatures: common-ligatures;
      }}

      .document {{
        width: 210mm;
        min-height: 297mm;
        padding: {tokens["margin_top"]} {tokens["margin_x"]} {tokens["margin_bottom"]};
        font-family: {DEFAULT_FONT_STACK};
      }}

      .document p,
      .document li,
      .document h1,
      .document h2 {{
        margin: 0;
      }}

      .document h1.name {{
        font-size: {tokens["name_font_size"]};
        line-height: {tokens["name_line_height"]};
        font-weight: 700;
        margin-bottom: {tokens["name_space_after"]};
        letter-spacing: -0.01em;
      }}

      .document h2.section-heading {{
        font-size: {tokens["section_font_size"]};
        line-height: {tokens["section_line_height"]};
        font-weight: 700;
        margin-top: {tokens["section_space_before"]};
        margin-bottom: {tokens["section_space_after"]};
      }}

      .document p.meta {{
        font-size: {tokens["meta_font_size"]};
        line-height: {tokens["meta_line_height"]};
        color: #374151;
        margin-bottom: {tokens["meta_space_after"]};
      }}

      .document p.emphasis {{
        font-size: {tokens["emphasis_font_size"]};
        line-height: {tokens["emphasis_line_height"]};
        font-weight: 600;
        margin-bottom: {tokens["emphasis_space_after"]};
        break-after: avoid;
      }}

      .document h2.section-heading {{
        font-size: {tokens["section_font_size"]};
        line-height: {tokens["section_line_height"]};
        font-weight: 700;
        margin-top: {tokens["section_space_before"]};
        margin-bottom: {tokens["section_space_after"]};
        break-after: avoid;
      }}

      .document .project-group {{
        break-inside: avoid;
      }}

      .document .link-line {{
        font-size: 0.75em;
        color: #6b7280;
        margin-top: -0.1em;
        margin-bottom: 0.3em;
      }}

      .document .link-line a {{
        color: #6b7280;
        text-decoration: none;
      }}

      .document p.body {{
        margin-bottom: {tokens["paragraph_space_after"]};
      }}

      .document .bullet-list {{
        margin: 0 0 {tokens["bullet_space_after"]} 0;
        padding-left: 1.15rem;
        break-before: avoid;
        page-break-before: avoid;
      }}

      .document .link-line + .blank-line + .bullet-list,
      .document .link-line + .bullet-list {{
        break-before: avoid;
        page-break-before: avoid;
      }}

      .document .bullet-list li {{
        margin: 0 0 {tokens["bullet_item_gap"]} 0;
        padding-left: 0.15rem;
      }}

      .document .section-break {{
        height: {tokens["section_break_height"]};
      }}

      .document .blank-line {{
        height: {tokens["blank_height"]};
      }}

      .document strong {{
        font-weight: 700;
      }}

      .document em {{
        font-style: italic;
      }}

      .document code {{
        font-family: {MONOSPACE_FONT_STACK};
      }}

      .style-wondercv h1.name {{
        text-align: center;
      }}

      .style-wondercv p.meta {{
        text-align: center;
      }}

      .style-wondercv h2.section-heading {{
        border-bottom: 1.2pt solid #333333;
        padding-bottom: 2pt;
      }}

      .style-wondercv p.emphasis {{
        color: #222222;
        border-bottom: 0.6pt dashed #cccccc;
        padding-bottom: 1.5pt;
      }}

      .style-wondercv .bullet-list li {{
        color: #333333;
      }}

      .document h3.sub-heading {{
        font-size: {tokens["emphasis_font_size"]};
        line-height: {tokens["emphasis_line_height"]};
        font-weight: 600;
        margin-bottom: {tokens["emphasis_space_after"]};
        margin-top: 0;
        break-after: avoid;
        page-break-after: avoid;
      }}

      .style-wondercv h3.sub-heading {{
        border-bottom: 0.6pt dashed #cccccc;
        padding-bottom: 1.5pt;
      }}

      .document .date-right {{
        float: right;
        font-weight: 400;
        font-size: 0.92em;
        min-width: 10em;
        text-align: right;
      }}
    """


def _style_config_to_css_tokens(style_config: dict, *, document_type: str, style: str) -> dict[str, str]:
    paragraph_space_after = style_config["paragraph_space_after"]
    body_leading = style_config["body_leading"]

    if document_type == "cover_letter":
        paragraph_space_after += 2
        body_leading += 0.8

    tokens = {
        "margin_x": f'{style_config["margin_x"]:.2f}in',
        "margin_top": f'{style_config["margin_top"]:.2f}in',
        "margin_bottom": f'{style_config["margin_bottom"]:.2f}in',
        "name_font_size": f'{style_config["name_font_size"]:.1f}pt',
        "name_line_height": f'{style_config["name_leading"]:.1f}pt',
        "name_space_after": f'{style_config["name_space_after"]:.1f}pt',
        "meta_font_size": f'{style_config["meta_font_size"]:.1f}pt',
        "meta_line_height": f'{style_config["meta_leading"]:.1f}pt',
        "meta_space_after": f'{style_config["meta_space_after"]:.1f}pt',
        "section_font_size": f'{style_config["section_font_size"]:.1f}pt',
        "section_line_height": f'{style_config["section_leading"]:.1f}pt',
        "section_space_before": f'{style_config["section_space_before"]:.1f}pt',
        "section_space_after": f'{style_config["section_space_after"]:.1f}pt',
        "emphasis_font_size": f'{style_config["emphasis_font_size"]:.1f}pt',
        "emphasis_line_height": f'{style_config["emphasis_leading"]:.1f}pt',
        "emphasis_space_after": f'{style_config["emphasis_space_after"]:.1f}pt',
        "body_font_size": f'{style_config["body_font_size"]:.1f}pt',
        "body_line_height": f"{body_leading:.1f}pt",
        "paragraph_space_after": f"{paragraph_space_after:.1f}pt",
        "bullet_space_after": f'{style_config["bullet_space_after"] + 2:.1f}pt',
        "bullet_item_gap": "1.0pt" if style == "compact" else "1.6pt",
        "blank_height": f'{style_config["blank_spacer"]:.2f}in',
        "section_break_height": f'{style_config["section_break_spacer"]:.2f}in',
    }

    if document_type == "cover_letter":
        tokens["section_space_before"] = f'{style_config["section_space_before"] + 2:.1f}pt'

    return tokens


def _render_html_to_pdf_with_playwright(html: str, output_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Install dependencies and run 'playwright install chromium'."
        ) from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.emulate_media(media="print")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            browser.close()


def _render_markdown_to_pdf_with_reportlab(
    markdown_text: str,
    output_path: Path,
    *,
    document_type: str = "resume",
    style: str = "classic",
) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    _ensure_pdf_fonts_registered()

    style_config = _get_style_config(style, document_type)
    styles = getSampleStyleSheet()
    latin_styles = _build_style_set(
        styles,
        style_config,
        regular_font=LATIN_REGULAR_FONT,
        emphasis_font=LATIN_BOLD_FONT,
        style_prefix="latin",
    )
    cjk_styles = _build_style_set(
        styles,
        style_config,
        regular_font=CJK_FONT,
        emphasis_font=CJK_FONT,
        style_prefix="cjk",
    )

    story = []
    for block in _parse_markdown_blocks(markdown_text):
        style_set = cjk_styles if _contains_cjk(block.text) else latin_styles

        if block.kind == "blank":
            story.append(Spacer(1, style_config["blank_spacer"]))
            continue

        if block.kind == "divider":
            story.append(Spacer(1, style_config["section_break_spacer"]))
            continue

        if block.kind == "heading":
            heading_style = style_set["name"] if block.level == 1 else style_set["section"]
            story.append(Paragraph(escape(block.text), heading_style))
            continue

        if block.kind == "bullet":
            bullet_text = _strip_markdown_inline(block.text)
            story.append(Paragraph(escape("- " + bullet_text), style_set["bullet"]))
            continue

        if block.kind == "meta":
            story.append(Paragraph(escape(block.text), style_set["centered"]))
            continue

        if block.kind == "emphasis":
            story.append(Paragraph(escape(block.text), style_set["emphasis"]))
            continue

        story.append(Paragraph(escape(_strip_markdown_inline(block.text)), style_set["normal"]))

    pdf = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=style_config["margin_x"],
        leftMargin=style_config["margin_x"],
        topMargin=style_config["margin_top"],
        bottomMargin=style_config["margin_bottom"],
    )
    pdf.build(story)


def _sanitize_pdf_text(text: str) -> str:
    """Replace common Unicode punctuation with PDF-safe ASCII equivalents."""
    return text.translate(UNICODE_PDF_SAFE_TRANSLATION)


def _extract_heading_text(text: str) -> str | None:
    match = re.match(r"^(#{1,6})\s+(.+)$", text)
    if not match:
        return None

    return _strip_markdown_inline(match.group(2).strip())


def _strip_markdown_inline(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    return text.strip()


def _ensure_pdf_fonts_registered() -> None:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    registered_fonts = pdfmetrics.getRegisteredFontNames()
    if CJK_FONT not in registered_fonts:
        pdfmetrics.registerFont(UnicodeCIDFont(CJK_FONT))


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _build_style_set(
    styles,
    style_config: dict,
    regular_font: str,
    emphasis_font: str,
    style_prefix: str,
) -> dict:
    from reportlab.lib.styles import ParagraphStyle

    return {
        "name": ParagraphStyle(
            f"{style_prefix}_name",
            parent=styles["Title"],
            fontName=emphasis_font,
            fontSize=style_config["name_font_size"],
            leading=style_config["name_leading"],
            alignment=style_config["header_alignment"],
            spaceAfter=style_config["name_space_after"],
        ),
        "centered": ParagraphStyle(
            f"{style_prefix}_centered",
            parent=styles["Normal"],
            fontName=regular_font,
            fontSize=style_config["meta_font_size"],
            leading=style_config["meta_leading"],
            alignment=style_config["header_alignment"],
            spaceAfter=style_config["meta_space_after"],
        ),
        "section": ParagraphStyle(
            f"{style_prefix}_section",
            parent=styles["Heading2"],
            fontName=emphasis_font,
            fontSize=style_config["section_font_size"],
            leading=style_config["section_leading"],
            spaceBefore=style_config["section_space_before"],
            spaceAfter=style_config["section_space_after"],
        ),
        "emphasis": ParagraphStyle(
            f"{style_prefix}_emphasis",
            parent=styles["Normal"],
            fontName=emphasis_font,
            fontSize=style_config["emphasis_font_size"],
            leading=style_config["emphasis_leading"],
            spaceAfter=style_config["emphasis_space_after"],
        ),
        "bullet": ParagraphStyle(
            f"{style_prefix}_bullet",
            parent=styles["Normal"],
            fontName=regular_font,
            fontSize=style_config["body_font_size"],
            leading=style_config["body_leading"] + (1 if regular_font == CJK_FONT else 0),
            leftIndent=0,
            firstLineIndent=0,
            spaceAfter=style_config["bullet_space_after"],
            wordWrap="CJK" if regular_font == CJK_FONT else None,
        ),
        "normal": ParagraphStyle(
            f"{style_prefix}_normal",
            parent=styles["Normal"],
            fontName=regular_font,
            fontSize=style_config["body_font_size"],
            leading=style_config["body_leading"] + (1 if regular_font == CJK_FONT else 0),
            spaceAfter=style_config["paragraph_space_after"],
            wordWrap="CJK" if regular_font == CJK_FONT else None,
        ),
    }


def _get_style_config(style: str, document_type: str) -> dict:
    base = {
        "header_alignment": HEADER_ALIGNMENT_LEFT,
        "margin_x": 0.72,
        "margin_top": 0.62,
        "margin_bottom": 0.62,
        "name_font_size": 17,
        "name_leading": 21,
        "name_space_after": 6,
        "meta_font_size": 10,
        "meta_leading": 13,
        "meta_space_after": 8,
        "section_font_size": 11.5,
        "section_leading": 15,
        "section_space_before": 7,
        "section_space_after": 4,
        "emphasis_font_size": 10.3,
        "emphasis_leading": 13.5,
        "emphasis_space_after": 2,
        "body_font_size": 10.2,
        "body_leading": 13.5,
        "bullet_space_after": 1.5,
        "paragraph_space_after": 3,
        "blank_spacer": 0.04,
        "section_break_spacer": 0.06,
    }

    if style == "ats":
        base.update(
            {
                "header_alignment": HEADER_ALIGNMENT_LEFT,
                "margin_x": 0.72,
                "name_font_size": 16,
                "name_leading": 19,
                "meta_space_after": 6,
                "section_font_size": 11.5,
                "section_leading": 14,
                "body_font_size": 9.8,
                "body_leading": 12.5,
                "paragraph_space_after": 2.5,
                "blank_spacer": 0.035,
                "section_break_spacer": 0.05,
            }
        )
    elif style == "compact":
        base.update(
            {
                "margin_x": 0.5,
                "margin_top": 0.45,
                "margin_bottom": 0.45,
                "name_font_size": 17,
                "name_leading": 20,
                "section_space_before": 6,
                "section_space_after": 4,
                "body_font_size": 9,
                "body_leading": 11,
                "bullet_space_after": 1,
                "paragraph_space_after": 2,
                "blank_spacer": 0.04,
                "section_break_spacer": 0.045,
            }
        )
    elif style == "wondercv":
        base.update(
            {
                "header_alignment": 1,  # centered
                "margin_x": 0.7,
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "name_font_size": 20,
                "name_leading": 24,
                "name_space_after": 2,
                "meta_font_size": 9.5,
                "meta_leading": 13,
                "meta_space_after": 6,
                "section_font_size": 11.5,
                "section_leading": 15,
                "section_space_before": 7,
                "section_space_after": 3,
                "emphasis_font_size": 10,
                "emphasis_leading": 13,
                "emphasis_space_after": 1.5,
                "body_font_size": 9.5,
                "body_leading": 12.5,
                "bullet_space_after": 1,
                "paragraph_space_after": 2,
                "blank_spacer": 0.02,
                "section_break_spacer": 0.02,
            }
        )

    if document_type == "cover_letter":
        base.update(
            {
                "meta_space_after": max(base["meta_space_after"], 10),
                "paragraph_space_after": base["paragraph_space_after"] + 2,
                "body_leading": base["body_leading"] + 0.8,
            }
        )

    return base


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"ERROR: file not found: {input_path}")

    markdown_text = input_path.read_text(encoding="utf-8")
    render_markdown_to_pdf(
        markdown_text,
        args.output,
        document_type=args.document_type,
        style=args.style,
    )
    print(f"OK: rendered PDF to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
