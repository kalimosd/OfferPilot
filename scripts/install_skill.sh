#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_SRC="$REPO_ROOT/SKILL.md"
PACK_SRC="$REPO_ROOT/skill-pack"

MODE="link"
TARGET="all"
FORCE=0

usage() {
  cat <<'EOF'
Usage: scripts/install_skill.sh [claude|codex|all] [--copy] [--force]

  claude   Install to ~/.claude/skills/offerpilot
  codex    Install to ~/.agents/skills/offerpilot
  all      Install for both (default)

  --copy   Copy SKILL.md and skill-pack/ instead of symlinking
  --force  Replace an existing non-symlink SKILL.md or skill-pack/ in the target

Environment overrides:
  CLAUDE_SKILLS_DIR  default: ~/.claude/skills
  AGENTS_SKILLS_DIR  default: ~/.agents/skills
EOF
}

for arg in "$@"; do
  case "$arg" in
    claude|codex|all) TARGET="$arg" ;;
    --copy) MODE="copy" ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

if [ ! -f "$SKILL_SRC" ]; then
  echo "ERROR: missing $SKILL_SRC" >&2
  exit 1
fi
if [ ! -d "$PACK_SRC" ]; then
  echo "ERROR: missing $PACK_SRC" >&2
  exit 1
fi

install_one() {
  local dest="$1"
  local platform="$2"

  mkdir -p "$dest"

  if [ -e "$dest/SKILL.md" ] && [ ! -L "$dest/SKILL.md" ] && [ "$FORCE" -ne 1 ]; then
    echo "ERROR: $dest/SKILL.md exists and is not a symlink; use --force or remove it" >&2
    exit 1
  fi
  if [ -e "$dest/skill-pack" ] && [ ! -L "$dest/skill-pack" ] && [ "$FORCE" -ne 1 ]; then
    echo "ERROR: $dest/skill-pack exists and is not a symlink; use --force or remove it" >&2
    exit 1
  fi

  if [ "$MODE" = "copy" ]; then
    rm -f "$dest/SKILL.md"
    rm -rf "$dest/skill-pack"
    cp "$SKILL_SRC" "$dest/SKILL.md"
    cp -R "$PACK_SRC" "$dest/skill-pack"
  else
    ln -sfn "$SKILL_SRC" "$dest/SKILL.md"
    ln -sfn "$PACK_SRC" "$dest/skill-pack"
  fi

  echo "Installed OfferPilot skill at $dest"
  case "$platform" in
    claude) echo "  Claude Code: /offerpilot <task>" ;;
    codex) echo "  Codex: \$offerpilot <task>  (or the /skills picker)" ;;
  esac
}

if [ "$TARGET" = "claude" ] || [ "$TARGET" = "all" ]; then
  install_one "${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/offerpilot" claude
fi
if [ "$TARGET" = "codex" ] || [ "$TARGET" = "all" ]; then
  install_one "${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}/offerpilot" codex
fi

echo
echo "If the skill does not appear, run /reload-skills (Claude Code) or restart the agent."
