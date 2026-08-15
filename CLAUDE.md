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

# Run a single test class or method (unittest)
python3 scripts/test_publish.py ScrubTextTests
python3 scripts/test_publish.py ScrubTextTests.test_<name>

# Validate a generated MCQ exam (requires python-docx)
python3 law-mcq-generator/validate_mcq.py exam.docx answer_key.docx

# Extract comments from Word documents (stdlib only, no pip deps)
python3 docx-comment-summary/scripts/extract_comments.py file1.docx [file2.docx ...] [-o output.md]

# Run an eddie regression fixture (black-box — diff the report against eddie/tests/expected.md)
/eddie skills/eddie/tests/fixtures/<fixture>.md be aggressive lessons=skills/eddie/tests/lessons.md
```

Tests (`test_publish.py`) run automatically before every publish. They guard the privacy-critical scrub paths (text regex, docx metadata, derived verification set). Pass `--skip-tests` to bypass; don't.

## Two-Tier Editing Model

Skills fall into two categories with different editing workflows:

**Synced skills (9)** — source of truth is `~/.claude/skills/`. Edit there, then run `scripts/publish.py` to copy, rename, and scrub into the repo. Never edit these in-repo — changes will be overwritten on next publish.

Synced: `law-mcq-generator`, `law-essay-generator`, `lecture-slide-reviewer`, `law-memo`, `law-document`, `law-email-style`, `docx-comment-summary`, `rex`, `eddie`

**Repo-maintained skills (3)** — edited directly in the repo. Not in the publish pipeline's `SKILL_MAP`.

Repo-maintained: `law-class-problems`, `law-class-prep`, `materials-md`

`materials-md` is a thin natural-language wrapper around the standalone
[`materials-converter`](https://github.com/ai-teaching-lab/materials-converter) tool
(installed via pip). It is intentionally repo-maintained rather than synced: the maintainer's
local `~/.claude/skills/materials-md/` still points at a local checkout, while the published
copy targets the pip-installed `materials-convert` command.

> **This repo is Dropbox-synced across two machines.** `git status` can show stale divergence
> (files dirty but byte-identical to upstream, or duplicate parallel commits with the same
> message but different SHAs) and even local git-object corruption — Dropbox syncs file
> contents and `.git` state at different rates. Before committing: `git fetch`, verify each
> dirty file with `git diff origin/main -- <path>`, and commit selectively by pathspec. Never
> `git add -A` blind, never force-push. The published skill copies are *derived artifacts*
> (regenerable via `publish.py` from `~/.claude` source), so a tangled local history is
> disposable — prefer realigning to `origin/main` and re-deriving over untangling parallel commits.

### Never switch branches in the working tree

Git assumes it owns the working tree. Dropbox does not know branches exist and re-syncs file
contents on its own schedule, so a `checkout` can be silently undone seconds after it reports
success. Observed 2026-07-28: `git checkout main` succeeded and `git status` reported a clean
tree; by the next command the working tree held the *other branch's* file contents while HEAD
still said `main`, and `git status` showed twelve modified files. A `git add` + `commit` there
would have put an entire feature branch onto `main` as one commit.

`git status` can lie in the direction of a clean tree, which is the direction that gets you to
commit. Treat a clean-tree report immediately after a checkout as unverified.

**To put a commit on a branch you are not standing on, never check it out — build the commit
from the object database, which Dropbox does not touch:**

```bash
S=/tmp/scratch   # anywhere outside the repo
git cat-file -p main:path/to/file > $S/orig        # read the target branch's blob
#   ... transform $S/orig into $S/new ...
NEWBLOB=$(git hash-object -w $S/new)
export GIT_INDEX_FILE=$S/tmpidx                    # temp index; never touches the real one
git read-tree main
git update-index --cacheinfo 100644,$NEWBLOB,path/to/file
TREE=$(git write-tree)
COMMIT=$(git commit-tree $TREE -p main -F $S/msg.txt)
git diff --stat main $COMMIT                       # verify BEFORE moving the ref
git update-ref refs/heads/main $COMMIT             # safe: main is not checked out
git push origin main
```

Verify with `git diff --stat main $COMMIT` before `update-ref`. If it lists a file you did not
intend to touch, the tree is wrong — discard the commit object and start over; nothing has moved
yet.

Two related habits: confirm a branch is fully pushed (`git rev-parse <branch>` equals
`git rev-parse origin/<branch>`) before any `checkout -f`, so a forced tree reset cannot lose
work. And prefer a byte-count or substitution-count check over eyeballing a diff — the tell that
caught the 2026-07-28 near-miss was a transform script reporting zero replacements on a file that
provably contained six, because it had read the wrong branch's copy.

## Publish Pipeline

`scripts/publish.py` syncs from the maintainer's `~/.claude/skills/` and `~/.claude/agents/`:

1. Copies skills listed in `SKILL_MAP` — source name → published name:
   - `polk-memo` → `law-memo`
   - `polk-document` → `law-document`
   - `polk-email-style` → `law-email-style`
   - All others keep their names (`law-mcq-generator`, `law-essay-generator`, `lecture-slide-reviewer`, `docx-comment-summary`, `rex`, `eddie`)
2. Copies agents listed in `AGENT_MAP` into `agents/<name>/` (16 agents, names unchanged)
3. `EXCLUDED_SKILLS` safety check blocks publication of `send-to-email`, `polk-slides`, `class-prep`, `project-folder-setup`, `polk-zotero` (Polk-personalized), and `md-to-pdf` (bundles licensed fonts)
4. Applies ordered regex scrub rules to skills AND agents (name, title, email → placeholders)
5. `SKIP_DIRS` excludes `plans/`, `specs/`, `_archive/`, `__pycache__/` (internal working artifacts)
6. `SKIP_FILE_PATTERNS` excludes `*.v1.md` versioned snapshots, backup cruft (`*.bak`/`*.bak2`/`*.backup`/`*.orig`/trailing `~`), and internal `NOTES-*.md` working notes
7. `SKIP_FILES` excludes `design.md`, `.DS_Store`
8. Validates skills against agentskills spec; validates agent frontmatter (name + description required)
9. Runs post-scrub verification on skills + agents — **verification strings are auto-derived from `SCRUB_RULES`** via `derive_private_strings()`, so they can't drift from the scrub patterns
10. Flags sync-drift — compares each published synced-skill file against what scrubbing its current source would produce; warns when in-repo hand edits would be overwritten
11. Warns about unfilled placeholders (`OWNER/REPO_NAME`, `YOUR_WEBHOOK_URL`) anywhere in the published tree (recursive)

**Privacy defenses (layered):**
- Text regex (SCRUB_RULES) — applied to `TEXT_EXTENSIONS` (`.md`, `.py`, `.json`, `.template`, etc.). Note `.template` is in the set: `NAMES.md.template` once shipped unscrubbed because `.template` wasn't recognized as text.
- docx metadata — `dc:creator`, `cp:lastModifiedBy`, and others cleared; `dcterms:created`/`dcterms:modified` normalized to `2000-01-01T00:00:00Z`
- docx body XML — `scrub_text` applied to `word/*.xml` and `customXml/*.xml` (body content, headers, footers, comments, footnotes) so identifiers in document text don't slip past the metadata-only scrub
- Pre-flight tests (`test_publish.py`) — run before every publish; fail-closed
- Post-scrub verification — auto-derived private-string set checked against text files, docx property XML, **and the raw bytes of any non-text/non-docx file** (closes the silent-leak path where an unrecognized extension was copied verbatim *and* skipped by verification)
- Sync-drift detection — catches hand edits that would be silently overwritten

> **⚠ The layers above protect the maintainer's identity automatically and third-party names only by hand.** `SCRUB_RULES` is comprehensive for one person and runs on every publish. Every other real person depends on someone remembering to add them to `publish-private-scrub.json`. Nothing detects the omission: post-scrub verification checks strings *derived from the scrub rules*, so a name nobody added is a name nobody checks. It verifies that known secrets stayed out; it cannot tell you an unknown one got in.
>
> This is not theoretical. On 2026-07-28 a routine read of `eddie/lessons.md` found eight unregistered third-party names in published output across 17 commits — including three students, one paired with their transcript characteristics as a calibration's worked example. They had published on every run since 2026-05-11 and the history required a `filter-repo` rewrite. **Whenever you add a real person's name to any source file — a calibration, a fixture, a worked example, a commit message — add a scrub rule and an anchor in the same edit.** Then check the published tree, not just the source.
>
> **Files outside the pipeline get no scrub at all.** `zz_docs/`, plan documents, and anything committed directly to the repo never pass through `publish.py`. The same 2026-07-28 review found a plan doc that had published two real-name→replacement pairs verbatim, explaining the fixture-naming convention. That is worse than leaking either name alone: a published mapping reverses the scrub for every file those replacements appear in. **Never write a real-name→replacement pair into any committed file.**

**Scrub rule ordering matters.** Specific patterns must come before catch-all patterns (e.g., compound "Polk Wagner" contexts before the standalone catch-all). See `SCRUB_RULES` in publish.py.

**Private scrub rules (third-party names).** Source skills/fixtures (notably the eddie ecosystem and its test fixtures) cite real colleagues and academics. Their name→fictional mappings must sanitize the *published* copy but must not appear in `publish.py` itself (it's public). So they load at runtime from `~/.claude/publish-private-scrub.json` (outside the repo; schema `{"rules": [[pattern, repl], ...], "anchors": [str]}`) and append after the static `SCRUB_RULES`. The maintainer's daily-use source keeps the real names (the affiliation web-verify tests depend on them). If the file is absent, `publish.py` prints a prominent warning and runs only the static (Polk-identity) scrub. The file is synced across machines via claude-sync (single-file pair) and backed up only to the *private* claude-sync repo.

## .gitignore: What's Local but Not Published

Several directories exist locally (as source skills or private skills) but are gitignored:

- `polk-memo/`, `polk-document/`, `polk-email-style/` — source versions of synced skills
- `send-to-email/`, `ip-problems/`, `class-prep-skill/`, `polk-zotero/` — private skills, not published (`polk-zotero` hardcodes Polk's Zotero userID and personal collection keys)
- `**/design.md` — design docs within skill directories
- Dropbox "conflicted copy" files (e.g., `README (Polk Wagner's conflicted copy ...).md`, `publish (... conflicted copy ...).py`) — artifacts of two-machine sync; safe to delete once reviewed

## Helper Scripts

- **`law-mcq-generator/validate_mcq.py`** — Post-generation validation for MCQ exams. Checks structural integrity, answer distribution, narrative coherence, and summary accuracy across exam and answer key .docx files. Requires `python-docx`.
- **`docx-comment-summary/scripts/extract_comments.py`** — Parses Word XML directly (stdlib `zipfile` + `ElementTree`, no pip deps) to extract comments with author, timestamp, anchored text, and replies.

## Eddie Fixture Regression Harness

Eddie is an LLM document-reviewer, so it's tested as a black box, not with assertions. `eddie/tests/` ships as published content (it's in source `~/.claude/skills/eddie/`, so it survives `copy_tree`):

- `tests/fixtures/*.md` — input documents, each engineered to provoke specific catches (personnel drift, misattributed affiliations, fabricated citations, a clean control).
- `tests/expected.md` — the validation reference (kept OUT of `fixtures/` so review agents reading the input directory cannot find the answer key): the P1/P2 findings each fixture *should* produce. Exact wording varies; check category and priority.
- `tests/NAMES.md` — the test name registry (auto-discovered by the orchestrator's tree walk). `tests/lessons.md` — test calibrations, passed via the `lessons=` invocation arg so they don't touch the real user-global lessons file.
- `templates/NAMES.md.template` — scaffolding the skill offers when a project has no name registry.

To validate after editing eddie: run each fixture with the command above, diff the report against `expected.md`. Fewer catches than expected → the spec regressed. More catches (false positives) → second-eyes/calibration regressed. Because eddie is **synced**, edit fixtures and calibrations in `~/.claude/skills/eddie/`, not in-repo.

`lessons.md` calibrations are user-global at `~/.claude/skills/eddie/lessons.md`; the repo's `eddie/lessons.md` is the published reference copy.

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
- **WeasyPrint**: Used by md-to-pdf, which is private and excluded from publish (see `EXCLUDED_SKILLS` in `scripts/publish.py`) — it bundles licensed ITC Stone Serif fonts that can't be redistributed
- **docx-comment-summary**: stdlib only (no pip dependencies) — parses .docx XML directly

## When Editing Skills

- Respect the two-tier model: synced skills are edited in `~/.claude/skills/`, repo-maintained skills are edited in-place
- After publishing, review the git diff carefully — scrub rule changes can have unintended cascading effects
- Test dual-environment path resolution when adding asset references
- Maintain the YAML frontmatter `description` field with accurate trigger phrases
- MCQ and essay skills use course presets; add new presets for additional courses
