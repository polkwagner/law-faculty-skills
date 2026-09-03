# Output formats and file generation

Extracted from `law-mcq-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Output

Generate content in two phases:

1. **Draft phase (markdown):** Write all content as `.md` files first.
   Run all QA stages (1-3) against the markdown drafts. Iterate and
   fix until every stage passes. Do not generate `.docx` files until
   all quality reviews are satisfied.

2. **Production phase (docx + csv):** Once the markdown drafts pass
   QA, generate the final `.docx` files from the approved content
   using pre-formatted templates, then generate the CSV. Run Stage 4
   validation on the `.docx` files as a final gate.

This separation keeps the revision loop fast (editing markdown is
cheaper than regenerating `.docx` files) and prevents wasted work on
documents that will need to be regenerated after QA fixes.

### Markdown Draft Files

Generate three draft files during the draft phase:

- `draft_full_set.md` — exam questions (all fact patterns + questions
  + answer choices, in delivery order)
- `draft_answer_key_full.md` — full answer key with all per-question
  metadata, explanations, and distractor analysis. Every distractor
  entry must be prefixed with the answer choice letter:
  `- (b) \[PA\]: explanation`. Never omit the letter — it identifies
  which answer choice the analysis refers to.
- `draft_answer_key_student.md` — student-facing answer key (correct
  answers + concise explanations + source citations only)

Use standard markdown formatting: `**bold**` for headings, `>` for
blockquotes (answer choices), `---` for em-dashes, `*italic*` for
case names and emphasis. These drafts are the authoritative source —
the `.docx` files are generated from them.

### Templates (for production phase)

Templates (`exam_template.docx`, `answer_key_template.docx`,
`student_answer_key_template.docx`) are stored in this skill's directory with
pre-defined styles. Use `gen_docx.py` in this skill's directory to build the
documents — it locates the templates relative to itself.

Each template contains placeholder paragraphs (one per style) to keep
style definitions alive. **Clear all placeholder paragraphs before
adding content** — they exist only to preserve the style XML.

### Page Setup (all documents)

- **Paper size:** Letter (8.5" × 11")
- **Margins:** 1" on all sides
- **Base font:** Times New Roman (inherited from Normal style)
- **Footer:** `Page X of Y.` — centered, auto-updating PAGE/NUMPAGES
  field codes (preserved from template)

### Document 1: Exam Questions

**Template:** `exam_template.docx`

**Header:** `[ COURSE CODE` + TAB + `COURSE NAME` + TAB + `SEMESTER YEAR ]`
Update the header text after loading the template. The tab stops are
pre-configured for three-column layout.

**Styles available in the exam template:**

| Style | Purpose | Key Properties |
|---|---|---|
| `First Paragraph` | Title page school name line | Body Text base; center it explicitly; bold + 14pt on the run |
| `Body Text` | Narrative text, instructions, centered headers | Justified, 1.5 line spacing, ~9pt space before/after |
| `Title` | `FACT PATTERN A` headers | Bold, centered, no space after |
| `Subtitle` | `The one with the [thing]` | Italic, centered, no space before |
| `Question` | Question stems (`1.` + TAB + stem text) | Hanging indent (left 1", first line -0.5"), 30pt space before |
| `Answer` | Answer choices `(a)` through `(d)` | Right indent 0.33", 1.15 line spacing, auto-numbered `(a)` format |
| `List Paragraph` | Bulleted instruction items | Left indent 0.5" |

**Answer choice numbering:** The `Answer` style uses Word list numbering
with `lowerLetter` format producing `(a)`, `(b)`, `(c)`, `(d)` labels
automatically. The template contains the numbering definitions. When
generating, create exactly 4 `Answer`-styled paragraphs per question.
If auto-numbering restart proves unreliable across questions, fall back
to prepending `(a) `, `(b) `, etc. as text in each Answer paragraph —
this is more reliable with python-docx.

**Title page structure (in order):**

1. School name (`First Paragraph`, centered, bold, 14pt on the run)
2. Course name with code (`Body Text`, centered, italic on the run)
3. `FINAL EXAMINATION — [SEMESTER YEAR]` (`Body Text`, centered)
4. Professor name (`Body Text`, centered)
5. Empty line (`Body Text`, centered)
6. `MULTIPLE CHOICE QUESTIONS` (`Body Text`, centered, bold on the run)
7. Empty line (`Body Text`, centered)
8. Instruction paragraphs (`Body Text`, justified — default alignment)
9. Instruction bullets (`List Paragraph`)

**Fact pattern structure (per cluster):**

1. `[ Questions X through Y relate to Fact Pattern [LETTER] ]` (`Body Text`, centered)
2. `FACT PATTERN [LETTER]` (`Title`)
3. `The one with the [thing]` (`Subtitle`)
4. Empty line (`Body Text`)
5. Narrative paragraphs (`Body Text` — justified, one paragraph per
   logical block of the narrative)
6. Questions: number + TAB + stem text (`Question`)
7. Answer choices: 4 paragraphs per question (`Answer`)

End with `[ END OF EXAM ]` (`Body Text`, centered).

### Document 2: Full Answer Key (Professor)

**Template:** `answer_key_template.docx`

**Styles available:**

| Style | Purpose |
|---|---|
| `First Paragraph` | `Question N` headers (bold on the run) |
| `Body Text` | Metadata lines, explanations, glossary, summary |
| `Compact` | Distractor analysis entries (plain text, no bullets) |
| `Normal` | Horizontal rule paragraphs (paragraph bottom border) |

**Document structure:**

1. Header block (school, course title, semester, professor)
2. **Notation glossary** — `KEY TO ANSWER KEY NOTATION` (centered, bold),
   followed by three sections:
   - **Cognitive Taxonomy Codes** (bold heading, then one line per code
     in 10pt: `EA = Element Application. [description].`)
   - **Difficulty Estimates** (bold heading, then one line per level
     in 10pt: `M = Moderate. [description].`)
   - **Distractor Taxonomy Codes** (bold heading, then one line per code
     in 10pt: `CW = Correct Rule, Wrong Application. [description].`)
   Bounded above and below by horizontal rules.
3. Per-question entries (see below), separated by horizontal rules
4. Exam-Level Summary at the end

**Horizontal rules:** Use a `Normal`-style paragraph with a bottom
border (`pBdr/bottom`: val=single, sz=6, color=808080, space=1) and
spacing before/after of 120 twips. Insert one before each question
except Question 1. This creates a thin gray line for quick visual
scanning.

**Per-question structure:**

1. `Question N` (`First Paragraph`, bold)
2. `Correct Answer: (x) | Taxonomy: XX | Difficulty: M/H/VH` (`Body Text`)
3. `Fact Pattern: [LETTER]` (`Body Text`)
4. `Doctrinal Area: [area]` (`Body Text`)
5. `Doctrinal Basis: [cases, statutes]` (`Body Text`)
6. `Course Material Source: [reading pp., class #]` (`Body Text`)
7. `Explanation: [2-3 sentences]` (`Body Text`, with "Explanation:" as
   a separate bold run followed by the content in a non-bold run)
8. `Distractor Analysis:` (`Body Text`, bold)
9. One `Compact` paragraph per distractor: `(letter) [CODE]: [explanation]`
   — prefixed with the answer choice letter in parens (e.g., `(b) [PA]:
   Delay in asserting...`), plain text, no bullets or numbering

**Content per question:**
- Course material source (specific reading assignment, slide topic, and
  transcript emphasis where available — construct alignment trace)
- Cognitive taxonomy code (EA/AE/FB/FS/DD/NR or preset labels)
- Difficulty estimate (M/H/VH)
- Doctrinal basis (specific rule, test, or case from course materials)
- Explanation of correctness (2-3 sentences, with inline case/statute
  citations drawn from the doctrinal basis)
- Distractor analysis (taxonomy code, why it's wrong)
- Challenge notes where applicable

Exam-Level Summary at the end (see Stage 3 in `references/qa-framework.md`).

### Document 3: Student Answer Key

**Template:** `student_answer_key_template.docx`

**Styles available:** `First Paragraph`, `Body Text`, `Normal`

**Structure:**

1. Centered header block (`Body Text`, centered):
   - School name
   - Course name with code
   - `[SEMESTER YEAR]`
   - Professor name
   - `ANSWER KEY FOR MULTIPLE CHOICE QUESTIONS`
2. Per question:
   - `Question N — Correct Answer: (x)` (`First Paragraph`, bold)
   - Explanation paragraph (`Body Text`) — concise version of the full
     answer key explanation (2-3 sentences, no distractor analysis)
   - `See: [reading], [class].` (`Body Text`, italic on the run)
   - Empty separator line (`Normal`)

### Document 4: CSV Answer Key

Generate a CSV file for quick-reference grading and data analysis. Columns:

| Column | Content |
|---|---|
| `Question #` | Question number (1, 2, 3, ...) |
| `Correct Answer` | Correct letter: `a`, `b`, `c`, or `d` |
| `Doctrinal Area` | E.g., `Patent`, `Copyright (Fair Use)`, `Trademark` |
| `Cognitive Taxonomy` | Taxonomy code: EA, AE, FB, RI, DD, NR |
| `Difficulty` | Difficulty estimate: M, H, VH |
| `Distractor 1` | Answer choice letter: `b`, `c`, etc. |
| `Distractor 1 Code` | Distractor taxonomy code: PA, CE, CW, etc. |
| `Distractor 2` | Answer choice letter |
| `Distractor 2 Code` | Distractor taxonomy code |
| `Distractor 3` | Answer choice letter |
| `Distractor 3 Code` | Distractor taxonomy code |

Plain letters only — no parentheses, no explanation text. The CSV is
for quick-reference grading and data analysis, not for reading.

Save all files to `~/Downloads/` (CLI) or `/mnt/user-data/outputs/` (web),
or to a user-specified path.
