#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
  printf 'usage: %s SOURCE_SKILL_DIR RUNTIME_SKILL_DIR [RUNTIME_SKILL_DIR ...]\n' "$0" >&2
  exit 2
fi

source_dir=$1
shift

portable_files() {
  cd "$source_dir"
  find SKILL.md lenses references tests -type f ! -name 'lessons.md' -print | sort
}

for runtime_dir in "$@"; do
  portable_files | while IFS= read -r relative; do
    if [ ! -f "$runtime_dir/$relative" ]; then
      printf '%s: missing %s\n' "$runtime_dir" "$relative" >&2
      exit 1
    fi
    source_hash=$(shasum -a 256 "$source_dir/$relative" | awk '{print $1}')
    runtime_hash=$(shasum -a 256 "$runtime_dir/$relative" | awk '{print $1}')
    if [ "$source_hash" != "$runtime_hash" ]; then
      printf '%s: differs from source: %s\n' "$runtime_dir" "$relative" >&2
      exit 1
    fi
  done
  printf 'Rex runtime parity passed: %s\n' "$runtime_dir"
done
