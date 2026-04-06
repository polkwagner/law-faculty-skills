# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A public collection of Claude Code custom skills for Penn Carey Law faculty. Each subdirectory is a standalone skill with a `SKILL.md` file that defines its behavior, triggers, and workflow. Faculty install individual skills into their `~/.claude/skills/` directory.

## Commands

```bash
# Publish skills from working installation to repo (run from repo root)
python3 scripts/publish.py

# Validate a generated MCQ exam (requires python-docx)
python3 law-mcq-generator/validate_mcq.py exam.docx answer_key.docx

# Extract comments from Word documents (stdlib only, no pip deps)
python3 docx-comment-summary/scripts/extract_comments.py file1.docx [file2.docx ...] [-o output.md]
```

There are no build steps, linters, or test suites. The repo is documentation and scripts — validation is manual (run publish, review the diff, check for leaked private strings in output).

## Two-Tier Editing Model

Skills fall into two categories with different editing workflows:

**Synced skills (10)** — source of truth is `~/.claude/skills/`. Edit there, then run `scripts/publish.py` to copy, rename, and scrub into the repo. Never edit these in-repo — changes will be overwritten on next publish.

Synced: `law-mcq-generator`, `law-essay-generator`, `lecture-slide-reviewer`, `law-memo`, `law-document`, `law-email-style`, `md-to-pdf`, `docx-comment-summary`, `rex`, `eddie`

**Repo-maintained skills (2)** — edited directly in the repo. Not in the publish pipeline's `SKILL_MAP`.

Repo-maintained: `law-class-problems`, `law-class-prep`

## Publish Pipeline

`scripts/publish.py` syncs from the maintainer's `~/.claude/skills/`:

1. Copies skills listed in `SKILL_MAP` (source name → published name)
2. Renames `polk-*` directories to `law-*` and applies file rename rules
3. Applies ordered regex scrub rules to generalize personal details (name, title, email → placeholders)
4. Skips excluded files (`design.md`, `.DS_Store`, `__pycache__/`)
5. Runs post-scrub verification — scans output for leaked private strings
6. Warns about unfilled placeholders (repo owner/name, webhook URLs)

**Scrub rule ordering matters.** Specific patterns must come before catch-all patterns (e.g., compound "Polk Wagner" contexts before the standalone catch-all). See `SCRUB_RULES` in publish.py.

## .gitignore: What's Local but Not Published

Several directories exist locally (as source skills or private skills) but are gitignored:

- `polk-memo/`, `polk-document/`, `polk-email-style/` — source versions of synced skills
- `send-to-email/`, `ip-problems/`, `class-prep-skill/` — private skills, not published
- `**/design.md` — design docs within skill directories

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
