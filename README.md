# OfferPilot AI

AI job assistant that turns weak applications into interview-ready ones.

Built fast as a practical AI product experiment, OfferPilot tackles a real problem: strong candidates often undersell themselves with generic resumes, weak positioning, and cover letters that sound the same. It helps turn raw experience into sharper, role-specific application materials that are more likely to earn interviews.

## Quick Example

Extract a resume from PDF:

```bash
python3 skill-pack/scripts/extract_text.py "resume.pdf" --output "resume.txt"
```

Export a reviewed draft to PDF:

```bash
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --document-type resume --style classic
```

Typical usage is simple:

1. Put your resume and target job description into local files.
2. Run the OfferPilot skill pack through a repository agent such as Cursor, Codex-style agents, or Claude Code.
3. Generate a stronger resume, a tailored version, or a cover letter.
4. Review the Markdown output and export it when ready.

## Example Output

**Before**

```text
- Responsible for Android development and worked with different teams.
- Helped fix bugs and improve app performance.
```

**After**

```text
- Improved Android system stability and performance by diagnosing rendering, memory, and ANR issues with Perfetto and Systrace, then driving fixes across platform teams.
- Owned delivery for recent-tasks features, coordinating engineering stakeholders to ship on schedule and close cross-team issues faster.
```

These outputs are meant to be directly usable with minimal editing.

## Why This Project

Many international students and early-career candidates do strong work but present it weakly.

Their resumes are often too generic, their cover letters feel interchangeable, and their most relevant experience gets buried. OfferPilot focuses on outcomes: clearer positioning, stronger materials, and better odds of getting interviews.

## Features

- **Resume optimization**: Tightens wording, removes filler, and strengthens bullet points without inventing facts.
- **Job-targeted rewriting**: Rewrites and reorders content around a specific job description.
- **Cover letter generation**: Produces concise, tailored letters grounded in real experience.
- **Profile datastore support**: Pulls the most relevant experience from a structured data source.
- **JD fit analysis**: Identifies match signals, gaps, and rewrite priorities.
- **Local workflow tooling**: Supports text extraction, validation, and PDF export.

## Tech Stack

- Python
- LLM-powered rewriting and analysis
- Modular skill-pack architecture
- YAML-based profile datastore
- Playwright-based PDF export

## Project Structure

- **main**: The `skill-pack/` directory, which contains the core workflow for resume optimization, targeted rewriting, JD-fit analysis, cover letters, examples, adapters, and scripts.
- **profile-datastore**: The structured experience store in `profile_store.yaml`, used to generate more targeted and higher-quality outputs from a richer source of truth.

## Roadmap

- RAG-based job search and resume knowledge system
- Interview simulation and feedback
- Better datastore retrieval and ranking
- Agent-driven application workflows
- Resume versioning and targeting automation

## Contributing / Feedback

Feedback, issues, and pull requests are welcome.

If you want to improve the workflow, test the output quality, or suggest product directions, open an issue or start a discussion.
