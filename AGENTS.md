# OfferPilot

This repository is an installable OfferPilot skill. The canonical skill entry point is `SKILL.md`; the workflow documents are under `skill-pack/`.

## When the user asks to install or configure OfferPilot

Run from the repository root:

```bash
./scripts/install_skill.sh codex
```

This links `SKILL.md` and `skill-pack/` into `~/.agents/skills/offerpilot`. Invoke the skill with `$offerpilot <task>` or the `/skills` picker. Codex does not document a `/offerpilot` slash command.

Do not copy only `SKILL.md`; it references `skill-pack/`. Manual steps, copy mode, Claude Code installation, and uninstall instructions are in `INSTALL.md`.

## Development

- Run tests with `.venv/bin/python -m pytest -q`.
- Read `skill-pack/WORKFLOW.md` before changing workflow behavior.
- Keep `SKILL.md` and `skill-pack/adapters/*/SKILL.md` frontmatter consistent (`name: offerpilot`).

## Git Rules

- Commit with the explicit identity `kalimosd <kalimosdzc@outlook.com>`; never fall back to the system user.
- Do NOT add `Co-Authored-By:` / `Co-authored-by:` trailers for AI tools (Claude, Cursor, etc.) to commit messages. The `.githooks/commit-msg` hook strips them; enable it on fresh clones with `git config core.hooksPath .githooks`.

