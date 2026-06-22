# AI Skills for Penn Carey Law Faculty

A collection of skills for AI coding assistants — built for teaching, document production, and course preparation at Penn Carey Law.

Every skill in this repository conforms to the **[agentskills specification](https://github.com/agentskills/agentskills)**, a cross-tool standard for AI assistant skills. That means they work with any compatible tool, not just one vendor. Currently supported tools include [Claude Code](https://claude.ai/code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [ChatGPT](https://chatgpt.com) (including ChatGPT EDU), and any other tool that reads the agentskills format. Pick the skills useful to you.

## What Are Agentskills?

Each skill is a directory containing a **SKILL.md** file — a markdown document with YAML frontmatter that tells the AI assistant what the skill does and how to execute it. The [agentskills specification](https://github.com/agentskills/agentskills) defines the format so that any compatible tool can discover and use skills without vendor-specific configuration.

```
law-mcq-generator/
  SKILL.md          ← skill definition (YAML frontmatter + instructions)
  assets/           ← images, logos (optional)
  scripts/          ← helper scripts (optional)
```

Skills are invoked naturally in conversation — you don't need special syntax:

- *"Write a memo to the faculty about the new grading policy"* → triggers law-memo
- *"Generate 20 multiple choice questions covering chapters 3-5"* → triggers law-mcq-generator
- *"Review my slides for Tuesday's class"* → triggers lecture-slide-reviewer
- *"Create a class problem for session 12"* → triggers law-class-problems
- *"Prep class 8"* → triggers law-class-prep

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
| **materials-md** | Convert PDF, DOCX, PPTX, or HTML to clean, AI-ready markdown | [materials-converter](https://github.com/ai-teaching-lab/materials-converter) (`docling`) |
| **rex** | Critical review of code, plans, or designs | None |
| **eddie** | Senior-level editorial review of any document — checks factual accuracy, citations, internal consistency, institutional sensitivity, voice/style, and AI failure modes | None |

Each skill's SKILL.md file contains the full reference for what it does and how to use it.

## Sub-Agents

Several skills dispatch parallel sub-agents for quality checks — these live under `agents/` in this repo. Install them into `~/.claude/agents/` (or the agents directory for your tool) to get the full experience.

| Used by | Agents |
|---|---|
| **eddie** | factual-pipeline-orchestrator (which in turn spawns factual-reviewer, institutional-claim-extractor, claim-merge-agent, fact-verifier, coverage-auditor, adversarial-reverifier, disagreement-analyzer), eddie-consistency-checker, voice-style-checker |
| **law-mcq-generator** | adversarial-balance-validator, construct-alignment-tracer, double-read-pass, emphasis-map-builder, mcq-structural-reviewer |
| **law-essay-generator** | adversarial-balance-validator, construct-alignment-tracer, double-read-pass, emphasis-map-builder |
| **lecture-slide-reviewer**, **law-class-prep** | slide-reading-alignment |

Skills work without their agents — each skill wraps agent calls in `if the <name> agent is available, spawn it` guards — but quality-of-result is meaningfully lower without them. On tools that don't support sub-agents (Gemini CLI, ChatGPT), skills fall back to running the checks inline where possible.

Copy all agents at once:
```bash
cp -r agents/* ~/.claude/agents/
```

## Prerequisites

1. **An AI coding assistant** — [Claude Code](https://claude.ai/code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [ChatGPT](https://chatgpt.com) (including ChatGPT EDU), or any tool that supports the [agentskills specification](https://github.com/agentskills/agentskills).

2. **Python 3** (for skills that produce .docx or .pdf output):
   ```bash
   pip install python-docx reportlab
   ```

3. **Pandoc** (for some document conversions):
   ```bash
   brew install pandoc    # macOS
   ```

## Installation

The method depends on which AI tool you use.

### Claude Code

Install directly from GitHub:
```
/install-skill https://github.com/polkwagner/law-faculty-skills/tree/main/law-mcq-generator
```

Or copy manually:
```bash
cp -r law-mcq-generator ~/.claude/skills/
```

### Gemini CLI

Copy the skill directory into Gemini's skills location:
```bash
cp -r law-mcq-generator ~/.gemini/skills/
```

### ChatGPT (including ChatGPT EDU)

ChatGPT has native [Skills](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) support on Business, Enterprise, and EDU plans — which includes Penn's ChatGPT EDU.

**Option 1 — Upload as a ChatGPT Skill (recommended):**

1. Download the SKILL.md file for the skill you want from this repository
2. In ChatGPT, go to your **Skills** page
3. Click **New skill** → **Upload from your computer**
4. Upload the SKILL.md file

The skill will appear in your skills list and can be shared with colleagues in your workspace.

**Option 2 — Use as a Custom GPT:**

If you prefer Custom GPTs, or if Skills aren't yet enabled in your workspace:

1. Open the SKILL.md file and copy the content below the `---` frontmatter block
2. Create a Custom GPT and paste it into the **Instructions** field

**What works well:** Skills focused on writing and analysis — law-email-style, law-class-problems, lecture-slide-reviewer, rex, and the exam generators (law-mcq-generator, law-essay-generator) when producing plain-text output.

**Limitations:** Skills that produce formatted .docx or .pdf files (law-memo, law-document, md-to-pdf) rely on Python scripts and file-system access that ChatGPT's environment handles differently. You'll get the content but may not get the exact Penn Carey Law formatting.

### Other tools

Copy skill directories into wherever your tool reads agentskills. The SKILL.md files conform to the [agentskills specification](https://github.com/agentskills/agentskills), so any compliant tool will discover and use them.

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

## Questions?

Contact Polk Wagner (pwagner@law.upenn.edu) for help getting started.
