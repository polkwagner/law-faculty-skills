# Rex Deployment Rules

The source repository is authoritative. Runtime copies in `~/.codex/skills/rex/`, `~/.claude/skills/rex/`, and `~/.agents/skills/rex/` must receive the same portable files: `SKILL.md`, `lenses/`, `references/`, and `tests/`.

Do not overwrite a runtime-local calibration file unless it is explicitly source-controlled. After synchronization, run `tests/validate_contract.sh` in every runtime copy, then run:

```sh
sh rex/tests/validate_runtime_parity.sh rex \
  ~/.codex/skills/rex ~/.claude/skills/rex ~/.agents/skills/rex
```

If a runtime cannot dispatch agents or run a test command, the skill still runs. Its preflight must report that limit and select the corresponding review mode.
