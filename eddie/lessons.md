# Eddie lessons (manually curated)

This file captures editorial calibrations across sessions — corrections [Your Name] has made to
Eddie's findings that should persist into future reviews. The eddie-second-eyes agent
reads this file and applies its rules when reviewing Eddie's findings.

**How to add a lesson:**
1. Run `/eddie` and review the output.
2. If a finding was a false positive AND the same false positive will recur on similar
   documents in the future, add a lesson here.
3. Eddie also auto-suggests lessons in the "Suggested lessons.md additions" section of
   each report — copy them here when they look right.

**What NOT to add:**
- One-off context errors (specific to one document)
- Lessons that contradict the senior-editor profile or banned-phrases list
- Lessons that [Your Name] isn't sure about — these create noise

**Format:** one bullet per lesson. Include date for traceability. Project-scoped lessons
go under "Project-specific" with the project name.

## Calibrations

  - "ensure" is acceptable when used in a quoted policy or contractual clause — don't flag as banned phrase.  (2026-05-10, validation)

  - Institute and center names with ampersands in their official logo/branding (e.g., "Institute for Law & Economics", "Center for Technology, Innovation & Competition") may be written with "and" in running prose. Flagging the ampersand vs. "and" choice as a factual error is house-style overreach unless the document mixes both forms.  (2026-05-10, PCL AI Initiative groundwork v2)

  - Pandoc `>`-prefixed bullets in markdown rendered from a `.docx` source are a rendering artifact, not a defect in the underlying document; do not flag unless the markdown itself is the deliverable.  (2026-05-10, PCL AI Initiative groundwork v2)

  - Internal cross-references like "see Building Tier 3 below" inside a short, single-author internal planning document with explicit tier/section headers are not orphaned references; the orphan-reference flag should require either an actual broken pointer or evidence the document is meant to be excerpted/forwarded.  (2026-05-10, PCL AI Initiative groundwork v2)

  - The "trailing summary" AI-tell pattern applies to bullet lists that restate just-completed prose. A closing deliverables register with explicit deadlines (e.g., "By Labor Day: what's in hand") is structurally load-bearing — it converts pillar-organized content into a deadline-organized deliverables list — and should not be flagged as redundant.  (2026-05-10, PCL AI Initiative groundwork v2)

  - In formal legal correspondence (recommendation letters to judges, formal client letters), closing offers of availability such as "Please do not hesitate to contact me if I can provide any further information" are an established convention and should NOT be flagged as banned phrases. The CLAUDE.md banned phrase "Please don't hesitate to reach out" targets the outreach-initiation register typical of business email, not the availability-for-follow-up register of formal letter sign-offs.  (2026-05-11, Threlfall rec)

  - In recommendation letters, a "two-year TA role" framing paired with "I asked her back for a second year, and would gladly have her for a third" is not a temporal contradiction. The first describes the cumulative relationship; the second describes the original asking-back decision plus a forward-looking endorsement. Don't flag this pattern.  (2026-05-11, Threlfall rec)

  - In [Your Name]'s clerkship A-letters, the doctrinal-anchor block's "course + grade + difficulty" parallel structure (first course + grade, then prior course + grade, then a progression sentence) is the prescribed template architecture (Recommendations project CLAUDE.md, A-letter block 2), not an AI parallelism tell. Don't flag matched grade-sentence structure across the two-course progression.  (2026-05-16, Vantrease rec)

  - In recommendation/formal letters built from an established template, the template's fixed opener/closer pair is a house-style arc, not a register mismatch with the body. Example: the [Your Name] B+ template opens "I am pleased to recommend X" and closes "I offer X a strong and enthusiastic recommendation"; the A template opens "I write with the greatest enthusiasm to recommend X" and closes "I recommend X to you with my highest enthusiasm and without reservation." Don't flag the closer as over-warm relative to a measured body when it matches the template's paired opener. Multiple single-context agents independently flagging the closer is a cross-agent bias pattern, not corroboration.  (2026-05-16, Brackenridge rec)

  - When a project designates the candidate's resume/cover letter as the primary source of truth (e.g., the Recommendations project), the letter tracking the resume's label for a credential is correct practice. A divergent official-transcript label for the same, substantively undisputed credential is a minor verification note (P3), not a P1 — do not escalate to P1 on source-tier divergence alone when the underlying substance is undisputed.  (2026-05-16, Brackenridge rec)

  - Do not infer the recommender's relationship scope from the transcript or resume ("only one course, no TA/RA, therefore the character/demeanor claims are unsupported"). Faculty routinely advise, mentor, and counsel students outside any enrolled course, and that contact appears on no transcript. Flag personal-quality claims as an exposure risk only when the document itself shows no plausible basis — not merely because the course record is thin — and confirm with the recommender before treating an out-of-class-knowledge claim as overreach.  (2026-05-16, Brackenridge rec)


## Project-specific

(Empty — populate per project.)
