# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A public collection of Claude Code custom skills for Penn Carey Law faculty. The repo contains two kinds of artifacts:

- **Skills** — each subdirectory at repo root is a standalone skill with a `SKILL.md` file. Faculty install individual skills into `~/.claude/skills/`.
- **Agents** — reusable sub-agents under `agents/<name>/<name>.md`. Skills reference agents by name via the `Task` tool. Faculty install them into `~/.claude/agents/`.

Several skills (eddie, law-mcq-generator, law-essay-generator, lecture-slide-reviewer, law-class-prep) dispatch parallel sub-agents for quality checks. Skills work on their own but degrade gracefully without agents — scrub rules wrap every agent call in "if the `X` agent is available, spawn it" hedges.

## Agentskills Spec Compliance

Every skill conforms to the [agentskills specification](https://github.com/agentskills/agentskills) — a cross-tool standard that lets the same SKILL.md work in Claude Code, Gemini CLI, and ChatGPT EDU (Skills or Custom GPTs). When editing skills, preserve:
- YAML frontmatter with `name` and `description` fields
- No Claude-specific tool assumptions in instructions
- Relative asset paths within the skill directory

## Commands

```bash
# Publish skills from working installation to repo (run from repo root)
python3 scripts/publish.py

# Preview a publish run without touching the repo (writes to a tmpdir)
python3 scripts/publish.py --dry-run

# Run the privacy-scrub tests directly (also runs as pre-flight in publish.py)
python3 scripts/test_publish.py

# Validate a generated MCQ exam (requires python-docx)
python3 law-mcq-generator/validate_mcq.py exam.docx answer_key.docx

# Extract comments from Word documents (stdlib only, no pip deps)
python3 docx-comment-summary/scripts/extract_comments.py file1.docx [file2.docx ...] [-o output.md]
```

Tests (`test_publish.py`) run automatically before every publish. They guard the privacy-critical scrub paths (text regex, docx metadata, derived verification set). Pass `--skip-tests` to bypass; don't.

## Two-Tier Editing Model

Skills fall into two categories with different editing workflows:

**Synced skills (10)** — source of truth is `~/.claude/skills/`. Edit there, then run `scripts/publish.py` to copy, rename, and scrub into the repo. Never edit these in-repo — changes will be overwritten on next publish.

Synced: `law-mcq-generator`, `law-essay-generator`, `lecture-slide-reviewer`, `law-memo`, `law-document`, `law-email-style`, `md-to-pdf`, `docx-comment-summary`, `rex`, `eddie`

**Repo-maintained skills (2)** — edited directly in the repo. Not in the publish pipeline's `SKILL_MAP`.

Repo-maintained: `law-class-problems`, `law-class-prep`

## Publish Pipeline

`scripts/publish.py` syncs from the maintainer's `~/.claude/skills/` and `~/.claude/agents/`:

1. Copies skills listed in `SKILL_MAP` — source name → published name:
   - `polk-memo` → `law-memo`
   - `polk-document` → `law-document`
   - `polk-email-style` → `law-email-style`
   - All others keep their names (`law-mcq-generator`, `law-essay-generator`, `lecture-slide-reviewer`, `md-to-pdf`, `docx-comment-summary`, `rex`, `eddie`)
2. Copies agents listed in `AGENT_MAP` into `agents/<name>/` (16 agents, names unchanged)
3. `EXCLUDED_SKILLS` safety check blocks publication of `send-to-email`, `polk-slides`, `class-prep` (Polk-personalized), `project-folder-setup` (Polk-personalized)
4. Applies ordered regex scrub rules to skills AND agents (name, title, email → placeholders)
5. `SKIP_DIRS` excludes `plans/`, `specs/`, `_archive/`, `__pycache__/` (internal working artifacts)
6. `SKIP_FILE_PATTERNS` excludes `*.v1.md` / `*.v2.md` backup snapshots
7. `SKIP_FILES` excludes `design.md`, `.DS_Store`
8. Validates skills against agentskills spec; validates agent frontmatter (name + description required)
9. Runs post-scrub verification on skills + agents — **verification strings are auto-derived from `SCRUB_RULES`** via `derive_private_strings()`, so they can't drift from the scrub patterns
10. Flags sync-drift — compares each published synced-skill file against what scrubbing its current source would produce; warns when in-repo hand edits would be overwritten
11. Warns about unfilled placeholders (`OWNER/REPO_NAME`, `YOUR_WEBHOOK_URL`) anywhere in the published tree (recursive)

**Privacy defenses (layered):**
- Text regex (SCRUB_RULES) — `.md`, `.py`, `.json`, etc.
- docx metadata — `dc:creator`, `cp:lastModifiedBy`, and others cleared; `dcterms:created`/`dcterms:modified` normalized to `2000-01-01T00:00:00Z`
- docx body XML — `scrub_text` applied to `word/*.xml` and `customXml/*.xml` (body content, headers, footers, comments, footnotes) so identifiers in document text don't slip past the metadata-only scrub
- Pre-flight tests (`test_publish.py`) — run before every publish; fail-closed
- Post-scrub verification — auto-derived private-string set checked against text files AND docx property XML
- Sync-drift detection — catches hand edits that would be silently overwritten

**Scrub rule ordering matters.** Specific patterns must come before catch-all patterns (e.g., compound "Polk Wagner" contexts before the standalone catch-all). See `SCRUB_RULES` in publish.py.

## .gitignore: What's Local but Not Published

Several directories exist locally (as source skills or private skills) but are gitignored:

- `polk-memo/`, `polk-document/`, `polk-email-style/` — source versions of synced skills
- `send-to-email/`, `ip-problems/`, `class-prep-skill/` — private skills, not published
- `**/design.md` — design docs within skill directories
- Dropbox "conflicted copy" files (e.g., `README (Polk Wagner's conflicted copy ...).md`, `publish (... conflicted copy ...).py`) — artifacts of two-machine sync; safe to delete once reviewed

## Helper Scripts

- **`law-mcq-generator/validate_mcq.py`** — Post-generation validation for MCQ exams. Checks structural integrity, answer distribution, narrative coherence, and summary accuracy across exam and answer key .docx files. Requires `python-docx`.
- **`docx-comment-summary/scripts/extract_comments.py`** — Parses Word XML directly (stdlib `zipfile` + `ElementTree`, no pip deps) to extract comments with author, timestamp, anchored text, and replies.

## Skill File Format (SKILL.md)

Every skill uses this structure:

```yaml
---
name: skill-name
description: >
  When to trigger this skill. Includes trigger phrases.
---
```

Followed by markdown sections: overview, environment paths, workflow steps, content requirements, output format, and anti-patterns.

## Key Conventions

### Dual-Environment Paths

All skills work in both CLI and web (claude.ai) environments:

| Resource | CLI | Web |
|---|---|---|
| Skills dir | `~/.claude/skills/` | `/mnt/skills/user/` |
| Output | `~/Downloads/` | `/mnt/user-data/outputs/` |
| Uploads | User provides path | `/mnt/user-data/uploads/` |

Logo resolution uses try-first fallback: attempt CLI path, fall to web path, fail loudly if neither exists.

### Shared Formatting (.docx output)

Skills producing Word documents share these conventions:
- Cambria 12pt, 1" margins (1440 twips), 1.15 line spacing (`w:line="276"`)
- Paragraph spacing: `w:after="160"`
- Headings: Cambria 12pt bold (same size as body)
- Bullets: em-dash with tab and hanging indent (never Word list bullets)
- Page numbers: centered footer, Cambria 10pt italic, "Page x of y."
- Penn Carey Law logo: sourced from `law-document/assets/`, resized to 2.875" width

### Course Material Discovery

Pedagogical skills (class-problems, class-prep, lecture-slide-reviewer, MCQ, essay) share a "First Steps" pattern:
1. Get course materials path from user
2. Read the syllabus
3. Check for existing resources
4. Read assigned materials thoroughly
5. Then begin work

All enforce construct alignment: every tested issue must trace to assigned readings.

## Dependencies

- **python-docx**: Used by memo, document, MCQ, essay, and validate_mcq for .docx generation/parsing
- **ReportLab**: Used by md-to-pdf for PDF rendering
- **docx-comment-summary**: stdlib only (no pip dependencies) — parses .docx XML directly

## When Editing Skills

- Respect the two-tier model: synced skills are edited in `~/.claude/skills/`, repo-maintained skills are edited in-place
- After publishing, review the git diff carefully — scrub rule changes can have unintended cascading effects
- Test dual-environment path resolution when adding asset references
- Maintain the YAML frontmatter `description` field with accurate trigger phrases
- MCQ and essay skills use course presets; add new presets for additional courses
