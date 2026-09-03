# Rex Deployment Rules

The source repository is authoritative. There is one canonical runtime copy, `~/.claude/skills/rex/`; Codex reaches it through the symlink `~/.codex/skills/rex` → `~/.claude/skills/rex`. The sync delivers the portable files to it: `SKILL.md`, `lenses/`, `references/`, and `tests/`.

Do not overwrite a runtime-local calibration file unless it is explicitly source-controlled. After synchronization, run `tests/validate_contract.sh` in the runtime copy. `tests/validate_runtime_parity.sh` is no longer needed — with a single copy there is nothing to compare — and is not part of the deployment check; the script file stays in place.

If a runtime cannot dispatch agents or run a test command, the skill still runs. Its preflight must report that limit and select the corresponding review mode.
