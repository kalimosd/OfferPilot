# Install OfferPilot as a Skill

This repository is an installable skill. The canonical entry point is the repository-root `SKILL.md`; the workflow documents live in `skill-pack/`.

## Quick Install

Run from the repository root:

```bash
./scripts/install_skill.sh claude   # Claude Code
./scripts/install_skill.sh codex    # Codex
./scripts/install_skill.sh all      # both
```

Then:

| Platform | Invocation |
|---|---|
| Claude Code | `/offerpilot 优化简历` |
| Codex | `$offerpilot 优化简历` or the `/skills` picker |

If the skill does not appear immediately, run `/reload-skills` in Claude Code or restart the agent.

## What the Installer Does

By default it creates a symlinked skill directory:

```text
~/.claude/skills/offerpilot/
├── SKILL.md      -> <repo>/SKILL.md
└── skill-pack/   -> <repo>/skill-pack

~/.agents/skills/offerpilot/
├── SKILL.md      -> <repo>/SKILL.md
└── skill-pack/   -> <repo>/skill-pack
```

Symlinking keeps the skill in sync with the repository and preserves the `skill-pack/...` paths referenced by `SKILL.md`.

To create a self-contained copy instead:

```bash
./scripts/install_skill.sh all --copy
```

If the target already contains a non-symlink `SKILL.md` or `skill-pack/`, the installer stops. Use `--force` to replace it, or remove the target directory first.

## Manual Install

### Claude Code

```bash
mkdir -p ~/.claude/skills/offerpilot
ln -sfn "$PWD/SKILL.md" ~/.claude/skills/offerpilot/SKILL.md
ln -sfn "$PWD/skill-pack" ~/.claude/skills/offerpilot/skill-pack
```

Claude Code reads personal skills from `~/.claude/skills/<name>/SKILL.md`. The frontmatter `name: offerpilot` makes the command `/offerpilot`; the directory name `offerpilot` is also a valid alias.

### Codex

```bash
mkdir -p ~/.agents/skills/offerpilot
ln -sfn "$PWD/SKILL.md" ~/.agents/skills/offerpilot/SKILL.md
ln -sfn "$PWD/skill-pack" ~/.agents/skills/offerpilot/skill-pack
```

Codex reads user skills from `~/.agents/skills/<name>/SKILL.md` and invokes them with `$offerpilot` or the `/skills` picker. Some Codex builds also read `~/.codex/skills/`; set `AGENTS_SKILLS_DIR` to that path if your build needs it:

```bash
AGENTS_SKILLS_DIR="$HOME/.codex/skills" ./scripts/install_skill.sh codex
```

## Environment Overrides

| Variable | Default |
|---|---|
| `CLAUDE_SKILLS_DIR` | `~/.claude/skills` |
| `AGENTS_SKILLS_DIR` | `~/.agents/skills` |

Useful for testing the installer or installing into a project-local skills directory.

## Project-Local Install

To make the skill available only inside a repository, create the same layout under `.claude/skills/offerpilot/` (Claude Code) or `.agents/skills/offerpilot/` (Codex) in that repository. Note that this repository's `.claude/` directory is gitignored, so a project-local install is not committed.

## Do Not Copy Only SKILL.md

`SKILL.md` references `skill-pack/README.md`, `skill-pack/WORKFLOW.md`, and other documents under `skill-pack/`. Copying only `SKILL.md` leaves every one of those references broken. Use the installer, symlink, or copy the whole `skill-pack/` directory alongside `SKILL.md`.

## Uninstall

```bash
rm -rf ~/.claude/skills/offerpilot
rm -rf ~/.agents/skills/offerpilot
```

If you used `--copy`, the installed directories are independent copies; removing them does not affect this repository.
