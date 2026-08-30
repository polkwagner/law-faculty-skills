# Voice and AI-tell checks

Extracted from `law-document/SKILL.md` to keep the skill body small; this file loads only when read.

## AI Writing Tell Check

Before delivering any document, scan the full text for these common AI writing patterns. They signal machine-generated prose and undermine credibility. Fix every instance found.

**Filler phrases to cut or replace:**
- "a wide range of" — replace with "many," "diverse," or just drop it
- "a variety of" — same treatment
- "it is important to note that" / "it is worth noting that" — banned; cut entirely
- "taken together" — AI transition; just start with the conclusion
- "reflecting the breadth of" — wordy; say it directly
- "in a structured way" / "in a meaningful way" / "in a comprehensive manner" — filler; cut
- "the larger point is" — throat-clearing; lead with the point

**Overused words to vary or cut:**
- "several" — AI defaults to "several" when it doesn't know the count. If it appears more than once in a document, vary with "some," "a few," "a number of," or give the actual number
- "curated" — AI favorite; usually unnecessary
- "robust" — banned per CLAUDE.md; be specific about what makes something strong
- "landscape" — banned per CLAUDE.md
- "nuanced" — AI filler; say what the nuance actually is
- "multifaceted" — cut; describe the actual facets instead
- "leveraging" / "utilizing" — banned; use "using"

**Structural tells:**
- Identical sentence patterns repeated across consecutive paragraphs or bullets (e.g., every bullet starting with "This program..." or every paragraph opening with "The...")
- Trailing summary lists that restate what was just said ("spanning X, Y, Z, and W")
- Overwrought framing where plain language would do ("spans every stage of the J.D. program" vs. "from all three class years")
- Excessive parallel structure in prose (fine in bullet lists, robotic in paragraphs)

**Em-dashes and semicolons:**
- Both are normal parts of [Your Name]'s prose. Keep them when they clarify a relationship, interruption, or qualification. Revise only mechanical repetition, ornamental punctuation, or a sentence made harder to follow; do not apply a numerical limit.

This check applies to all output — documents, memos, emails, and any prose produced on the user's behalf.

**Automated review:** After writing the document file:
1. If the `factual-reviewer` agent is available, spawn it and pass it the file path. Fix any factual issues it flags.
2. If the factual reviewer lists claims needing live verification, if the `fact-verifier` agent is available, spawn it with those claims. Correct any contradicted claims; flag unverifiable ones for the user.
3. If the `voice-style-checker` agent is available, spawn it and pass it the file path. Fix any style issues it flags.
Complete all steps before delivering to the user.

---
