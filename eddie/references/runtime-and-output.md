# Runtime and Output Rules

## Capability Discovery

Determine the active runtime from its available tools and skill locations. Common locations are `~/.codex/skills/eddie/`, `~/.claude/skills/eddie/`, `~/.agents/skills/eddie/`, and web-runtime mounted skill directories. Do not assume one exists, and do not hard-code a required agent-file path.

Check whether a role can actually be dispatched before allocating it. Record a capability as unavailable when the runtime rejects a dispatch, lacks agent slots, or cannot reach its source tools. Use the compact tier rather than retrying an unavailable call repeatedly.

## Agent Budget

Assign roles by capability, not by product name:

1. Evidence review, including quotation extraction and citation checking.
2. Adversarial/structural review.
3. Voice and consistency review.
4. Second eyes, reserved when there are P1/P2 findings or a dispute about a finding.
5. Fix verification, only for externally verifiable replacement values.

For a limited runtime, combine roles 1-3 in one deliberate pass and disclose the limitation. Do not create nested orchestration trees. If fewer than two slots are available, preserve the independent second-eyes slot over a low-risk style pass.

## Safe Report Locations

Use this order:

1. A project-configured, nonpublished review directory that is excluded from version control or explicitly intended for internal reports.
2. The runtime's user-output directory.
3. A user-specified directory after checking it is not published accidentally.

If none is available, provide the detailed report inline and do not write a file. A saved report must state whether it is intended to be committed, retained locally, or discarded.
