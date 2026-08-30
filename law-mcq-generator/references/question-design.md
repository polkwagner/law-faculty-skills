# Question design, taxonomies, and difficulty calibration

Extracted from `law-mcq-generator/SKILL.md` to keep the skill body small; this file loads only when read.

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

### Distractor Mix Requirement (Critical)

Each question's three distractors MUST use a mix of error types:
- **~2 distractors: Correct legal principle, wrong application to the
  specific facts** (CW, IA, or SA codes). These require reading the fact
  pattern to evaluate — a student who knows the doctrine but hasn't read
  the facts cannot eliminate them.
- **~1 distractor: Subtly wrong legal principle** (CE, PA, or DC codes).
  Tests doctrinal knowledge. Must sound plausible — a common student
  misunderstanding, not an obvious fabrication.

**Why this matters:** The most common MCQ generation failure mode is
distractors that ALL state obviously wrong legal principles. When every
wrong answer is eliminable from pure doctrinal recall, students can answer
correctly without reading the fact patterns — defeating the purpose of
fact-pattern-based assessment. In testing, this pattern made 92% of
questions answerable from general knowledge alone.

**The fix is not to make ALL distractors state correct law.** That
overcorrects and fails to test whether students know the doctrine at all.
The mix ensures that (1) doctrinal knowledge helps (eliminates ~1
distractor) but (2) students must still read and apply the facts to
choose among the remaining options.

**Self-check:** For each question, ask: "If I cover the fact pattern and
read only the stem and choices, can I identify the correct answer?" If
yes, too many distractors state wrong law. At least 2 of 3 distractors
should require the fact pattern to evaluate.

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

Tag every wrong answer choice with one of these codes. Each question MUST
use at least 2 different distractor types across its three wrong answers,
and MUST follow the distractor mix requirement from the Answer Architecture
section (~2 fact-dependent distractors + ~1 doctrine-testing distractor):

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
