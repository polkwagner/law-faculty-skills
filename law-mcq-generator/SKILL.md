---
name: law-mcq-generator
description: >
  Generate high-quality multiple choice exam questions for any law school course.
  Use when asked to create MCQ exam questions, practice questions, or question banks
  for law school exams. Trigger phrases include "exam questions", "multiple choice",
  "MCQ", "practice questions", "question bank", "generate questions", or references
  to creating law exam content. Also trigger when asked to create narrative-based or
  fact-pattern-based multiple choice questions for any doctrinal law course including
  IP, contracts, torts, con law, civ pro, etc. Supports course presets for quick
  setup. Always use this skill rather than generating exam questions freehand — it
  enforces critical quality controls including distractor validation, cognitive
  taxonomy tagging, and coverage balancing derived from the psychometric research
  literature.
license: CC-BY-4.0
metadata:
  author: "[Your Name]"
---

# Law School MCQ Exam Generator

## Agent Dependencies

This skill dispatches several sub-agents for quality checks. Each call is guarded — the skill works without them, but item-writing compliance, distractor validation, and coverage balancing are significantly weaker.

- `emphasis-map-builder` — ranked emphasis map of testable doctrines from course materials.
- `mcq-structural-reviewer` — per-question item-writing rule checks (Haladyna-Downing-Rodriguez taxonomy).
- `adversarial-balance-validator` — adversarial challenge per question with fact-pattern citation requirement.
- `construct-alignment-tracer` — verifies every tested issue traces to assigned course materials.
- `double-read-pass` — fresh-eyes review of the generated exam and answer key.
- `voice-style-checker` — AI-tell scan.

Install from the `agents/` directory of this skill's repo into `~/.claude/agents/`.

## Environment

This skill works in both **Claude Code CLI** and **Claude.ai / Cowork**:

- **Output:** `~/Downloads/` or user-specified path (CLI) or `/mnt/user-data/outputs/` (web)
- **Course materials:** ask user for path (CLI) or use `project_knowledge_search` and `/mnt/user-data/uploads/` (web)

## Overview

This skill generates research-grounded multiple choice exam questions for law
school courses. It works with any doctrinal law course — the skill reads the
course syllabus and materials to discover the subject matter, doctrinal areas,
and coverage weights at runtime.

The quality assurance framework is based on the Haladyna-Downing-Rodriguez
taxonomy of evidence-based item-writing guidelines (2002), classical test theory
metrics for item analysis, and research on structural flaws and distractor
functioning in MCQ assessment.

## Course Presets

Presets store default paths and metadata for known courses. When the user
mentions a preset course by name (e.g., "generate IP exam questions"), use
the preset values and skip to step 2 of the workflow. The user can override
any preset value.

If the user's course isn't in the preset list, fall through to the standard
"ask for everything" flow.

| Field | IP |
|---|---|
| **Course name** | Intellectual Property |
| **School** | University of Pennsylvania Carey Law School |
| **Professor** | [Your Name] |
| **Casebook** | IPNTA |
| **Materials path** | Ask user — e.g., `~/path/to/IP/course-materials/` |
| **Doctrinal areas** | Trade Secret, Patent, Copyright, Trademark, Right of Publicity |
| **Coverage weight note** | Patent, Copyright, and Trademark are the "big three" — they should receive the most questions. Trade Secret and Right of Publicity are also studied but are minor doctrines relative to the big three. |
| **Cognitive taxonomy note** | Use "RI" (Regime Identification) instead of "FS" — "Which IP regime applies or best protects" |

To add a new preset: add a column to this table with the course's defaults.
Fields left blank fall through to the standard discovery flow (read syllabus).

## First Steps (Do This Every Time)

1. **Identify the course.** Check if it matches a preset. If so, load defaults
   and confirm with the user. If not, ask for:
   - The path to the folder containing the course materials (syllabus, readings,
     slides, class problems, transcripts, problem debriefs — whatever is
     available). The folder may contain all materials in one place or organized
     in subfolders.
   - How many questions to generate
   - Any specific preferences or constraints (e.g., "focus on the second half
     of the course," "no questions on [topic]," "match the style of my 2024 exam")

2. **Read the syllabus** from the course materials folder. Identify and extract:
   - **Course metadata**: course name, professor name, school name, semester/year,
     casebook or primary text (use preset values where available)
   - Each class session and its topic
   - The assigned readings for each session
   - The major doctrinal areas covered

   If no syllabus is found, ask the user for the course name, doctrinal areas,
   and approximate coverage weights.

3. **Calculate coverage distribution** by counting the number of class sessions
   devoted to each major doctrinal area. Use this as the proportional weight
   for question distribution. Round to whole questions. Present the planned
   distribution to the user and ask if they want to adjust it.

4. **Build the emphasis map.** If the `emphasis-map-builder` agent is available, spawn it and pass
   it the course materials folder path, course name, and doctrinal areas. The
   agent reads all available materials and returns a ranked emphasis map.
   Not all material types will be available for every course — the agent uses
   whatever is provided. The course materials folder may contain any combination
   of the following, listed in order of their role:

   **Primary source (defines what can be tested):**
   - **Assigned readings** (PDF or markdown) — the ultimate source of course
     coverage. These define the "testable universe." If a doctrine, case, or
     framework is not in the assigned readings, it cannot be tested on the
     exam. Every question must trace to a specific reading.

   **Emphasis signals (determine what SHOULD be tested):**
   - **Slide decks** (PDFs) — the primary emphasis signal. Topics that made
     it onto slides received deliberate instructional emphasis and should be
     weighted higher when selecting which doctrines to test. Slides may also
     contain some substantive material not fully covered in the readings —
     this material is testable.
   - **Class transcripts** (markdown) — a supporting emphasis signal that
     reinforces the slides. Scan for extended discussions, repeated returns
     to a topic, and Socratic exchanges. Time-on-topic proxies importance.
     **Practical note:** read transcripts only for class sessions whose
     doctrines are candidates for questions, not the entire course.
   - **Class problems** (markdown or Google Docs) — provide context about
     which topics were emphasized through adversarial practice. MCQs can
     test these doctrines at a different cognitive level but should not
     simply repeat what the problem already tested.
   - **Problem debriefs** (markdown) — reveal which arguments the professor
     considered strongest and what common student errors looked like.

   Rank all testable doctrines by emphasis level. When fewer material types
   are available, use whatever is provided — the ranking degrades gracefully:

   | Level | Criteria | MCQ Role |
   |---|---|---|
   | **High** | In readings + emphasized on slides + reinforced by transcript or class problem | Strong candidate for a question |
   | **Medium-High** | In readings + on slides but no problem or transcript signal | Good candidate — taught but not yet practiced |
   | **Medium** | In readings only (or on slides only for substantive slide-only material) | Fair game but should not dominate the exam |
   | **Excluded** | Not in readings and not substantively on slides | Cannot be tested |

   If only readings are available (no slides, transcripts, or problems),
   all doctrines rank MEDIUM and selection is based on coverage weight and
   the depth of treatment in the readings.

   Present this emphasis ranking to the user before planning narrative clusters.

5. **Plan the narrative clusters.** Determine how many fact patterns are needed
   and which doctrinal areas each will cover. Each narrative should span at
   least 2 doctrinal areas. Plan 4-6 questions per narrative. The total across
   all clusters should hit the requested question count and the coverage
   distribution.

6. **Present the plan** to the user: number of narratives, doctrinal coverage
   per narrative, total question count per doctrinal area, and the course
   metadata that will appear on the exam. Get approval before generating.

## Narrative Design

### Format
- 200-400 words
- A single coherent, realistic (but fictional) scenario
- Include a memorable subtitle in the style "The one with the [thing]"
- Realistic settings with fictional entity and character names
- Include temporal markers where timing matters (statutes of limitations,
  filing deadlines, priority dates, effective dates, first use dates, etc.)

### Content Requirements
- At least one party whose actions raise legal issues
- Facts relevant to multiple doctrinal areas (minimum 2 per narrative)
- 2-3 subtly ambiguous facts — capable of supporting arguments on both sides
  but with a clearly better answer
- Red herrings or facts that cut against the intuitive answer
- Enough factual detail to support 4-6 questions without padding

### What to Avoid
- Scenarios that are too clean or obvious
- Real company names or real people in the narratives (though questions can
  reference real doctrines, statutes, cases, and legal standards)
- Facts so ambiguous that reasonable experts would disagree on the answer
- Narratives that require specialized non-legal knowledge beyond what's
  provided in the fact pattern
- Narrative language (titles, descriptions, characterizations) that
  contradicts or undermines the analytical framing a planned question's
  correct answer depends on — e.g., describing an article with a
  supportive title when the correct answer requires treating it as
  critical analysis

## Question design

**Read `references/question-design.md` before writing any question.** It carries question construction, the cognitive taxonomy tagging scheme, the distractor taxonomy, and difficulty calibration — the psychometric core of this skill.

## Quality Assurance Framework

**Read `references/qa-framework.md` before Stages 1-3.** It carries the per-stage checks, the distractor validation rules, the fact-answer alignment test, and the two-direction fact dependency test.

The QA stages depend on sub-agents (see Agent Dependencies). **This pipeline has never been run end-to-end** — the agents were added 2026-04-18 and the skill has not been invoked since. Treat the first run as a test: confirm each agent actually returns before trusting a clean report.

## Output

**Read `references/output-format.md`** for the markdown draft schema, the production file layout, and the `.docx` generation details. Drafts are written as markdown first and only converted after Stages 1-3 pass.

## Workflow Summary

1. Identify course (check presets) → confirm with user
2. Ask for question count, materials path (if not preset), and any preferences
3. Read syllabus → extract course metadata → calculate coverage distribution → present to user
4. `emphasis-map-builder` agent (if available) → returns emphasis map
5. Present emphasis map to user for steering
6. Plan narrative clusters and question allocation → present to user → get approval
7. **Generate markdown drafts** — write `draft_full_set.md`,
   `draft_answer_key_full.md`, and `draft_answer_key_student.md`
   - **7a. Narrative framing review (before writing questions against each
     narrative):** Review each narrative's analytical signals — titles,
     labels, verbs, and descriptive characterizations. For each planned
     question, verify the narrative's language supports the analytical path
     the correct answer requires. If a title, description, or
     characterization contradicts or undermines an intended answer (e.g.,
     a title suggests endorsement when the answer requires treating the
     work as criticism), revise the narrative before writing questions
     against it.
8. **Stage 1 QA** (on markdown drafts): `mcq-structural-reviewer` agent (if available) → per-question item-writing rule checks; fix any violations in the `.md` files
9. **Stage 2 QA** (on markdown drafts): `adversarial-balance-validator` agent (if available) (type: mcq) → adversarial challenge for each question with fact-pattern citation requirement. Run fact-answer alignment check and two-direction fact dependency test. `construct-alignment-tracer` agent (if available) → verify construct alignment. Fix any issues in the `.md` files.
10. **Stage 3 QA** (on markdown drafts): Exam-Level Summary — distributions, flagged items. Fix any issues.
11. **Generate production files** — only after Stages 1-3 pass on the markdown drafts:
    - Generate `.docx` files from the approved markdown content using templates
    - Generate the CSV answer key
12. **Stage 4 QA**: Output Validation Gate — run `validate_mcq.py` against the generated .docx files. **This is a blocking gate.** If any check fails, fix the markdown source, regenerate `.docx`, and re-run. If the same check fails twice, stop and report.
13. `double-read-pass` agent (if available) → fresh-eyes review of the `.docx` documents; fix any problems in the markdown, then regenerate `.docx`
14. `voice-style-checker` agent (if available) → fix any AI writing tells in the markdown, then regenerate `.docx`
15. Present all files to user (3 `.docx`, 1 `.csv`, markdown drafts retained as source)

## What NOT to Do

- Do not generate questions without first reading the syllabus and course materials
- Do not hardcode doctrinal areas — derive them from the syllabus (presets provide defaults, not overrides)
- Do not use any prohibited question formats
- Do not create questions testable by rote memorization alone
- Do not create questions with two genuinely defensible answers
- Do not create policy or theory questions (those belong on essays)
- Do not use real names in fact pattern narratives
- Do not make all questions the same difficulty
- Do not cluster correct answers at one letter position
- Do not skip Stages 1 and 2 of the QA framework
- **Do not deliver documents that have not passed Stage 4 validation.** Stage 4
  is a blocking gate. If the validation script reports any failure, fix the
  defect and re-run validation before presenting files to the user. A missing
  narrative, a missing answer choice, or a mismatched answer key is a
  catastrophic defect — treat it as one.
