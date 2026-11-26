#!/bin/bash
# Link the repository's complete cloning skills into a local Codex skill folder.
set -euo pipefail

usage() {
  cat <<'EOF'
사용법: bash scripts/install_cloners.sh [--help]

clone-app, clone-website, true-web-clone을 로컬 Codex 스킬 폴더에 연결합니다.
기본 경로: $HOME/.agents/skills
경로 지정: CODEX_CLONER_SKILLS_DIR=/원하는/경로
기존의 다른 파일이나 링크는 덮어쓰지 않습니다. 외부 도구는 설치하지 않습니다.
EOF
}

fail() {
  printf '설치 중단: %s\n' "$1" >&2
  exit 1
}

if [[ $# -gt 0 ]]; then
  if [[ $# -eq 1 && ( "$1" == '--help' || "$1" == '-h' ) ]]; then
    usage
    exit 0
  fi
  printf '지원하지 않는 인자입니다. --help로 사용법을 확인해 주세요.\n' >&2
  exit 2
fi

# macOS's built-in Bash and readlink do not provide readlink -f.
script_path="${BASH_SOURCE[0]}"
if [[ "$script_path" != /* ]]; then
  script_path="$PWD/$script_path"
fi
link_depth=0
while [[ -L "$script_path" ]]; do
  link_depth=$((link_depth + 1))
  [[ $link_depth -le 40 ]] || fail '설치 스크립트의 심볼릭 링크가 너무 많거나 순환합니다.'
  script_dir="$(cd -P -- "$(dirname "$script_path")" && pwd -P)"
  link_path="$(readlink "$script_path")"
  if [[ "$link_path" == /* ]]; then
    script_path="$link_path"
  else
    script_path="$script_dir/$link_path"
  fi
done
repo_root="$(cd -P -- "$(dirname "$script_path")/.." && pwd -P)"

if [[ -n "${CODEX_CLONER_SKILLS_DIR:-}" ]]; then
  skills_root="$CODEX_CLONER_SKILLS_DIR"
else
  [[ -n "${HOME:-}" ]] || fail 'HOME 또는 CODEX_CLONER_SKILLS_DIR을 지정해 주세요.'
  skills_root="$HOME/.agents/skills"
fi
if [[ "$skills_root" != /* ]]; then
  skills_root="$PWD/$skills_root"
fi

skill_names=(clone-app clone-website true-web-clone)

# Preflight every source and destination before creating any directory or link.
for skill in "${skill_names[@]}"; do
  source_dir="$repo_root/.agents/skills/$skill"
  [[ -d "$source_dir" && -f "$source_dir/SKILL.md" ]] || fail "스킬 원본이 없습니다: $source_dir/SKILL.md"
done

# Resolve existing directory symlinks and parent segments without creating paths.
# Otherwise a missing "new/../" prefix can hide an existing target conflict.
remaining_path="${skills_root#/}"
skills_root='/'
while [[ -n "$remaining_path" ]]; do
  component="${remaining_path%%/*}"
  if [[ "$remaining_path" == */* ]]; then
    remaining_path="${remaining_path#*/}"
  else
    remaining_path=''
  fi
  case "$component" in
    ''|.) continue ;;
    ..) skills_root="$(dirname "$skills_root")"; continue ;;
  esac
  next_dir="${skills_root%/}/$component"
  if [[ -e "$next_dir" || -L "$next_dir" ]]; then
    [[ -d "$next_dir" ]] || fail "설치 경로가 디렉터리가 아닙니다: $next_dir"
    skills_root="$(cd -P -- "$next_dir" && pwd -P)"
  else
    skills_root="$next_dir"
  fi
done

for skill in "${skill_names[@]}"; do
  source_dir="$repo_root/.agents/skills/$skill"
  target="$skills_root/$skill"
  if [[ -e "$target" || -L "$target" ]]; then
    [[ "$target" -ef "$source_dir" ]] || fail "기존 경로와 충돌합니다. 그대로 유지했습니다: $target"
  fi
done

mkdir -p "$skills_root"
skills_root="$(cd -P -- "$skills_root" && pwd -P)"
for skill in "${skill_names[@]}"; do
  source_dir="$repo_root/.agents/skills/$skill"
  target="$skills_root/$skill"
  if [[ "$target" -ef "$source_dir" ]]; then
    printf '이미 연결됨: %s\n' "$target"
  else
    # Pass the parent directory so an existing child directory is not traversed.
    # No force option: a target that appears after preflight is preserved.
    ln -s "$source_dir" "$skills_root/"
    printf '연결 완료: %s\n' "$target"
  fi
done
