---
name: materials-md
description: >
  Convert PDF, DOCX, PPTX, or HTML files to clean markdown for AI ingestion using the
  materials-converter tool (https://github.com/ai-teaching-lab/materials-converter). Use
  when the user wants a "clean markdown version" of a document, wants to feed a document to
  another tool (fact-checker, editor, document generator) and needs the markdown form first,
  or wants to extract speaker notes from a deck. Trigger on phrases like "convert this PDF",
  "make this article markdown", "extract the speaker notes", "give me the lecture text",
  "give me a clean version of this", or any request to turn a non-markdown document into
  markdown. This skill dispatches to a deterministic Python CLI — it does NOT re-implement
  conversion in the model.
---

# materials-md — natural-language wrapper for materials-converter

This skill is a thin dispatcher. It reads natural-language requests, picks the right
conversion flags, runs the `materials-convert` CLI, and reports where the output landed.
**Conversion logic itself lives in deterministic Python** — do not try to convert files
yourself by reading the source and re-summarizing. The whole point of the Python tool is
byte-identical reproducibility for legal and scholarly materials; running content through a
model defeats that.

The underlying tool is [`materials-converter`](https://github.com/ai-teaching-lab/materials-converter),
an open-source (Apache 2.0) converter built on IBM Research's **Docling**.

## Prerequisite — install the converter

The skill calls the `materials-convert` command, which comes from the `materials-converter`
package:

```bash
pip install git+https://github.com/ai-teaching-lab/materials-converter
```

**First-run note:** Docling downloads its model weights (a few hundred MB) on first use and
caches them locally, so the first conversion needs network access and runs slower than later
ones. If `materials-convert` is not found on the `PATH`, install it as above before
converting.

## When to use this skill

Trigger when the user asks you to:

- Convert a PDF, DOCX, PPTX, or HTML file to markdown
- Get a "clean markdown version" of a document
- Extract speaker notes from a deck (`--notes-only`)
- Convert a document to markdown so it can be fed to another tool (a fact-checker, an editor,
  a document generator) downstream
- "make this AI-ready", "give me the lecture text", "convert that for me", or similar

If the user hands you a `.pdf`, `.docx`, `.pptx`, `.htm`, or `.html` file and the request
involves text extraction or downstream processing, this skill is the right entry point.

## When NOT to use this skill

- The file is already markdown (`.md`) — no conversion needed
- The user wants to *create* a document from prose (use a document- or PDF-generation tool)
- The conversion is already done and the user just wants to discuss the output
- The user explicitly asks for a different tool (pandoc, Acrobat export, etc.)

## How to invoke

```
materials-convert <input-path> -o <output-path>
```

Default output is `<input-dir>/converted/<input-stem>.md` if `-o` is omitted, but it's
almost always better to pick an explicit output path so the user knows where to find it. For
ad-hoc conversions, default to the user's downloads directory.

## Mapping requests to flags

| User says | Flag(s) | Format |
|---|---|---|
| "convert this" / no qualifier | (none — default mode for the format) | any |
| "give me just the lecture text" / "extract the speaker notes" / "transcript" | `--notes-only` | PPTX |
| "include the reviewer comments" / "with comments" | `--full` | DOCX |
| "show the tracked changes" / "with redlines" / "show edits" | `--show-revisions` | DOCX |
| "keep the images" / "extract the figures" | `--keep-images` | DOCX |
| "extract the images" / "get the figures" | `--images` | PDF |
| "strip the navigation" / "clean it up" / "no nav/footer" | `--strip-html-noise` | HTML |
| "without the page markers" / "no markers" | `--no-page-markers` | any |
| "just pages 1-50" / "first 20 pages" | `--pages 1-50` | PDF |
| "the whole folder" / "convert all of these" | `--batch` | dir |
| "and subfolders too" / "recurse" | `--recursive` (with `--batch`) | dir |
| "use 4 workers" / "fast" / "in parallel" | `--workers 4` (with `--batch`) | dir |
| "stop on first failure" / "strict batch" | `--no-continue-on-error` (with `--batch`) | dir |
| "save the report" / "give me a JSON summary" | `--save-report` (with `--batch`) | dir |
| "verbose" / "show me what it's doing" / "debug output" | `-v` / `--verbose` | any |
| "save the log to X" | `--log-file X` | any |
| "OCR this scanned PDF" | `--ocr` | PDF |

If you're not sure what flags to pick, default to the no-flag invocation. The lean defaults
are tuned for AI ingestion.

## Output paths

- **Ad-hoc** (the user just wants to see the markdown): write to the downloads directory and
  tell the user where it landed.
- **Project work** where the user pointed at a specific folder: use the CLI's default
  (`<input-dir>/converted/<stem>.md`) so the output sits beside the source.
- **Pipeline work** ("then fact-check it", "then format it"): write to a tmp path the
  downstream tool can read, and chain.

## Batch conversion

For a whole folder, pass the directory with `--batch`:

```
materials-convert <folder> --batch --workers 4 --save-report
```

Each worker pays a one-time model-warmup cost, so for small batches (≤ ~8 files) the serial
default is faster. `--save-report` writes a JSON summary with per-file statistics. Note: the
batch writes its log and (optionally) report into a `converted/` subdirectory — make sure
that directory can be created (an explicit `--log-file` whose parent does not yet exist will
fail).

## Reading the output

Once conversion succeeds, the markdown contains position markers that downstream tools can
use to cite passages:

- **PDF**: `<!-- Page i -->`, `<!-- Page 1 -->` (uses the PDF's actual page labels — Roman
  for front matter, decimal for body)
- **PPTX**: `<!-- Slide N -->` and `<!-- Speaker notes -->`
- **DOCX**: `<!-- Section N: heading-text -->`
- **HTML**: `<!-- Section N: heading-text -->`

When telling the user the conversion is done, mention any non-trivial details from the output
— e.g., "got the reviewer comments in a `## Reviewer Comments` appendix", "`--notes-only`
produced a 1,200-word transcript dropping bullet content."

## What this skill does NOT do

- It does not read PDFs/DOCX/PPTX directly via the model. The CLI does the conversion
  deterministically; the model orchestrates and reports.
- It does not modify the conversion logic. Bugs in the CLI are fixed in the
  [materials-converter repo](https://github.com/ai-teaching-lab/materials-converter), not by
  editing this skill.
- It does not retry failed conversions automatically. If `materials-convert` exits non-zero,
  surface the stderr message to the user and ask how to proceed.
- It does not invoke `--batch` against a directory unless the user explicitly asks for batch
  behavior. A single file is the default unit of work.
- It does not go the other direction (markdown → PDF/DOCX). That's a document-generation
  tool's job.
