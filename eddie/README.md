# Eddie the Editor

Eddie is a cross-runtime, evidence-first editorial review skill for written artifacts and static website content. It reviews factual support, citations, hidden claims, institutional risk, structure, consistency, and voice. It reports findings; it does not silently rewrite or publish the target.

## Use

```text
/eddie path/to/file.md
/eddie path/to/file.md intensity=aggressive
/eddie path/to/file.md plan=docs/plans/current.md
/eddie path/to/file.md save-report report-dir=reviews/internal
```

Natural-language requests such as “run an Eddie review” also activate the skill. `save-report` is opt-in; reviews are inline by default.

## What Changed in v3

- Runs in Claude, Codex, and any runtime with the required capabilities; it no longer assumes `~/.claude` or treats a local agent file as proof that the role can run.
- Selects `full`, `standard`, or `compact` review based on stakes and actual agent capacity. A missing agent reduces coverage but does not abort the review.
- Uses one agent budget, reserves second eyes for material findings, and assigns quotation extraction to the factual pass to avoid duplicate work.
- Excludes completed and historical plans from automatic reconciliation.
- Adds a static-website mode for links, public/private boundaries, semester freshness, deep links, headings, and link text.
- Requires an evidence ledger for material factual and citation findings.
- Does not save reports into a repository unless the user requests a safe location.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Portable review workflow and output contract. |
| `senior_editor_profile.md` | Editorial standards and professional posture. |
| `references/runtime-and-output.md` | Capability discovery, agent budgets, and safe output policy. |
| `references/document-modes.md` | Mode-specific review checks. |
| `eddie_desktop_project_instructions.md` | Claude Project version of the workflow. |
| `lessons.md` | Calibrations from prior review work. |
| `tests/` | Fixtures, expected catches, and contract validation. |

## Validation

Run the contract check from the skill source root:

```sh
sh eddie/tests/validate_contract.sh
```

The manual fixture protocol and expected findings are in [tests/expected.md](tests/expected.md). The source repository is authoritative; installed runtime copies should be synchronized after validation.
