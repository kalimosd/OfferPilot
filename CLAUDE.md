# OfferPilot

This repository is an installable OfferPilot skill. The canonical skill entry point is `SKILL.md`; the workflow documents are under `skill-pack/`.

## When the user asks to install or configure OfferPilot

Run from the repository root:

```bash
./scripts/install_skill.sh claude
```

This links `SKILL.md` and `skill-pack/` into `~/.claude/skills/offerpilot`. After that the user can invoke `/offerpilot <task>`. If the command does not appear, run `/reload-skills` or start a new session.

Do not copy only `SKILL.md`; it references `skill-pack/`. Manual steps, copy mode, Codex installation, and uninstall instructions are in `INSTALL.md`.

## Development

- Run tests with `.venv/bin/python -m pytest -q`.
- Read `skill-pack/WORKFLOW.md` before changing workflow behavior.
- Keep `SKILL.md` and `skill-pack/adapters/*/SKILL.md` frontmatter consistent (`name: offerpilot`).
