# Assessment science, fact-pattern design, and prompt style

Extracted from `law-essay-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Assessment-Science Framework

### SOLO Taxonomy for Issue Layering

Every essay is designed with issues at three complexity levels:

| SOLO Level | What It Looks Like | Rubric Role | Target % of Points |
|---|---|---|---|
| **Unistructural** | Spot a single doctrine and apply it correctly (e.g., "this qualifies as a trade secret because...") | The floor — most students get these | ~30% |
| **Relational** | Connect multiple doctrines, weigh competing arguments, recognize that one claim is stronger than another (e.g., "the patent claim is weaker than the trade secret claim here because...") | Separates B from C | ~45% |
| **Extended Abstract** | Synthesize across regimes, recognize strategic tradeoffs, identify issues the fact pattern deliberately leaves ambiguous (e.g., "the best overall IP strategy depends on whether the client plans to license or litigate") | Separates A from B | ~25% |

Tag every issue with its SOLO level during design. This ensures layering is
intentional, not accidental.

### Construct Alignment

Every testable issue must map to something the students were actually taught.
The skill produces an explicit alignment table:

```
Issue → Reading source (casebook pages) → Slide coverage → Transcript emphasis
```

If an issue cannot be traced to the assigned materials, it cannot appear on
the exam. No exceptions.

### Discrimination by Design

The fact pattern must include all of the following:
- **2-3 surface facts** that signal obvious issues (visible to everyone)
- **2-3 buried facts** whose legal significance emerges only on careful reading
  (parenthetical details, timeline implications, throwaway clauses)
- **1-2 ambiguous facts** that support arguments on both sides (the stronger
  argument is identifiable but not obvious)
- **At least one red herring** — a fact that looks legally significant but
  triggers a doctrine that does not actually apply (tests negative recognition)

## Fact Pattern Design

### Cross-Doctrinal Requirement (Non-Negotiable)

Every essay fact pattern must implicate **at least 3 doctrinal areas** from
the course. The areas must **overlap on the same facts** — not separate
sub-scenarios that happen to share a narrative. The student must decide which
doctrinal framework provides the strongest analysis for the same asset or
the same conduct.

For IP courses, "doctrinal areas" means IP regimes (trade secret, patent,
copyright, trademark, right of publicity). For other courses, the preset
defines the relevant doctrinal areas (e.g., for Contracts: formation,
interpretation, performance, remedies).

This is the core design principle: the A student analyzes all applicable
frameworks and explains which is strongest and why. The B student analyzes
each framework in isolation. The C student identifies only the obvious one.

### Structure
- **600-1200 words** (longer than MCQ narratives, shorter than a full case)
- A single coherent scenario with **named characters**, a **realistic industry
  setting**, and a **clear timeline**
- **Temporal markers** where they matter doctrinally (filing dates, first use
  dates, publication dates, employment start/end dates, patent expiration dates)
- A memorable subtitle: "The one with the [thing]"
- **No real company names or real people** in the narrative
- The call of the question follows the user's chosen **prompt style** (see
  the Prompt Style section above). If the user chose open-ended, use a
  regime-neutral directive. If role-playing, frame around a client and
  specific task. If no preference was stated, default based on the exam
  structure (single essay → open-ended; multiple essays → role-playing).

### Fact Engineering for Layering

| Fact Type | Purpose | Example |
|---|---|---|
| **Surface** | Signal obvious issues; visible to everyone | Employee leaves with client list → trade secret |
| **Buried** | Reward careful reading | Parenthetical noting the NDA was signed "during onboarding" with no additional consideration → enforceability issue |
| **Ambiguous** | Support arguments on both sides | Product shown at trade show "in a private suite by invitation only" → was this public disclosure? |
| **Red herring** | Test negative recognition | A character's distinctive catchphrase is copied → looks like right of publicity but the character is fictional |

### Cross-Cutting Design

The strongest essays present **a single asset or piece of conduct that could
be analyzed under multiple regimes** — forcing comparative assessment rather
than siloed issue-spotting. For example: a distinctive product design could
be trade dress (trademark), a design patent (patent), a copyrightable
sculptural work (copyright), or none of the above (functional, unoriginal,
or generic). The A student analyzes all three and explains which is strongest.

## Prompt Style

The call of the question can use one of two styles. Ask the user which they prefer, and recommend based on the exam structure:

### Open-Ended Analysis (Recommended for single-essay exams)

> "Analyze the intellectual property issues raised by the facts above. For each issue you identify, state the applicable legal framework, apply it to the facts, and assess the strength of each party's position."

**Tests:** Issue identification without prompting, multi-perspective analysis (both sides of each issue), organizational judgment, triage under word constraints.

**Recommended when:**
- The exam has only one essay question (the single essay must test cross-doctrinal breadth)
- The essay is designed to test cross-doctrinal synthesis (GEN-level issues)
- The essay is paired with a discrete-knowledge component (e.g., MCQs) that already tests specific doctrinal recall

**Trade-offs:** Higher issue-spotting burden on students. No organizational scaffolding — weaker students may produce disorganized answers. Requires balanced analysis rather than one-sided advocacy.

### Role-Playing Directive (Recommended for multi-essay exams)

> "[Client] has hired you to [write a memo / draft a letter / assess the risks]. [Specific directive about perspective, organization, or doctrinal scope]."

**Tests:** Professional writing in context, directed analysis from a specific perspective, depth within a narrower doctrinal scope.

**Recommended when:**
- The exam has multiple essay questions (each can afford to narrow its scope)
- The question targets specific doctrinal depth rather than breadth
- The professor wants to control the organizational structure of student answers

**Trade-offs:** Pre-selects doctrines (reduces issue-spotting burden), constrains perspective to one side, provides organizational scaffolding that may mask analytical skill.

### Choosing a Style

| Exam Structure | Recommended Style | Reason |
|---|---|---|
| 1 essay + MCQs | Open-ended | The single essay must test what MCQs cannot: integrated analysis, issue identification, triage |
| 2-3 essays, each focused | Role-playing | Each question can afford to narrow scope and go deeper |
| 1 essay, no MCQs | Open-ended or hybrid | Depends on how much ground the essay needs to cover |

A **hybrid** approach is also possible: use a role-playing setup ("You are counsel for X") but keep the directive open ("analyze the IP issues and advise your client"). This provides professional context without narrowing the doctrinal scope.
