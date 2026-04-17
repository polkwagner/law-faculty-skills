#!/usr/bin/env python3
"""Publish skills from working installation to public repo.

Copies included skills, applies privacy scrub rules, renames directories and files.
Validates published output against the agentskills specification
(https://github.com/agentskills/agentskills).

Run from repo root: python3 scripts/publish.py
"""

import os
import re
import shutil
import sys
from pathlib import Path

import yaml

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
EXCLUDED_SKILLS = {"send-to-email", "polk-slides"}

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

    # --- Agent references — make conditional for published skills ---
    # Full sentence form: "Spawn the `agent` agent and..."
    (r"Spawn the `([a-z-]+)` agent", r"If the `\1` agent is available, spawn it"),
    # Lowercase form: "spawn the `agent` agent..."
    (r"spawn the `([a-z-]+)` agent", r"if the `\1` agent is available, spawn it"),
    # Workflow summary form: "Spawn `agent` agent →" / "spawn `agent` agent →"
    (r"Spawn `([a-z-]+)` agent", r"`\1` agent (if available)"),
    (r"spawn `([a-z-]+)` agent", r"`\1` agent (if available)"),

    # --- Directory/skill name cross-references (broadest — last) ---
    (r"ip-problems", "law-class-problems"),
    (r"(?<![a-z-])class-prep(?![a-z-])", "law-class-prep"),
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
    """Verify no excluded skills would be committed to the output repo.

    Presence alone is not a failure — what matters is whether git would track
    the directory. If it's gitignored, it cannot leak on push. Only flag
    excluded skills that are NOT gitignored (i.e. actually reachable by git).
    """
    import subprocess
    problems = []
    for name in EXCLUDED_SKILLS:
        path = REPO_ROOT / name
        if not path.exists():
            continue
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", "-q", name],
            capture_output=True,
        )
        # check-ignore exit codes: 0 = ignored, 1 = not ignored, 128 = error
        if result.returncode == 1:
            problems.append(
                f"Excluded skill '{name}' exists at {path} and is NOT gitignored"
            )
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


# --- Agentskills Spec Validation ---
# See https://agentskills.io/specification

ALLOWED_FRONTMATTER_FIELDS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
}

# Name: lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens, ≤64 chars
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def fix_name_field(dest_dir: Path):
    """Ensure the name field in SKILL.md matches the destination directory name.

    After scrubbing, the name field should already match (e.g., polk-memo -> law-memo),
    but this provides an explicit safety net rather than relying on scrub rules alone.
    """
    skill_md = dest_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    text = skill_md.read_text(encoding="utf-8")
    expected_name = dest_dir.name

    # Target just the name: line — works regardless of surrounding fields
    new_text = re.sub(
        r"(?m)^(name:\s*)\S+",
        rf"\g<1>{expected_name}",
        text,
        count=1,
    )

    if new_text != text:
        skill_md.write_text(new_text, encoding="utf-8")
        return True
    return False


def validate_published_skill(dest_dir: Path) -> list[str]:
    """Validate a published skill's SKILL.md against the agentskills spec.

    Returns a list of error strings (empty if valid).
    """
    errors = []
    skill_md = dest_dir / "SKILL.md"

    if not skill_md.exists():
        return [f"SKILL.md not found"]

    text = skill_md.read_text(encoding="utf-8")

    # Check frontmatter delimiters
    m = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not m:
        return [f"No valid YAML frontmatter (missing --- delimiters)"]

    # Parse frontmatter
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(fm, dict):
        return [f"Frontmatter is not a YAML mapping"]

    # Unknown fields
    unknown = set(fm.keys()) - ALLOWED_FRONTMATTER_FIELDS
    if unknown:
        errors.append(f"Unknown fields: {', '.join(sorted(unknown))}")

    # name: required, ≤64 chars, valid format, matches directory
    name = fm.get("name")
    if not name or not isinstance(name, str):
        errors.append("Missing or empty required field: name")
    else:
        if name != dest_dir.name:
            errors.append(f"name '{name}' does not match directory '{dest_dir.name}'")
        if len(name) > 64:
            errors.append(f"name exceeds 64 chars ({len(name)})")
        if "--" in name:
            errors.append(f"name contains consecutive hyphens")
        if not NAME_PATTERN.match(name):
            errors.append(f"name '{name}' invalid (must be lowercase alphanumeric + hyphens)")

    # description: required, ≤1024 chars
    desc = fm.get("description")
    if not desc:
        errors.append("Missing or empty required field: description")
    else:
        desc_str = str(desc)
        if len(desc_str) > 1024:
            errors.append(f"description exceeds 1024 chars ({len(desc_str)})")

    # compatibility: optional, ≤500 chars
    compat = fm.get("compatibility")
    if compat is not None and len(str(compat)) > 500:
        errors.append(f"compatibility exceeds 500 chars ({len(str(compat))})")

    # metadata: optional, must be a mapping if present
    meta = fm.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        errors.append(f"metadata must be a mapping, got {type(meta).__name__}")

    return errors


def main():
    print("Publishing skills from", SOURCE_DIR)
    print("Destination:", REPO_ROOT)
    print()

    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}")
        return

    manifest = ["# Publish Manifest", f"Source: {SOURCE_DIR}", f"Dest: {REPO_ROOT}", ""]
    has_errors = False

    for source_name, dest_name in SKILL_MAP.items():
        copy_skill(source_name, dest_name, manifest)

    # Fix name fields to match destination directories (safety net after scrub)
    manifest.append("\n--- Name field fixup ---")
    for dest_name in SKILL_MAP.values():
        dest_dir = REPO_ROOT / dest_name
        if dest_dir.exists() and fix_name_field(dest_dir):
            manifest.append(f"  FIXED: {dest_name}/SKILL.md name field -> '{dest_name}'")
    manifest.append("  Done")

    # Validate published skills against agentskills spec
    manifest.append("\n--- Agentskills spec validation ---")
    for dest_name in SKILL_MAP.values():
        dest_dir = REPO_ROOT / dest_name
        if not dest_dir.exists():
            continue
        errors = validate_published_skill(dest_dir)
        if errors:
            has_errors = True
            manifest.append(f"  FAIL: {dest_name}:")
            manifest.extend(f"    - {e}" for e in errors)
        else:
            manifest.append(f"  OK: {dest_name}")
    # Also validate repo-maintained skills
    for extra_skill in ["law-class-problems", "law-class-prep"]:
        extra_dir = REPO_ROOT / extra_skill
        if extra_dir.exists():
            errors = validate_published_skill(extra_dir)
            if errors:
                has_errors = True
                manifest.append(f"  FAIL: {extra_skill}:")
                manifest.extend(f"    - {e}" for e in errors)
            else:
                manifest.append(f"  OK: {extra_skill}")
    if not has_errors:
        manifest.append("  All skills pass agentskills spec validation")

    # Safety check: excluded skills
    problems = safety_check()
    if problems:
        has_errors = True
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
                    has_errors = True

    if not found_leaks:
        manifest.append("  OK: No private strings found in output")

    # Placeholder check
    placeholder_warnings = check_placeholders()
    if placeholder_warnings:
        manifest.append("\n--- Placeholder warnings ---")
        manifest.extend(f"  WARNING: {w}" for w in placeholder_warnings)

    print("\n".join(manifest))

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
