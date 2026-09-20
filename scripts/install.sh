#!/usr/bin/env bash
# Instala (via symlink) as skills deste repositório em Claude e Cursor.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_SKILLS="${HOME}/.claude/skills"
CURSOR_SKILLS="${HOME}/.cursor/skills"

mkdir -p "$CLAUDE_SKILLS" "$CURSOR_SKILLS"

skip_name() {
  case "$1" in
    scripts|.git|.github) return 0 ;;
    *) return 1 ;;
  esac
}

link_skill() {
  local dest="$1"
  local src="$2"
  local name="$3"

  if [ -L "$dest" ]; then
    ln -sfn "$src" "$dest"
    echo "link ${dest}"
  elif [ -e "$dest" ]; then
    echo "skip ${name} em ${dest} (pasta real já existe — não sobrescreve)"
  else
    ln -sfn "$src" "$dest"
    echo "link ${dest}"
  fi
}

installed=0
for dir in "$REPO"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  skip_name "$name" && continue
  [ -f "${dir}SKILL.md" ] || continue

  # rsync e find deixam barra no fim; o symlink deve apontar para a pasta da skill
  src="${dir%/}"
  link_skill "${CLAUDE_SKILLS}/${name}" "$src" "$name"
  link_skill "${CURSOR_SKILLS}/${name}" "$src" "$name"
  installed=$((installed + 1))
done

echo
echo "Instaladas ${installed} skills em:"
echo "  ${CLAUDE_SKILLS}"
echo "  ${CURSOR_SKILLS}"
echo
echo "Fonte: ${REPO}"
echo "Remote: git@github.com:abnerndr/skills.git"
