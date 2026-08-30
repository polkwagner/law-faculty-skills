# Quality Assurance Framework

Extracted from `law-mcq-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Quality Assurance Framework

Quality assurance occurs at four stages, numbered in execution order.
Stages 1–3 run during content development (before document generation).
Stage 4 runs after document generation as a blocking output gate.

### Stages at a glance

| Stage | When | What | Blocking? |
|-------|------|------|-----------|
| 1 | During content development | Per-question item-writing rules | Mandatory |
| 2 | During content development | Substantive review (adversarial challenge, fact-answer alignment, fact dependency) | Mandatory |
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

**Fact-answer alignment check (critical):**
- For each question, identify the factual characterization the correct
  answer depends on (e.g., "this article is critical analysis," "this
  use is commercial," "this work is a derivative work").
- Trace that characterization back to the fact pattern. Verify the
  narrative's language — especially titles, labels, descriptions, and
  action verbs — actually conveys the characterization to a cold reader.
- If the fact pattern is neutral on, or contradicts, a premise the
  correct answer requires, this is a **blocking issue**. Revise the
  narrative to align with the intended answer, or revise the question
  to match what the narrative actually conveys.
- Pay special attention to titles and names embedded in fact patterns —
  these carry strong analytical signals. A title like "How to Recreate X"
  implies instruction; "Where Tradition Meets Hype" implies criticism.
  The title must be consistent with the question's analytical framing.

**Fact dependency test (two-direction):**
- **Direction 1 — Without facts:** Cover the narrative and read only the
  stem and answer choices. If you can answer correctly without the
  narrative, the question is testing general knowledge, not application.
  Revise to make the answer depend on specific facts. The most common
  cause of fact-independence is distractors that state wrong legal
  principles — see the Distractor Mix Requirement above.
- **Direction 2 — From facts only:** Now read the narrative and the stem
  without the answer key. Answer based solely on what the facts convey.
  If the fact-informed answer differs from the keyed correct answer, the
  narrative's framing is misleading and needs revision. This catches
  cases where the facts point toward a distractor — the most dangerous
  type of misalignment because the question punishes careful readers.

**Automated fact-dependency validation (optional but recommended):**
After generating the full exam, run the no-materials test from the MCQ
dry-run infrastructure at `~/code/mcq-dry-run/`. This sends the exam
to two AI models (GPT-4o and Gemini Flash) without any fact patterns
or course materials. Questions both models answer correctly are
fact-independent candidates. Target: fewer than 25% of questions
answered correctly by both models without materials. If this threshold
is exceeded, the distractor mix is likely wrong — too many distractors
state incorrect legal principles rather than misapplying correct ones.
Run with: `python run_phase.py phase1` (cost: ~$0.10, time: ~5 min).

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

**Flag resolution gate:** Before proceeding to document generation,
every flagged item from Stages 1-3 must be either (a) resolved by
revising the question, answer, or explanation, or (b) explicitly
accepted by the user with documented justification. Do not defer flags
with notes like "being addressed separately" — they will not be
addressed separately. Unresolved flags are a blocking condition for
document generation, just as Stage 4 failures are a blocking condition
for delivery.

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
- [ ] Every distractor analysis entry begins with the answer choice
      letter in parentheses — e.g., `(b) [PA]:`. An entry that starts
      with `[PA]:` without the letter prefix is a blocking failure.
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
