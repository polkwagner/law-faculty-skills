---
name: law-memo
description: Draft and produce formatted Word document (.docx) memos in Penn Carey Law style. Use this skill whenever the user asks to write, draft, or create a memo, memorandum, or formal internal document for faculty, committees, or the Dean's office. Trigger phrases include "write a memo", "draft a memo", "memo to faculty", "memo to EPC", "memorandum", or any request to produce a formal internal communication as a document. Always use this skill — do not attempt to format or draft memos freehand without consulting it first.
---

# Law Memo Skill

Produces fully formatted Penn Carey Law memos as `.docx` files, matching [Your Name]'s established style: Penn Carey Law letterhead, standard header block, Cambria body text. Voice baseline (tone, banned phrases, preferred expressions) is defined in CLAUDE.md — that always applies. This skill adds memo-specific formatting and structure.

---

## Environment

This skill works in both **Claude Code CLI** and **Claude.ai / Cowork**. Use whichever paths exist:

- **Skills:** `~/.claude/skills/` (CLI) or `/mnt/skills/user/` (web)
- **Output:** `~/Downloads/` or user-specified path (CLI) or `/mnt/user-data/outputs/` (web)

---

## Before Drafting

1. If a sample memo exists at `~/.claude/skills/law-memo/law-memo_sample.docx` (CLI) or `/mnt/skills/user/law-memo/law-memo_sample.docx` (web), clone it as the base for exact formatting
2. Clarify with the user if needed: recipient, subject/RE line, key points to cover, any attachments or action items

---

## Document Formatting Spec

### Page Setup
- **Margins**: 1" on all sides (1440 twips)
- **Font**: Cambria 12pt throughout — header block AND body text. Do NOT use Book Antiqua.
- **Line spacing**: 276 / auto (~1.15)

### Logo
- Centered paragraph, `w:after="200"`
- Image: `PennCareyLaw_UPenn_Blue-WhiteBkrnd.png` from `~/.claude/skills/law-memo/assets/` (CLI) or `/mnt/skills/user/law-memo/assets/` (web)
- EMU dimensions: `cx="2628900" cy="476250"` (matches sample exactly)
- **ALWAYS include the logo. This is mandatory.**

### MEMORANDUM Title
- Centered, `w:after="240"`, Cambria bold 12pt

### Header Block
```
TO:     [Recipient]
FROM:   [Your Name], [Your Title]
DATE:   [Full date — e.g. March 11, 2026. Always use the actual current date, never just month/year.]
RE:     [Subject — bold]
```

Each header line paragraph:
- Tab stop at 1440 twips: `<w:tabs><w:tab w:val="left" w:pos="1440"/></w:tabs>`
- Spacing: `w:line="276" w:lineRule="auto" w:after="160"`
- Label run: Cambria bold 12pt
- Value run: Cambria regular 12pt (tab + value), EXCEPT RE value which is bold

**RE line specifically**: add a hanging indent so long subjects wrap under the text, not under "RE:":
```xml
<w:ind w:left="1440" w:hanging="1440"/>
```

### Horizontal Rule
Paragraph with bottom border, `w:after="240"`:
```xml
<w:pBdr><w:bottom w:val="single" w:color="000000" w:sz="6" w:space="1"/></w:pBdr>
```

### Body Text
- Cambria 12pt, `w:line="276" w:lineRule="auto" w:after="160"`
- **No Book Antiqua anywhere**
- Bold used sparingly for key terms and section heads
- Section headings: bold Cambria 12pt, `w:before="200" w:after="80"`

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

### Footer
Italic Cambria 10pt "Page x of y." centered. If cloning from sample, the footer is preserved automatically.

### Section Properties (sectPr)
```xml
<w:sectPr>
  <w:footerReference w:type="default" r:id="rId6"/>
  <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
  <w:pgNumType/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
```

---

## Memo-Specific Voice

Memos layer these conventions on top of the CLAUDE.md voice baseline:

- More formal than emails but never bureaucratic
- Opens directly with the situation or context — no throat-clearing
- States recommendations clearly: "I recommend," "the EPC should," "faculty should be advised"
- Bullet lists always introduced by a full sentence, never launched cold
- Closes with a concrete next-steps or action paragraph
- No personal sign-off; memo ends with the action/next-steps paragraph
- Collegial but authoritative — writes as a peer who has done the work and is sharing conclusions

**FROM line**: Always "[Your Name], [Your Title]" unless context clearly calls for a different title.

---

## Structural Patterns

### Standard policy/recommendation memo
1. **Situation paragraph** — what is the issue and why it matters (2-4 sentences)
2. **Recommendation paragraph** — what [Your Name] recommends, leading into bullet list if needed
3. **Bullet list** (if applicable) — em-dash style
4. **Implications/advisory paragraph** (if applicable)
5. **Next steps paragraph** — who will do what, closing the loop

### Short informational memo
1. **Purpose sentence** — one sentence stating what the memo does
2. **Body** — 2-4 paragraphs of substance
3. **Closing** — brief action or availability statement

---

## Filename Convention
`Memo_[Topic]_[YYYY-MM].docx` (e.g., `Memo_OCI-Calendar_2025-09.docx`)

---

## Quick Checklist Before Delivering

- [ ] **LOGO INCLUDED** — Penn Carey Law logo in title block (MANDATORY, ALWAYS)
- [ ] MEMORANDUM centered, Cambria bold 12pt
- [ ] Header block: TO / FROM / DATE / RE — labels bold, tab at 1440, spacing after 160
- [ ] DATE is the actual current date (full: e.g. "March 18, 2026") — never just month/year
- [ ] RE value is bold, with hanging indent (`w:left="1440" w:hanging="1440"`)
- [ ] Horizontal rule after header (bottom border, sz=6, after=240)
- [ ] Cambria 12pt throughout — NO Book Antiqua
- [ ] Em-dash bullets with hanging indent, never Word list bullets
- [ ] Footer: italic Cambria 10pt "Page x of y." centered
- [ ] Tone follows CLAUDE.md voice baseline (direct, active, no filler)
- [ ] Closes with action/next-steps paragraph
