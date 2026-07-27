# Rex + Eddie: Opus 5 Recalibration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retune the `rex` and `eddie` skills and their agents for Opus 5 / Sonnet 5 behavior — restore reviewer recall lost to literal severity-filtering, cap subagent fan-out, calibrate report length, and retier agent model assignments.

**Architecture:** Three independent change sets against prose and YAML frontmatter. (1) Rex gains an explicit find-then-filter split so the severity bar is applied after the search rather than during it. (2) Eddie's Agent 2 stops self-filtering and hands its clearance rules to `eddie-second-eyes`, which already exists as the dedicated filter stage. (3) Six agents change model tier: two off Haiku 4.5, three off Opus onto Sonnet 5, plus one optional out-of-scope agent.

**Tech Stack:** Markdown skill files with YAML frontmatter; `scripts/publish.py` sync pipeline; eddie's black-box fixture harness (`~/.claude/skills/eddie/tests/`).

**Revision note:** This is v2. A Rex review of v1 found two blockers and four majors, all in the verification layer. v2 changes: a new fixture actually exercising the Agent 2 change (v1 used `clean.md`, which cannot); named-expectation gating instead of count gating (v1 treated non-deterministic runs as deterministic); model changes reordered ahead of prose changes for clean attribution; a corrected Rex asymmetry sentence; pre-flight gates on alias resolution and `NAMES.md` discovery; a file snapshot before any edit; and a planted-defect target for the Rex A/B.

## ⚠️ Discovered during execution: Eddie's factual pipeline cannot run

**This is pre-existing, unrelated to this change set, and already published. It is the most consequential thing this work surfaced.**

`factual-pipeline-orchestrator` is Eddie's only hard-required agent. Its entire job is to spawn eight sub-agents across four stages (dual extraction → merge and verify → coverage audit → adversarial re-verify). **It cannot dispatch any of them.**

Diagnosis, in order:

1. Its frontmatter declares `tools: Read, Grep, Glob, WebSearch, WebFetch, Bash` — no dispatch tool. No agent in `~/.claude/agents/` declares one.
2. That looked like a one-line fix. It is not. A probe granting **both** `Task` and `Agent` in the frontmatter produced no change: the agent still reported only `Read, WebSearch, WebFetch, Bash`. `Grep` and `Glob` were silently dropped as well, despite being declared.
3. **Subagents cannot dispatch subagents in this harness, regardless of frontmatter.** The nested-orchestrator architecture cannot execute in Claude Code as designed.

**Why it matters more than a broken feature.** The orchestrator that ran during this work refused to improvise, stating: *"Fabricating subagent output — or quietly substituting my own read of the document for what four named specialist agents were supposed to produce — is exactly the failure mode you said you're testing for."* It behaved that way only because the dispatch prompt explicitly demanded that dispatch failures be reported. An ordinary run has a cheaper path available: read the document, emit plausible P1/P2 entries with confidence fields, and return them. The surrounding report would then claim four stages ran when one agent read the file once. Which of those has been happening in past runs is unknown from here.

**What still works.** Everything that does not require nesting: Agent 2 (inline to Eddie), `voice-style-checker`, `eddie-consistency-checker`, `eddie-second-eyes`, and `fix-verifier` are all direct dispatches from Eddie's main session. Checkpoint B is therefore fully valid; only the factual pipeline is affected.

**The fix is architectural** — flatten the design so Eddie's main session dispatches the eight pipeline agents directly and performs the stage sequencing itself. That is a redesign of Eddie's core with its own testing needs, deliberately **out of scope here**. Track it separately.

**Consequence inside this plan:** Task 6 was reverted. Its rationale was "sequencer, not a reviewer" — false while nesting is impossible, since whatever the orchestrator does today is improvised review, which warrants the stronger model. Revisit the retier once the pipeline genuinely sequences.

---

## Global Constraints

- **Both skills are SYNCED.** Source of truth is `~/.claude/skills/<name>/` and `~/.claude/agents/<name>/`. Never edit `rex/`, `eddie/`, or `agents/` inside the repo — `publish.py` overwrites them and its sync-drift detector will warn. Every file edit in this plan targets a `~/.claude/...` path.
- **`~/.claude` changes need no manual commit.** `claude-sync` mirrors `~/.claude/skills/` and `~/.claude/agents/` and self-commits daily. The git commits in this plan are of the *derived* repo artifacts produced by `publish.py`, plus this plan file. Because that commit is only daily, Task 2's snapshot is the actual intra-day revert point — not git.
- **Dropbox-synced repo.** Before any commit: `git fetch`, then verify each dirty file with `git diff origin/main -- <path>`. Never `git add -A`. Commit selectively by pathspec. Never force-push.
- **Never push without an explicit ask.** Committing is in scope; pushing is not — stop and ask.
- **Commit message trailer** (every commit): `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
- **Do not change `SKILL_MAP` or `AGENT_MAP`** in `scripts/publish.py`. No skills or agents are added or removed. The new fixture in Task 3 lands inside an already-mapped skill directory and needs no pipeline change.
- **Public fixtures are sanitized.** Any new fixture uses fictional names only. `expected.md` states this convention explicitly for the affiliations fixture; follow it.
- **Preserve YAML frontmatter shape.** Only the `model:` value changes in Tasks 5–6. Do not add, reorder, or reformat other keys.
- **`effort:` in agent frontmatter is OUT OF SCOPE.** Whether Claude Code agent frontmatter accepts an `effort:` key is unverified. Do not add one.

## How this plan gates pass/fail

Eddie and Rex are LLM reviewers. Two identical runs produce different finding counts. The verification design therefore separates two kinds of signal, and **only the first kind can revert a change**:

- **Gating signals — named expectations.** Specific catches enumerated in `~/.claude/skills/eddie/tests/fixtures/expected.md`, and the specific planted defects in Task 4's Rex target. These are near-deterministic. A gating signal that fails is grounds to revert.
- **Advisory signals — counts and totals.** Finding totals, tier distributions, report length. These drift run to run. Record them, look for large swings, but **never revert on a count delta alone.** A count swing is a prompt to look at the named signals, not a verdict.

If you want counts to carry statistical weight, you need three baseline runs per fixture — roughly doubling the plan's cost. That is a deliberate decision, not a default. This plan assumes one run each and gates accordingly.

## Pre-existing repo state

`git status` shows `M eddie/lessons.md` at plan time — a modification predating this work. Task 1 resolves it. Do not fold it into a commit from this plan.

## Task order and why

Model changes are one-line and trivially revertable. The prose change is complex and multi-hunk. Running models first with a regression checkpoint between the two change sets is what makes failure attribution possible — v1 landed all three change sets before the first eddie run and could not tell them apart.

```
1  preflight            5  models: 4 agents      9  rex: cap + length + A/B
2  snapshot + gates     6  models: orchestrator  10 eddie: Agent 2 -> second-eyes
3  new fixture          7  CHECKPOINT A          11 CHECKPOINT B
4  baselines            8  rex: recall fix       12 publish + commit
                                                 13 optional (out of scope)
```

## File map

| File | Task | Change |
|---|---|---|
| `~/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md` | 3 | **New** — the fixture that exercises Agent 2 |
| `~/.claude/skills/eddie/tests/fixtures/expected.md` | 3 | New expectations section |
| `~/.claude/agents/voice-style-checker/voice-style-checker.md` | 5 | `haiku` → `sonnet` |
| `~/.claude/agents/eddie-consistency-checker/eddie-consistency-checker.md` | 5 | `haiku` → `sonnet` |
| `~/.claude/agents/quote-extractor/quote-extractor.md` | 5 | `opus` → `sonnet` |
| `~/.claude/agents/coverage-auditor/coverage-auditor.md` | 5 | `opus` → `sonnet` |
| `~/.claude/agents/factual-pipeline-orchestrator/factual-pipeline-orchestrator.md` | 6 | `opus` → `sonnet` (isolated) |
| `~/.claude/skills/rex/SKILL.md` | 8, 9 | Find-then-filter split, delegation cap, length calibration |
| `~/.claude/skills/eddie/SKILL.md` | 10 | Agent 2 discipline block replaced |
| `~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md` | 10 | Receives the moved clearance rules |
| `~/.claude/agents/mcq-structural-reviewer/mcq-structural-reviewer.md` | 13 | OPTIONAL, out of scope |
| repo `zz_docs/plans/2026-07-27-rex-eddie-opus5-revisions.md` | 1, 12 | This file |

Substitute your session scratchpad directory for `<scratchpad>` throughout.

---

### Task 1: Clean the working tree and decide the plan-file disposition

**Files:**
- Inspect: `eddie/lessons.md` (repo)
- Modify: `.gitignore` (repo) — conditional, see Step 3

- [ ] **Step 1: Fetch and inspect the pre-existing dirty file**

```bash
cd "/Users/polk/Penn Law Dropbox/Polk Wagner/code/skills"
git fetch
git diff origin/main -- eddie/lessons.md
```

Then compare the working copy against the `~/.claude` source, ignoring the scrub substitution:

```bash
diff <(sed 's/\[Your Name\]/Polk/g' eddie/lessons.md) /Users/polk/.claude/skills/eddie/lessons.md
```

**Note the scrub.** Published output is *never* byte-identical to its source — replacing the maintainer's name with `[Your Name]` is the whole point of the pipeline. A raw `diff` against the source will always show differences and tells you nothing. Normalize the scrub first, as above, or the test is meaningless. (v1 of this plan got this wrong and would have escalated a healthy file.)

Four possible outcomes:
- **Empty diff vs `origin/main`** — byte-identical to upstream; Dropbox produced a phantom modification. Run `git checkout -- eddie/lessons.md`.
- **Differs from `origin/main`; scrub-normalized diff vs source is empty** — legitimate uncommitted `publish.py` output. Leave it; **Task 12's** publish run regenerates it and commits it there. *(This is the observed state as of 2026-07-27: 88 lines, 7 differing, all `Polk` → `[Your Name]`.)*
- **Scrub-normalized diff shows the source is a superset** — the source gained calibrations since the last publish. Also fine; Task 12 picks them up.
- **Scrub-normalized diff shows content in the repo copy that is absent from the source** — a genuine in-repo hand edit of a synced file, which `publish.py` will destroy. Stop and ask.

- [ ] **Step 2: Confirm the tree is otherwise clean**

```bash
git status --short
```

Expected: empty, or only `M eddie/lessons.md` under outcome 2.

- [ ] **Step 3: Decide whether this plan ships publicly**

This repo is public. `zz_docs/` is not gitignored and `publish.py` does not touch it, so committing this plan publishes it verbatim, including the maintainer's name. That name is already present in the repo's `CLAUDE.md` and `README.md`, so this is not a new disclosure, and the standing convention is that plan documents stay in the repo as a record of design decisions.

**Default: commit it.** No `.gitignore` change.

Alternative, if internal working artifacts should stay out of the public tree (`docs/` is already ignored for this reason):

```bash
printf '\n# Internal working artifacts (plans, notes) — not part of the public release\nzz_docs/\n' >> .gitignore
```

This is Polk's call. Ask if unsure; do not silently pick.

- [ ] **Step 4: Commit only if `.gitignore` changed**

```bash
git add .gitignore
git commit -m "chore: keep zz_docs internal working artifacts out of the public tree

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Snapshot the source files and clear two pre-flight gates

**Why this is a task:** every edit in this plan targets `~/.claude`, whose git mirror self-commits only once a day. An intra-day mistake may have no committed baseline. Two additional assumptions are load-bearing and unverified — that `sonnet`/`opus` resolve to the current generation, and that the fixture harness finds the test `NAMES.md` when invoked by absolute path. Both are cheap to check and expensive to get wrong: a `NAMES.md` discovery failure produces exactly the symptom that Task 7 reads as "the model retier cost recall."

**Files:**
- Create: `<scratchpad>/snapshot/` (copies of every file this plan edits)

**Interfaces:**
- Produces: `<scratchpad>/snapshot/` — the revert source referenced by every rollback step in this plan.

- [ ] **Step 1: Snapshot every file this plan will touch**

```bash
mkdir -p <scratchpad>/snapshot
cp ~/.claude/skills/rex/SKILL.md                                              <scratchpad>/snapshot/rex-SKILL.md
cp ~/.claude/skills/eddie/SKILL.md                                            <scratchpad>/snapshot/eddie-SKILL.md
cp ~/.claude/skills/eddie/tests/fixtures/expected.md                          <scratchpad>/snapshot/expected.md
cp ~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md                     <scratchpad>/snapshot/eddie-second-eyes.md
cp ~/.claude/agents/voice-style-checker/voice-style-checker.md                 <scratchpad>/snapshot/voice-style-checker.md
cp ~/.claude/agents/eddie-consistency-checker/eddie-consistency-checker.md     <scratchpad>/snapshot/eddie-consistency-checker.md
cp ~/.claude/agents/quote-extractor/quote-extractor.md                         <scratchpad>/snapshot/quote-extractor.md
cp ~/.claude/agents/coverage-auditor/coverage-auditor.md                       <scratchpad>/snapshot/coverage-auditor.md
cp ~/.claude/agents/factual-pipeline-orchestrator/factual-pipeline-orchestrator.md <scratchpad>/snapshot/factual-pipeline-orchestrator.md
ls -1 <scratchpad>/snapshot/
```

Expected: nine files. **Every revert instruction in this plan restores from here** — `cp <scratchpad>/snapshot/<file> <original path>`.

- [ ] **Step 2: GATE — verify model alias resolution**

The entire retier rationale (Tasks 5–6) rests on `model: sonnet` resolving to Sonnet 5 and `model: opus` to Opus 5. If those aliases pin to an older generation, moving `coverage-auditor` and `quote-extractor` down is a straight capability cut with no compensating argument.

Confirm what generation the aliases resolve to in this Claude Code version — via `/model`, the Claude Code documentation, or by dispatching any existing `model: sonnet` agent and asking it to state its own model ID.

| Result | Action |
|---|---|
| `sonnet` → Sonnet 5 **and** `opus` → Opus 5 | Proceed. |
| Either resolves to an older generation | **Stop.** Tasks 5–6 need re-deriving from the actual generation gap. Tasks 8–10 (prose) are unaffected and may proceed alone. |
| Cannot determine | **Stop and ask.** Do not guess — this is the assumption the whole retier rests on. |

Record the answer in this plan file before continuing.

- [ ] **Step 3: GATE — verify `NAMES.md` discovery under absolute-path invocation**

`expected.md` documents the fixture command as repo-relative and says the test registry is "auto-discovered by the orchestrator's tree walk." This plan invokes with absolute `~/.claude/...` paths. Confirm the walk still lands on the test registry.

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/personnel-drift.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/baseline-eddie-personnel-drift.md`. **This is also the Task 4 Step 2 baseline — do not re-run it there.**

Inspect the report for which registry it used:

| Signal | Meaning |
|---|---|
| Report cites `~/.claude/skills/eddie/tests/NAMES.md`, and "Mark Calloway" / "Kathy Lambert" are caught as Stage 1c registry hits | **Pass.** Absolute-path invocation works. Use it throughout. |
| Report cites the user-global `~/.claude/NAMES.md`, or no registry, or the two names are not caught as registry hits | **Fail.** Switch every fixture command in this plan to the repo-relative form from `expected.md` (`/eddie skills/eddie/tests/fixtures/<name>.md ...`, run from `~/code/`), re-run this step, and confirm before proceeding. |

A silent failure here invalidates every personnel expectation downstream and looks identical to a retier regression. Do not skip.

- [ ] **Step 4: Commit nothing**

Snapshots and baselines live in the scratchpad.

---

### Task 3: Author the fixture that actually exercises Agent 2

**Why this exists:** Task 10 changes Agent 2 — adversarial reading, structural discipline, institutional sensitivity — and moves three clearance rules about *exposure risk* and *absence-as-implication* into `eddie-second-eyes`. No existing fixture covers any of that. `clean.md` in particular cannot: it is a 12-line faculty email with no exposure-risk surface, and at well under 200 words it falls below the threshold where Eddie's SKILL.md permits a single-pass review with no agent dispatch at all. Verifying Task 10 against `clean.md` would test nothing while reporting success.

The new fixture is over 500 words specifically so Eddie dispatches agents rather than taking the single-pass path.

**Files:**
- Create: `~/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md`
- Modify: `~/.claude/skills/eddie/tests/fixtures/expected.md` (new section, inserted before `## clean.md`)

**Interfaces:**
- Produces: a fixture with three planted items — one that must be caught, two that must be cleared — consumed as gating signals by Tasks 4, 7, and 11.

- [ ] **Step 1: Create the fixture**

Write exactly this to `~/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md`.

**Every name here is invented, and the memo's author and contact are added to the source test registry** (`~/.claude/skills/eddie/tests/NAMES.md`) by Step 1b below, so they pass Eddie's Stage 1c check cleanly instead of drawing unknown-person flags.

**Two naming traps, both hit during execution — read before touching names in any eddie fixture:**

1. *v1 used the maintainer's real name and a real colleague's*, on the theory that `publish.py`'s private scrub covers both. It does, and the existing `clean.md` relies on exactly that. Changed anyway: this fixture's planted flaw is a confidential hiring steer, so an absent `publish-private-scrub.json` would publish it as the maintainer disclosing a private personnel decision. Invented names remove the dependency.
2. *The obvious replacements were the scrub's own output.* The fictional names visible in the repo's fixtures and `expected.md` exist **nowhere in source** — they are what the private scrub generates from the real names it replaces. Adopting one as a source name yields two entries with the same name in the published registry, and worse, a document that pairs a generated name with the real one it stands for is a decoder ring: it reverses the scrub for every file that name appears in. **When choosing fixture names, read the source tree under `~/.claude/skills/eddie/`, never the published copy in the repo; check candidates against the replacement column of `~/.claude/publish-private-scrub.json`; and never write a real-name→replacement pair into any file that gets committed.**

- [ ] **Step 1b: Register the two principals**

Add to `~/.claude/skills/eddie/tests/NAMES.md` under the existing `## People` heading, matching the formatting of the entries already there. Leave the pre-existing entries and the known-fabrications table untouched — they are real people covered by the private scrub, and naming them here would pair a real name with its published replacement in a committed file (see the decoder-ring trap above).

- **Adaeze Fontaine-Whitlock** — Title: `Deputy Dean for Academic Affairs and Innovation`; Affiliation: `University of Pennsylvania Carey Law School`; Authoritative source: `test fixture (not a real URL)`; Notes: `Fictional. Memo author in institutional-sensitivity.md.`
- **Bertrand Oyelaran** — Title: `Practice Professor of Law`; Affiliation: `University of Pennsylvania Carey Law School`; Authoritative source: `test fixture (not a real URL)`; Notes: `Fictional. Contact in institutional-sensitivity.md.`

```markdown
# Memorandum

**To:** Faculty Appointments Committee
**From:** Adaeze Fontaine-Whitlock, Deputy Dean for Academic Affairs and Innovation
**Date:** March 12, 2026
**Re:** Spring appointments cycle — process, criteria, and timeline

## Background

The Appointments Committee has operated under the 2019 procedures memo since its adoption, with minor amendments in 2021 and again in 2023. Those procedures were themselves a response to the 2018 process review, which followed the restructuring of the entry-level hiring sequence, which in turn grew out of concerns first raised during the 2016 curriculum review. The committee has met annually to review its charge since then, and the charge has remained substantially unchanged across that entire period. Members joining the committee this cycle may not have encountered the earlier documents, so this history is offered for orientation.

For completeness, the 2019 memo itself superseded a 2014 practice note that the faculty never formally adopted. The committee's standing rules still cross-reference that note in two places. Nothing in the present cycle turns on those references, and no member has raised them in recent memory.

## This cycle

We received forty-one applications for two entry-level positions. The subcommittee met twice in October to produce the initial screen and forwarded eleven files for full committee review.

I've decided the committee will forward two names to the full faculty rather than the customary three. Between us, the Dean has already signaled he wants Rosalind Achebe-Farrar, so a third slot would be decorative, and I'd rather not put a candidate through a campus visit that cannot succeed.

## Workshop series

The workshop series supporting this cycle features four speakers: Tobias Klemm of Northfield College, Ingrid Sorensen of the Vasari Institute, Emmanuel Baptiste-Roux of Camden Polytechnic, and Yuki Ashworth-Nakamura of the Halloran Center. Each will present current work and meet with candidates informally afterward.

## Evaluation criteria

Candidates will be evaluated on scholarship, teaching, and service, weighted in that order.

Scholarship means published or forthcoming work in peer-reviewed or flagship venues. The committee has consistently treated a single placement in a top-tier venue as comparable to two in second-tier venues, though this has never been written down and members have occasionally disagreed about it in past cycles.

Teaching means demonstrated classroom performance, evidenced either by student evaluations from a prior appointment or by the job talk itself. Where a candidate has no teaching record, the committee will weight the job talk more heavily rather than treating the absence as disqualifying.

Service means institutional citizenship: committee work, mentoring, and professional contribution. As the clinical-appointments discussion above makes clear, this factor carries the least weight, and the committee has historically used it only to break ties. In practice this has meant that a candidate with an unusually strong record of professional contribution is occasionally advanced over one with a marginally stronger publication record, though the committee has never articulated a threshold for when that substitution is appropriate.

## Logistics

Files will be distributed through the committee's shared folder rather than by email, as we did last cycle. Members who need paper copies should tell Bertrand Oyelaran by March 18. Reading rooms are reserved for the week of March 23. Please do not remove files from the building or circulate them outside the committee.

## Timeline

Files circulate March 20. Committee discussion is April 3. Campus visits, if any, run the last two weeks of April. The recommendation goes to the full faculty at the May meeting.

Questions to me or to Bertrand Oyelaran, Practice Professor of Law.

Adaeze
```

- [ ] **Step 2: Add the expectations section**

In `~/.claude/skills/eddie/tests/fixtures/expected.md`, insert this section immediately before the line `## clean.md`:

```markdown
## institutional-sensitivity.md

**Test intent:** validate the Agent 2 / second-eyes split. Agent 2 surfaces findings without self-filtering; `eddie-second-eyes` applies the standing clearance rules. This fixture plants one finding that must survive and two that must be cleared. It is deliberately over 500 words so Eddie dispatches agents rather than taking the single-pass path.

**Must be caught (gating):**

- **P1 or P2 — institutional sensitivity** — "Between us, the Dean has already signaled he wants Rosalind Achebe-Farrar, so a third slot would be decorative" is a concrete exposure risk: it pre-decides an outcome, reveals a private steer, and would be damaging if forwarded or FOIAed. This must appear in the final report. If it does not, Agent 2 or second-eyes has over-corrected and the change is broken.
- **P2 or P3 — role/authority boundary** — "I've decided the committee will forward two names" asserts a decision that is the committee's to make. Expect a flag on the verb.
- **P3 — orphaned reference** — "As the clinical-appointments discussion above makes clear, this factor carries the least weight" refers to a discussion that does not exist: clinical appointments appear nowhere in the memo. *(v1 phrased this as "As discussed above…", which was too weak to gate on — the criteria section already states the three factors "weighted in that order," giving the reference a plausible antecedent. A reviewer could reasonably decline to flag it.)*

**Must be cleared, not suppressed upstream (gating):**

These two exist to prove the pipeline surfaces marginal findings and clears them *visibly*. Passing means either (a) they appear under "Considered but cleared" with the standing rule cited, or (b) they never appear at all. Failing means they appear as live findings in the final report.

- **Absence-as-implication** — all four workshop speakers are external. A speculative reviewer flags this as an unintended signal about internal faculty. The standing rule in `eddie-second-eyes` Sub-pass 1 says external speakers at internal workshops are routine; this clears.
- **Hypothetical inference** — "The subcommittee met twice in October" invites "a reader could infer the screen was rushed." No specific signal in the text supports that. The standing rule says hypothetical reader inferences with no grounding are speculation; this clears.

**Advisory (do not gate):**

- Structural discipline should fire somewhere on the Background section — four nested historical antecedents to explain an unchanged charge. Priority and phrasing will vary.
- "ensure" does not appear; voice/style findings here are incidental.
- The candidate ("Rosalind Achebe-Farrar") and the four workshop speakers are not in the test registry and may each draw an unknown-person flag at P2. That is expected noise orthogonal to this fixture's purpose, not a failure. The memo's author and contact ARE registered (Step 1b), so they should pass Stage 1c without flags.

**Diagnostic value:** if both "must be cleared" items appear as live findings, second-eyes is not applying the standing rules — check that Task 10 Step 3's renumbering (step 5 → 6) did not disturb Sub-pass 1. If the "must be caught" exposure risk is missing, Agent 2 is still self-filtering — check that Task 10 Step 1 applied.
```

- [ ] **Step 3: Verify both files**

```bash
wc -w ~/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md
grep -c "Achebe-Farrar" ~/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md
grep -n "## institutional-sensitivity.md" ~/.claude/skills/eddie/tests/fixtures/expected.md
grep -n "## clean.md" ~/.claude/skills/eddie/tests/fixtures/expected.md
```

Expected: word count **above 500** — measured at 578 as written, and the plan's copy of the fixture was expanded specifically to clear this bar. If your count comes in under 500, the fixture will likely take Eddie's single-pass path and test nothing; pad the Background section until it clears. `Achebe-Farrar` appears **once**. The new section's line number in `expected.md` is *lower* than `## clean.md`'s.

- [ ] **Step 4: No commit yet** — published and committed in Task 12.

---

### Task 4: Capture behavioral baselines

**Why this is a task and not a note:** these are black-box LLM reviewers. There is no assertion to write; the only test is a before/after comparison, and the "before" half is unrecoverable once the prompts change.

**Files:**
- Create: `<scratchpad>/baseline-eddie-institutional.md`
- Create: `<scratchpad>/baseline-eddie-clean.md`
- Create: `<scratchpad>/rex-target.py`
- Create: `<scratchpad>/baseline-rex.md`

**Interfaces:**
- Consumes: `<scratchpad>/baseline-eddie-personnel-drift.md` from Task 2 Step 3 — already captured.
- Produces: four baseline artifacts consumed by Tasks 7, 9, and 11.

- [ ] **Step 1: Baseline the new Agent 2 fixture**

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/baseline-eddie-institutional.md`. At the top of that file record, for each of the five gating items in `expected.md` § institutional-sensitivity.md: caught / cleared / absent, and at what priority.

Expect the two "must be cleared" items to appear as **live findings or not at all** in this baseline — Agent 2 currently self-filters, so they are being suppressed upstream rather than cleared visibly. That is the pre-change state and is exactly what Task 11 measures against.

- [ ] **Step 2: Personnel-drift baseline — already captured**

Task 2 Step 3 produced `<scratchpad>/baseline-eddie-personnel-drift.md`. Confirm it exists and records whether each of the three catches in `expected.md` § personnel-drift.md appeared, and at what priority. Do not re-run.

- [ ] **Step 3: Baseline the false-positive control**

`clean.md` does **not** test the Agent 2 change (see Task 3). It tests that the voice/style and registry paths still behave — which is what the Task 5 `voice-style-checker` retier touches.

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/clean.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/baseline-eddie-clean.md`. Record: whether any P1/P2 appeared (expected: none), whether the quoted-policy "ensure" was cleared with the test lesson cited, and whether "Maya Calloway" / "Diane Holloway" passed Stage 1c without flags.

- [ ] **Step 4: Build the Rex target with planted defects**

Rex has no fixture harness, and a well-maintained real file makes a poor A/B — a genuine recall improvement shows as a zero delta when there is nothing to find. Write exactly this to `<scratchpad>/rex-target.py`:

```python
"""Config and hook dispatch for the publish pipeline."""
import json
import os
import subprocess

CACHE = {}


def load_config(path):
    with open(path) as f:
        return json.load(f)


def run_hook(name, payload):
    cmd = "python3 hooks/" + name + " '" + json.dumps(payload) + "'"
    return subprocess.run(cmd, shell=True, capture_output=True).stdout


def cache_result(key, value):
    CACHE[key] = value
    return value


def mean_size(items):
    total = 0
    for item in items:
        total += item["size"]
    return total / len(items)
```

Four planted items, each with a defined expected outcome:

| # | Defect | Expected |
|---|---|---|
| **D1** | `run_hook` builds a shell string by concatenation and runs it with `shell=True` — command injection via `name` or `payload` | **Gating.** Must be reported at Blocker or Major, before and after. |
| **D2** | `mean_size` divides by `len(items)` with no empty-list guard — `ZeroDivisionError` | **Gating after the change.** The borderline finding a conservative filter drops. |
| **D3** | `CACHE` is an unbounded module-level dict — grows without eviction | **Gating after the change.** Same class as D2: real, small, easily suppressed. |
| **D4** | `os` is imported and never used | **Negative control.** Must **not** be reported, before or after. Rex does not comment on style nits; reporting it means the change over-corrected into padding. |

- [ ] **Step 5: Baseline Rex against the planted target**

```
/rex review <scratchpad>/rex-target.py
```

Save to `<scratchpad>/baseline-rex.md`. Record which of D1–D4 were reported and at what tier, plus advisory notes: subagent count and review word count.

The expected baseline shape is D1 reported, D4 not reported, and **at least one of D2/D3 missing** — that gap is the recall the filter is suppressing and is what Task 9 should close. If the baseline already reports all of D1–D3, say so: the Rex change may be unnecessary, and that is a finding worth recording rather than overriding.

> **MEASURED 2026-07-27 — the baseline came back 4 of 4, and this A/B is therefore uninformative.** A fresh-context Rex on Opus 5 reported D1 (Blocker), D2 (Major), D3 (Major), *and* D4 (Minor), with no subagents, on the 28-line file. Two conclusions, both recorded rather than worked around:
>
> 1. **No headroom.** D2 and D3 were supposed to be the suppressed-by-the-filter findings. They weren't suppressed, so Task 9's A/B cannot show improvement — a zero delta here means the target was too easy, not that the change failed. The recall problem this plan addresses only bites on artifacts large or ambiguous enough that the filter has real work to do; a 28-line file with four obvious defects isn't one.
> 2. **D4 was a bad negative control.** An unused import is a legitimate lint-level defect, not a "style preference" in the tabs-vs-spaces sense Rex's skill actually disclaims. Reporting it at Minor is defensible behavior, so D4 cannot detect over-correction either.
>
> **Consequence for Task 9 Step 4:** treat the whole planted-defect table as advisory. The gating check reduces to D1 still being reported at Blocker or Major — i.e. the change didn't break Rex's core function. Verification of Tasks 8–9 rests on prose review, which the plan should say plainly rather than implying evidence it doesn't have. Designing a harder target is a separate exercise, not a blocker for this change set.

- [ ] **Step 6: Confirm all baselines exist**

```bash
wc -l <scratchpad>/baseline-eddie-institutional.md \
      <scratchpad>/baseline-eddie-personnel-drift.md \
      <scratchpad>/baseline-eddie-clean.md \
      <scratchpad>/baseline-rex.md
```

Expected: four non-zero line counts. Re-run any that failed — proceeding without a baseline makes the corresponding checkpoint unverifiable.

- [ ] **Step 7: Commit nothing.**

---

### Task 5: Retier four judgment agents onto Sonnet 5

**Gate:** Task 2 Step 2 must have passed. Do not execute otherwise.

**Rationale:** the current tiering predates Sonnet 5 and assumes Haiku 4.5 is the current small model. Sonnet 5 is now near-Opus on analytical work; Haiku 4.5 is two generations old with no successor, and two Haiku agents are doing subtle judgment work (AI-tell detection, cross-section numeric agreement) a small model will miss. Two Opus agents are doing bounded extraction Sonnet 5 handles.

Unchanged, deliberately: `claim-merge-agent` (mechanical deduplication, stays Haiku); `factual-reviewer` and `institutional-claim-extractor` (recall floor for the whole pipeline, stay Opus); `eddie-second-eyes`, `fix-verifier`, `adversarial-reverifier` (calibration judgment and independent verification, stay Opus).

**Files:**
- Modify: frontmatter `model:` in `voice-style-checker`, `eddie-consistency-checker`, `quote-extractor`, `coverage-auditor`

- [ ] **Step 1: Record current state**

```bash
grep -H "^model:" ~/.claude/agents/{voice-style-checker,eddie-consistency-checker,quote-extractor,coverage-auditor}/*.md
```

Expected: `voice-style-checker` → `haiku`, `eddie-consistency-checker` → `haiku`, `quote-extractor` → `opus`, `coverage-auditor` → `opus`. Any deviation means someone changed these since the plan was written — stop and re-derive.

- [ ] **Step 2: Apply the four changes**

Edit only the `model:` line in each file.

| File | From | To |
|---|---|---|
| `voice-style-checker/voice-style-checker.md` | `model: haiku` | `model: sonnet` |
| `eddie-consistency-checker/eddie-consistency-checker.md` | `model: haiku` | `model: sonnet` |
| `quote-extractor/quote-extractor.md` | `model: opus` | `model: sonnet` |
| `coverage-auditor/coverage-auditor.md` | `model: opus` | `model: sonnet` |

- [ ] **Step 3: Verify the distribution**

```bash
grep -H "^model:" ~/.claude/agents/*/*.md | sed 's|.*/||' | sort
grep -L "^model:" ~/.claude/agents/*/*.md
```

Expected after this task, before Task 6 — 19 agents total:

- **`sonnet` (11):** `adversarial-balance-validator`, `construct-alignment-tracer`, `coverage-auditor`, `disagreement-analyzer`, `double-read-pass`, `eddie-consistency-checker`, `emphasis-map-builder`, `fact-verifier`, `quote-extractor`, `slide-reading-alignment`, `voice-style-checker`
- **`haiku` (2):** `claim-merge-agent`, `mcq-structural-reviewer`
- **`opus` (6):** `adversarial-reverifier`, `eddie-second-eyes`, `factual-pipeline-orchestrator`, `factual-reviewer`, `fix-verifier`, `institutional-claim-extractor`

11 + 2 + 6 = 19. The second command must return no output — every agent still has a `model:` field.

- [ ] **Step 4: Revert path**

`cp <scratchpad>/snapshot/<agent-file> ~/.claude/agents/<name>/<name>.md` for any file needing rollback.

- [ ] **Step 5: No commit yet** — tested in Task 7, committed in Task 12.

---

### Task 6: Retier the factual pipeline orchestrator (isolated — highest risk) — **APPLIED, THEN REVERTED**

> **Outcome 2026-07-27: reverted; the orchestrator stays on `opus`.** Isolating this change in its own task is what made a clean revert possible, so the plan's structure did its job. The retier rationale — "sequencer, not a reviewer" — turned out to be false: the orchestrator cannot sequence at all (see the discovered-during-execution section above), so whatever it does today is improvised review, and review warrants the stronger model. Re-apply this task only after the pipeline is flattened and genuinely sequences.

**Gate:** Task 2 Step 2 must have passed.

**Why isolated:** `factual-pipeline-orchestrator` spawns eight sub-agents across four stages and passes structured data between them. Its own prompt says it is a "sequencer, not a reviewer," which is the argument for Sonnet — no editorial judgment, and it sits on the critical path where latency compounds. But orchestration failures show up as malformed handoffs rather than missing findings, and isolating this change means Task 7 can revert it without unwinding Task 5.

**Files:**
- Modify: `~/.claude/agents/factual-pipeline-orchestrator/factual-pipeline-orchestrator.md` (frontmatter `model:`)

- [ ] **Step 1: Apply the change**

`model: opus` → `model: sonnet`. Nothing else changes.

- [ ] **Step 2: Verify**

```bash
grep -H "^model:" ~/.claude/agents/factual-pipeline-orchestrator/*.md
```

Expected: `model: sonnet`. Distribution is now sonnet 12 / haiku 2 / opus 5 = 19.

- [ ] **Step 3: No commit yet** — tested immediately in Task 7.

---

### Task 7: CHECKPOINT A — regression after the model changes only — **PARTIALLY BLOCKED**

> **Outcome 2026-07-27.** Ran with the prose reverted, so attribution was clean. The gating signals could not be produced: they all depend on Stage 1c of the factual pipeline, which cannot execute (see the discovered-during-execution section above). The run is recorded as **UNVERIFIABLE for the pipeline path**, not as a pass.
>
> What the run did establish, and it is not nothing:
> - `voice-style-checker` on Sonnet 5 correctly found the fixture clean, flagged one sub-threshold echo, and explicitly declined to pad — *"I'm not inventing findings to pad it."*
> - `eddie-consistency-checker` on Sonnet 5 returned clean on all three axes with sound reasoning, and spontaneously noticed the planted personnel drift while correctly noting it fell outside its own rubric.
>
> Those two are half of Task 5's retier and they were genuinely exercised. `quote-extractor` and `coverage-auditor` are pipeline-internal and remain unexercised — they are dispatched only by the orchestrator, so they cannot be reached until the pipeline is flattened.

At this point the prose is untouched. Any regression here is attributable to Tasks 5–6 and nothing else.

**Files:**
- Create: `<scratchpad>/checkA-eddie-personnel-drift.md`, `<scratchpad>/checkA-eddie-clean.md`

- [ ] **Step 1: Re-run the pipeline fixture**

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/personnel-drift.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/checkA-eddie-personnel-drift.md`.

- [ ] **Step 2: Evaluate gating signals**

| Gating signal | Pass |
|---|---|
| "Mark Calloway" flagged P1, Stage 1c registry drift | present |
| "Kathy Lambert" flagged P1, Stage 1c known fabrication | present |
| "Quentin Reynolds-Maxwell" flagged P1 or P2 as unknown | present, not below P2 |
| Report structure | all sections present; no stage reports a handoff, parse, or "pipeline unavailable" failure |

Advisory only, do not gate: total finding count, tier distribution, run duration.

- [ ] **Step 3: Re-run the voice/style control**

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/clean.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/checkA-eddie-clean.md`.

| Gating signal | Pass |
|---|---|
| Quoted-policy "ensure" cleared with the test lesson cited | present in "Considered but cleared" |
| "Maya Calloway" / "Diane Holloway" | pass Stage 1c without flags |
| P1/P2 findings | none |

Advisory only: the P3 count. A single P3 delta is noise, not a `voice-style-checker` regression.

- [ ] **Step 4: Triage a failure to a specific task**

| Symptom | Cause | Action |
|---|---|---|
| Malformed report, missing stage, handoff failure | Task 6 — orchestration | `cp <scratchpad>/snapshot/factual-pipeline-orchestrator.md ~/.claude/agents/factual-pipeline-orchestrator/`, re-run Step 1, record the outcome |
| Named personnel catch missing, report otherwise well-formed | Task 6 first (single file), then Task 5 | Revert Task 6, re-run. If still failing, revert Task 5's four files |
| Quoted-"ensure" no longer cleared | Not a model issue — check `lessons.md` path resolution | Re-verify Task 2 Step 3's gate |

Record every revert in this file. A reverted change that goes undocumented gets silently re-attempted next quarter.

- [ ] **Step 5: No commit yet.**

---

### Task 8: Rex — separate finding from reporting

**The problem this fixes:** Opus 5 follows severity-filter instructions literally. The cost-asymmetry line and the no-padding line currently sit in the same pass as the search, so a candidate finding gets suppressed at the moment Rex notices it — before it is ever evaluated. Precision rises, recall falls, and nothing in the output shows the difference.

**Files:**
- Modify: `~/.claude/skills/rex/SKILL.md` — insert one paragraph after line 64; insert a new section after line 73; rewrite line 132

**Interfaces:**
- Produces: a section titled `## Find First, Filter Second`, referenced by name from line 132 and from Task 9's delegation bullet.

- [ ] **Step 1: Scope the asymmetry to tier assignment**

The v1 draft of this step *replaced* the asymmetry sentence and inverted its logic — it read as "a false Blocker is cheaper than any missed finding," which argues for escalating on suspicion and is the exact failure the surrounding section exists to prevent. **Leave the original sentence intact.** Add a scoping paragraph after it.

Find this paragraph (line 64, opening "Verify Before You Assert"):

```
Rex's confidence is earned, not performed. The fastest way to destroy a review is one confident "this will break" that doesn't — the author finds the false alarm, stops trusting Rex, and now every real finding gets the same skepticism as the wrong one. A false Blocker costs more than a missed Minor.
```

Leave it byte-for-byte unchanged and insert immediately after it, as a new paragraph:

```
That asymmetry governs the *tier*, not whether Rex speaks up. An issue he couldn't verify gets reported at a lower tier with the check handed over — never escalated to Blocker on suspicion, and never dropped for being uncertain. Silence is not the safe option; a wrong tier is recoverable, a finding the author never sees is not.
```

- [ ] **Step 2: Insert the find-then-filter section**

After line 73 (the paragraph ending `...a hypothesis to verify, not a finding to ship.`) and before `## Cross-Cutting: Intellectual Rigor`, insert:

```markdown
## Find First, Filter Second

Rex separates searching from reporting. They are different jobs, and running them together loses findings.

**While reading**, Rex enumerates everything he notices — including items he is unsure about, items he suspects are minor, and items he thinks are probably fine. He does not apply the severity bar during this pass. A candidate suppressed at the moment he notices it never gets evaluated at all, and Rex has no way to know what he threw away.

**Before writing**, Rex takes that internal list and applies the bar: assign a tier to what survives, drop what turns out to be a style preference or a non-issue on second look, and demote anything he couldn't verify (see Verify Before You Assert).

The reader sees only the filtered list. Rex still doesn't pad. What changes is that the padding judgment runs *after* the search, against a complete inventory, instead of during it.
```

- [ ] **Step 3: Point the no-padding bullet at the new section**

Find (line 132, in "What Rex Does NOT Do"):

```
- Rex does not pad reviews with minor issues to seem thorough. If there are only two problems, he lists two problems.
```

Replace with:

```
- Rex does not pad reviews with minor issues to seem thorough. If two problems survive the filter pass, he lists two problems. But the filter runs after the search, not during it (see Find First, Filter Second) — "nothing else worth reporting" is a conclusion Rex reaches, not a bar he applies while reading.
```

- [ ] **Step 4: Verify**

```bash
grep -c "Find First, Filter Second" ~/.claude/skills/rex/SKILL.md
grep -n "A false Blocker costs more than a missed Minor" ~/.claude/skills/rex/SKILL.md
grep -n "governs the \*tier\*" ~/.claude/skills/rex/SKILL.md
```

Expected at this point: `Find First, Filter Second` appears **twice** (section heading + line-132 cross-reference; Task 9 adds a third). The original asymmetry sentence is still present — if it is gone, Step 1 was misapplied as a replacement. The scoping paragraph appears once.

- [ ] **Step 5: Revert path**

`cp <scratchpad>/snapshot/rex-SKILL.md ~/.claude/skills/rex/SKILL.md`

- [ ] **Step 6: No commit yet** — verified in Task 9.

---

### Task 9: Rex — cap delegation, calibrate length, verify

**Two Opus 5 shifts, both containment problems.** Opus 5 reaches for subagents markedly more readily than 4.8 did, and Rex's current text is an open invitation with no ceiling. Separately, Opus 5's default response length is longer, and `effort` does not reliably shorten visible output — only prompting does.

**Files:**
- Modify: `~/.claude/skills/rex/SKILL.md:105-107` and `:111-118`

**Interfaces:**
- Consumes: `## Find First, Filter Second` from Task 8; `<scratchpad>/rex-target.py` and `<scratchpad>/baseline-rex.md` from Task 4.

- [ ] **Step 1: Add the delegation cap**

Find (tail of Step 1 under "How Rex Works"):

```
For large reviews (multiple files, long documents), Rex may use subagents to examine sections in parallel, then synthesize findings into a single cohesive review. For smaller artifacts, Rex works in a single pass. Rex decides — he doesn't ask permission to parallelize.
```

Replace with:

```
For large reviews (multiple files, long documents), Rex may use subagents to examine sections in parallel, then synthesize findings into a single cohesive review. For smaller artifacts, Rex works in a single pass. Rex decides — he doesn't ask permission to parallelize.

Delegation is not free: each subagent re-establishes context, re-explores, and reports back, and Rex then re-reads the report. He delegates only when the artifact is genuinely too large to hold at once, and never for:

- **Work he could finish in a handful of tool calls** — a few file reads, one targeted search, a single-file review.
- **Verifying his own findings.** Rex verifies inside his own loop (see Verify Before You Assert and Find First, Filter Second), not by spawning a checker.
- **Splitting one modest artifact into pieces.** Parallel subagents are for genuinely independent tracks — unrelated modules, a wide multi-file sweep — not for slicing one moderate job.

If one subagent can cover it, use one. Never more than six in parallel unless the user asks for more.
```

- [ ] **Step 2: Add finding-length calibration**

Find (end of Step 3 under "How Rex Works"):

```
Issues are grouped by severity tier (all Blockers first, then Majors, then Minors), and ordered within each tier by importance.
```

Replace with:

```
Issues are grouped by severity tier (all Blockers first, then Majors, then Minors), and ordered within each tier by importance.

Keep each finding to those five elements and nothing more. Two to four sentences is the target; a Blocker carrying a trace can run longer. Rex does not restate the artifact back to the author, does not explain the general principle behind a finding when the specific instance already makes it obvious, and does not append a closing summary that recaps the issue list. The verdict line is the close.
```

- [ ] **Step 3: Verify the edits landed**

```bash
grep -n "Never more than six in parallel" ~/.claude/skills/rex/SKILL.md
grep -n "The verdict line is the close" ~/.claude/skills/rex/SKILL.md
grep -c "Find First, Filter Second" ~/.claude/skills/rex/SKILL.md
```

Expected: one match each for the first two; `Find First, Filter Second` now appears **three** times.

- [ ] **Step 4: A/B against the planted target**

```
/rex review <scratchpad>/rex-target.py
```

Save to `<scratchpad>/after-rex.md` and compare against `<scratchpad>/baseline-rex.md`.

| Gating signal | Pass | Fail |
|---|---|---|
| **D1** shell injection in `run_hook` | reported, Blocker or Major | missing — the change broke Rex's core function |
| **D2** `mean_size` empty-list division | reported at any tier | missing in *both* baseline and after — recall fix did not take |
| **D3** unbounded `CACHE` | reported at any tier | missing in *both* baseline and after — same |
| **D4** unused `os` import | **not** reported | reported — over-corrected into padding, which is the failure mode the change must not introduce |

The intended outcome is D2 and D3 moving from absent-in-baseline to present-after. If the baseline already reported all of D1–D3, this A/B cannot demonstrate improvement; record that and rely on prose review, rather than reading a zero delta as success.

Advisory only, do not gate: subagent count (should be ≤ 6 and low for a 25-line file), review word count (should not exceed baseline).

- [ ] **Step 5: Revert path**

`cp <scratchpad>/snapshot/rex-SKILL.md ~/.claude/skills/rex/SKILL.md` — this reverts Tasks 8 and 9 together, since both edit the same file. If only one needs rolling back, restore the snapshot and re-apply the other task's steps.

- [ ] **Step 6: No commit yet** — committed in Task 12.

---

### Task 10: Eddie — move Agent 2's clearance rules into the second-eyes filter stage

**The problem this fixes:** Eddie already has the find-then-filter architecture Rex just gained — broad agents feeding a dedicated `eddie-second-eyes` pass. Agent 2's "Discipline — when NOT to flag" block undercuts it by filtering *inside* the finding stage, which on Opus 5 drops findings second-eyes would have evaluated. The rules are sound; they are in the wrong stage.

Three of the five bullets move. Two stay in Agent 2 because they target *invention* and *applicability*, not severity, and so don't trip the recall problem.

**Files:**
- Modify: `~/.claude/skills/eddie/SKILL.md:211-218`
- Modify: `~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md:13` and `:36`

**Interfaces:**
- Produces: Agent 2 findings now carry `Confidence: high / medium / low`. Consumed by `eddie-second-eyes` Sub-pass 1. Eddie's merge step (step 6) already merges heterogeneous finding fields and needs no change.

- [ ] **Step 1: Replace Agent 2's discipline block**

In `~/.claude/skills/eddie/SKILL.md`, find this exact block (lines 211–218, from the italic header through the `Return findings` line):

```
   *Discipline — when NOT to flag:*
   - **Exposure risks require a concrete, identifiable downside grounded in the text.** Hypothetical reader inferences ("a reader could infer that...") with no specific signal in the document are speculation, not exposure risk. Do not flag.
   - **Absence-as-implication is not exposure risk.** That a workshop has no internal speakers, a roster omits one possible name, or a list does not include every category is not, by itself, an unintended signal. External speakers at internal workshops, partial lists, and selective summaries are routine. Flag only when the absence creates a *concrete* misleading impression — not when it could be read uncharitably.
   - **Self-acknowledged-marginal findings should not be returned.** If your own confidence on a flag is "low" and the finding is framed as "worth noting only because..." or "very minor," do not ship it. The second-eyes pass will clear it; surface only findings that survive your own judgment.
   - **On short documents (under 200 words), structural-discipline categories rarely apply.** Excessive background, redundant argumentation, scope sprawl, and defensive over-documentation require a document long enough to exhibit them. Say "not applicable at this length" rather than padding the findings list.
   - **Do not fabricate concerns to appear thorough.** If the document is clean on a given axis, say so directly. A short list of high-confidence findings beats a long list of low-confidence speculation every time.

   - Return findings as prioritized revision entries.
```

Replace with:

```
   *Discipline — report what you find, tag your confidence:*
   - **Report every issue you find, including ones you are uncertain about.** Do not filter for importance or confidence at this stage. The second-eyes pass is the filter, and it runs against Polk's `lessons.md` calibrations — which you cannot see. Surfacing a finding that later gets cleared costs one line in "Considered but cleared"; suppressing a real one costs the whole point of the review.
   - **Tag every finding with `Confidence: high / medium / low`.** This is how the second-eyes pass ranks and clears them. A low-confidence finding with an honest tag is useful. A suppressed one is invisible.
   - **Do not fabricate concerns to appear thorough.** Reporting what you actually noticed is not the same as inventing concerns to fill a quota. If the document is clean on a given axis, say so directly.
   - **On short documents (under 200 words), structural-discipline categories rarely apply.** Excessive background, redundant argumentation, scope sprawl, and defensive over-documentation require a document long enough to exhibit them. Say "not applicable at this length" rather than padding the findings list.

   - Return findings as prioritized revision entries, each carrying a `Confidence:` value.
```

- [ ] **Step 2: Tell second-eyes that findings now carry confidence tags**

In `~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md`, find (item 2 under "What You Receive"):

```
2. **The merged findings list** — all findings from Eddie's parallel agents (factual, adversarial reading, voice/style, consistency, plan reconciliation), in Eddie's standard format
```

Replace with:

```
2. **The merged findings list** — all findings from Eddie's parallel agents (factual, adversarial reading, voice/style, consistency, plan reconciliation), in Eddie's standard format. Adversarial-reading findings carry a `Confidence: high / medium / low` tag; those agents deliberately do not self-filter, so the list you receive includes marginal findings by design. Clearing them is your job.
```

- [ ] **Step 3: Add the standing clearance rules to Sub-pass 1**

In the same file, find (step 5 of Sub-pass 1's per-finding checklist):

```
5. Decide: keep, remove, or adjust.
```

Replace with:

```
5. **Apply the standing clearance rules.** These are always-on calibrations, independent of `lessons.md`. Upstream agents deliberately no longer apply them, so borderline findings reach you instead of being dropped silently:
   - **Exposure risks require a concrete, identifiable downside grounded in the text.** A hypothetical reader inference ("a reader could infer that...") with no specific signal in the document is speculation, not exposure risk. Remove it.
   - **Absence-as-implication is not exposure risk.** That a workshop has no internal speakers, a roster omits one possible name, or a list does not include every category is not, by itself, an unintended signal. External speakers at internal workshops, partial lists, and selective summaries are routine. Keep the finding only when the absence creates a *concrete* misleading impression — not when it could merely be read uncharitably.
   - **`Confidence: low` findings framed as marginal** ("worth noting only because...", "very minor") clear by default — unless the category carries a risk floor under Sub-pass 2, which overrides this rule.
6. Decide: keep, remove, or adjust.
```

- [ ] **Step 4: Verify the move — no duplication, no orphan**

```bash
grep -n "Discipline — when NOT to flag" ~/.claude/skills/eddie/SKILL.md
grep -n "Tag every finding with" ~/.claude/skills/eddie/SKILL.md
grep -n "standing clearance rules" ~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md
grep -c "Absence-as-implication" ~/.claude/skills/eddie/SKILL.md ~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md
grep -n "^6. Decide" ~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md
```

Expected: first grep returns **nothing** (old header gone); second and third return one match each; `Absence-as-implication` count is **0 in SKILL.md and 1 in eddie-second-eyes.md** — a count of 1 in both means Step 1 didn't apply and the rule now runs in two stages, which reintroduces the exact bug this task fixes; the renumbered `6. Decide` line is present.

- [ ] **Step 5: Revert path**

```bash
cp <scratchpad>/snapshot/eddie-SKILL.md ~/.claude/skills/eddie/SKILL.md
cp <scratchpad>/snapshot/eddie-second-eyes.md ~/.claude/agents/eddie-second-eyes/eddie-second-eyes.md
```

- [ ] **Step 6: No commit yet** — tested in Task 11.

---

### Task 11: CHECKPOINT B — regression after the prose change

The models were validated at Checkpoint A. Any regression here is attributable to Task 10.

**Files:**
- Create: `<scratchpad>/checkB-eddie-institutional.md`, `<scratchpad>/checkB-eddie-clean.md`

- [ ] **Step 1: Re-run the Agent 2 fixture — the primary gate for this task**

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/institutional-sensitivity.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/checkB-eddie-institutional.md`.

- [ ] **Step 2: Evaluate against `expected.md` § institutional-sensitivity.md**

| Gating signal | Pass | Fail means |
|---|---|---|
| Dean/Achebe-Farrar exposure risk | reported, P1 or P2 | Agent 2 or second-eyes over-corrected — the change is broken, revert Task 10 |
| "I've decided the committee will forward" authority flag | reported | as above |
| "As discussed above" orphaned reference | reported P3 | as above |
| All-external workshop speakers | **cleared** (in "Considered but cleared" with the standing rule cited) **or absent** | appears as a live finding → second-eyes is not applying the standing rules; check Step 3's renumbering |
| "met twice in October" hypothetical inference | **cleared or absent** | as above |

Compare against `<scratchpad>/baseline-eddie-institutional.md`. The intended shift is the two clearable items moving from *invisible* (suppressed inside Agent 2) to *visible under "Considered but cleared"*. **More cleared entries than baseline is the designed outcome and is a pass** — that is suppressed work becoming auditable.

- [ ] **Step 3: Re-run the false-positive control**

```
/eddie /Users/polk/.claude/skills/eddie/tests/fixtures/clean.md be aggressive lessons=/Users/polk/.claude/skills/eddie/tests/lessons.md
```

Save to `<scratchpad>/checkB-eddie-clean.md`. Gate on the same three signals as Task 7 Step 3: no P1/P2, quoted-"ensure" cleared with the lesson cited, registry names pass Stage 1c. P3 counts remain advisory.

`clean.md` is well under 200 words, so Agent 2's structural categories are expected to report "not applicable at this length" — that retained rule is doing its job.

- [ ] **Step 4: Record the regression outcome in this file**

Append a results block: which fixtures ran, pass/fail per gating signal at both checkpoints, advisory counts, and any revert applied with its reason. This is what makes the change set auditable later.

- [ ] **Step 5: No commit yet.**

---

### Task 12: Publish and commit

**Files:**
- Run: `scripts/publish.py`
- Modify (generated): `rex/`, `eddie/`, `agents/`
- Add: `zz_docs/plans/2026-07-27-rex-eddie-opus5-revisions.md` (unless Task 1 Step 3 chose to gitignore it)

- [ ] **Step 1: Dry-run the publish**

```bash
cd "/Users/polk/Penn Law Dropbox/Polk Wagner/code/skills"
python3 scripts/publish.py --dry-run
```

Expected: pre-flight `test_publish.py` passes; post-scrub verification passes; sync-drift warnings appear **only** for files this plan intentionally changed. A warning naming an untouched file means someone hand-edited a synced skill in-repo — stop and investigate.

**If `~/.claude/publish-private-scrub.json` is missing**, `publish.py` warns and runs only the static identity scrub. **Do not proceed on that warning** — eddie's fixtures cite real colleagues. Restore the file from the private `claude-sync` repo first.

- [ ] **Step 2: Run the real publish**

```bash
python3 scripts/publish.py
```

- [ ] **Step 3: Review the generated diff before staging**

```bash
git fetch
git status --short
git diff -- rex/ eddie/ agents/
```

Confirm the diff contains only: Rex's four prose edits, Eddie's Agent 2 block swap, second-eyes' two edits, the new fixture plus its `expected.md` section, and five `model:` lines (four from Task 5, one from Task 6 — four if Task 6 was reverted).

**Check the new fixture specifically:** `git diff -- eddie/tests/fixtures/institutional-sensitivity.md` must show the maintainer's name replaced by the scrub placeholder. If a real name survives into the published copy, stop — the scrub rules need updating before this ships.

- [ ] **Step 4: Commit by pathspec, in three commits**

```bash
git add eddie/tests/fixtures/institutional-sensitivity.md eddie/tests/fixtures/expected.md
git commit -m "test(eddie): add institutional-sensitivity fixture

No existing fixture exercised Agent 2's adversarial-reading, structural-
discipline, or institutional-sensitivity paths. clean.md cannot: it has no
exposure-risk surface and falls below the word count where Eddie dispatches
agents at all. This fixture plants one finding that must survive and two
that must be cleared by second-eyes' standing rules.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

```bash
git add agents/voice-style-checker/ agents/eddie-consistency-checker/ \
        agents/quote-extractor/ agents/coverage-auditor/ \
        agents/factual-pipeline-orchestrator/
git commit -m "agents: retier for the Sonnet 5 / Haiku 4.5 gap

Sonnet 5 is near-Opus on analytical work; Haiku 4.5 is two generations old
with no successor and was doing judgment work it will miss.

haiku -> sonnet: voice-style-checker, eddie-consistency-checker
opus -> sonnet:  quote-extractor, coverage-auditor,
                 factual-pipeline-orchestrator (sequencer, not reviewer)

Unchanged: claim-merge-agent (mechanical, stays haiku); factual-reviewer and
institutional-claim-extractor (recall floor); eddie-second-eyes, fix-verifier,
adversarial-reverifier (calibration and independent verification).

Verified at checkpoint A against personnel-drift.md and clean.md, before any
prose change, so the result is attributable to the model retier alone.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

```bash
git add rex/SKILL.md eddie/SKILL.md agents/eddie-second-eyes/
git commit -m "skills: separate finding from filtering in rex and eddie for Opus 5

Opus 5 follows severity-filter instructions literally, so precision-first
language inside a finding pass silently suppresses real findings.

- rex: add Find First, Filter Second; scope the false-Blocker asymmetry to
  tier assignment rather than whether to report; cap subagent fan-out at six
  and bar verification subagents; calibrate finding length.
- eddie: Agent 2 stops self-filtering and tags findings with Confidence. Its
  three clearance rules move to eddie-second-eyes, already the dedicated
  filter stage.

Verified at checkpoint B against institutional-sensitivity.md.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

Adjust the second message and drop `agents/factual-pipeline-orchestrator/` if Task 6 was reverted.

- [ ] **Step 5: Commit the plan**

Skip if Task 1 Step 3 chose to gitignore `zz_docs/`.

```bash
git add zz_docs/plans/2026-07-27-rex-eddie-opus5-revisions.md
git commit -m "docs(plans): rex + eddie Opus 5 recalibration plan and results

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: Stop. Do not push.**

Report the commit SHAs and ask whether to push.

---

### Task 13 (OPTIONAL — outside the rex/eddie scope): retier `mcq-structural-reviewer`

**Files:**
- Modify: `~/.claude/agents/mcq-structural-reviewer/mcq-structural-reviewer.md`

`mcq-structural-reviewer` belongs to `law-mcq-generator`, not to rex or eddie. It is on `haiku` and applies Haladyna-Downing-Rodriguez item-writing rules, which needs reading comprehension rather than pattern-matching — the same argument that moves `voice-style-checker` and `eddie-consistency-checker` in Task 5.

**Skip this task** to keep the change set confined to the two skills under discussion. It has no regression coverage here: eddie's fixtures don't exercise it, and validating it means generating an MCQ exam and running `law-mcq-generator/validate_mcq.py`.

- [ ] **Step 1: Snapshot, then apply**

```bash
cp ~/.claude/agents/mcq-structural-reviewer/mcq-structural-reviewer.md <scratchpad>/snapshot/
```

Then change `model: haiku` to `model: sonnet`.

- [ ] **Step 2: Verify**

```bash
grep -H "^model:" ~/.claude/agents/mcq-structural-reviewer/*.md
```

Expected: `model: sonnet`

- [ ] **Step 3: Publish and commit separately**

```bash
python3 scripts/publish.py
git add agents/mcq-structural-reviewer/
git commit -m "agents: move mcq-structural-reviewer off haiku

Item-writing rule checks need reading comprehension, not pattern matching.
Not covered by the eddie fixture harness — validate with an MCQ generation
run and validate_mcq.py before relying on it.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Cost

Six heavy eddie runs (Task 2 Step 3, Task 4 Steps 1 and 3, Task 7 Steps 1 and 3, Task 11 Steps 1 and 3 — seven if `clean.md` is run at every checkpoint), each dispatching roughly a dozen agents, plus two Rex runs. That is the price of black-box testing an LLM reviewer: there is no assertion to write, only before/after comparison, and the "before" is unrecoverable once prompts change.

If you need to trim, the cheapest cut is `clean.md` at Checkpoint A — the `voice-style-checker` retier it covers is the lowest-risk change in the set. **Do not cut** the `institutional-sensitivity.md` runs (the only coverage Task 10 has) or the `personnel-drift.md` runs (the only coverage Tasks 5–6 have).

## Out of scope, deliberately

- **`effort:` in agent frontmatter.** Unverified whether Claude Code supports it. A silently-ignored frontmatter key is worse than no key. Verify first, plan separately.
- **Fable 5 for any agent.** Its strengths are long-horizon autonomous runs and hardest-tier reasoning, at above-Opus pricing with minutes-long turns. Every rex and eddie agent is a short, bounded task.
- **Eddie's four-stage factual pipeline.** The Opus 5 guidance to delete verification scaffolding targets *self*-verification instructions. `adversarial-reverifier`, `coverage-auditor`, and `fix-verifier` run in independent contexts, where fresh-context verifiers still outperform self-critique.
- **Reducing the `adversarial-reverifier` sample rate.** Plausible cost saving, but it trades away the pipeline's independent-check property. Separate decision, separate evidence.
- **Three-run baselines for statistical confidence in count deltas.** Roughly doubles cost. This plan gates on named expectations instead. Revisit if count drift becomes a recurring source of false alarms.
