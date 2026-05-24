#!/usr/bin/env python3
"""Validate an OfferPilot profile_store.yaml file."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

VALID_IMPACTS = {"quantified", "qualitative", "context-only"}
VALID_LEVELS = {"familiar", "proficient", "expert"}
DEFAULT_ALIASES = Path("skill-pack/data/skill_aliases.zh-en.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate OfferPilot profile datastore YAML.")
    parser.add_argument("path", help="profile_store.yaml path.")
    parser.add_argument(
        "--aliases",
        default=str(DEFAULT_ALIASES),
        help="Alias JSON file used to check canonical tags.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    store = _load_yaml(Path(args.path), errors)
    aliases = _load_aliases(Path(args.aliases), warnings)
    canonical_tags = set(aliases)
    alias_to_key = {
        alias.lower(): key
        for key, values in aliases.items()
        for alias in values
        if isinstance(alias, str)
    }

    if store is not None:
        _validate_store(store, canonical_tags, alias_to_key, errors, warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print("OK: profile datastore passed OfferPilot checks.")
    return 0


def _load_yaml(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(f"Missing profile datastore: {path}")
        return None

    try:
        import yaml
    except ImportError:
        errors.append("Missing dependency: PyYAML. Install project dependencies before validating YAML.")
        return None

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - surface YAML parser details to users.
        errors.append(f"Could not parse {path}: {exc}")
        return None

    if not isinstance(data, dict):
        errors.append("Profile datastore must be a YAML mapping at the top level.")
        return None
    return data


def _load_aliases(path: Path, warnings: list[str]) -> dict[str, list[str]]:
    if not path.exists():
        warnings.append(f"Alias file missing, tag canonical checks skipped: {path}")
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"Alias file is not valid JSON, tag canonical checks skipped: {exc}")
        return {}

    if not isinstance(data, dict):
        warnings.append("Alias file must be a JSON object; tag canonical checks skipped.")
        return {}

    aliases: dict[str, list[str]] = {}
    for key, values in data.items():
        if isinstance(key, str) and isinstance(values, list):
            aliases[key] = [value for value in values if isinstance(value, str)]
    return aliases


def _validate_store(
    store: dict[str, Any],
    canonical_tags: set[str],
    alias_to_key: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> None:
    meta = store.get("meta")
    if not isinstance(meta, dict):
        errors.append("Missing or invalid required section: meta")
    else:
        _require_non_empty_string(meta, "name", "meta.name", errors)
        _validate_birth_year(meta.get("birth_year"), errors, warnings)

    for section in ("experience", "projects"):
        entries = store.get(section, [])
        if entries is None:
            continue
        if not isinstance(entries, list):
            errors.append(f"{section} must be a list.")
            continue
        for idx, entry in enumerate(entries):
            _validate_entry(section, idx, entry, canonical_tags, alias_to_key, errors, warnings)

    skills = store.get("skills", [])
    if skills is not None:
        _validate_skills(skills, errors, warnings)

    achievements = store.get("achievements", [])
    if isinstance(achievements, list):
        for idx, item in enumerate(achievements):
            if isinstance(item, dict) and "tags" in item:
                _validate_tags(
                    item.get("tags"),
                    f"achievements[{idx}].tags",
                    canonical_tags,
                    alias_to_key,
                    errors,
                    warnings,
                )


def _validate_entry(
    section: str,
    idx: int,
    entry: Any,
    canonical_tags: set[str],
    alias_to_key: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"{section}[{idx}]"
    if not isinstance(entry, dict):
        errors.append(f"{prefix} must be a mapping.")
        return

    required = ("company", "role", "start", "end") if section == "experience" else ("name",)
    for field in required:
        _require_non_empty_string(entry, field, f"{prefix}.{field}", errors)

    bullets = entry.get("bullets")
    if not isinstance(bullets, list) or not bullets:
        errors.append(f"{prefix}.bullets must be a non-empty list.")
        return

    for bullet_idx, bullet in enumerate(bullets):
        _validate_bullet(
            f"{prefix}.bullets[{bullet_idx}]",
            bullet,
            canonical_tags,
            alias_to_key,
            errors,
            warnings,
        )


def _validate_bullet(
    prefix: str,
    bullet: Any,
    canonical_tags: set[str],
    alias_to_key: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not isinstance(bullet, dict):
        errors.append(f"{prefix} must be a mapping.")
        return

    _require_non_empty_string(bullet, "text", f"{prefix}.text", errors)
    _validate_tags(bullet.get("tags"), f"{prefix}.tags", canonical_tags, alias_to_key, errors, warnings)

    impact = bullet.get("impact")
    if impact and impact not in VALID_IMPACTS:
        errors.append(f"{prefix}.impact must be one of: {', '.join(sorted(VALID_IMPACTS))}.")


def _validate_tags(
    tags: Any,
    label: str,
    canonical_tags: set[str],
    alias_to_key: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not isinstance(tags, list) or not tags:
        errors.append(f"{label} must be a non-empty list.")
        return

    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            errors.append(f"{label} contains a non-empty non-string tag.")
            continue

        normalized = tag.strip().lower()
        if normalized != tag:
            errors.append(f"{label} tag should be lowercase without surrounding whitespace: {tag!r}")
        if "-" in normalized:
            warnings.append(f"{label} tag '{tag}' should usually use spaces instead of hyphens.")
        if canonical_tags and normalized not in canonical_tags:
            canonical = alias_to_key.get(normalized)
            if canonical:
                warnings.append(f"{label} tag '{tag}' is an alias; prefer canonical tag '{canonical}'.")
            else:
                warnings.append(f"{label} tag '{tag}' is not covered by the alias mapping.")


def _validate_skills(skills: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(skills, list):
        errors.append("skills must be a list.")
        return

    for idx, skill in enumerate(skills):
        prefix = f"skills[{idx}]"
        if not isinstance(skill, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        _require_non_empty_string(skill, "name", f"{prefix}.name", errors)

        level = skill.get("level")
        if level and level not in VALID_LEVELS:
            errors.append(f"{prefix}.level must be one of: {', '.join(sorted(VALID_LEVELS))}.")

        years = skill.get("years")
        if years is not None and (not isinstance(years, (int, float)) or years < 0):
            errors.append(f"{prefix}.years must be a non-negative number.")

        evidence = skill.get("evidence")
        if evidence is not None and not isinstance(evidence, list):
            warnings.append(f"{prefix}.evidence should be a list of concrete uses.")


def _require_non_empty_string(
    mapping: dict[str, Any],
    field: str,
    label: str,
    errors: list[str],
) -> None:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required and must be a non-empty string.")


def _validate_birth_year(value: Any, errors: list[str], warnings: list[str]) -> None:
    if value in (None, ""):
        return
    if not isinstance(value, int):
        errors.append("meta.birth_year must be a four-digit integer when provided.")
        return
    current_year = date.today().year
    if value < 1900 or value > current_year:
        errors.append(f"meta.birth_year must be between 1900 and {current_year}.")
    elif current_year - value < 16:
        warnings.append("meta.birth_year implies age under 16. Confirm this is intentional.")


if __name__ == "__main__":
    raise SystemExit(main())
