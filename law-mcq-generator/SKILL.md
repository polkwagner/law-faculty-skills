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
---

# Law School MCQ Exam Generator

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

4. **Read the course materials** and build the emphasis map. Not all material
   types will be available for every course — use whatever is provided. The
   course materials folder may contain any combination of the following,
   listed in order of their role:

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

## Question Design

### Structure
- 4 answer choices (A through D)
- Positively phrased stems (no "which of the following is NOT...")
- Each question tests one doctrinal concept or analytical skill
- Questions within a cluster are independent — getting one wrong does not
  prevent answering another
- Use "Assume for purposes of this question only that..." framing when a
  question requires a premise not established in the main narrative, or
  when the governing law is emerging or unsettled — specify the authority
  students should apply

### Prohibited Formats
- "All of the above"
- "None of the above"
- "(A) and (B)" compound answer choices
- "(A) and (B) but not (C)" compound answer choices
- Roman numeral lists with combination answer choices (e.g., "I, II, and IV")
- Negatively phrased stems ("which is NOT...")

### Answer Architecture (per question)
- **One correct answer**: Definitively best. Must survive adversarial challenge.
- **One strong distractor**: Wrong, but requires careful analysis to eliminate.
  This is where discrimination happens.
- **One moderate distractor**: Plausible on first read, identifiably wrong
  with solid doctrinal knowledge.
- **One weak distractor**: Clearly wrong to a prepared student, but might
  attract someone guessing or underprepared.

Research consistently shows that four-option items are optimal for high-stakes
assessment — three strong distractors outperform four distractors where the
weakest is nonfunctional (Rodriguez 2005; Raymond et al. 2019). Do not add a
fifth option.

### Answer Choice Formatting
- All four choices should be roughly similar in length, specificity, and
  grammatical structure
- Avoid patterns where the correct answer is consistently longer, more
  hedged, or more detailed than distractors
- Vary the position of the correct answer across questions (don't cluster
  correct answers at one letter)

### Reading Load Budget
Excessive text shifts the construct being measured from doctrinal knowledge
to reading speed (NBME Item-Writing Guide). Target these limits:
- **Narrative:** 270-300 words per fact pattern (hard floor: 200, hard ceiling: 400)
- **Stem:** under 75 words (shorten stems over 80 words)
- **Answer choice:** under 35 words per option; each option states one legal
  proposition, not a multi-step argument
- **Total exam words** (narratives + stems + all options): under 250 words
  per question on average. For a 40-question exam, target ~10,000 total words.
  Exceeding 12,000 total words indicates the exam is too text-heavy and should
  be trimmed before administration.

## Cognitive Taxonomy

Tag every question with one of these codes. Aim for the specified distribution
across the full exam:

| Code | Type                   | Description                                                        | Target |
|------|------------------------|--------------------------------------------------------------------|--------|
| EA   | Element Application    | Apply specific doctrinal elements or tests to facts                | 30%    |
| AE   | Argument Evaluation    | Identify which party has the stronger or best argument             | 20%    |
| FB   | Factor Balancing       | Weigh factors in a multi-factor test against ambiguous facts       | 15%    |
| FS   | Framework Selection    | Identify which legal framework, test, or body of law governs      | 15%    |
| DD   | Doctrinal Distinction  | Distinguish between related or easily confused doctrines           | 10%    |
| NR   | Negative Recognition   | Recognize when a doctrine does not apply despite surface similarity| 10%    |

Course presets may rename codes (e.g., IP uses "RI" for "FS"). Use the preset
label if one is active.

No policy or theory questions — those belong on essay portions of the exam.
MCQs should test application, analysis, and judgment, not abstract reasoning
about legal policy.

## Distractor Taxonomy

Tag every wrong answer choice with one of these codes. Each question should
use at least 2 different distractor types across its three wrong answers:

| Code | Type                            | Description                                             |
|------|---------------------------------|---------------------------------------------------------|
| CW   | Correct Rule, Wrong Application | Right legal standard, misapplied to these facts         |
| PA   | Plausible Argument, Not the Law | Sounds right as policy but isn't the doctrine           |
| TN   | True but Non-Responsive         | Accurate legal statement, doesn't answer this question  |
| IA   | Incomplete Analysis             | Gets part right, misses a critical element              |
| CE   | Common Student Error            | Reflects a typical misconception or conflation          |
| DC   | Doctrine Confusion              | Applies analysis from the wrong legal framework         |
| SA   | Superficially Attractive        | Matches a surface feature but misses the deeper issue   |

## Difficulty Calibration

### Per-Cluster Target
- 1-2 questions: Moderate (70-85% of well-prepared students get it right)
- 2-3 questions: Hard (40-65% of well-prepared students)
- 0-1 question: Very Hard / Discriminating (20-40% of well-prepared students)

Not every cluster needs a VH item. Distribute VH items across the exam so
that roughly 10-15% of all questions are VH. Overloading clusters with
hard and very hard items increases construct-irrelevant difficulty.

### Difficulty Estimate Scale
Tag each question with an estimated difficulty:
- **M** (Moderate): Straightforward application of a clear rule to facts
- **H** (Hard): Requires multi-step reasoning, factor balancing, or distinguishing
  similar doctrines
- **VH** (Very Hard): Requires transfer to novel facts, resolving genuine ambiguity,
  or recognizing non-obvious doctrinal boundaries

### Difficulty Should Come From
- Analytical complexity (multi-step reasoning)
- Factual ambiguity (facts cut both ways, requiring judgment)
- Doctrinal precision (distinguishing similar concepts)
- Transfer distance (how far the facts are from course materials)

### Difficulty Should NOT Come From
- Trick wording or double negatives
- Obscure or peripheral doctrinal points
- Ambiguity in what the question is asking
- Two genuinely defensible correct answers

## Quality Assurance Framework

Quality assurance occurs at four stages, numbered in execution order.
Stages 1–3 run during content development (before document generation).
Stage 4 runs after document generation as a blocking output gate.

### Stages at a glance

| Stage | When | What | Blocking? |
|-------|------|------|-----------|
| 1 | During content development | Per-question item-writing rules | Mandatory |
| 2 | During content development | Substantive review (adversarial challenge, fact dependency) | Mandatory |
| 3 | During content development | Exam-level distribution summary | Lightweight |
| 4 | After document generation | Programmatic output validation of .docx files | **Blocking gate** |

### Stage 1: Structural Review (Mandatory)

Check every question against these item-writing rules (Haladyna-Downing-Rodriguez).
Violations are empirically associated with decreased discrimination and
measurement error.

**Content rules:**
- [ ] Each item tests a single, specific doctrinal concept or skill
- [ ] Content is important and non-trivial (no peripheral minutiae)
- [ ] Novel fact application is used rather than restating course material verbatim
- [ ] Each item is independent — answering it does not require information
      from another item's answer

**Stem rules:**
- [ ] The stem presents a clear, focused problem or question
- [ ] The stem contains the central idea; answer choices complete or respond
      to it without redundancy
- [ ] The stem is positively worded (no "which is NOT" or negatively phrased stems)
- [ ] The stem contains no irrelevant information designed to trick rather than test
- [ ] The stem is grammatically compatible with all answer choices

**Answer choice rules:**
- [ ] There is one and only one defensible best answer
- [ ] All distractors are plausible to a student with partial knowledge
- [ ] Answer choices are homogeneous in content type (all are legal conclusions,
      or all are factual statements, or all are arguments — not a mix)
- [ ] Answer choices are roughly similar in length and specificity
- [ ] Answer choices are listed in a logical or natural order where applicable
- [ ] No "all of the above" or "none of the above"
- [ ] No compound answers ("(a) and (b)")
- [ ] No overlapping answer choices (where selecting one logically entails another)
- [ ] Each answer choice states one legal proposition — avoid compound
      "assertion + because + rationale" structures that turn options into
      mini-briefs. Move embedded rationales to the answer key.
- [ ] Answer choices avoid absolute terms ("always," "never,"
      "automatically," "categorically," "conclusively," "per se") unless
      doctrinally accurate — these serve as unintended cueing that allows
      test-wise students to eliminate distractors without doctrinal
      knowledge. Absolute terms should appear roughly equally in correct
      and incorrect options, or not at all.
- [ ] No grammatical cues (singular/plural mismatches, article agreement)
- [ ] No convergence cues (correct answer overlaps most with other options)

Note: answer choice length balance and correct answer position distribution
are checked programmatically by Stage 4 with defined thresholds. Do not
duplicate those checks here — Stage 1 focuses on content-level item-writing
rules that require human judgment.

### Stage 2: Substantive Review (Mandatory)

These tests catch genuinely flawed questions. Do not skip them.

**Single best answer test:**
- For each question, write a 2-3 sentence explanation of why the correct
  answer is right. If this cannot be done clearly and concisely, revise.

**Distractor justification:**
- For each wrong answer, articulate specifically why it is wrong. Tag
  each with its distractor taxonomy code. If you cannot articulate a
  clear reason it's wrong, revise.

**Adversarial challenge (critical):**
- For each question, argue the best possible case for each wrong answer
  being correct.
- If any wrong answer's best case is genuinely competitive with the
  correct answer — meaning a reasonable expert could defend it —
  revise the facts, stem, or answer choices until one answer is clearly best.
- Document close calls as "Challenge notes" in the answer key.

**Fact dependency test:**
- Cover the narrative and read only the stem and answer choices. If you
  can answer correctly without the narrative, the question is testing
  general knowledge, not application. Revise.

**Course material alignment test (construct alignment):**
- For each question, trace the tested doctrine back to a specific source
  in the course materials: reading assignment (with page range or section),
  slide deck (with topic), and transcript emphasis (if available).
- If the question requires knowledge not found in any assigned material,
  revise or flag for the professor.
- Questions testing HIGH-emphasis doctrines (in readings + on slides + in
  problems + in transcripts) should outnumber questions testing MEDIUM
  doctrines. The emphasis map built in workflow step 4 guides this balance.

### Stage 3: Exam-Level Summary (Lightweight)

After generating all questions, compile a one-page summary. Do not
over-invest in predicted statistics — they're estimates, not measurements.

- **Difficulty spread**: Count of M / H / VH questions. Flag if the mix
  is lopsided (e.g., all Hard, no Moderate).
- **Cognitive taxonomy distribution**: Actual vs. target percentages (±5%).
  Adjust if a category is missing entirely.
- **Coverage balance**: Actual vs. syllabus-derived weights (±10%).
- **Adversarial challenge log**: List any questions where the challenge
  identified a close call, with the resolution.
- **Flagged items**: Any questions with suspected non-functioning distractors
  or structural concerns surviving Stage 1.

Note: correct answer position distribution and answer choice length balance
are verified programmatically by Stage 4. Do not duplicate those checks here.

### Stage 4: Output Validation Gate (Blocking)

This stage catches catastrophic defects — missing content, mismatched
documents, broken structure — that would make the exam undeliverable.

**Run the reference validation script** located at
`~/.claude/skills/law-mcq-generator/validate_mcq.py` (CLI) or write
and execute an equivalent script (web). Do not eyeball these checks.

```
python3 ~/.claude/skills/law-mcq-generator/validate_mcq.py \
  path/to/exam.docx path/to/answer_key.docx
```

The script checks all of the following. Every check must PASS.

**Exam document — narrative completeness:**
- [ ] Every fact pattern has narrative text between the subtitle
      ("The one with the...") and the first question. A fact pattern
      with only a header and questions is a blocking failure.
- [ ] Each narrative is between 200 and 400 words.

**Exam document — question structure:**
- [ ] Every question has exactly 4 answer choices labeled (a) through (d),
      appearing in order immediately after the stem.
- [ ] Question numbering is sequential (1, 2, 3, ...) with no gaps,
      no duplicates, and the total matches the planned count.
- [ ] Each "Questions X through Y relate to Fact Pattern [LETTER]"
      header correctly states the question range that follows.
- [ ] No two answer choices within the same question have identical text.

**Exam document — answer choice balance:**
- [ ] No question has a "longest answer is correct" pattern: the correct
      answer's character count must not exceed 1.4× the median character
      count of all four choices in the same question. If it does, lengthen
      distractors or trim the correct answer.
- [ ] Across the full exam, correct answer position distribution is
      within ±2 of uniform (for 40 questions with 4 options, each letter
      should appear 8–12 times).
- [ ] Within each fact pattern cluster, correct answers use at least
      3 different letters (for clusters of 5+ questions) or at least
      2 different letters (for clusters of 3–4 questions).

**Exam document — narrative-question coherence:**
- [ ] Every proper noun or entity name (capitalized multi-word name like
      "NovaDyne Robotics," "Dr. Tamura," "PathSense") that appears in a
      question stem within a cluster also appears somewhere in the
      cluster's narrative text or in an "Assume for purposes of this
      question only" instruction within the cluster. A question that
      references a character or entity not introduced in the narrative
      is a blocking failure.

**Cross-document consistency:**
- [ ] Every question number in the exam document has a corresponding
      "Question N" entry in the answer key document.
- [ ] Every "Correct Answer: (X)" in the answer key names a letter
      (a–d) that corresponds to an actual answer choice in the exam.
- [ ] The answer key's distractor analysis for each question covers
      exactly 3 choices (the three non-correct letters). No missing
      entries, no extra entries.
- [ ] Every taxonomy code in the answer key is a valid code from the
      defined set (EA, AE, FB, FS/RI, DD, NR) or a course-preset alias.
- [ ] Every difficulty code is valid (M, H, or VH).
- [ ] The exam-level summary statistics (difficulty counts, position
      counts, taxonomy counts, coverage counts) are arithmetically
      correct — they match a fresh recount from the per-question data.

**If any check fails:** fix the defect in the generation code, regenerate
the documents, and re-run the validation script. **If the same check
fails twice,** stop and report the systematic issue to the user — do not
retry a third time. A repeated failure indicates a bug in the generation
logic, not a transient error.

## Output

Generate TWO Word documents (.docx) using python-docx.

### Document Formatting

Both documents should use consistent Penn Law formatting:

- **Font**: Cambria 12pt throughout (body, headings, answer choices)
- **Margins**: 1" on all sides
- **Line spacing**: 1.15 (`w:line="276" w:lineRule="auto"`)
- **Paragraph spacing**: `w:after="160"` for body text
- **Headings**: Cambria 12pt bold, same size as body — weight distinguishes them
- **Page numbers**: centered footer, Cambria 10pt italic, "Page x of y."

### Document 1: Exam Questions

- Header: "[SCHOOL NAME]" | "[COURSE NAME]: FINAL EXAM" | "[SEMESTER YEAR]"
- Title page with course name, professor name, school name, and instructions
- For each fact pattern:
  - "Questions X through Y relate to Fact Pattern [LETTER]"
  - "FACT PATTERN [LETTER]" centered heading
  - Subtitle in italics: "The one with the [thing]"
  - Narrative text
  - Numbered questions with lettered answer choices (a) through (d)
- Page numbers centered at bottom
- "[ END OF EXAM ]" after the last question

### Document 2: Answer Key with Quality Analysis

Per-question analysis including:
- Question number and correct answer
- **Course material source** (specific reading assignment, slide topic, and
  transcript emphasis where available — construct alignment trace)
- Cognitive taxonomy code (EA/AE/FB/FS/DD/NR or preset labels)
- Difficulty estimate (M/H/VH)
- Doctrinal basis (specific rule, test, or case from course materials)
- Explanation of correctness (2-3 sentences)
- Distractor analysis (taxonomy code, why it's wrong)
- Challenge notes where applicable

Exam-Level Summary at the end (see Stage 3 above).

Save both files to `~/Downloads/` (CLI) or `/mnt/user-data/outputs/` (web), or to a user-specified path.

## Workflow Summary

1. Identify course (check presets) → confirm with user
2. Ask for question count, materials path (if not preset), and any preferences
3. Read syllabus → extract course metadata → calculate coverage distribution → present to user
4. Read course materials (readings, slides, transcripts, problems, debriefs) → build emphasis map
5. Present emphasis map to user for steering
6. Plan narrative clusters and question allocation → present to user → get approval
7. Generate narratives and questions
8. **Stage 1 QA**: Per-Question Structural Review — fix any item-writing violations
9. **Stage 2 QA**: Substantive Review — adversarial challenge, distractor justification, fact dependency, construct alignment
10. **Stage 3 QA**: Exam-Level Summary — distributions, flagged items
11. Generate both output documents
12. **Stage 4 QA**: Output Validation Gate — run `validate_mcq.py` against the generated .docx files. **This is a blocking gate.** If any check fails, fix and regenerate. If the same check fails twice, stop and report the issue to the user.
13. Present both files to user

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
