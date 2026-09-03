#!/usr/bin/env python3
"""Validate a generated .docx and repair the two corruption patterns that stop
Word from opening a file.

Usage:  validate_docx.py path/to/output.docx [more.docx ...]

Prints one line per file:
  VALID: <path>                       nothing wrong
  REPAIRED <path>: <what was fixed>   the file was rewritten in place
and exits non-zero only on a hard failure (missing file, not a .docx zip,
no word/styles.xml). A REPAIRED line means the generation method produced a
corrupted file: regenerate with python-docx rather than trusting the repair.

Both checks target Pandoc artifacts. python-docx does not produce them, but
the check stays as a safety net regardless of how the file was built.
"""
import os
import re
import sys
import zipfile
from collections import Counter

STYLE_ID_RE = re.compile(r'<w:style\s[^>]*w:styleId="([^"]*)"')
STYLE_BLOCK_RE = re.compile(
    r'(<w:style\s[^>]*w:styleId="([^"]*)"[^>]*>.*?</w:style>)', re.DOTALL
)


def validate_and_repair_docx(filepath: str) -> list[str]:
    """Check one .docx for known corruption; repair in place. Returns repairs."""
    repairs = []
    with zipfile.ZipFile(filepath, "r") as z:
        styles_xml = z.read("word/styles.xml").decode("utf-8")

        # Check 1: duplicate style IDs. Word refuses the file outright.
        dupes = [k for k, v in Counter(STYLE_ID_RE.findall(styles_xml)).items() if v > 1]
        if dupes:
            repairs.append(f"Duplicate style IDs found: {dupes}")
            seen = set()

            def dedup(m):
                sid = m.group(2)
                if sid in seen:
                    return ""
                seen.add(sid)
                return m.group(1)

            styles_xml = STYLE_BLOCK_RE.sub(dedup, styles_xml)
            styles_xml = re.sub(r"\n\s*\n", "\n", styles_xml)

        # Check 2: images named after relationship IDs. Reported, not rewritten:
        # renaming them safely means rewriting the relationships too, and the
        # right fix is regeneration.
        bad_images = [
            n for n in z.namelist()
            if n.startswith("word/media/rId") and n.endswith(".png")
        ]
        if bad_images:
            repairs.append(f"Images with rId names found: {bad_images}")

        if repairs:
            tmp = filepath + ".tmp"
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z_out:
                for item in z.infolist():
                    if item.filename == "word/styles.xml":
                        z_out.writestr(item, styles_xml.encode("utf-8"))
                    else:
                        z_out.writestr(item, z.read(item.filename))
    if repairs:
        os.replace(tmp, filepath)
    return repairs


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    rc = 0
    for filepath in argv[1:]:
        if not os.path.isfile(filepath):
            print(f"ERROR: not a file: {filepath}", file=sys.stderr)
            rc = 1
            continue
        try:
            repairs = validate_and_repair_docx(filepath)
        except (zipfile.BadZipFile, KeyError) as e:
            print(f"ERROR: {filepath} is not a readable .docx ({e})", file=sys.stderr)
            rc = 1
            continue
        if repairs:
            print(f"REPAIRED {filepath}: {'; '.join(repairs)}")
        else:
            print(f"VALID: {filepath}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
