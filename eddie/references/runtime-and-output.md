# Runtime and Output Rules

## Capability Discovery

Determine the active runtime from its available tools and skill locations. Common locations are `~/.claude/skills/eddie/` (which `~/.codex/skills/eddie/` symlinks to) and web-runtime mounted skill directories. Do not assume one exists, and do not hard-code a required agent-file path.

Check whether a role can actually be dispatched before allocating it. Record a capability as unavailable when the runtime rejects a dispatch, lacks agent slots, or cannot reach its source tools. Use the compact tier rather than retrying an unavailable call repeatedly.

For the evidence role, prefer the dispatchable `factual-pipeline-orchestrator`. It is one bounded orchestration layer and may dispatch its named extractor, merger, verifier, coverage, and adversarial roles. Do not substitute `factual-reviewer`: despite its name, that role only extracts claims and performs no verification. A successful evidence pass must return verification results, not merely a claim list.

Agent definitions must inherit the active runtime's model. Do not pin Claude model aliases such as `opus`, `sonnet`, or `haiku` in Eddie agent frontmatter; Codex cannot instantiate those aliases on a ChatGPT account. Runtime inheritance keeps the same definitions usable in both Claude and Codex.

## Agent Budget

Assign roles by capability, not by product name:

1. Evidence review, including quotation extraction and citation checking.
2. Adversarial/structural review.
3. Voice and consistency review.
4. Second eyes, reserved when there are P1/P2 findings or a dispute about a finding.
5. Fix verification, only for externally verifiable replacement values.

For a limited runtime, combine roles 1-3 in one deliberate pass and disclose the limitation. Do not create additional nested orchestration trees beyond the single bounded factual pipeline. If fewer than two slots are available, preserve the independent second-eyes slot over a low-risk style pass.

## Safe Report Locations

Use this order:

1. A project-configured, nonpublished review directory that is excluded from version control or explicitly intended for internal reports.
2. The runtime's user-output directory.
3. A user-specified directory after checking it is not published accidentally.

If none is available, provide the detailed report inline and do not write a file. A saved report must state whether it is intended to be committed, retained locally, or discarded.
