#!/usr/bin/env python3
"""Validate OfferPilot input files before running a skill workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".yaml", ".yml"}
GENERATED_NAME_HINTS = (
    "optimized",
    "cover_letter",
    "cover-letter",
    "targeted",
    "final",
    "output",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check whether OfferPilot source inputs look safe and plausible."
    )
    parser.add_argument("paths", nargs="+", help="Input files to validate.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"Missing file: {path}")
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            errors.append(
                f"Unsupported extension for {path}: {path.suffix or '[no extension]'}"
            )

        lowered_name = path.name.lower()
        if any(hint in lowered_name for hint in GENERATED_NAME_HINTS):
            warnings.append(
                f"{path} looks like a generated artifact. Prefer the original resume if available."
            )

    for warning in warnings:
        print(f"WARNING: {warning}")

    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print("OK: input files passed basic OfferPilot checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
