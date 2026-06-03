---
name: md-to-pdf
description: >
  Render Markdown files as high-quality, professionally formatted PDFs in
  Penn Carey Law house style. Use when asked to convert markdown to PDF,
  create a PDF from markdown content, render a readable PDF, make a polished
  PDF document, or format a document as PDF. Trigger phrases include "render
  as PDF", "convert to PDF", "make a PDF", "PDF version", "formatted PDF",
  "polished PDF", "readable PDF", or any request involving markdown-to-PDF
  conversion. Also trigger when the user has a .md file and wants a
  nice-looking PDF output.
license: CC-BY-4.0
compatibility: "Requires reportlab"
metadata:
  author: "[Your Name]"
---

# Markdown to PDF Renderer — Penn Carey Law Style

## Overview

This skill converts Markdown content into professionally typeset PDFs using
Python's ReportLab library. Output matches Penn Carey Law house style:
Times Roman body text, Penn Blue headings, styled tables with dark blue
headers, shaded info boxes, and header/footer treatment with Penn Carey Law
logo on the first page.

## Environment

This skill works in both **Claude Code CLI** and **Claude.ai / Cowork**. Use whichever paths exist:

- **Skills:** `~/.claude/skills/` (CLI) or `/mnt/skills/user/` (web)
- **Output:** `~/Downloads/` or user-specified path (CLI) or `/mnt/user-data/outputs/` (web)

## Filename Convention

When converting a markdown source to PDF inside a project folder following the `project-folder-setup` pattern, the PDF must carry the same `vN` version stamp as the source markdown — and stay synced as the markdown iterates. Source `topic-v0.md` → `Topic_v0.pdf`; bumping markdown to `v1` → rebuild as `Topic_v1.pdf`. For one-off conversions (no versioned source), the default `[Topic]_[YYYY-MM].pdf` pattern is fine. Version semantics: v0 = preliminary, v1 = first distributed, v2+ = post-distribution modifications. See `~/.claude/skills/project-folder-setup/SKILL.md` for the full versioning workflow and the canonical project folder layout (`zz_working/`, `zz_archives/`, `zz_source-material/`, `zz_docs/`).

## Dependencies

```bash
pip install reportlab
```

ReportLab is the only dependency. No PIL, numpy, or other packages needed.

## Font Note

Uses Times-Roman (ReportLab built-in) rather than Cambria (used in the
.docx skills) to avoid TTF font registration complexity. If Cambria
consistency with .docx output is needed, register the font:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Cambria', '/path/to/cambria.ttc'))
```

## Logo

The Penn Carey Law logo with white background (no compositing needed):

**Path:** `~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png` (CLI)
or `/mnt/skills/user/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png` (web).
Try CLI path first; if not found, try web path.

If neither path works, stop and tell the user — do not produce a PDF without it.

**Sizing:** Source is 2000×358 pixels (aspect ratio 5.587:1). Target width 3.2 inches.
Height = 3.2 / 5.587 = 0.573 inches.

```python
import os
# Try CLI path first, then web path
for _p in [
    os.path.expanduser("~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png"),
    "/mnt/skills/user/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png",
]:
    if os.path.exists(_p):
        LOGO_PATH = _p
        break
else:
    LOGO_PATH = None  # will be caught in first_page()
LOGO_WIDTH = 3.2 * inch
LOGO_HEIGHT = LOGO_WIDTH * (358 / 2000)  # proportional: 0.573 inches
```

## Visual Specification

```
Page:           US Letter (8.5 x 11), 1-inch margins all sides
Body:           Times-Roman 10.5pt, justified, #1A1A1A
H1:             Times-Bold 14pt, Penn Blue (#011F5B), 24pt space before,
                thin bottom rule in medium gray
H2:             Times-Bold 12pt, dark gray (#333333), 16pt space before
H3:             Times-BoldItalic 11pt, dark gray, 12pt space before
Bullets:        En-dash (–) bullet, 36pt left indent, Times-Roman 10.5pt
Nested bullets: Bullet dot (•), 54pt left indent
Tables:         Penn Blue (#011F5B) header row with white text,
                alternating white / light gray (#F5F5F5) rows,
                0.5pt medium gray (#E0E0E0) grid, Times-Roman 9.5pt
Info boxes:     Light gray (#F5F5F5) background, medium gray border,
                18pt internal padding, optional centered italic blue title
Code blocks:    Courier 9pt on light gray background, 36pt left indent
Inline code:    Courier face within body text
Links:          Accent blue (#2E75B6) with underline
Header (p2+):   "Document Title" left, "Subtitle" right, Penn Blue text,
                1.5pt Penn Blue rule below, Times-Bold 8.5pt
Footer:         Centered "Page N", Times-Roman 8.5pt, dark gray
First page:     Penn Carey Law logo centered at top, no header bar, footer only
```

## Color Palette

```python
PENN_BLUE   = "#011F5B"   # Headings, header text, table headers
ACCENT_BLUE = "#2E75B6"   # Links, box titles
DARK_GRAY   = "#333333"   # H2/H3, footer text
TEXT_COLOR   = "#1A1A1A"   # Body text
LIGHT_GRAY  = "#F5F5F5"   # Table alt rows, code bg, info box bg
MED_GRAY    = "#E0E0E0"   # Borders, grid lines, rules
PENN_RED    = "#990000"    # Available for emphasis (e.g., "CONFIDENTIAL")
```

## Complete ReportLab Implementation

### Imports and Setup

```python
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Frame, PageTemplate, NextPageTemplate,
    Preformatted, KeepTogether, Image as RLImage,
)

PAGE_W, PAGE_H = letter
L_MARGIN = R_MARGIN = T_MARGIN_LATER = B_MARGIN = 1.0 * inch
T_MARGIN_FIRST = 1.2 * inch  # extra space for logo
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN

# --- Logo ---
# Try CLI path first, then web path
for _p in [
    os.path.expanduser("~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png"),
    "/mnt/skills/user/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png",
]:
    if os.path.exists(_p):
        LOGO_PATH = _p
        break
else:
    LOGO_PATH = None  # will be caught in first_page()
LOGO_WIDTH = 3.2 * inch
LOGO_HEIGHT = LOGO_WIDTH * (358 / 2000)  # proportional

# --- Colors ---
PENN_BLUE = HexColor("#011F5B")
ACCENT_BLUE = HexColor("#2E75B6")
DARK_GRAY = HexColor("#333333")
TEXT_COLOR = HexColor("#1A1A1A")
LIGHT_GRAY = HexColor("#F5F5F5")
MED_GRAY = HexColor("#E0E0E0")

# --- Document metadata (set these before building) ---
doc_title = ""       # Displayed in header bar on pages 2+
doc_subtitle = ""    # Displayed in header bar on pages 2+
```

### Style Definitions

```python
sBody = ParagraphStyle(
    "Body", fontName="Times-Roman", fontSize=10.5, leading=14,
    textColor=TEXT_COLOR, alignment=TA_JUSTIFY, spaceAfter=8,
)

sH1 = ParagraphStyle(
    "H1", fontName="Times-Bold", fontSize=14, leading=18,
    textColor=PENN_BLUE, spaceBefore=24, spaceAfter=10,
)
# Note: add HRFlowable after each H1 to create the bottom rule

sH2 = ParagraphStyle(
    "H2", fontName="Times-Bold", fontSize=12, leading=15,
    textColor=DARK_GRAY, spaceBefore=16, spaceAfter=8,
)

sH3 = ParagraphStyle(
    "H3", fontName="Times-BoldItalic", fontSize=11, leading=14,
    textColor=DARK_GRAY, spaceBefore=12, spaceAfter=6,
)

sBullet = ParagraphStyle(
    "Bullet", parent=sBody,
    leftIndent=36, firstLineIndent=0, bulletIndent=18, spaceAfter=4,
    bulletFontName="Times-Roman", bulletFontSize=10.5,
)

sBulletInner = ParagraphStyle(
    "BulletInner", parent=sBullet,
    leftIndent=54, bulletIndent=36,
)

sTableHeader = ParagraphStyle(
    "TableHeader", fontName="Times-Bold", fontSize=9.5, leading=12,
    textColor=white, alignment=TA_LEFT,
)

sTableCell = ParagraphStyle(
    "TableCell", fontName="Times-Roman", fontSize=9.5, leading=12,
    textColor=TEXT_COLOR, alignment=TA_LEFT,
)

sCode = ParagraphStyle(
    "Code", fontName="Courier", fontSize=9, leading=12,
    leftIndent=36, spaceAfter=8, backColor=LIGHT_GRAY,
)

sBoxTitle = ParagraphStyle(
    "BoxTitle", fontName="Times-BoldItalic", fontSize=11,
    textColor=ACCENT_BLUE, alignment=TA_CENTER,
    spaceBefore=8, spaceAfter=6,
)

sBoxBody = ParagraphStyle(
    "BoxBody", parent=sBody,
    leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4,
)

sTitle = ParagraphStyle(
    "DocTitle", fontName="Times-Bold", fontSize=22, leading=26,
    textColor=PENN_BLUE, alignment=TA_CENTER, spaceAfter=6,
)

sSubtitle = ParagraphStyle(
    "DocSubtitle", fontName="Times-Italic", fontSize=13, leading=16,
    textColor=DARK_GRAY, alignment=TA_CENTER, spaceAfter=4,
)

sAuthor = ParagraphStyle(
    "Author", fontName="Times-Italic", fontSize=10, leading=13,
    textColor=DARK_GRAY, alignment=TA_CENTER, spaceAfter=20,
)

sFootnote = ParagraphStyle(
    "Footnote", parent=sBody, fontSize=8.5, leading=11,
    textColor=DARK_GRAY,
)
```

### Helper Functions

```python
def make_table(headers, rows, col_widths=None):
    w = CONTENT_W
    if col_widths is None:
        n = len(headers)
        col_widths = [w / n] * n

    data = [[Paragraph(h, sTableHeader) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), sTableCell) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PENN_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))
    return t


def info_box(title, body_text):
    data = []
    if title:
        data.append([Paragraph(title, sBoxTitle)])
    data.append([Paragraph(body_text, sBoxBody)])
    t = Table(data, colWidths=[CONTENT_W - 1.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 1, MED_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def h1_with_rule(text):
    """H1 heading followed by a thin gray rule."""
    return [
        Paragraph(text, sH1),
        HRFlowable(width="100%", thickness=0.5, color=MED_GRAY,
                    spaceBefore=0, spaceAfter=8),
    ]
```

### Page Templates

```python
def later_pages(canvas_obj, doc):
    """Header bar with title/subtitle + footer. Used on pages 2+."""
    canvas_obj.saveState()
    y = PAGE_H - 0.75 * inch
    # Header rule
    canvas_obj.setStrokeColor(PENN_BLUE)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(L_MARGIN, y, PAGE_W - R_MARGIN, y)
    # Header text
    canvas_obj.setFont("Times-Bold", 8.5)
    canvas_obj.setFillColor(PENN_BLUE)
    canvas_obj.drawString(L_MARGIN, y + 6, doc_title)
    canvas_obj.drawRightString(PAGE_W - R_MARGIN, y + 6, doc_subtitle)
    # Footer
    canvas_obj.setFont("Times-Roman", 8.5)
    canvas_obj.setFillColor(DARK_GRAY)
    canvas_obj.drawCentredString(PAGE_W / 2, 0.6 * inch, f"Page {doc.page}")
    canvas_obj.restoreState()

def first_page(canvas_obj, doc):
    """Logo centered at top + footer only. No header bar."""
    canvas_obj.saveState()
    if os.path.exists(LOGO_PATH):
        x = (PAGE_W - LOGO_WIDTH) / 2
        y = PAGE_H - 0.9 * inch
        canvas_obj.drawImage(
            LOGO_PATH, x, y - LOGO_HEIGHT + 0.3 * inch,
            width=LOGO_WIDTH, height=LOGO_HEIGHT,
            preserveAspectRatio=True,
        )
    # Footer
    canvas_obj.setFont("Times-Roman", 8.5)
    canvas_obj.setFillColor(DARK_GRAY)
    canvas_obj.drawCentredString(PAGE_W / 2, 0.6 * inch, f"Page {doc.page}")
    canvas_obj.restoreState()


def build_doc(output_path):
    """Create the document with first-page and later-page templates."""
    frame = Frame(L_MARGIN, B_MARGIN, CONTENT_W,
                  PAGE_H - T_MARGIN_LATER - B_MARGIN, id="normal")

    doc = BaseDocTemplate(
        output_path, pagesize=letter,
        leftMargin=L_MARGIN, rightMargin=R_MARGIN,
        topMargin=T_MARGIN_LATER, bottomMargin=B_MARGIN,
    )

    template_first = PageTemplate(id="first", frames=frame, onPage=first_page)
    template_later = PageTemplate(id="later", frames=frame, onPage=later_pages)
    doc.addPageTemplates([template_first, template_later])
    return doc
```

### Markdown Inline Formatting

Convert inline markdown to ReportLab XML markup. **Escape HTML entities
first**, then apply formatting conversions:

```python
def md_inline(text):
    """Convert inline markdown to ReportLab Paragraph XML."""
    # Step 1: Escape XML entities
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # Step 2: Smart quotes
    text = text.replace(" \"", " \u201C")  # opening double
    text = re.sub(r'"(\s|$|[.,;:!?)])', r'\u201D\1', text)  # closing double
    text = text.replace("\"", "\u201C")  # remaining opening
    text = text.replace(" '", " \u2018")
    text = text.replace("'", "\u2019")  # apostrophes and closing single

    # Step 3: Bold + italic (do *** before ** before *)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)

    # Step 4: Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', text)

    # Step 5: Links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)',
                  r'<font color="#2E75B6"><u>\1</u></font>', text)

    return text
```

### Block-Level Parsing

```python
def parse_md_to_flowables(md_text):
    """Parse markdown text into a list of ReportLab flowables."""
    lines = md_text.split("\n")
    story = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line — skip
        if not stripped:
            i += 1
            continue

        # Code fence
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code_text = "\n".join(code_lines)
            code_text = code_text.replace("&", "&amp;")
            code_text = code_text.replace("<", "&lt;")
            code_text = code_text.replace(">", "&gt;")
            story.append(Preformatted(code_text, sCode))
            continue

        # Headings
        if stripped.startswith("### "):
            story.append(Paragraph(md_inline(stripped[4:]), sH3))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(md_inline(stripped[3:]), sH2))
            i += 1
            continue
        if stripped.startswith("# "):
            story.extend(h1_with_rule(md_inline(stripped[2:])))
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=1,
                         color=MED_GRAY, spaceBefore=12, spaceAfter=12))
            i += 1
            continue

        # Table (lines starting with |)
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
            rows = []
            for tl in table_lines[2:]:  # skip separator row
                rows.append([md_inline(c.strip()) for c in tl.split("|")[1:-1]])
            header_texts = [md_inline(h) for h in headers]
            story.append(make_table(header_texts, rows))
            story.append(Spacer(1, 0.1 * inch))
            continue

        # Blockquote
        if stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            story.append(info_box(None, md_inline(" ".join(quote_lines))))
            continue

        # Nested bullet
        if re.match(r'^  +[-*] ', line):
            text = re.sub(r'^  +[-*] ', '', line)
            story.append(Paragraph(md_inline(text), sBulletInner,
                         bulletText="\u2022"))
            i += 1
            continue

        # Bullet
        if re.match(r'^[-*] ', stripped):
            text = re.sub(r'^[-*] ', '', stripped)
            story.append(Paragraph(md_inline(text), sBullet,
                         bulletText="\u2013"))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\. ', stripped)
        if m:
            num = m.group(1)
            text = stripped[len(num) + 2:]
            story.append(Paragraph(md_inline(text), sBullet,
                         bulletText=f"{num}."))
            i += 1
            continue

        # Body paragraph — accumulate consecutive non-blank, non-special lines
        para_lines = []
        while (i < len(lines) and lines[i].strip()
               and not lines[i].strip().startswith("#")
               and not lines[i].strip().startswith("```")
               and not lines[i].strip().startswith("|")
               and not lines[i].strip().startswith("> ")
               and not re.match(r'^[-*] ', lines[i].strip())
               and not re.match(r'^\d+\. ', lines[i].strip())
               and lines[i].strip() not in ("---", "***", "___")):
            para_lines.append(lines[i].strip())
            i += 1
        if para_lines:
            story.append(Paragraph(md_inline(" ".join(para_lines)), sBody))

    return story
```

## Workflow

1. **Get the markdown**: Read from file path or conversation content.

2. **Verify the logo exists** at
   `~/.claude/skills/law-document/assets/PennCareyLaw_UPenn_Blue-WhiteBkrnd.png`.
   If missing, stop and tell the user.

3. **Determine title metadata**: Extract from the first H1 in the markdown,
   or ask the user. Set `doc_title` and `doc_subtitle` — these appear in
   the header bar on pages 2+. If the markdown has a clear title and subtitle
   structure, use those. Otherwise use the filename.

4. **Parse the markdown** using `parse_md_to_flowables()`.

5. **Build the PDF**: Create doc with `build_doc(output_path)`. Assemble the
   story with title area, `NextPageTemplate("later")` after the first page
   content, and parsed flowables. Build with `doc.build(story)`.

6. **Present the PDF** path to the user.

## What NOT to Do

- Do not use `SimpleDocTemplate` — use `BaseDocTemplate` with page templates
- Do not use Unicode bullet characters in Paragraph text
- Do not use `\n` inside Paragraphs — use `<br/>` or separate flowables
- Do not forget to escape `&` as `&amp;` before adding markup
- Do not use `mask='auto'` on drawImage for logos (causes rendering issues)
