#!/usr/bin/env python3
"""Validate OfferPilot skill alias mappings."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate skill-pack/data/skill_aliases.zh-en.json."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="skill-pack/data/skill_aliases.zh-en.json",
        help="Alias JSON file to validate.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    path = Path(args.path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        print(f"ERROR: Missing alias file: {path}")
        return 1

    try:
        aliases = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {path}: {exc}")
        return 1

    if not isinstance(aliases, dict):
        print("ERROR: Alias file must be a JSON object.")
        return 1

    seen_terms: dict[str, str] = {}
    for key, values in aliases.items():
        if not isinstance(key, str) or not key.strip():
            errors.append("Alias keys must be non-empty strings.")
            continue

        canonical = key.strip()
        if canonical != key:
            errors.append(f"Alias key has surrounding whitespace: {key!r}")
        if canonical.lower() != canonical:
            errors.append(f"Alias key must be lowercase: {key}")
        if "-" in canonical:
            warnings.append(f"Prefer spaces over hyphens in canonical tag: {key}")

        if not isinstance(values, list) or not values:
            errors.append(f"Alias key '{key}' must map to a non-empty list.")
            continue

        _record_term(canonical, key, seen_terms, warnings)
        for value in values:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"Alias under '{key}' must be a non-empty string.")
                continue
            alias = value.strip()
            if alias != value:
                errors.append(f"Alias under '{key}' has surrounding whitespace: {value!r}")
            if alias.lower() == canonical:
                warnings.append(f"Alias under '{key}' duplicates its canonical key: {value}")
            _record_term(alias.lower(), key, seen_terms, warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(f"OK: validated {len(aliases)} canonical alias keys.")
    return 0


def _record_term(
    term: str,
    key: str,
    seen_terms: dict[str, str],
    warnings: list[str],
) -> None:
    existing = seen_terms.get(term)
    if existing and existing != key:
        warnings.append(f"Alias term '{term}' appears under both '{existing}' and '{key}'.")
    else:
        seen_terms[term] = key


if __name__ == "__main__":
    raise SystemExit(main())
