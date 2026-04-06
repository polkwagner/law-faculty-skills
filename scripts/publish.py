#!/usr/bin/env python3
"""Publish skills from working installation to public repo.

Copies included skills, applies privacy scrub rules, renames directories and files.
Run from repo root: python3 scripts/publish.py
"""

import os
import re
import shutil
from pathlib import Path

# --- Configuration ---

SOURCE_DIR = Path(os.path.expanduser("~/.claude/skills"))
REPO_ROOT = Path(__file__).resolve().parent.parent

# Skills to include (source_name -> published_name)
SKILL_MAP = {
    "law-mcq-generator":     "law-mcq-generator",
    "law-essay-generator":   "law-essay-generator",
    "lecture-slide-reviewer": "lecture-slide-reviewer",
    "polk-memo":             "law-memo",
    "polk-document":         "law-document",
    "polk-email-style":      "law-email-style",
    "md-to-pdf":             "md-to-pdf",
    "docx-comment-summary":  "docx-comment-summary",
    "rex":                   "rex",
    "eddie":                 "eddie",
}

# Skills that should NOT appear in output (safety check)
EXCLUDED_SKILLS = {"send-to-email"}

# law-class-problems and law-class-prep are maintained directly in the repo,
# not synced from source. They are not in SKILL_MAP so they won't be touched.

# Files to skip during copy
SKIP_FILES = {".DS_Store", "design.md"}

# File extensions to apply scrub rules to
TEXT_EXTENSIONS = {".md", ".py", ".js", ".txt", ".json", ".yaml", ".yml"}

# --- File Rename Rules ---
FILE_RENAME_RULES = [
    ("polk-memo", "law-memo"),
    ("polk-document", "law-document"),
    ("polk-email-style", "law-email-style"),
]

# --- Scrub Rules ---
# Applied IN ORDER to all text file content.
# ORDERING MATTERS: specific patterns first, catch-all last.

SCRUB_RULES = [
    # --- Email addresses ---
    (r"pwagner@law\.upenn\.edu", "your-email@law.upenn.edu"),
    (r"polk@polkwagner\.com", "your-email@example.com"),

    # --- Webhook URLs (safety net) ---
    (r"https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec", "YOUR_WEBHOOK_URL"),

    # --- Title (before name rules) ---
    (r"Deputy Dean for Academic Affairs and Innovation", "[Your Title]"),

    # --- Compound name+title patterns (most specific first) ---
    (r'Always "Polk Wagner, \[Your Title\]"',
     'Always "[Your Name], [Your Title]"'),
    (r"FROM:\s+Polk Wagner,\s*\[Your Title\]",
     "FROM:   [Your Name], [Your Title]"),

    # --- Skill title headers ---
    (r"# Polk Wagner Memo Skill", "# Law Memo Skill"),
    (r"# Polk Wagner Document Skill", "# Law Document Skill"),
    (r"# Polk Wagner Email Style Guide", "# Law Email Style Guide"),

    # --- Name in specific compound contexts ---
    (r"\|\s*\*\*Professor\*\*\s*\|\s*Polk Wagner\s*\|",
     "| **Professor** | [Your Name] |"),
    (r"\*\*Author:\*\*\s*Polk Wagner \+ Claude",
     "**Author:** [Your Name] + Claude"),
    (r"in Polk Wagner Penn Carey Law style", "in Penn Carey Law style"),
    (r"Polk Wagner's Penn Carey Law style", "Penn Carey Law style"),
    (r"in Polk Wagner's", "in your"),

    # --- Catch-all "Polk Wagner" (sweeps anything specific rules missed) ---
    (r"Polk Wagner", "[Your Name]"),

    # --- Standalone "Polk" in specific contexts (AFTER catch-all) ---
    (r"Clarify with Polk", "Clarify with the user"),
    (r"Polk asks", "the user asks"),
    (r"Polk often uses", "The default style uses"),
    (r"on Polk's behalf", "on the user's behalf"),
    (r'Just "Polk" on its own line', 'Just your first name on its own line'),

    # --- Eddie-specific standalone "Polk" patterns ---
    # "the author" — referring to the person whose document is being reviewed
    (r"hurt Polk", "hurt the author"),
    (r"\. Polk's voice", ". The author's voice"),
    (r"Polk's voice", "the author's voice"),
    (r"implies Polk is", "implies the author is"),
    (r"implying Polk is", "implying the author is"),
    (r"people Polk outranks", "people the author outranks"),
    (r"authority Polk doesn't hold", "authority the author doesn't hold"),
    (r"helps Polk", "helps you"),
    (r"help Polk", "help you"),
    (r"Polk should fix", "you should fix"),
    # "the user" — referring to the person invoking Eddie
    (r"when Polk says", "when the user says"),
    (r"If Polk just", "If the user just"),
    (r"If Polk says", "If the user says"),
    (r"Polk says", "the user says"),
    (r"Polk mentioned", "the user mentioned"),
    (r"Polk gave", "the user gave"),
    # Section header and sign-off
    (r"## About Polk", "## About the Author"),
    (r'just "Polk"', 'just "[Your First Name]"'),
    (r'"Best,\\nPolk"', '"Best,\\n[Your First Name]"'),

    # --- Final standalone "Polk" catch-all (sweeps any remaining) ---
    (r"\bPolk\b", "[Your Name]"),

    # --- Directory/skill name cross-references (broadest — last) ---
    (r"ip-problems", "law-class-problems"),
    (r"class-prep-skill", "law-class-prep"),
    (r"polk-document", "law-document"),
    (r"polk-memo", "law-memo"),
    (r"polk-email-style", "law-email-style"),
]


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def rename_file(filename: str) -> str:
    """Apply file rename rules to a filename."""
    for old_prefix, new_prefix in FILE_RENAME_RULES:
        if filename.startswith(old_prefix):
            return new_prefix + filename[len(old_prefix):]
    return filename


def scrub_text(text: str) -> tuple[str, list[str]]:
    """Apply all scrub rules to text. Returns (scrubbed_text, list_of_changes)."""
    changes = []
    for pattern, replacement in SCRUB_RULES:
        new_text = re.sub(pattern, replacement, text)
        if new_text != text:
            matches = re.findall(pattern, text)
            changes.append(f"  '{pattern}' -> '{replacement}' ({len(matches)} match(es))")
            text = new_text
    return text, changes


def copy_skill(source_name: str, dest_name: str, manifest: list[str]):
    """Copy a skill directory, applying scrub rules and file renames."""
    src = SOURCE_DIR / source_name
    dst = REPO_ROOT / dest_name

    if not src.exists():
        manifest.append(f"WARNING: SKIP {source_name}: not found at {src}")
        return

    if dst.exists():
        shutil.rmtree(dst)

    manifest.append(f"\n--- {source_name} -> {dest_name} ---")

    for src_file in sorted(src.rglob("*")):
        if not src_file.is_file():
            continue
        if src_file.name in SKIP_FILES:
            manifest.append(f"  {src_file.relative_to(src)} (SKIPPED)")
            continue
        if "__pycache__" in str(src_file):
            continue

        rel = src_file.relative_to(src)

        # Apply file rename rules
        new_name = rename_file(rel.name)
        if new_name != rel.name:
            renamed_rel = rel.with_name(new_name)
            manifest.append(f"  {rel} -> {renamed_rel} (renamed)")
            rel = renamed_rel

        dst_file = dst / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        if is_text_file(src_file):
            text = src_file.read_text(encoding="utf-8")
            scrubbed, changes = scrub_text(text)
            dst_file.write_text(scrubbed, encoding="utf-8")
            if changes:
                manifest.append(f"  {rel} (scrubbed):")
                manifest.extend(changes)
            else:
                manifest.append(f"  {rel}")
        else:
            shutil.copy2(src_file, dst_file)
            manifest.append(f"  {rel} (binary copy)")


def safety_check():
    """Verify no excluded skills ended up in the output."""
    problems = []
    for name in EXCLUDED_SKILLS:
        path = REPO_ROOT / name
        if path.exists():
            problems.append(f"Excluded skill '{name}' exists at {path}")
    return problems


def check_placeholders():
    """Warn about unfilled placeholders in top-level markdown."""
    problems = []
    for md_file in REPO_ROOT.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for placeholder in ["OWNER/REPO_NAME", "YOUR_WEBHOOK_URL"]:
            if placeholder in content:
                problems.append(f"Unfilled placeholder '{placeholder}' in {md_file.name}")
    return problems


def main():
    print("Publishing skills from", SOURCE_DIR)
    print("Destination:", REPO_ROOT)
    print()

    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}")
        return

    manifest = ["# Publish Manifest", f"Source: {SOURCE_DIR}", f"Dest: {REPO_ROOT}", ""]

    for source_name, dest_name in SKILL_MAP.items():
        copy_skill(source_name, dest_name, manifest)

    # Safety check: excluded skills
    problems = safety_check()
    if problems:
        manifest.append("\nSAFETY CHECK FAILURES:")
        manifest.extend(f"  - {p}" for p in problems)

    # Post-scrub verification
    private_strings = ["pwagner@", "polk@polkwagner", "AKfycbw", "Polk Wagner",
                       "Deputy Dean for Academic Affairs"]
    manifest.append("\n--- Post-scrub verification ---")
    found_leaks = False
    for dest_name in SKILL_MAP.values():
        dest_dir = REPO_ROOT / dest_name
        if not dest_dir.exists():
            continue
        for f in dest_dir.rglob("*"):
            if not f.is_file() or not is_text_file(f):
                continue
            content = f.read_text(encoding="utf-8")
            for s in private_strings:
                if s in content:
                    manifest.append(f"  LEAK: '{s}' found in {f.relative_to(REPO_ROOT)}")
                    found_leaks = True

    if not found_leaks:
        manifest.append("  OK: No private strings found in output")

    # Placeholder check
    placeholder_warnings = check_placeholders()
    if placeholder_warnings:
        manifest.append("\n--- Placeholder warnings ---")
        manifest.extend(f"  WARNING: {w}" for w in placeholder_warnings)

    print("\n".join(manifest))


if __name__ == "__main__":
    main()
