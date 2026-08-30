# Output formats and rubric structure

Extracted from `law-essay-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Outputs

Generate **four Word documents (.docx)** per essay using python-docx.

### Document Formatting

All documents use Penn Law formatting:
- **Font:** Cambria 12pt throughout (body, headings, answer choices)
- **Margins:** 1" on all sides
- **Line spacing:** 1.15
- **Paragraph spacing:** `w:after="160"` for body text
- **Headings:** Cambria 12pt bold, same size as body
- **Page numbers:** centered footer, Cambria 10pt italic, "Page x of y."

Read the `law-document` skill for detailed .docx formatting conventions:
`~/.claude/skills/law-document/SKILL.md` (CLI) or
`/mnt/skills/user/law-document/SKILL.md` (web).

### Output 1: Exam Question

- Title page: school name, course name, professor, semester, time limit,
  word limit, instructions
- "ESSAY [N]" centered heading
- Subtitle in italics: "The one with the [thing]"
- Fact pattern (justified)
- Call of the question (bold)
- Page numbers centered at bottom

### Output 2: Issue Checklist / Rubric

For each issue in the fact pattern:

```
ISSUE [N]: [Name] — [X] points
SOLO Level: [Unistructural / Relational / Extended Abstract]
Doctrinal Area: [Trade Secret / Patent / Copyright / Trademark / ROP]
Source: [reading, page range] → [slide coverage] → [transcript emphasis]

Full credit ([X] pts):
— Required elements (ALL must appear for full credit):
   CASE/STATUTE: [specific case name or statutory section the student must
     invoke — e.g., "TrafFix Devices v. Marketing Displays" or "§ 1201(a)(2)"]
   FACT REFERENCE: [specific fact from the pattern the student must cite —
     e.g., "the expired utility patent on the honeycomb sole"]
   ANALYTICAL MOVE: [the specific doctrinal step — e.g., "applies the
     two-part Mayo test at Step 2" or "balances Sleekcraft factors"]
— Quality indicators (strengthen the analysis but not required):
   [e.g., "addresses counterargument that the design is aesthetically
   functional" or "connects to the trade secret disclosure issue"]

Partial credit ([Y] pts):
— [specific criteria — e.g., "identifies the issue and states the correct
   framework but applies superficially without referencing specific facts"
   or "applies well but uses the wrong framework"]

No credit:
— [e.g., "misses the issue entirely" or "applies a completely inapplicable
   doctrine"]

Common errors (AI grader should flag and deduct):
— [specific wrong answer]: [why it's wrong]
   e.g., "Applies the Abercrombie spectrum to product design trade dress —
   this is a Wal-Mart v. Samara question, not an Abercrombie question"
```

**Rubric marker consistency rule:** Every "Required element" must use one of
the three marker types (CASE/STATUTE, FACT REFERENCE, ANALYTICAL MOVE). This
ensures the AI grading tool can match student text against rubric criteria
using a consistent vocabulary. Do not use vague markers like "discusses
functionality" or "addresses the issue." Name the case, the fact, and the
doctrinal step.

After all issues, include summary tables:
- **Point distribution by SOLO level** (verify ~30% / ~45% / ~25%)
- **Point distribution by doctrinal area** (verify proportional to coverage ±10%)
- **Cross-doctrinal bonus issues** — places where connecting two regimes earns
  points that siloed analysis misses

### Output 3: Model Answer

- An A+ analysis written **within the student word limit**
- Organized **by issue, not by regime** — demonstrates the cross-cutting
  analysis the rubric rewards
- For each issue: states the framework, applies to specific facts, argues
  both sides, reaches a conclusion
- **Cross-doctrinal synthesis moves** are explicitly flagged (e.g.,
  "[CROSS-DOCTRINAL: This point connects the trade secret analysis to the
  patent disclosure issue]")
- Demonstrates that a complete analysis is achievable within the word limit

### Output 4: Quality Analysis

This document explains *why* the essay is well-designed. It serves two
purposes: letting the professor evaluate the skill's work, and providing
language for defending the exam's validity.

Contents:
- **Construct alignment table** — every issue mapped to reading source,
  slide coverage, and transcript emphasis
- **SOLO distribution analysis** — actual point distribution across
  unistructural/relational/extended abstract, with explanation of how the
  layering creates discrimination (what a C student sees vs. what an A
  student sees)
- **Cross-doctrinal design explanation** — identifies the central asset or
  conduct where regimes overlap and explains why this forces comparative
  analysis rather than siloed issue-spotting
- **Discrimination features** — catalogs each buried fact, ambiguous fact,
  and red herring, explaining what cognitive skill each tests and which
  SOLO level it serves
- **Emphasis alignment** — shows that highest-point issues correspond to
  highest-emphasis doctrines from the course materials
- **Theme engagement** — identifies which course themes the fact pattern
  engages and how (e.g., "the trade secret vs. patent election in Issues
  2-3 engages the channeling theme; the Extended Abstract synthesis issue
  rewards students who recognize this")
- **Difficulty calibration** — explains why the essay is achievable within
  the time and word limits (issue count, expected depth per issue, model
  answer as proof of feasibility)
- **Prior exam differentiation** (if prior exams were provided) — for each
  prior essay, documents how the new essay differs on scenario type, issue
  set, cross-cutting asset, and discrimination features
- **Potential weaknesses** — honest self-assessment of areas where the essay
  design could be stronger (e.g., "Right of publicity receives only 8% of
  points, which means only one issue tests this area")

## Rubric Format for Machine Grading

In addition to the human-readable rubric .docx (Output 2), generate a
machine-readable JSON file alongside it. This enables the essay dry run tool
and future grading tools to parse the rubric programmatically.

Save as `[exam_name]_rubric.json` in the same output directory as the .docx.

### JSON Schema

```json
[
  {
    "id": "TS-1",
    "description": "Trade secret analysis of the flavor-pairing database...",
    "doctrinal_area": "trade_secret",
    "solo_level": "unistructural",
    "full_credit": "Must cite UTSA §1(4)... Must reference that Mira compiled...",
    "partial_credit": "Identifies trade secret issue but doesn't address...",
    "no_credit": "Misses the trade secret issue entirely",
    "points_full": 10,
    "points_partial": 5,
    "points_no": 0
  }
]
```

### ID Convention

Use the pattern `[AREA]-[N]` where AREA is:
- TS = Trade Secret
- PAT = Patent
- CR = Copyright
- TM = Trademark
- ROP = Right of Publicity
- GEN = General / Cross-cutting
- RH = Red Herring (0 points, flagged for deduction if over-analyzed)

### Required Fields

Every issue must include all of: `id`, `description`, `doctrinal_area`,
`solo_level`, `full_credit`, `partial_credit`, `no_credit`, `points_full`,
`points_partial`, `points_no`.

The `full_credit`, `partial_credit`, and `no_credit` fields should contain
the same textual markers as the .docx rubric (CASE/STATUTE, FACT REFERENCE,
ANALYTICAL MOVE) so the grading tool can match student text against criteria.
