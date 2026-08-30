# Double-read review pass

Extracted from `law-essay-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Double Read

After completing all four outputs (exam question, rubric, model answer,
quality analysis), perform a fresh re-read of the entire work product as
a second pair of eyes. This is a separate step from the self-check — the
self-check verifies structural compliance; the double read catches
substantive problems that checklists miss.

### How to Double Read

1. **Re-read the fact pattern cold.** Read it as a student would — without
   the rubric in front of you. Ask:
   - Are the facts clear and unambiguous where they should be?
   - Are the buried facts actually findable on a careful read, or are they
     so hidden that even a strong student would miss them?
   - Does the timeline make sense? Are there contradictions or impossible
     sequences?
   - Is there anything a student might reasonably misread that would lead
     them down a wrong path through no fault of their own?
   - Does the fact pattern inadvertently invite analysis under legal
     frameworks outside the course (e.g., contract law, antitrust, tort,
     constitutional law) that students were not taught? If so, either
     revise the facts to eliminate the outside-course issue or add a scope
     note to the call of the question ("Limit your analysis to intellectual
     property issues").

2. **Re-read the rubric against the fact pattern.** For each issue:
   - Can the required CASE/STATUTE, FACT REFERENCE, and ANALYTICAL MOVE
     actually be performed with the facts provided? (If the rubric expects
     students to apply *TrafFix* but the fact pattern doesn't include facts
     about functionality, the rubric is broken.)
   - Are the partial credit criteria distinguishable from full credit? Could
     a grader (human or AI) reliably tell the difference?
   - Are the common errors realistic — would a student actually make these
     mistakes given these facts?

3. **Re-read the model answer against the rubric.** Verify that the model
   answer would earn full credit on every issue under the rubric's own
   criteria. If the model answer doesn't reference a required element, either
   the rubric or the model answer needs revision.

4. **Check for internal consistency across all four documents.** The fact
   pattern, rubric, model answer, and quality analysis should all describe
   the same issues with the same names, the same point values, and the same
   doctrinal frameworks. Flag any discrepancies.

If the double read reveals problems, fix them before running the self-check.

**AI tell scan:** After the double read, if the `voice-style-checker` agent is available, spawn it and pass it the fact pattern file path. Fix any issues it flags before running the self-check.
