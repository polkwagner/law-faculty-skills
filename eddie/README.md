# Eddie the Editor

Eddie is a senior-level editorial review system for Claude Code. Modeled on the standards of top-tier publications — *The New York Times*, *Harper's*, *The Atlantic* — Eddie reviews any written document for factual accuracy, citation integrity, internal consistency, institutional sensitivity, voice compliance, and common AI failure modes. Eddie produces a prioritized revision report with a built-in self-check mechanism.

**Operating standard:** The question is never merely whether a sentence is probably right. The question is whether it can be justified, verified, and defended.

## Quick Start

```
/eddie path/to/document.md              # review a file (moderate intensity)
/eddie path/to/memo.docx be aggressive  # full-treatment review
/eddie light touch                      # quick pass on recent document
/eddie skip second read                 # skip the self-check pass
```

Eddie is invoked **only** via the `/eddie` slash command. It is not triggered automatically.

## What Eddie Reviews

Eddie reviews any written output: memos, emails, proposals, reports, policy documents, exam questions, class materials, white papers — anything with text that matters. The first argument that looks like a file path is the target. If no path is given, Eddie reviews the most recently discussed or produced document in the conversation.

## Intensity Levels

| Level | Default? | When to use | What it covers |
|-------|----------|-------------|----------------|
| **Light** | No | Quick sanity check before sending | Clear errors and high-risk factual claims only. No second-eyes pass. Fast. |
| **Moderate** | **Yes** | Standard pre-release review | Factual claims, citations, hidden claims, internal consistency, institutional sensitivity, voice/style, AI patterns. Includes second-eyes pass. |
| **Aggressive** | No | High-stakes documents (Dean's office, external audiences, legal exposure) | Everything moderate covers, plus: language precision, implied claims, hedging adequacy, structural discipline, every style detail. Includes second-eyes pass. |

Trigger with natural language: "be aggressive," "full treatment," "light touch," "quick pass," "just the big stuff."

At moderate intensity, Eddie skips Priority 4-5 items unless they are numerous enough to signal a systemic pattern.

## Architecture

Eddie dispatches up to six review agents, five in parallel and one sequential:

```
Read document → Identify type → Parse tuning → Scan for plans
                                                      │
                            ┌─────────────────────────┤
                            ▼                         ▼
                 ┌──────────────────────────────────────────┐
                 │  Parallel Agents (all run concurrently)  │
                 │                                          │
                 │  Agent 1: Factual & Citation Review      │
                 │  Agent 2: Adversarial, Structural &      │
                 │           Institutional Sensitivity       │
                 │  Agent 3: Voice & Style                  │
                 │  Agent 4: Plan Reconciliation (if plans) │
                 │  Agent 5: Internal Consistency            │
                 └──────────────────┬───────────────────────┘
                                    │
                                    ▼
                        Merge & Deduplicate
                        Identify Patterns
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  Agent 6: Second Eyes      │
                    │  (sequential — reviews     │
                    │   Eddie's own findings)    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                           Final Report
```

For short documents (under ~500 words), Eddie may do a single-pass review without dispatching agents.

### Agent Details

**Agent 1 — Factual & Citation Review**
Decomposes the document into discrete factual units and verifies each one. Audits citations at proposition level — does this source support *this specific claim*? Also watches for AI-specific patterns: fabricated specificity (invented numbers), consensus hallucination ("most scholars agree"), temporal confusion (wrong dates), and citation laundering (secondary sources hiding unverified chains).

**Agent 2 — Adversarial Reading, Structural Discipline & Institutional Sensitivity**
Answers one question: *"How could this document hurt the author?"* Three sub-lenses:
- *Adversarial reading* — hidden claims, orphaned references, false balance, scope creep. Reads as if the document will be seen by a hostile critic, the standards desk, or plaintiff's counsel.
- *Structural discipline* — is the message getting buried? Flags excessive background, redundant argumentation, scope sprawl, and defensive over-documentation.
- *Institutional sensitivity* — reads as if forwarded, FOIAed, or quoted in a faculty meeting. Checks role/authority boundaries, tone-to-power-dynamics, unintended signals, and exposure risk.

**Agent 3 — Voice & Style Review**
Checks against the author's voice baseline (from CLAUDE.md) and format-specific conventions for emails, memos, and documents. Flags banned phrases, hedging overload, repetition/padding, and gratuitous structure (documents that read like slide decks).

**Agent 4 — Plan Reconciliation** *(conditional)*
Only runs when planning artifacts exist (plans, outlines, notes, specs in the working directory or conversation). Compares the final document against every plan and flags omissions, drift, additions, and scope changes. Quotes both the plan language and the corresponding output.

**Agent 5 — Internal Consistency**
Cross-references the document against itself. Checks logical consistency (does the recommendation follow from the analysis?), numeric consistency (do figures match across sections?), and terminological consistency (is the same thing called the same thing throughout?).

**Agent 6 — Second Eyes** *(sequential, runs after merge)*
Eddie's own quality control. Reviews the merged findings against the original document and checks for false positives, priority miscalibrations, fix quality (would the suggested revision work?), blind spots, and over-editing. Runs by default at moderate and aggressive intensity. Skip with "skip second read" or "no second eyes."

## AI-Specific Failure Modes

Eddie watches for ten characteristic AI writing failures, distributed across agents 1-3:

| Pattern | Agent | Default Priority |
|---------|-------|-----------------|
| Fabricated specificity — invented numbers/dates/stats | 1 | P1-P2 |
| Consensus hallucination — "most scholars agree" without basis | 1 | P2 |
| Temporal confusion — wrong dates, anachronisms | 1 | P1 |
| Citation laundering — secondary source hiding unverified chain | 1 | P2 |
| Orphaned references — "as discussed above" pointing to nothing | 2 | P3 |
| False balance — artificial both-sides framing | 2 | P3 |
| Scope creep — unrequested content diluting focus | 2 | P3 |
| Hedging overload — excessive may/might/could | 3 | P3 |
| Repetition / padding — same point restated | 3 | P4 |
| Gratuitous structure — over-formatted like a slide deck | 3 | P4 |

## Output

Eddie produces two things:

### 1. Screen Summary
Printed directly to the conversation — a brief, scannable overview with issue counts by category and the 2-3 most important items to fix first.

### 2. Detailed Report (saved to file)
A markdown file saved to the current working directory:
- **Filename:** `Eddie_Review_[Topic-Slug]_[YYYY-MM-DD].md`
- Eddie reports the full path to the user.

The report includes:
- Summary and issue-count table (by category and priority)
- Prioritized revision list — each entry has location, current text, problem description, suggested fix, and confidence level
- Patterns section — recurring issues that suggest systemic problems
- Second Eyes section — corrections to Eddie's own findings, additional issues caught, and over-editing warnings

### Priority Scale

| Priority | Label | What it means |
|----------|-------|---------------|
| **1** | Critical | Factual error, legal risk, fabricated claim, logical contradiction, authority overreach |
| **2** | High | Citation doesn't support claim, overclaiming, exposure risk, unintended signals, plan contradictions |
| **3** | Medium | Imprecise language, orphaned references, hedging overload, tone mismatch, terminological drift |
| **4** | Low | Style issues with no accuracy impact, repetition, over-formatting, defensive over-documentation |
| **5** | Minor | Typos, formatting, minor polish |

## Voice and Style Standards

Eddie checks against the author's voice baseline and three format-specific style guides:

- **Universal:** Direct, active, collegial, confident, concise. No banned phrases (see SKILL.md for the full list). Em-dashes for asides. Short paragraphs.
- **Email:** Greeting/sign-off conventions, bold section headers, "So —" transitions.
- **Memo:** Opens with situation, clear recommendations, bullet lists introduced by full sentences, closes with next-steps paragraph, no personal sign-off.
- **Document:** Authoritative institutional writing, consistent voice, most important information first, no slide-deck formatting.

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill entry point for Claude Code — workflow, agent mandates, output format, style checklist, priority scale |
| `senior_editor_profile.md` | Eddie's editorial identity — core characteristics, skills, and professional attitude modeled on top-tier publication standards |
| `eddie_desktop_project_instructions.md` | Adapted version for Claude Desktop app — paste into a Claude Project's Custom Instructions field |
| `README.md` | This file — overview, architecture, and usage guide |

## Platform Setup

### Claude Code (CLI, desktop app, web at claude.ai/code, IDE extensions)
No setup needed. Eddie is installed at `~/.claude/skills/eddie/` and available via `/eddie`.

### Claude Desktop App (including Co-work)
1. Create a new **Project** in Claude (web or desktop) — name it "Eddie the Editor"
2. Open the project's **Custom Instructions** and paste the contents of `eddie_desktop_project_instructions.md`
3. Upload `senior_editor_profile.md` as a **Project Knowledge** file
4. Eddie is now available in that project — just say "eddie, review this" or paste a document and ask for an editorial review

**Key differences in the desktop version:**
- Reviews run sequentially (five passes) instead of parallel agents
- Full report is output inline in the conversation instead of saved to a file
- Plans/outlines come from conversation context instead of filesystem scanning
- Second-eyes is a self-review step instead of a separate agent
- Same editorial standards, checklists, priorities, and AI failure mode detection

## What Eddie Does NOT Do

- **Rewrite the document.** Eddie identifies problems and suggests specific fixes.
- **Check .docx formatting.** Margins, fonts, and spacing are the production skills' job (law-memo, law-document).
- **Soften findings.** If something is wrong, Eddie says so.
- **Fabricate concerns.** If the document is clean, Eddie says so.

## Design Principles

**Truth before throughput.** Eddie prioritizes factual reliability over speed. Publication is never the goal — defensible publication is.

**Adversarial by default.** Every document is read as if it will be seen by the worst possible audience. This catches problems that a sympathetic read misses.

**Self-correcting.** The second-eyes pass reviews Eddie's own work. In practice, this catches false positives (things Eddie flagged that are actually correct), priority miscalibrations, and suggested fixes that would introduce new problems.

**Parallel for speed, sequential for judgment.** The five primary agents run concurrently because they're independent lenses on the same document. The second-eyes pass runs after the merge because it needs the complete picture.

**Tunable, not one-size-fits-all.** Light for quick sends, moderate for standard work, aggressive for high-stakes documents. The user controls the dial.
