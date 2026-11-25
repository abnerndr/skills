#!/usr/bin/env bash
# Instala todas as skills deste repositório nos agentes locais (CLI e desktop).
# De qualquer pasta:
#   curl -fsSL https://raw.githubusercontent.com/abnerndr/skills/main/scripts/install.sh | bash
set -euo pipefail

REMOTE_HTTPS="https://github.com/abnerndr/skills.git"
REMOTE_SSH="git@github.com:abnerndr/skills.git"

script_dir_from_source() {
  local src="${BASH_SOURCE[0]:-}"
  case "$src" in
    ""|bash|main|/dev/fd/*|/proc/*) return 1 ;;
  esac
  [[ -f "$src" ]] || return 1
  cd "$(dirname "$src")" && pwd
}

REPO=""
if script_dir="$(script_dir_from_source)"; then
  if [[ -f "$script_dir/../README.md" ]]; then
    REPO="$(cd "$script_dir/.." && pwd)"
  fi
fi

if [[ -z "$REPO" ]]; then
  dest="${SKILLS_REPO:-$HOME/www/skills}"
  mkdir -p "$(dirname "$dest")"
  if [[ ! -d "$dest/.git" ]]; then
    echo "clonando ${REMOTE_HTTPS} em ${dest}"
    if ! git clone "$REMOTE_SSH" "$dest"; then
      git clone "$REMOTE_HTTPS" "$dest"
    fi
  elif git -C "$dest" diff --quiet && git -C "$dest" diff --cached --quiet; then
    echo "atualizando ${dest}"
    git -C "$dest" pull --ff-only
  else
    echo "repo local com alterações; não fiz pull: ${dest}"
  fi
  exec bash "$dest/scripts/install.sh"
fi

skip_name() {
  case "$1" in
    scripts|.git|.github) return 0 ;;
    *) return 1 ;;
  esac
}

is_windows_home() {
  case "$1" in
    /mnt/c/Users/*|/mnt/c/users/*|/c/Users/*|/c/users/*) return 0 ;;
    *) return 1 ;;
  esac
}

has_glob() {
  local pattern="$1"
  shopt -s nullglob
  local matches=( $pattern )
  shopt -u nullglob
  [[ ${#matches[@]} -gt 0 ]]
}

add_home() {
  local candidate="$1"
  [[ -n "$candidate" && -d "$candidate" ]] || return 0
  local existing
  for existing in "${HOMES[@]}"; do
    [[ "$existing" == "$candidate" ]] && return 0
  done
  HOMES+=("$candidate")
}

add_dest() {
  local candidate="${1%/}"
  [[ -n "$candidate" ]] || return 0
  local existing
  for existing in "${DESTS[@]}"; do
    [[ "$existing" == "$candidate" ]] && return 0
  done
  DESTS+=("$candidate")
}

windows_profile() {
  command -v cmd.exe >/dev/null 2>&1 || return 1
  local profile
  profile="$(cmd.exe /d /c "echo %USERPROFILE%" 2>/dev/null | tr -d '\r' | tail -n 1)"
  [[ "$profile" == *:\\* || "$profile" == *:* ]] || return 1
  wslpath -u "$profile"
}

collect_homes() {
  HOMES=()
  add_home "$HOME"
  if [[ -n "${WSL_DISTRO_NAME:-}" ]] || grep -qi microsoft /proc/version 2>/dev/null; then
    local win
    win="$(windows_profile || true)"
    add_home "$win"
  elif command -v wsl.exe >/dev/null 2>&1; then
    local wsl_home
    wsl_home="$(wsl.exe -e bash -lc 'printf %s "$HOME"' 2>/dev/null | tr -d '\r' | tail -n 1 || true)"
    add_home "$wsl_home"
  fi
}

destinations_for_home() {
  local home="$1"
  # Pedidos explicitamente, mais o Cursor (desktop e remote).
  add_dest "$home/.agents/skills"
  add_dest "$home/.claude/skills"
  add_dest "$home/.codex/skills"
  add_dest "$home/.gemini/skills"
  add_dest "$home/.cursor/skills"

  if [[ -d "$home/.gemini/antigravity" || -d "$home/.gemini/antigravity-cli" || -x "$home/.local/bin/agy" || -d "$home/AppData/Local/Programs/antigravity" ]]; then
    add_dest "$home/.gemini/config/skills"
  fi

  if [[ -x "$home/.local/bin/opencode" || -d "$home/.config/opencode" ]] || has_glob "$home/.nvm/versions/node/*/bin/opencode"; then
    add_dest "$home/.config/opencode/skills"
  fi

  if [[ -x "$home/.local/bin/qwen" ]] || has_glob "$home/.nvm/versions/node/*/bin/qwen"; then
    add_dest "$home/.qwen/skills"
  fi

  if [[ -x "$home/.local/bin/kiro" || -d "$home/AppData/Local/Programs/Kiro" ]]; then
    add_dest "$home/.kiro/skills"
  fi

  if [[ -d "$home/.copilot" || -d "$home/AppData/Local/Programs/Microsoft VS Code" ]]; then
    add_dest "$home/.copilot/skills"
  fi
}

skill_is_managed() {
  local manifest="$1"
  local name="$2"
  [[ -f "$manifest" ]] && grep -qxF "$name" "$manifest"
}

remember_managed() {
  local manifest="$1"
  local name="$2"
  touch "$manifest"
  if ! grep -qxF "$name" "$manifest"; then
    echo "$name" >>"$manifest"
  fi
}

install_symlink() {
  local dest="$1"
  local src="$2"
  local name="$3"

  if [[ -L "$dest" || ! -e "$dest" ]]; then
    ln -sfn "$src" "$dest"
    echo "link ${dest}"
  else
    echo "skip ${name} em ${dest} (pasta real já existe — não sobrescreve)"
  fi
}

install_copy() {
  local dest="$1"
  local src="$2"
  local name="$3"
  local root
  root="$(dirname "$dest")"
  local manifest="${root}/.abnerndr-managed"

  if [[ -e "$dest" && ! -L "$dest" ]] && ! skill_is_managed "$manifest" "$name"; then
    echo "skip ${name} em ${dest} (pasta real já existe — não sobrescreve)"
    return 0
  fi

  rm -rf -- "$dest"
  mkdir -p "$dest"
  cp -a "$src/." "$dest/"
  remember_managed "$manifest" "$name"
  echo "copy ${dest}"
}

install_one() {
  local dest="$1"
  local src="$2"
  local name="$3"
  local root
  root="$(dirname "$dest")"
  mkdir -p "$root"

  if is_windows_home "$root" && [[ "$REPO" != /mnt/c/* && "$REPO" != /c/* ]]; then
    install_copy "$dest" "$src" "$name"
  else
    install_symlink "$dest" "$src" "$name"
  fi
}

collect_homes
DESTS=()
for home in "${HOMES[@]}"; do
  destinations_for_home "$home"
done

installed=0
for dir in "$REPO"/*/; do
  [[ -d "$dir" ]] || continue
  name="$(basename "$dir")"
  skip_name "$name" && continue
  [[ -f "${dir}SKILL.md" ]] || continue
  src="${dir%/}"
  for dest_root in "${DESTS[@]}"; do
    install_one "${dest_root}/${name}" "$src" "$name"
  done
  installed=$((installed + 1))
done

echo
echo "Instaladas ${installed} skills em:"
for dest_root in "${DESTS[@]}"; do
  echo "  ${dest_root}"
done
echo
echo "Fonte: ${REPO}"
echo "Remote: ${REMOTE_SSH}"
echo "No Windows as pastas são cópias. Rode este script de novo para atualizar."
