#!/usr/bin/env python3
"""Validate OfferPilot output naming, placement, and lightweight content rules."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

OUTPUTS_ROOT = "outputs"
ALLOWED_SUBDIRS = {"resumes", "research", "interview", "pipeline", "misc"}
OUTPUT_HINTS = (
    "resume",
    "cover",
    "letter",
    "评估",
    "匹配",
    "简历",
    "面试",
    "产品研究",
    "外联",
    "pipeline",
)
PLACEHOLDER_RE = re.compile(
    r"<(?:name|email|phone|姓名|邮箱|电话|公司|岗位)[^>]*>",
    re.IGNORECASE,
)
RESUME_SECTION_ORDER = [
    "教育背景",
    "工作经历",
    "强相关项目",
    "实习经历",
    "其他项目",
    "技能",
]
PAIR_EXEMPT_NAME_HINTS = ("评估", "匹配", "诊断", "cover", "letter", "外联", "产品研究", "面试")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run lightweight checks on OfferPilot output files."
    )
    parser.add_argument("paths", nargs="+", help="Output files to validate.")
    parser.add_argument(
        "--english-name",
        default=None,
        help="Optional English candidate name to check, e.g. 'GivenName FamilyName'.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    paths = [Path(raw_path) for raw_path in args.paths]

    for path in paths:
        if not path.exists():
            errors.append(f"Missing output file: {path}")
            continue

        _check_output_location(path, errors, warnings)
        _check_filename(path, warnings)
        _check_content(path, errors, warnings)

    _check_markdown_pdf_pairs(paths, warnings)
    _check_english_name(args.english_name, errors, warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")

    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print("OK: output files passed OfferPilot checks.")
    return 0


def _check_output_location(path: Path, errors: list[str], warnings: list[str]) -> None:
    parts = path.parts
    if OUTPUTS_ROOT not in parts:
        warnings.append(f"{path} is outside outputs/. Confirm this is intentional.")
        return

    root_idx = parts.index(OUTPUTS_ROOT)
    if len(parts) <= root_idx + 2:
        errors.append(f"{path} is saved directly under outputs/. Use a task subdirectory.")
        return

    subdir = parts[root_idx + 1]
    if subdir not in ALLOWED_SUBDIRS:
        errors.append(
            f"{path} uses unknown outputs/ subdirectory '{subdir}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_SUBDIRS))}."
        )


def _check_filename(path: Path, warnings: list[str]) -> None:
    if path.suffix.lower() not in {".md", ".pdf", ".txt"}:
        warnings.append(f"{path} has an unusual output extension: {path.suffix or '[none]'}.")

    lowered_name = path.name.lower()
    if not any(hint in lowered_name for hint in OUTPUT_HINTS):
        warnings.append(f"{path} does not look like a standard OfferPilot output filename.")

    if _is_resume_deliverable(path) and not re.search(r"_v\d+(?:\.[^.]+)$", path.name):
        warnings.append(f"{path} should usually include a version suffix like _v1.")


def _check_content(path: Path, errors: list[str], warnings: list[str]) -> None:
    if path.suffix.lower() not in {".md", ".txt"}:
        return

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        warnings.append(f"{path} is not valid UTF-8; content checks were skipped.")
        return

    if PLACEHOLDER_RE.search(text):
        errors.append(f"{path} contains unresolved placeholder contact or identity fields.")

    _check_resume_section_order(path, text, warnings)


def _check_resume_section_order(path: Path, text: str, warnings: list[str]) -> None:
    if not _is_resume_deliverable(path):
        return

    headings = [
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("## ")
    ]
    seen: list[tuple[int, str]] = []
    for heading in headings:
        for idx, expected in enumerate(RESUME_SECTION_ORDER):
            if expected in heading:
                seen.append((idx, heading))
                break

    if not seen:
        return

    order = [idx for idx, _ in seen]
    if order != sorted(order):
        warnings.append(
            f"{path} has resume sections out of the recommended order: "
            + " -> ".join(heading for _, heading in seen)
        )


def _check_markdown_pdf_pairs(paths: list[Path], warnings: list[str]) -> None:
    given = {path.resolve() for path in paths if path.exists()}
    for path in paths:
        if not path.exists() or path.suffix.lower() != ".md" or not _is_resume_deliverable(path):
            continue
        expected_pdf = path.with_suffix(".pdf")
        if expected_pdf.resolve() not in given and not expected_pdf.exists():
            warnings.append(f"{path} is a resume deliverable without matching PDF {expected_pdf}.")


def _check_english_name(
    english_name: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    if not english_name:
        return

    name = english_name.strip()
    if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)+", name):
        errors.append(
            "--english-name must look like 'GivenName FamilyName' using letters and spaces."
        )
        return

    parts = name.split()
    if len(parts) != 2:
        warnings.append(
            "English name has more than two parts. Confirm the intended Given Name + Family Name order manually."
        )


def _is_resume_deliverable(path: Path) -> bool:
    lowered_name = path.name.lower()
    if any(hint in lowered_name for hint in PAIR_EXEMPT_NAME_HINTS):
        return False

    parts = path.parts
    if OUTPUTS_ROOT in parts:
        root_idx = parts.index(OUTPUTS_ROOT)
        if len(parts) > root_idx + 1 and parts[root_idx + 1] == "resumes":
            return True

    return any(hint in lowered_name for hint in ("resume", "简历"))


if __name__ == "__main__":
    raise SystemExit(main())
