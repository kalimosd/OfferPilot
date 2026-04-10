"""Optional CLI helper for OfferPilot skill-pack workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _scripts_dir() -> Path:
    return _repo_root() / "skill-pack" / "scripts"


def _run_script(script_name: str, args: list[str]) -> int:
    script_path = _scripts_dir() / script_name
    if not script_path.exists():
        print(f"ERROR: missing helper script: {script_path}", file=sys.stderr)
        return 1
    command = [sys.executable, str(script_path), *args]
    return subprocess.call(command, cwd=str(_repo_root()))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="offerpilot",
        description=(
            "Optional helper entry for OfferPilot. "
            "The skill-pack docs remain the primary workflow source of truth."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    scan = subparsers.add_parser("scan", help="Scan portals for new listings.")
    scan.add_argument("--config", default="portals_cn.yml", help="Portal config YAML.")
    scan.add_argument("--greenhouse-only", action="store_true", help="Only scan Greenhouse API.")
    scan.add_argument("--playwright-only", action="store_true", help="Only scan Playwright companies.")
    scan.add_argument("--cn-only", action="store_true", help="Only scan Chinese company APIs.")
    scan.add_argument("--search-only", action="store_true", help="Only run web search queries.")
    scan.add_argument("--dry-run", action="store_true", help="Show results without writing files.")

    pdf = subparsers.add_parser("pdf", help="Render markdown-like output to PDF.")
    pdf.add_argument("input", help="Input markdown file path.")
    pdf.add_argument("output", help="Output PDF path.")
    pdf.add_argument(
        "--document-type",
        choices=["resume", "cover_letter"],
        default="resume",
        help="Document type to render.",
    )
    pdf.add_argument(
        "--style",
        choices=["classic", "ats", "compact", "standard_cn"],
        default="classic",
        help="PDF style.",
    )
    pdf.add_argument("--photo", default=None, help="Optional photo path for header.")

    extract = subparsers.add_parser("extract", help="Extract plain text from source files.")
    extract.add_argument("path", help="Source file path (.txt/.md/.pdf/.docx).")
    extract.add_argument("--output", default=None, help="Optional output text file path.")

    v_in = subparsers.add_parser("validate-inputs", help="Validate workflow input files.")
    v_in.add_argument("paths", nargs="+", help="Input files to validate.")

    v_out = subparsers.add_parser("validate-outputs", help="Validate generated output files.")
    v_out.add_argument("paths", nargs="+", help="Output files to validate.")
    v_out.add_argument(
        "--english-name",
        default=None,
        help="Optional English name in GivenName FamilyName format.",
    )

    run = subparsers.add_parser(
        "run",
        help="Run a minimal pipeline: validate-inputs then render PDF.",
    )
    run.add_argument("resume", help="Resume markdown source path.")
    run.add_argument("pdf_output", help="Output PDF path.")
    run.add_argument(
        "--style",
        choices=["classic", "ats", "compact", "standard_cn"],
        default="classic",
        help="PDF style.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "scan":
        forwarded = [
            "--config",
            args.config,
            *(["--greenhouse-only"] if args.greenhouse_only else []),
            *(["--playwright-only"] if args.playwright_only else []),
            *(["--cn-only"] if args.cn_only else []),
            *(["--search-only"] if args.search_only else []),
            *(["--dry-run"] if args.dry_run else []),
        ]
        return _run_script("scan_portals.py", forwarded)

    if args.command == "pdf":
        forwarded = [
            args.input,
            args.output,
            "--document-type",
            args.document_type,
            "--style",
            args.style,
            *(["--photo", args.photo] if args.photo else []),
        ]
        return _run_script("render_pdf.py", forwarded)

    if args.command == "extract":
        forwarded = [args.path, *(["--output", args.output] if args.output else [])]
        return _run_script("extract_text.py", forwarded)

    if args.command == "validate-inputs":
        return _run_script("validate_inputs.py", args.paths)

    if args.command == "validate-outputs":
        forwarded = [*args.paths, *(["--english-name", args.english_name] if args.english_name else [])]
        return _run_script("validate_outputs.py", forwarded)

    if args.command == "run":
        validation_code = _run_script("validate_inputs.py", [args.resume])
        if validation_code != 0:
            return validation_code
        return _run_script(
            "render_pdf.py",
            [args.resume, args.pdf_output, "--document-type", "resume", "--style", args.style],
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
