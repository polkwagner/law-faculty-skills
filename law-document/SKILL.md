---
name: law-document
description: "Draft and produce formatted Word document (.docx) general documents - proposals, reports, briefing docs, white papers, and other formal written materials - in Penn Carey Law style. Use this skill whenever the user asks to write, draft, or create a document that is not a memo or email: proposals, policy documents, reports, briefing materials, white papers, or any substantive standalone written work. Trigger phrases include write a proposal, draft a document, create a report, briefing doc, policy document, white paper, or any request to produce a formal standalone document. Use the law-memo skill instead for memos specifically."
---

# Law Document Skill

Produces professional Penn Carey Law documents as `.docx` files — proposals, reports, briefing docs, and similar materials. Shares formatting conventions with the memo skill (Cambria, 1" margins) but uses document-appropriate structure rather than the memo header block.

---

## Environment

This skill works in both **Claude Code CLI** and **Claude.ai / Cowork**. Use whichever paths exist:

- **Skills:** `~/.claude/skills/` (CLI) or `/mnt/skills/user/` (web)
- **Output:** `~/Downloads/` or user-specified path (CLI) or `/mnt/user-data/outputs/` (web)

## Before Drafting

1. Read the **docx skill** if available — all file production follows those instructions
2. Identify the **document type** (see patterns below) and clarify with [Your Name] if needed
3. Confirm: audience, purpose, approximate length

---

## Logo — Required First Step

Every document begins with the Penn Carey Law logo centered in the title block. This is the first step of file production, not a checklist item.

**Path:** `~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png` (CLI)
or `/mnt/skills/user/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png` (web).
Try CLI path first; if not found, try web path.

If neither path works, **stop and tell the user** — do not produce a document without it.

**Sizing:** The logo must be resized proportionally. The source image is 2000×358 pixels (aspect ratio 5.587:1). Target width is 2.875 inches.

- EMU values: `cx="2628900" cy="470573"`
- Formula: 1 inch = 914400 EMU. Width = 2.875 × 914400 = 2628900. Height = width × (358 / 2000) = 470573.
- Never set width and height independently — always derive height from width using the source aspect ratio.

```python
from docx.shared import Emu

# Try CLI path first, then web path
for p in [
    os.path.expanduser("~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png"),
    "/mnt/skills/user/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png",
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

All formatting uses the same precise values as the memo skill so documents from the same office look consistent.

### Page Setup
- **Margins**: 1" on all sides (1440 twips)
- **Font**: Cambria throughout — headings AND body. No other fonts.
- **Body size**: 12pt (24 half-points)
- **Line spacing**: `w:line="276" w:lineRule="auto"` (~1.15)
- **Paragraph spacing**: `w:after="160"` for body text

```python
from docx.shared import Pt, Inches, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Page setup
section = document.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
```

### Title Block (for proposals and reports)
```
[Penn Carey Law logo — centered, 2.875" wide, proportionally scaled]

[DOCUMENT TITLE]        ← centered, bold, Cambria 12pt, all caps or title case
[Subtitle if needed]    ← centered, not bold
[Author / Date / Prepared for — left aligned or centered, as appropriate]
────────────────────────────────────  ← horizontal rule (bottom border)
```

Title paragraph: `alignment=CENTER`, Cambria bold 12pt, `w:after="80"`

For shorter or internal documents, a simpler title is fine — just bold centered title, date below.

### Horizontal Rule
Same as memo skill — paragraph with bottom border:
```xml
<w:pBdr><w:bottom w:val="single" w:color="000000" w:sz="6" w:space="1"/></w:pBdr>
```
With `w:after="240"`.

### Headings
- **Section headings**: Bold, left-aligned, Cambria 12pt — same size as body, weight distinguishes them. `w:before="200" w:after="80"`
- **Sub-headings**: Bold italic, left-aligned, 12pt. `w:before="160" w:after="80"`
- No heading numbering unless document is long (5+ sections) and navigation is useful

### Body Text
- Cambria 12pt, `w:line="276" w:lineRule="auto" w:after="160"`
- Paragraphs separated by spacing, not blank lines
- **Bold** used sparingly for key terms, action items, or critical facts
- Tables: clean, minimal borders; Cambria 12pt in cells; used for comparative or structured data

### Em-Dash Bullets
Manual em-dash with tab, hanging indent — never Word list bullets:
```xml
<w:pPr>
  <w:spacing w:line="276" w:lineRule="auto" w:after="120"/>
  <w:ind w:left="720" w:hanging="360"/>
</w:pPr>
<w:r>...<w:t>—	bullet text here</w:t></w:r>
```
For bold lead-in bullets, use separate runs: em-dash+tab run, bold run (lead phrase), normal run (rest of text).

Numbered lists: standard Arabic numerals for sequential/ordered items, same indent values.

### Footer (multi-page documents)
Centered, Cambria 10pt italic, "Page x of y."

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

footer = section.footer
footer.is_linked_to_previous = False
p = footer.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Build "Page X of Y." with proper field codes
for text, field in [("Page ", None), (None, "PAGE"), (" of ", None), (None, "NUMPAGES"), (".", None)]:
    run = p.add_run(text or "")
    run.font.name = "Cambria"
    run.font.size = Pt(10)
    run.font.italic = True
    if field:
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), field)
        run._element.append(fld)
```

### Section Properties
```xml
<w:sectPr>
  <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
           w:header="708" w:footer="708" w:gutter="0"/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
```

---

## Tone and Voice

Voice baseline (tone, banned phrases, preferred expressions) is defined in CLAUDE.md — that always applies. Documents layer on these additional conventions:

- More formal than emails but never bureaucratic — authoritative, well-organized institutional writing
- For committee-authored documents: "The [committee] recommends," "The [committee] proposes"
- Uses "I" or institutional voice consistently throughout — doesn't switch
- Organized with the most important information first (not buried in conclusions)
- Bullet lists always introduced by a full sentence
- No heading styles that feel like PowerPoint slides

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

1. **Initialize with logo** — load and insert the Penn Carey Law logo as the first element (see Logo section above)
2. Build the title block appropriate to document type
3. Apply Cambria 12pt throughout — headings are bold same-size, not larger
4. Em-dash bullets for unordered lists; Arabic numerals for ordered lists
5. Add footer with page numbers on multi-page documents
6. Save to `~/Downloads/` (CLI) or `/mnt/user-data/outputs/` (web)
7. Filename convention: `[DocType]_[Topic]_[YYYY-MM].docx` (e.g., `Proposal_StudentProjects_2025-11.docx`)

---

## Quick Checklist Before Delivering

- [ ] Logo present and centered in title block, proportionally scaled (2.875" wide)
- [ ] Cambria 12pt throughout — no other fonts
- [ ] Title block present and appropriate to document type
- [ ] Section headings: bold, 12pt, `w:before="200" w:after="80"`
- [ ] Body paragraphs: `w:line="276" w:after="160"`
- [ ] Em-dash bullets with hanging indent; lists introduced by full sentences
- [ ] Tone follows CLAUDE.md voice baseline (direct, active, no filler)
- [ ] Closes with concrete next steps or recommendations
- [ ] Footer present on multi-page documents (centered, Cambria 10pt italic, "Page x of y.")
- [ ] Saved and presented to user
