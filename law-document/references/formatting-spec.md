# Document formatting specification

Extracted from `law-document/SKILL.md` to keep the skill body small; this file loads only when read.

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
the `tufte-visuals` skill installed beside this one. Anything carrying data also needs its
integrity check (zero baselines, lie factor, stated normalization) run while the
source numbers are still in scope, which is before the document is assembled,
not after.

### Bullets
**Real Word list bullets.** Never a hand-typed `•`, and never em-dash bullets.

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
