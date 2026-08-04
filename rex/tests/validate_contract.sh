#!/bin/sh
set -eu

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
skill="$skill_dir/SKILL.md"

require() {
  if ! grep -Fq "$1" "$skill"; then
    printf 'missing required contract text: %s\n' "$1" >&2
    exit 1
  fi
}

reject() {
  if grep -Fq "$1" "$skill"; then
    printf 'obsolete contract text remains: %s\n' "$1" >&2
    exit 1
  fi
}

require '## Preflight'
require '## Review Modes'
require '## Scope and Evidence'
require 'Risk alone does not make something a Blocker.'
require 'Needs verification'
require 'No material findings.'
require 'Apply a lens only where it fits the artifact.'
reject 'occasionally sardonic'
reject 'No verdict line'

for required in \
  "$skill_dir/references/deployment.md" \
  "$skill_dir/lenses/architecture.md" \
  "$skill_dir/lenses/code.md" \
  "$skill_dir/lenses/design-spec.md" \
  "$skill_dir/lenses/impl-plan.md" \
  "$skill_dir/lenses/pr.md" \
  "$skill_dir/lenses/prd.md" \
  "$skill_dir/tests/fixtures/critical-auth-diff.md" \
  "$skill_dir/tests/fixtures/docs-only-plan.md" \
  "$skill_dir/tests/fixtures/unverified-query-risk.md" \
  "$skill_dir/tests/expected.md"; do
  test -f "$required"
done

printf 'Rex v2 contract checks passed.\n'
