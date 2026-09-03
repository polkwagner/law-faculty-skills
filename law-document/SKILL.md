---
name: law-document
description: Produce formatted Word (.docx) documents in Penn Carey Law style — proposals, reports, briefing docs, white papers. Use for formal standalone documents (not memos or emails).
license: CC-BY-4.0
compatibility: "Requires python-docx"
metadata:
  author: "[Your Name]"
---

# Law Document Skill

Produces professional Penn Carey Law documents as `.docx` files — proposals, reports, briefing docs, and similar materials. Shares formatting conventions with the memo skill (Cambria, 1" margins) but uses document-appropriate structure rather than the memo header block.

---

## Agent Dependencies

This skill dispatches sub-agents for pre-delivery quality checks. Each call is guarded — the document still produces without them, but factual and style verification are weaker.

- `factual-reviewer` — extracts discrete factual claims for verification.
- `fact-verifier` — live web/source verification of specific claims.
- `voice-style-checker` — voice, style, and AI-tell scan.

Each requires the agent on the current runtime: `~/.claude/agents/<name>/<name>.md` (Claude Code) or `~/.codex/agents/<name>.toml` (Codex).

---

## Environment

Resolve files relative to this skill's directory: `~/.claude/skills/law-document/` in Claude Code and, via the `~/.codex/skills/` symlink, in Codex; `/mnt/skills/user/law-document/` on claude.ai. Output to `~/Downloads/` (or a user-specified path) locally, `/mnt/user-data/outputs/` on claude.ai.

## Before Drafting

1. Read the **docx skill** if available — all file production follows those instructions
2. Identify the **document type** (see patterns below) and clarify with [Your Name] if needed
3. Confirm: audience, purpose, approximate length

---

## Logo — Required First Step

Every document begins with the Penn Carey Law logo centered in the title block. This is the first step of file production, not a checklist item.

**Path:** `<this-skill-dir>/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png`, resolved relative to this skill's directory (the candidate list in the snippet below covers Claude Code, Codex, and claude.ai).

If no candidate exists, **stop and tell the user** — do not produce a document without it.

**Sizing:** The logo must be resized proportionally. The source image is 2000×358 pixels (aspect ratio 5.587:1). Target width is 2.875 inches.

- EMU values: `cx="2628900" cy="470573"`
- Formula: 1 inch = 914400 EMU. Width = 2.875 × 914400 = 2628900. Height = width × (358 / 2000) = 470573.
- Never set width and height independently — always derive height from width using the source aspect ratio.

```python
from docx.shared import Emu

# Resolve relative to this skill's directory on whichever runtime is active
_LOGO = "law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png"
for p in [
    os.path.expanduser("~/.claude/skills/" + _LOGO),   # Claude Code
    os.path.expanduser("~/.codex/skills/" + _LOGO),    # Codex (symlink to the same files)
    "/mnt/skills/user/" + _LOGO,                       # claude.ai
]:
    if os.path.exists(p):
        LOGO_PATH = p
        break
else:
    raise FileNotFoundError("Penn Carey Law logo not found at any known path")
LOGO_WIDTH = Emu(2628900)   # 2.875 inches
LOGO_HEIGHT = Emu(470573)   # proportional: 2628900 × (358/2000)

logo_paragraph = document.add_paragraph()
logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
logo_paragraph.paragraph_format.space_after = Pt(10)
run = logo_paragraph.add_run()
run.add_picture(LOGO_PATH, width=LOGO_WIDTH, height=LOGO_HEIGHT)
```

---

## Document Formatting Spec

**Read `references/formatting-spec.md`** for the full Penn Carey Law spec — margins, Cambria body, heading hierarchy, spacing, and the python-docx construction details.

## Tone and Voice

Voice baseline (tone, banned phrases, preferred expressions) is defined in the global instructions (CLAUDE.md in Claude Code, AGENTS.md in Codex), Writing & Tone section — that always applies. **For longer-form institutional prose, also load `polk-voice-corpus`** — its `references/memo-committee.md` carries verified samples of [Your Name]'s committee memos, including the closed-up em-dash convention and the situation-before-recommendation opening, both of which differ from the general Writing & Tone guidance. Where a sample and a rule conflict, the sample wins.

Documents layer on these additional conventions:

- More formal than emails but never bureaucratic — authoritative, well-organized institutional writing
- For committee-authored documents: "The [committee] recommends," "The [committee] proposes"
- Uses "I" or institutional voice consistently throughout — doesn't switch
- Organized with the most important information first (not buried in conclusions)
- Bullet lists always introduced by a full sentence
- No heading styles that feel like PowerPoint slides
- **Brevity scales with audience knowledge.** When the reader knows the institution, strip explanatory detail. Don't describe what they already know. A donor who sits on the board doesn't need to be told what CTIC is.
- **AI-researched facts must be verified.** When content originates from web scraping or AI research agents, every factual claim (names, dates, program names, affiliations, statistics) must be verified before inclusion. AI-generated research frequently invents plausible-sounding details.

---

## Document Type Patterns

### Proposal (most common)
1. **Purpose / Recommendation** — one paragraph stating what is proposed and by whom
2. **Background / Context** — brief (1-3 paragraphs); what led to this proposal
3. **The Proposal** — substantive section; may use numbered or bulleted items for specific changes
4. **Rationale** — why each element of the proposal makes sense; can be integrated into #3
5. **Implementation / Next Steps** — what happens if approved; who does what

### Report or Briefing Doc
1. **Summary** — 2-4 sentence overview of findings/conclusions up front
2. **Background** — context needed to understand the report
3. **Findings / Analysis** — organized by section with bold headings
4. **Recommendations or Conclusions**
5. **Appendices** if needed (data, supporting materials)

### White Paper / Policy Document
1. **Executive Summary** (1-2 paragraphs)
2. **Issue / Problem Statement**
3. **Analysis** (organized sections)
4. **Recommendations**
5. **Conclusion**

---

## File Production

**Always use python-docx to generate .docx files.** Write a Python script that builds
the document programmatically. Do NOT write markdown and convert with Pandoc — Pandoc
produces corrupted OOXML with duplicate style IDs, misnamed image files, and malformed
relationships that cause Word to refuse to open the file.

1. **Initialize with logo** — load and insert the Penn Carey Law logo as the first element (see Logo section above)
2. Build the title block appropriate to document type
3. Apply Cambria 12pt throughout — headings are bold same-size, not larger
4. Real Word list bullets (`style="List Bullet"`) for unordered lists; Arabic numerals for ordered lists
5. Add footer with page numbers on multi-page documents
6. Save to `~/Downloads/` (CLI) or `/mnt/user-data/outputs/` (web)
7. **Run the Post-Generation Validation** step (see below) before delivering
8. Filename convention:
   - **Default (one-off documents):** `[DocType]_[Topic]_[YYYY-MM].docx` (e.g., `Proposal_StudentProjects_2025-11.docx`).
   - **Project-folder iterations (when generating from a versioned `-vN.md` source in a project that follows the project-folder-setup pattern):** the published `.docx` filename must carry the same version stamp as its source markdown — and must **always stay in sync** with it. Source `Topic-v0.md` → `Topic_v0.docx`; source bumps to `Topic-v1.md` → rebuild as `Topic_v1.docx`. Never let the working markdown drift to a different version stamp than the published `.docx`. Keeping the version stamp synced is the primary signal of where the editing state lives; without it, reviewers can't tell which round of edits the docx reflects.
   - **Version semantics:** v0 = preliminary / first draft, internal editing only (not yet distributed). v1 = first distributed draft (the bump from v0 to v1 marks distribution). v2, v3, v4, … = subsequent modifications after distribution. Multiple internal Eddie reviews, polish rounds, and fact-checks all happen at v0; the bump to v1 is the distribution moment. See the `project-folder-setup` skill installed beside this one for the full versioning workflow.

---

## Voice checks before delivering

**Read `references/voice-checks.md`** for the AI-writing-tell pass, the voice-score procedure, and how to capture voice feedback.

Also load **`polk-voice-corpus`** — verified samples of [Your Name]'s own institutional prose. Where a sample and a rule disagree, the sample wins.

## Post-Generation Validation (Required)

After generating any .docx file, run the bundled validator. It catches the
structural issues (duplicate style IDs, images named after relationship IDs)
that stop Word from opening the file, and repairs the first kind in place.

```bash
python3 <this-skill-dir>/scripts/validate_docx.py path/to/output.docx
```

Read its output: `VALID:` means done; a `REPAIRED` line means the file was
corrupted and has been patched; a non-zero exit means the file could not be
read as a .docx at all.

If validation reports any repairs, that means the generation method produced a
corrupted file. **Switch to python-docx and regenerate** — do not rely on the
repair as the primary fix. The repair is a safety net, not a substitute for
correct generation.

---

## Quick Checklist Before Delivering

- [ ] Logo present and centered in title block, proportionally scaled (2.875" wide)
- [ ] Cambria 12pt throughout — no other fonts
- [ ] Title block present and appropriate to document type
- [ ] Section headings: bold, 12pt, `w:before="200" w:after="80"`
- [ ] Body paragraphs: `w:line="276" w:after="160"`
- [ ] Real Word list bullets (`style="List Bullet"`, runs set to Cambria 12pt); lists introduced by full sentences
- [ ] Tables: `prevent_table_split()` called on every table (no page breaks mid-table)
- [ ] Tone follows the global-instructions voice baseline (direct, active, no filler)
- [ ] AI writing tell check passed (see section above)
- [ ] Closes with concrete next steps or recommendations
- [ ] Footer present on multi-page documents (centered, Cambria 10pt italic, "Page x of y.")
- [ ] Saved and presented to user
