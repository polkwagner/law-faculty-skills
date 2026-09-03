#!/bin/sh
set -eu

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
repo_root=$(CDPATH= cd -- "$skill_dir/../.." && pwd)
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

require 'Review Tiers'
require 'Static website mode'
require 'Saved reports are opt-in.'
require 'Do not reconcile against plans marked complete'
require 'The factual pass owns direct-quotation extraction'
require 'use it for the factual pass'
require 'only a claim extractor'
require 'evidence ledger'
require 'Natural-language requests are valid'
reject 'Hard abort if `factual-pipeline-orchestrator` is missing.'
reject 'Always dispatch agents 1-5 concurrently'

test -f "$skill_dir/references/runtime-and-output.md"
test -f "$skill_dir/references/document-modes.md"
test -f "$skill_dir/tests/fixtures/static-site.md"
test -f "$skill_dir/tests/fixtures/completed-plan.md"

for agent in \
  factual-pipeline-orchestrator \
  factual-reviewer \
  institutional-claim-extractor \
  quote-extractor \
  claim-merge-agent \
  fact-verifier \
  coverage-auditor \
  adversarial-reverifier \
  disagreement-analyzer \
  eddie-consistency-checker \
  eddie-second-eyes \
  fix-verifier \
  voice-style-checker
do
  agent_file="$repo_root/agents/$agent/$agent.md"
  test -f "$agent_file"
  if grep -Eq '^model: *(opus|sonnet|haiku) *$' "$agent_file"; then
    printf 'Claude-only model pin breaks Codex agent dispatch: %s\n' "$agent_file" >&2
    exit 1
  fi
done

printf 'Eddie v3 contract checks passed.\n'
