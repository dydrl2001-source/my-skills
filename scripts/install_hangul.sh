#!/bin/bash
set -euo pipefail

require_command() {
  if ! command -v "$1" >/dev/null; then
    printf '설치에 필요한 명령을 찾을 수 없습니다. %s\n' "$1" >&2
    exit 1
  fi
}

for dependency in git codex node npm python3; do
  require_command "$dependency"
done

if ! node -e 'process.exit(Number(process.versions.node.split(".")[0]) < 20 ? 1 : 0)'; then
  printf 'Node.js 20 이상을 설치한 후 다시 실행해 주세요.\n' >&2
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
  printf 'Python 3.10 이상을 설치한 후 다시 실행해 주세요.\n' >&2
  exit 1
fi

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
install_root="${CODEX_HANGUL_INSTALL_DIR:-$HOME/.local/share/codex-hangul}"
skills_root="${CODEX_HANGUL_SKILLS_DIR:-$HOME/.agents/skills}"
hwpkit_revision=bd55ee61010fc98c98ec38e6dced26fb3144661e
hwpkit_root="$install_root/hwpkit-$hwpkit_revision"
mcp_root="$install_root/hwp-mcp-0.3.0"
node_path="$(command -v node)"

for skill in hwpkit hwpx-editing; do
  test -f "$repo_root/.agents/skills/$skill/SKILL.md"
done
mkdir -p "$install_root" "$skills_root"

if [[ ! -d "$hwpkit_root/.git" ]]; then
  git init -q "$hwpkit_root"
fi
if [[ "$(git -C "$hwpkit_root" rev-parse --verify HEAD 2>/dev/null || true)" != "$hwpkit_revision" ]]; then
  git -C "$hwpkit_root" fetch --depth 1 https://github.com/yuyu04/hwpkit.git "$hwpkit_revision"
  git -C "$hwpkit_root" checkout --detach FETCH_HEAD
fi
test -f "$hwpkit_root/scripts/hwp-mcp.mjs"

npm install --prefix "$mcp_root" --no-audit --no-fund --ignore-scripts hwp-mcp@0.3.0
test -f "$mcp_root/node_modules/hwp-mcp/dist/server.js"

if [[ ! -x "$install_root/venv/bin/python" ]]; then
  python3 -m venv "$install_root/venv"
fi
"$install_root/venv/bin/python" -m pip install 'lxml>=5,<7' 'openpyxl>=3.1,<4' 'python-docx>=1,<2'

for skill in hwpkit hwpx-editing; do
  target="$skills_root/$skill"
  source="$repo_root/.agents/skills/$skill"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ ! "$target" -ef "$source" ]]; then
      printf '기존 스킬 경로를 유지했습니다. %s\n' "$target" >&2
    fi
  else
    ln -s "$source" "$target"
  fi
done

register_mcp() {
  if codex mcp get "$1" >/dev/null 2>&1; then
    printf '기존 MCP 설정을 유지했습니다. %s\n' "$1"
  else
    codex mcp add "$1" -- "$node_path" "$2"
  fi
}

register_mcp hwpkit "$hwpkit_root/scripts/hwp-mcp.mjs"
register_mcp hwp-mcp "$mcp_root/node_modules/hwp-mcp/dist/server.js"
codex mcp list
