---
name: law-essay-generator
description: >
  Generate assessment-science-grounded essay exam questions for law school courses.
  Use when asked to create essay questions, issue spotters, exam essays, or essay
  fact patterns for law school exams. Trigger phrases include "essay question",
  "essay exam", "issue spotter", "write an essay", "exam essay", "generate an
  essay", or any request to create law school essay exam questions. Also trigger
  when asked to create cross-doctrinal fact patterns, grading rubrics, or model
  answers for law school essay exams. Supports course presets for quick setup.
  Always use this skill rather than generating essay questions freehand — it
  enforces assessment-science quality controls including SOLO taxonomy layering,
  construct alignment to course materials, and rubrics designed for AI-assisted
  grading.
license: CC-BY-4.0
compatibility: "Requires python-docx"
metadata:
  author: "[Your Name]"
---

# Law School Essay Exam Generator

## Agent Dependencies

This skill dispatches several sub-agents for quality checks. Each call is guarded — the skill works without them, but coverage balancing, construct alignment, and AI-tell checks are significantly weaker.

- `emphasis-map-builder` — ranked emphasis map of testable doctrines from course materials.
- `construct-alignment-tracer` — verifies every tested issue traces back to assigned readings or class content.
- `adversarial-balance-validator` — validates that both sides of each legal issue can make credible arguments.
- `double-read-pass` — fresh-eyes review of fact pattern, rubric, and model answer.
- `voice-style-checker` — AI-tell scan on the fact pattern.

Install from the `agents/` directory of this skill's repo into `~/.claude/agents/`.

## Environment

This skill works in both **Claude Code CLI** and **Claude.ai / Cowork**:

- **Output:** `~/Downloads/` or user-specified path (CLI) or `/mnt/user-data/outputs/` (web)
- **Course materials:** ask user for path (CLI) or use `project_knowledge_search`
  and `/mnt/user-data/uploads/` (web)

## Overview

This skill generates research-grounded essay exam questions for law school
courses. It produces cross-doctrinal issue-spotter fact patterns with evaluative
components, tightly tied to the specific cases, tests, and frameworks students
encountered in the assigned course materials.

The assessment framework is grounded in:
- **SOLO Taxonomy** (Biggs & Collis) — layered issue complexity for discrimination
- **Construct Alignment** (Biggs) — every testable issue maps to taught material
- **Emphasis Detection** — slides, class problems, and transcripts reveal what
  was actually emphasized vs. what the syllabus merely lists

## Course Presets

Presets store default paths and metadata for known courses. When the user
mentions a preset course by name, use the preset values and skip to step 2
of the workflow. The user can override any preset value.

| Field | IP |
|---|---|
| **Course name** | Intellectual Property |
| **School** | University of Pennsylvania Carey Law School |
| **Professor** | [Your Name] |
| **Casebook** | IPNTA (2025 edition) |
| **Materials path** | Ask user |
| **Doctrinal areas** | Trade Secret, Patent, Copyright, Trademark, Right of Publicity |
| **Coverage weight note** | Patent, Copyright, and Trademark are the "big three" — they should receive prominent treatment in essay questions. Trade Secret and Right of Publicity are also studied but are minor doctrines relative to the big three. |

To add a new preset: add a column to this table with the course's defaults.

## First Steps (Do This Every Time)

1. **Identify the course.** Check if it matches a preset. If so, load defaults
   and confirm with the user. If not, ask for the course name and doctrinal areas.

2. **Ask the user for:**
   - Path to the course materials folder (syllabus, readings, slides, problems,
     transcripts — whatever is available)
   - How many essay questions to generate
   - Time allocation per essay (determines issue count and depth)
   - Maximum word count per essay (constrains scope)
   - Any topics to emphasize or avoid
   - **Path to former exam questions folder** (if available). The folder should
     contain an INDEX.md with YAML frontmatter describing each exam file. If
     no index exists, read the exam files directly and extract the dimensions
     for the Prior Exam Check. See the Prior Exam Check section below.
   - **Prompt style preference:** open-ended analysis or role-playing directive.
     See the Prompt Style section below for guidance on when to use each.

3. **Read the syllabus.** Identify class sessions, topics, reading assignments,
   and calculate coverage weights by doctrinal area (number of sessions per area).

4. **Build the emphasis map.** If the `emphasis-map-builder` agent is available, spawn it and pass
   it the course materials folder path, course name, and doctrinal areas. The
   agent reads all available materials (readings, slides, transcripts, problems,
   debriefs), ranks doctrines by emphasis level, and identifies course themes.
   See the Emphasis Detection section below for the ranking criteria.

5. **Review the agent's output.** Check that the emphasis ranking and course
   themes make sense given what you know about the course structure.

6. **Present findings to the user for steering:** the emphasis map AND the
   identified course themes. Ask the user to confirm, correct, or add themes.

7. **Plan each essay and present to the user. STOP and wait for approval.**
   This is a hard gate — do not draft the fact pattern, rubric, model answer,
   or any output document until the user has reviewed and approved the plan.

   Present the following to the user in conversation:

   **a. Issue plan table:**
   | # | Issue | Doctrinal Area | SOLO Level | ~Points | Key Case/Statute |
   (one row per planned issue, including the red herring)

   **b. Cross-cutting design:** What single asset or conduct sits at the
   intersection of regimes? Why does this force comparative analysis?

   **c. Fact pattern concept:** 2-3 sentence summary of the scenario (industry,
   characters, central conflict) — enough to evaluate without writing the
   full narrative.

   **d. Discrimination features:** What will be buried, what will be ambiguous,
   what is the red herring?

   **e. Course themes engaged:** Which themes does this design activate?

   **f. Prior exam differentiation:** How this design differs from each prior
   exam on the 5 dimensions (doctrinal areas, scenario type, issue set,
   cross-cutting asset, discrimination features).

   **g. Point distribution summary:** Points by SOLO level (vs. ~30/45/25
   target) and by doctrinal area (vs. course coverage weights).

   Ask: "Does this plan look right, or should I adjust anything before
   drafting?"

8. **Get explicit approval** before writing anything. If the user says
   "looks right" or "go ahead," proceed. If they give feedback, revise the
   plan and re-present. Do NOT interpret silence as approval.

## Inputs

### Required
- **Syllabus** — coverage weights, reading assignments, class topics
- **Assigned readings** (PDF or markdown) — the ultimate source of course
  coverage. These define the "testable universe." If a doctrine, case, or
  framework is not in the assigned readings, it cannot be an issue on the
  essay. Every issue must trace to a specific reading.
- **Number of essays** — ask the user
- **Time allocation per essay** — determines how many issues are reasonable
  (see Issue Count Calibration below)
- **Maximum word count per essay** — the model answer must fit within this limit

### Issue Count Calibration

Use this table to scope the essay before designing. The fact pattern should
contain the target number of issues; the model answer must fit within the
word limit. If the model answer exceeds the limit, reduce the issue count —
do not compress the analysis.

| Time | Word Limit | Target Issues | Unistructural | Relational | Extended Abstract |
|------|-----------|---------------|---------------|------------|-------------------|
| 45 min | 1000 words | 4-5 | 1-2 | 2-3 | 1 |
| 60 min | 1250 words | 5-6 | 2 | 3 | 1 |
| 70 min | 1500 words | 6-8 | 2-3 | 3-4 | 1-2 |
| 90 min | 2000 words | 7-10 | 2-3 | 4-5 | 1-2 |

For time/word combinations not in the table, interpolate. When in doubt,
fewer issues with deeper analysis is better than more issues with shallow
treatment.

### Optional (Emphasis Signals)

Not all material types will be available for every course — use whatever is
provided. The skill degrades gracefully when inputs are missing.

**Emphasis signals (determine what SHOULD be tested):**
- **Slide decks** (PDFs) — the primary emphasis signal. Topics that made it
  onto slides received deliberate instructional emphasis and should be weighted
  higher when selecting which doctrines to test. Slides may also contain some
  substantive material not fully covered in the readings — this material is
  testable.
- **Class transcripts** (markdown) — a supporting emphasis signal that
  reinforces the slides. Scan for extended discussions, repeated returns to a
  topic, and Socratic exchanges. Time-on-topic proxies importance. **Practical
  note:** read transcripts only for class sessions whose doctrines are
  candidates for the essay, not the entire course.
- **Class problems** (markdown) — provide context about which topics were
  emphasized through adversarial practice. The essay should test these
  doctrines at a deeper SOLO level or test different doctrines to avoid
  repetition.
- **Problem debriefs** (markdown) — reveal which arguments the professor
  considered strongest and what common student errors looked like.

## Emphasis Detection

The skill ranks all testable doctrines by emphasis level. When fewer material
types are available, use whatever is provided — the ranking degrades gracefully:

| Level | Criteria | Essay Role |
|---|---|---|
| **High** | In readings + emphasized on slides + reinforced by transcript or class problem | Strong candidate for a major essay issue |
| **Medium-High** | In readings + on slides but no problem or transcript signal | Good candidate — taught but not yet practiced |
| **Medium** | In readings only (or on slides only for substantive slide-only material) | Fair game but should not be a major point-earner |
| **Excluded** | Not in readings and not substantively on slides | Cannot be tested |

If only readings are available (no slides, transcripts, or problems), all
doctrines rank MEDIUM and selection is based on coverage weight and the depth
of treatment in the readings.

Present this ranking to the user before designing the fact pattern.

## Course context

**Read `references/course-context.md`** when deriving themes from course materials or checking a draft against prior exams for repetition.

## Design framework

**Read `references/design-framework.md` before drafting.** It carries the SOLO-taxonomy layering, fact-pattern construction, and prompt style.

## Outputs

**Read `references/output-format.md`** for the deliverable set, file layout, and the machine-gradeable rubric structure.

## Workflow Summary

1. Identify course (check presets) → confirm with user
2. Ask for: materials path, number of essays, time per essay, word limit,
   preferences, and whether prior exam essays are available
3. Read syllabus → calculate coverage weights
4. Read prior exam essays (if provided) → look for INDEX.md with YAML
   frontmatter; extract 5 dimensions (doctrinal areas, scenario type, issue
   set, cross-cutting asset, discrimination features); present novelty matrix
5. `emphasis-map-builder` agent (if available) → returns emphasis map + course themes
6. Present emphasis map AND course themes to user for steering
7. Plan each essay → present issue table, cross-cutting design, scenario
   concept, discrimination features, themes, prior exam differentiation,
   and point distribution to user. STOP and wait for approval.
8. Get explicit approval before writing — revise plan if user gives feedback
9. Write fact pattern (engineer facts for layering)
10. Build rubric (concrete textual markers for AI-assisted grading)
11. Write model answer (within student word limit)
12. Produce quality analysis (including prior exam differentiation)
13. `construct-alignment-tracer` agent (if available) → verify every issue traces to course materials
14. `adversarial-balance-validator` agent (if available) → verify both sides can argue each issue
15. `double-read-pass` agent (if available) → fresh-eyes review of all four outputs; fix any problems found
16. `voice-style-checker` agent (if available) → fix any style issues in the fact pattern
17. Run self-check
18. Generate four .docx files per essay
19. Generate machine-readable rubric JSON alongside the .docx rubric (see
    Rubric Format for Machine Grading below)
20. **Recommend running the essay dry run tool** (`~/code/essay-dry-run/`)
    to stress-test the essay with multiple AI models before finalizing.
    This is an external tool run from the terminal, not a subagent.
    Results feed back into potential revisions to the fact pattern or rubric.

## Double Read

**Read `references/double-read.md`** for the fresh-eyes review procedure. It dispatches the `double-read-pass` agent — **never exercised** (added 2026-04-18; skill last run 2026-03-27). Confirm the agent returns before trusting a clean pass.

## Self-Check Before Delivering

Run every check. If any fails, revise before delivering.

- [ ] Every issue maps to assigned course materials (construct alignment)
- [ ] SOLO distribution is ~30% / ~45% / ~25% (±5%)
- [ ] Point distribution matches doctrinal coverage weights (±10%)
- [ ] No issue requires knowledge outside the readings
- [ ] No issue invites analysis under legal frameworks outside the course
  (the essay tests a closed universe of course subject matter only)
- [ ] Model answer fits within the student word limit
- [ ] Rubric has concrete textual markers for every criterion
- [ ] At least one cross-doctrinal bonus issue exists
- [ ] At least one red herring is present
- [ ] Ambiguous facts have arguments on both sides (no obvious answers on
  relational/extended abstract issues)
- [ ] Fact pattern implicates 3+ doctrinal areas overlapping on the same facts
- [ ] Prior exam compliance: new essay differs from each prior exam on at
  least 3 of 5 dimensions (doctrinal areas, scenario type, issue set,
  cross-cutting asset, discrimination features) — or no prior exams were
  provided
- [ ] Named characters, realistic setting, clear timeline with specific dates
- [ ] Call of the question is regime-neutral

## What NOT to Do

- Do not generate essay questions without first reading the syllabus and
  course materials
- Do not design a fact pattern before presenting the plan for approval
- Do not test doctrines not covered in the assigned readings
- Do not create separate sub-scenarios for each IP regime — the regimes
  must overlap on shared facts
- Do not write policy questions — essay questions test doctrinal application
  and evaluative analysis, not abstract reasoning about what the law should be.
  Policy goals underlying a doctrine (e.g., "patent disclosure promotes
  innovation") can strengthen a doctrinal argument, but the essay should
  never require or primarily reward policy reasoning over doctrine
- Do not create a model answer that exceeds the student word limit
- Do not include rubric criteria without concrete textual markers — vague
  criteria like "discusses functionality" are unusable for AI-assisted grading
- Do not skip the emphasis map step — present it to the user before designing
- Do not use real company names or real people in fact pattern narratives
- Do not assign more than ~25% of points to extended abstract issues —
  the exam should be achievable, not a trap
- Do not generate an essay that is substantially identical to a prior exam —
  this violates institutional policy. When prior exams are provided, verify
  differentiation on at least 3 of 4 dimensions before delivering
