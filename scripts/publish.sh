#!/usr/bin/env bash
# Publica uma skill deste repositório no GitHub (abnerndr/skills).
# Uso:
#   scripts/publish.sh <skill-name>
#   scripts/publish.sh                 # publica todas as mudanças pendentes
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_URL="git@github.com:abnerndr/skills.git"
cd "$REPO"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -b main
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REMOTE_URL"
fi

skill_name="${1:-}"

if [ -n "$skill_name" ]; then
  skill_dir="${REPO}/${skill_name}"
  if [ ! -f "${skill_dir}/SKILL.md" ]; then
    echo "erro: ${skill_dir}/SKILL.md não encontrado" >&2
    exit 1
  fi
  git add "$skill_name"
  msg="Add skill ${skill_name}"
  if git diff --cached --quiet; then
    echo "nada novo em ${skill_name} — tentando push do que já está commitado"
  else
    git commit -m "$(cat <<EOF
${msg}

EOF
)"
  fi
else
  git add -A
  if git diff --cached --quiet; then
    echo "nada para commitar — tentando push"
  else
    git commit -m "$(cat <<'EOF'
Update skills

EOF
)"
  fi
fi

git push -u origin HEAD
echo
echo "publicado em ${REMOTE_URL}"
