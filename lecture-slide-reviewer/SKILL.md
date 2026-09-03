---
name: lecture-slide-reviewer
description: >
  Review lecture slides against assigned readings for a law school class session:
  coverage, gaps, and pacing. Use for a slide review or pacing check; for full class
  prep use law-class-prep.
license: CC-BY-4.0
metadata:
  author: "[Your Name]"
---
# Lecture Slide Reviewer

## Agent Dependencies

This skill dispatches one sub-agent for alignment analysis. The call is guarded — the reviewer still runs without it, but the deep slide-to-reading alignment pass is skipped.

- `slide-reading-alignment` — compares slides against assigned readings session-by-session and returns a coverage report.

Requires the agent on the current runtime: `~/.claude/agents/slide-reading-alignment/slide-reading-alignment.md` (Claude Code) or `~/.codex/agents/slide-reading-alignment.toml` (Codex).

## Context

You are reviewing lecture slides for a law school class session. The goal is to
help the professor identify gaps, misalignments, and pacing issues before class.

## First Steps (Do This Every Time)

Before writing anything:

1. **Get the materials path.** Ask the user for the path to the course materials
   folder (or the slide deck and readings specifically) if not already provided
   in the conversation.

2. **Read the syllabus** to identify the class session, its topic, and the
   assigned readings. If no syllabus is available, ask the user which readings
   are assigned to this session and what was covered in prior sessions.

3. **Confirm the class duration.** Default is 75 minutes. If the user specifies
   a different duration, use that for the pacing assessment.

4. **Read the slide deck** thoroughly, noting the topic and structure of each slide.

5. **Read the assigned readings** thoroughly, noting the key concepts, cases,
   doctrines, and frameworks covered.

6. If the `slide-reading-alignment` agent is available, spawn it and pass it the slide deck path,
   readings path, and class duration. Present the agent's report to the user.

The agent handles the full analysis below. The criteria are documented here
for reference and for environments where the agent is unavailable.

## What to Check

### 1. Slide-to-Reading Alignment

For each slide, determine whether the content is covered in the assigned readings.

Flag any slide that:
- References a case, doctrine, statute, or concept **not found** in the
  assigned readings
- Uses terminology or frameworks the students won't have encountered yet

For each flag, note the specific slide and what it references that isn't in
the readings.

### 2. Reading Coverage Gaps

Identify any significant concept, case, or doctrine in the assigned readings
that has **no corresponding slide coverage**.

Not everything in the readings needs a slide — focus on:
- Major cases that are likely discussion-worthy
- Core doctrinal frameworks or tests
- Statutory provisions the readings spend significant time on

For each gap, note what's missing and where it appears in the readings.

### 3. Pacing and Density Assessment

Assess whether the slide deck is appropriate for the class duration.

Consider:
- **Total slide count** relative to the class duration — as a rough guide, plan
  for 2-4 minutes per substantive slide (not counting title/agenda slides)
- **Dense slides** — flag any slide that tries to cover too many concepts
  at once and may need to be split
- **Light slides** — flag any slide that could be combined with an adjacent
  slide without losing clarity
- **Discussion breaks** — note whether the deck leaves room for class
  discussion or runs wall-to-wall with content

## Output Format

Organize your review into three sections:

### Coverage Report
A table or list mapping each slide to the readings it draws from, with flags
for any misalignment.

### Reading Gaps
A list of significant concepts from the readings that lack slide coverage,
with a brief note on why each might warrant a slide.

### Pacing Assessment
An overall assessment of the deck's density for the class duration, with specific
flags for slides that are too dense or too light, and a recommendation on
whether the deck needs trimming, expansion, or restructuring.

End with a brief summary: the top 2-3 actionable suggestions for improving
the deck.

## What NOT to Do

- Do not rewrite the slides — this is a review, not a redesign
- Do not flag every minor omission from the readings — focus on significant gaps
- Do not assume knowledge of what was covered in prior sessions — read the
  syllabus to determine this
- Do not assess the visual design of the slides — focus on content and pacing
