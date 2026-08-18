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

Install from the `agents/` directory of this skill's repo into `~/.claude/agents/`.

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
- Tables: clean, minimal borders; Cambria 12pt in cells; used for comparative or structured data; **must not split across pages** (see Tables section below)

### Tables
Tables must not split across pages. After building any table, apply `cantSplit` to every row and `keepNext` to all paragraphs in every row except the last. This prevents individual rows from breaking mid-row and keeps the entire table on one page.

```python
def prevent_table_split(table):
    """Prevent table rows from splitting across pages and keep table together."""
    rows = table.rows
    for i, row in enumerate(rows):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        # keepNext on all rows except the last keeps the table together
        if i < len(rows) - 1:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    pPr = paragraph._element.get_or_add_pPr()
                    pPr.append(OxmlElement("w:keepNext"))
```

Call `prevent_table_split(table)` after populating every table. For very large tables (20+ rows) that genuinely cannot fit on one page, Word will still break them at a row boundary — these properties ensure it never breaks mid-row.

**Table and figure design.** For how a table should be *built* — number
alignment, how few rules it needs, sort order, significant digits — and for any
chart or diagram going into the document, read
`~/.claude/skills/tufte-visuals/SKILL.md`. Anything carrying data also needs its
integrity check (zero baselines, lie factor, stated normalization) run while the
source numbers are still in scope, which is before the document is assembled,
not after.

### Bullets
**Real Word list bullets** (changed 2026-08-13 — the old manual `•`-plus-tab approach is superseded). Never em-dash bullets.

Since this skill builds with python-docx from a fresh `Document()`, use the built-in style. Verified 2026-08-13: python-docx's default template defines `ListBullet` with a `w:numPr` referencing `numId 1`, which resolves in `numbering.xml` to a level-0 `bullet` format. It renders as a proper round bullet with no numbering setup of your own:

```python
p = document.add_paragraph("bullet text here", style="List Bullet")
```

Do **not** also write a literal `•` or a leading tab — the list supplies the marker, and adding one by hand doubles it. Do not set a manual `w:ind`; the numbering definition owns the indent.

**Set the font on the runs explicitly.** `List Bullet` inherits from the template's defaults, not from this document's Cambria 12pt body style, so an untouched list paragraph can come out in the wrong face:

```python
for run in p.runs:
    run.font.name = "Cambria"
    run.font.size = Pt(12)
```

For bold lead-in bullets, add the paragraph with the list style, then append runs: a bold run (lead phrase) and a normal run (the rest). There is no longer a bullet+tab run.

### List Formatting Tips
- **Colons after named entities in compressed lists.** When a bullet lists items about a named entity and the list items themselves contain commas, use a colon after the entity name: "Center (Smith and Jones): research, conferences, student fellowships." This avoids ambiguity.
- **Thematic sub-headings for long bullet lists.** When a document has more than ~10 bullets, group them under bold italic sub-headings to prevent a "laundry list" feel. Sub-headings should be short (3-5 words) and thematic.
- **Merging status categories.** When a document has both accomplished and pipeline items, consider merging them under thematic headings with pipeline items marked by a leading "(*)" rather than separating into two sections. Add a legend: "Items marked (*) are in development."

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
   - **Version semantics:** v0 = preliminary / first draft, internal editing only (not yet distributed). v1 = first distributed draft (the bump from v0 to v1 marks distribution). v2, v3, v4, … = subsequent modifications after distribution. Multiple internal Eddie reviews, polish rounds, and fact-checks all happen at v0; the bump to v1 is the distribution moment. See `~/.claude/skills/project-folder-setup/SKILL.md` for the full versioning workflow.

---

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

## Post-Generation Validation (Required)

After generating any .docx file, run this validation script to catch structural
issues that prevent Word from opening the file. This is mandatory — do not skip it.

```python
import zipfile, re, os

def validate_and_repair_docx(filepath):
    """Check a .docx for common corruption issues and repair if needed."""
    repairs = []
    z = zipfile.ZipFile(filepath, 'r')
    styles_xml = z.read('word/styles.xml').decode('utf-8')

    # Check 1: Duplicate style IDs (Pandoc artifact — should not happen with
    # python-docx, but check anyway as a safety net)
    pattern = r'<w:style\s[^>]*w:styleId="([^"]*)"'
    style_ids = re.findall(pattern, styles_xml)
    from collections import Counter
    dupes = {k: v for k, v in Counter(style_ids).items() if v > 1}
    if dupes:
        repairs.append(f"Duplicate style IDs found: {list(dupes.keys())}")
        # Remove duplicates via regex on raw XML (preserves exact structure)
        seen = set()
        full_pattern = r'(<w:style\s[^>]*w:styleId="([^"]*)"[^>]*>.*?</w:style>)'
        def dedup(m):
            sid = m.group(2)
            if sid in seen:
                return ''
            seen.add(sid)
            return m.group(1)
        styles_xml = re.sub(full_pattern, dedup, styles_xml, flags=re.DOTALL)
        styles_xml = re.sub(r'\n\s*\n', '\n', styles_xml)

    # Check 2: Images named after relationship IDs (another Pandoc artifact)
    bad_images = [n for n in z.namelist()
                  if n.startswith('word/media/rId') and n.endswith('.png')]
    if bad_images:
        repairs.append(f"Images with rId names found: {bad_images}")

    if repairs:
        # Rewrite the file with fixes
        tmp = filepath + '.tmp'
        z_out = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        for item in z.infolist():
            if item.filename == 'word/styles.xml':
                z_out.writestr(item, styles_xml.encode('utf-8'))
            else:
                z_out.writestr(item, z.read(item.filename))
        z_out.close()
        z.close()
        os.replace(tmp, filepath)
        print(f"REPAIRED {filepath}: {'; '.join(repairs)}")
    else:
        z.close()
        print(f"VALID: {filepath}")

validate_and_repair_docx("path/to/output.docx")
```

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
- [ ] Tone follows CLAUDE.md voice baseline (direct, active, no filler)
- [ ] AI writing tell check passed (see section above)
- [ ] Closes with concrete next steps or recommendations
- [ ] Footer present on multi-page documents (centered, Cambria 10pt italic, "Page x of y.")
- [ ] Saved and presented to user
