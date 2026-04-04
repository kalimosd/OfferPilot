from __future__ import annotations

import argparse
import sys

from offerpilot.cover import build_cover_letter_prompt
from offerpilot.export import render_markdown_to_pdf
from offerpilot.io import load_text_from_file, save_text_to_file
from offerpilot.llm import call_llm
from offerpilot.resume import (
    build_resume_diagnosis_prompt,
    build_resume_optimization_prompt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="offerpilot",
        description="Legacy CLI compatibility layer for the OfferPilot skill pack.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("hello", help="Run a basic health check.")

    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Optimize a resume with the configured LLM provider.",
    )
    optimize_parser.add_argument(
        "resume_path",
        help="Path to a .txt, .md, .pdf, or .docx resume.",
    )
    optimize_parser.add_argument(
        "--job",
        default=None,
        help="Optional path to a .txt, .md, .pdf, or .docx job description for tailored resume optimization.",
    )
    optimize_parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the optimized resume.",
    )
    optimize_parser.add_argument(
        "--lang",
        choices=["same", "zh", "en"],
        default="same",
        help="Output language for the optimized resume. Default: same.",
    )
    optimize_parser.add_argument(
        "--format",
        choices=["md", "pdf"],
        default="md",
        help="Output format for the optimized resume. Default: md.",
    )
    optimize_parser.add_argument(
        "--style",
        choices=["classic", "ats", "compact"],
        default="classic",
        help="Output style for the optimized resume. Default: classic.",
    )
    optimize_parser.add_argument(
        "--provider",
        default="deepseek",
        help="LLM provider to use. Default: deepseek.",
    )
    optimize_parser.add_argument(
        "--model",
        default=None,
        help="Optional model override.",
    )

    diagnose_parser = subparsers.add_parser(
        "diagnose",
        help="Diagnose a resume and identify strengths, gaps, and risks.",
    )
    diagnose_parser.add_argument(
        "resume_path",
        help="Path to a .txt, .md, .pdf, or .docx resume.",
    )
    diagnose_parser.add_argument(
        "--job",
        default=None,
        help="Optional path to a .txt, .md, .pdf, or .docx job description for fit diagnosis.",
    )
    diagnose_parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the diagnosis report.",
    )
    diagnose_parser.add_argument(
        "--lang",
        choices=["same", "zh", "en"],
        default="same",
        help="Output language for the diagnosis. Default: same.",
    )
    diagnose_parser.add_argument(
        "--provider",
        default="deepseek",
        help="LLM provider to use. Default: deepseek.",
    )
    diagnose_parser.add_argument(
        "--model",
        default=None,
        help="Optional model override.",
    )

    cover_parser = subparsers.add_parser(
        "cover",
        help="Generate a tailored cover letter from a resume and job description.",
    )
    cover_parser.add_argument(
        "resume_path",
        help="Path to a .txt, .md, .pdf, or .docx resume.",
    )
    cover_parser.add_argument(
        "job_path",
        help="Path to a .txt, .md, .pdf, or .docx job description.",
    )
    cover_parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the cover letter.",
    )
    cover_parser.add_argument(
        "--lang",
        choices=["same", "zh", "en"],
        default="same",
        help="Output language for the cover letter. Default: same.",
    )
    cover_parser.add_argument(
        "--format",
        choices=["md", "pdf"],
        default="md",
        help="Output format for the cover letter. Default: md.",
    )
    cover_parser.add_argument(
        "--style",
        choices=["classic", "ats", "compact"],
        default="classic",
        help="PDF style for the generated cover letter. Default: classic.",
    )
    cover_parser.add_argument(
        "--provider",
        default="deepseek",
        help="LLM provider to use. Default: deepseek.",
    )
    cover_parser.add_argument(
        "--model",
        default=None,
        help="Optional model override.",
    )

    ask_parser = subparsers.add_parser(
        "ask",
        help="Send a simple prompt to the configured LLM provider.",
    )
    ask_parser.add_argument("prompt", help="Prompt text to send.")
    ask_parser.add_argument(
        "--provider",
        default="deepseek",
        help="LLM provider to use. Default: deepseek.",
    )
    ask_parser.add_argument(
        "--model",
        default=None,
        help="Optional model override.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "hello":
        print("OfferPilot running")
        return 0

    if args.command == "optimize":
        try:
            resume_text = _load_required_text(args.resume_path, "resume file")
            job_text = (
                _load_required_text(args.job, "job description file")
                if args.job
                else None
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        prompt = build_resume_optimization_prompt(
            resume_text,
            target_language=args.lang,
            style=args.style,
            job_text=job_text,
        )

        try:
            optimized_resume = call_llm(
                prompt,
                provider=args.provider,
                model=args.model,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"LLM request failed: {exc}", file=sys.stderr)
            return 1

        if args.format == "pdf":
            if not args.output:
                print("Error: --output is required when --format pdf.", file=sys.stderr)
                return 1

            saved_path = render_markdown_to_pdf(
                optimized_resume,
                args.output,
                document_type="resume",
                style=args.style,
            )
            print(f"Optimized resume saved to {saved_path}")
            return 0

        if args.output:
            saved_path = save_text_to_file(args.output, optimized_resume + "\n")
            print(f"Optimized resume saved to {saved_path}")
            return 0

        print(optimized_resume)
        return 0

    if args.command == "diagnose":
        try:
            resume_text = _load_required_text(args.resume_path, "resume file")
            job_text = (
                _load_required_text(args.job, "job description file")
                if args.job
                else None
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        prompt = build_resume_diagnosis_prompt(
            resume_text,
            target_language=args.lang,
            job_text=job_text,
        )

        try:
            diagnosis = call_llm(
                prompt,
                provider=args.provider,
                model=args.model,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"LLM request failed: {exc}", file=sys.stderr)
            return 1

        if args.output:
            saved_path = save_text_to_file(args.output, diagnosis + "\n")
            print(f"Resume diagnosis saved to {saved_path}")
            return 0

        print(diagnosis)
        return 0

    if args.command == "ask":
        try:
            result = call_llm(
                args.prompt,
                provider=args.provider,
                model=args.model,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"LLM request failed: {exc}", file=sys.stderr)
            return 1

        print(result)
        return 0

    if args.command == "cover":
        try:
            resume_text = _load_required_text(args.resume_path, "resume file")
            job_text = _load_required_text(args.job_path, "job description file")
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        prompt = build_cover_letter_prompt(
            resume_text,
            job_text,
            target_language=args.lang,
        )

        try:
            cover_letter = call_llm(
                prompt,
                provider=args.provider,
                model=args.model,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"LLM request failed: {exc}", file=sys.stderr)
            return 1

        if args.format == "pdf":
            if not args.output:
                print("Error: --output is required when --format pdf.", file=sys.stderr)
                return 1

            saved_path = render_markdown_to_pdf(
                cover_letter,
                args.output,
                document_type="cover_letter",
                style=args.style,
            )
            print(f"Cover letter saved to {saved_path}")
            return 0

        if args.output:
            saved_path = save_text_to_file(args.output, cover_letter + "\n")
            print(f"Cover letter saved to {saved_path}")
            return 0

        print(cover_letter)
        return 0

    return 0


def _load_required_text(path: str, label: str) -> str:
    text = load_text_from_file(path)
    if not text:
        raise ValueError(f"{label.capitalize()} is empty.")
    return text


if __name__ == "__main__":
    raise SystemExit(main())
