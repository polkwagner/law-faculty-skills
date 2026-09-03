---
name: docx-comment-summary
description: >
  Extract reviewer comments (text, author, timestamp, anchored passage, replies) from
  one or more Word .docx files into a markdown report. Use for any request to pull,
  digest, or compare comments.
license: CC-BY-4.0
metadata:
  author: "[Your Name]"
---

# DOCX Comment Summary Skill

Extracts and summarizes comments from one or more .docx files into a clean
markdown report in document order. Captures: comment text, author, timestamp,
anchored text (the passage the comment is attached to), and threaded replies.

## Environment

Resolve files relative to this skill's directory: `~/.claude/skills/docx-comment-summary/` in Claude Code and, via the `~/.codex/skills/` symlink, in Codex; `/mnt/skills/user/docx-comment-summary/` on claude.ai. Output to `~/Downloads/` (or a user-specified path) locally, `/mnt/user-data/outputs/` on claude.ai. User uploads on claude.ai are in `/mnt/user-data/uploads/`.

## Workflow

### Step 1 — Get file paths

Ask the user which .docx file(s) to process. They may provide:
- One or more explicit file paths
- A directory to scan for .docx files
- A description like "the files I just mentioned" — resolve from conversation context

If given a directory, find all .docx files in it:
```bash
find /path/to/dir -maxdepth 1 -name "*.docx" -type f
```

On claude.ai, uploads live in `/mnt/user-data/uploads/`: match the files the user
named, or if they simply uploaded files, process every .docx found there.

### Step 2 — Run extraction script

The script is bundled with this skill (resolve it relative to this skill's directory; write the output to the runtime's output location):

```bash
python3 <this-skill-dir>/scripts/extract_comments.py \
  "/path/to/file1.docx" "/path/to/file2.docx" -o ~/Downloads/comment_summary.md
```

Pass all .docx files in a single call. The script handles multiple files and
labels each section by filename.

### Step 3 — Read and present results

Read the output file and present the markdown directly in the conversation:

```bash
cat ~/Downloads/comment_summary.md
```

The output is markdown and renders well in the chat. Also tell the user where
the file is saved in case they want to keep it.

### Step 4 — Offer follow-up

When the reviewer count or comment volume makes it useful, offer to regroup by author or theme, or to compare across files (who said what, consensus vs. outliers).

---

## Output Format

The script produces markdown. For a single file it outputs directly. For
multiple files it adds a `# filename` header per file.

Each comment looks like:

```
---
**Comment 3** — Jane Smith · 2025-03-10 14:22
> "the proposed timeline for Phase II"
This seems optimistic — we haven't accounted for the IRB review period.

> **↳ Reply** — John Doe · 2025-03-11 09:05
> Good catch. I'll add two weeks.
```

---

## How the Script Works

The extraction script (`scripts/extract_comments.py`) is pure stdlib Python —
no pip dependencies. It:

1. Opens the .docx as a zip archive
2. Parses `word/comments.xml` for comment text, author, and dates
3. Walks `word/document.xml` to find anchored text and document order
4. Resolves reply threading from two sources:
   - `w14:paraIdParent` attributes on comment paragraphs (Word 2013+)
   - `word/commentsExtended.xml` or `word/commentsExtensible.xml` (Word 2016+)
5. Nests replies under parent comments and renders to markdown

Reply threading requires matching `paraId` values (not comment IDs) across
these XML files. The script builds a `paraId → comment_id` mapping to resolve
the relationship correctly.

---

## Troubleshooting

**No comments found** — The file may use an older comment format or comments
were already resolved/deleted. Check manually:
```bash
python3 -c "
import zipfile, sys
with zipfile.ZipFile(sys.argv[1]) as z:
    names = [n for n in z.namelist() if 'comment' in n.lower()]
    print(names or 'No comment files found in archive')
" /path/to/file.docx
```

**Anchored text is empty** — Some Word versions don't use `commentRangeStart`/
`End` markup consistently. The comment body will still be extracted; the anchor
field will just be blank.

**Replies showing as top-level comments** — This happens when the .docx was
created by a Word version or third-party tool that doesn't write `paraId`
attributes or extended comment files. The comment content is still correct;
only the threading is lost.
