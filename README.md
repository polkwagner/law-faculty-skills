# Claude Code Skills for Penn Carey Law Faculty

A collection of [Claude Code](https://claude.ai/code) skills for teaching, document production, and course preparation at Penn Carey Law. Each skill extends Claude Code with specialized capabilities — pick the ones useful to you.

## Prerequisites

Before installing skills, you need:

1. **Claude Code** — install from [claude.ai/code](https://claude.ai/code) or via your terminal:
   ```bash
   # macOS (Homebrew)
   brew install claude-code
   ```

2. **Python 3** (for document-producing skills):
   ```bash
   pip install python-docx reportlab
   ```

3. **Pandoc** (for some document conversions):
   ```bash
   brew install pandoc
   ```

## Available Skills

| Skill | What It Does | Extra Dependencies |
|---|---|---|
| **law-mcq-generator** | Generate multiple-choice exam questions for any law course, grounded in psychometric research | python-docx |
| **law-essay-generator** | Generate essay exam questions with SOLO taxonomy layering and rubrics | python-docx |
| **law-class-problems** | Create and revise adversarial in-class problems for any law course | None |
| **law-class-prep** | Full class prep: slide alignment, problem review, and lecture guide | python-docx |
| **lecture-slide-reviewer** | Review lecture slides against assigned readings for coverage and pacing | None |
| **law-memo** | Produce formatted .docx memos with Penn Carey Law letterhead | python-docx |
| **law-document** | Produce formatted .docx proposals, reports, and briefing documents | python-docx |
| **law-email-style** | Draft emails in a professional academic voice | None |
| **md-to-pdf** | Render Markdown as professionally formatted PDFs in Penn Carey Law style | reportlab |
| **docx-comment-summary** | Extract and summarize all comments from Word documents | None (stdlib only) |
| **rex** | Critical review of code, plans, or designs | None |
| **eddie** | Senior-level editorial review of any document — checks factual accuracy, citations, internal consistency, institutional sensitivity, voice/style, and AI failure modes | None |

## Installation

### Option A: Install from GitHub (recommended)

Install individual skills directly in Claude Code:

```
/install-skill https://github.com/polkwagner/law-faculty-claude-skills/tree/main/SKILL_NAME
```

For example, to install the MCQ generator:
```
/install-skill https://github.com/polkwagner/law-faculty-claude-skills/tree/main/law-mcq-generator
```

### Option B: Manual installation

1. Clone or download this repository
2. Copy the skill folder(s) you want into `~/.claude/skills/`:
   ```bash
   cp -r law-mcq-generator ~/.claude/skills/
   ```
3. Restart Claude Code

## Customization

After installing a skill, customize it for your own use:

### Your name and title
Several skills use placeholder text that you should replace with your own information. Open the SKILL.md file in any installed skill and search for:
- `[Your Name]` — replace with your name
- `[Your Title]` — replace with your title (e.g., "Professor of Law")

### Course presets
The exam-generation skills (law-mcq-generator, law-essay-generator) include an IP course preset. To add your own course:
- Open the skill's SKILL.md
- Find the "Course Presets" table
- Add a row with your course name, casebook, and doctrinal areas

### Document formatting
The memo, document, and PDF skills use Penn Carey Law branding (logo, Cambria font). These work out of the box — the logo is bundled with the skill.

## How Skills Work

Skills are markdown instruction files that Claude Code reads when triggered. You invoke them naturally in conversation:

- *"Write a memo to the faculty about the new grading policy"* → triggers law-memo
- *"Generate 20 multiple choice questions covering chapters 3-5"* → triggers law-mcq-generator
- *"Review my slides for Tuesday's class"* → triggers lecture-slide-reviewer
- *"Create a class problem for session 12"* → triggers law-class-problems
- *"Prep class 8"* → triggers law-class-prep

Each skill's SKILL.md file contains the full reference for what it does and how to use it.

## Questions?

Contact Polk Wagner (pwagner@law.upenn.edu) for help getting started.
