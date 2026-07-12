#!/opt/homebrew/bin/python3
"""Publish skills from working installation to public repo.

Copies included skills, applies privacy scrub rules, renames directories and files.
Validates published output against the agentskills specification
(https://github.com/agentskills/agentskills).

Run from repo root: python3 scripts/publish.py
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

# --- Configuration ---

SOURCE_SKILLS_DIR = Path(os.path.expanduser("~/.claude/skills"))
SOURCE_AGENTS_DIR = Path(os.path.expanduser("~/.claude/agents"))
REPO_ROOT = Path(__file__).resolve().parent.parent

# OUTPUT_ROOT is where published content is written. In normal mode this equals
# REPO_ROOT. In --dry-run mode `main` reassigns it to a tmpdir so nothing in
# the real working tree is mutated.
OUTPUT_ROOT = REPO_ROOT
AGENTS_OUTPUT_DIR = OUTPUT_ROOT / "agents"

# Skills to include (source_name -> published_name)
SKILL_MAP = {
    "law-mcq-generator":     "law-mcq-generator",
    "law-essay-generator":   "law-essay-generator",
    "lecture-slide-reviewer": "lecture-slide-reviewer",
    "polk-memo":             "law-memo",
    "polk-document":         "law-document",
    "polk-email-style":      "law-email-style",
    "docx-comment-summary":  "docx-comment-summary",
    "rex":                   "rex",
    "eddie":                 "eddie",
}

# Agents to include (source_name -> published_name). Agents are shared
# infrastructure — skills reference them by name. Published to agents/<name>/.
AGENT_MAP = {
    "adversarial-balance-validator":  "adversarial-balance-validator",
    "adversarial-reverifier":         "adversarial-reverifier",
    "claim-merge-agent":              "claim-merge-agent",
    "construct-alignment-tracer":     "construct-alignment-tracer",
    "coverage-auditor":               "coverage-auditor",
    "disagreement-analyzer":          "disagreement-analyzer",
    "double-read-pass":               "double-read-pass",
    "eddie-consistency-checker":      "eddie-consistency-checker",
    "emphasis-map-builder":           "emphasis-map-builder",
    "fact-verifier":                  "fact-verifier",
    "factual-pipeline-orchestrator":  "factual-pipeline-orchestrator",
    "factual-reviewer":               "factual-reviewer",
    "institutional-claim-extractor":  "institutional-claim-extractor",
    "mcq-structural-reviewer":        "mcq-structural-reviewer",
    "slide-reading-alignment":        "slide-reading-alignment",
    "voice-style-checker":            "voice-style-checker",
}

# Skills that should NOT appear in output (safety check)
#   send-to-email, polk-slides, polk-zotero: private skills with personal
#     infrastructure (polk-zotero hardcodes Polk's Zotero userID and
#     personal collection keys)
#   class-prep, project-folder-setup: Polk-personalized (repo has generalized
#     law-class-prep; project-folder-setup has no public counterpart yet)
#   md-to-pdf: ships Polk's personal DD letterhead art (his name, title, and
#     signature mark). Private by design — it deploys to his own Anthropic
#     account (API + claude.ai) via deploy.py, but never to this public repo.
#     NOTE: an earlier version also bundled licensed ITC Stone Serif; that was
#     replaced with Caladea (open-licensed Cambria metric clone). The font is no
#     longer a reason for this exclusion — the letterhead art still is. Do not
#     remove md-to-pdf from EXCLUDED_SKILLS.
EXCLUDED_SKILLS = {"send-to-email", "polk-slides", "class-prep", "project-folder-setup",
                   "polk-zotero", "md-to-pdf"}

# law-class-problems and law-class-prep are maintained directly in the repo,
# not synced from source. They are not in SKILL_MAP so they won't be touched.

# Files to skip during copy (exact filename match)
SKIP_FILES = {".DS_Store", "design.md"}

# Directory names to skip anywhere in the source tree (plans, specs, and old
# archives are internal working artifacts, not part of a skill's published API)
SKIP_DIRS = {"plans", "specs", "_archive", "__pycache__"}

# Filename patterns to skip (regex, matched against basename).
#   - `.v1.md` etc. are versioned snapshots, not live agents.
#   - `.bak` / `.bak2` / `.backup` / `.orig` / trailing `~` are editor/backup
#     cruft. CRITICAL: these are never text-scrubbed (non-TEXT_EXTENSIONS) and,
#     before this rule, were copied verbatim AND skipped by post-scrub
#     verification — a silent private-data leak path. They are never API surface.
#   - `NOTES-*.md` are internal working notes (e.g. deferred-work logs), not
#     part of a skill's published interface.
SKIP_FILE_PATTERNS = [
    re.compile(r"\.v\d+\.md$"),
    re.compile(r"\.(bak\d*|backup|orig)$"),
    re.compile(r"~$"),
    re.compile(r"^NOTES-.*\.md$"),
]

# File extensions to apply scrub rules to
TEXT_EXTENSIONS = {".md", ".py", ".js", ".txt", ".json", ".yaml", ".yml", ".template"}

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
    (r"Professor Wagner", "[Your Name]"),

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
    # Sign-off forms: handle both single-newline and double-newline (formal) variants
    (r'"Best,\\n\\nPolk"', '"Best,\\n\\n[Your First Name]"'),
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


# docx property fields that can carry personal identifiers. Clearing to empty
# element form (<tag/>) is equivalent to "unknown author" in Word.
DOCX_PERSONAL_TAGS = [
    "dc:creator", "dc:contributor", "cp:lastModifiedBy",
    "Company", "Manager",
]

# docx timestamp fields. These aren't identifiers but they fingerprint when a
# file was created on Polk's machine. Normalize to a fixed sentinel so every
# published doc has the same timestamps regardless of when it was scrubbed.
DOCX_TIMESTAMP_TAGS = ["dcterms:created", "dcterms:modified"]
DOCX_SENTINEL_DATE = "2000-01-01T00:00:00Z"


def scrub_docx_metadata(xml_text: str) -> tuple[str, list[str]]:
    """Clear personal identifier fields and normalize timestamps in docx property XML."""
    subs = []
    for tag in DOCX_PERSONAL_TAGS:
        # Match <tag>value</tag> with any content (only scrub when non-empty)
        pattern = rf"<{re.escape(tag)}>[^<]+</{re.escape(tag)}>"
        empty_form = f"<{tag}/>"
        new_text, n = re.subn(pattern, empty_form, xml_text)
        if n > 0:
            subs.append(f"cleared {tag} ({n})")
            xml_text = new_text
    for tag in DOCX_TIMESTAMP_TAGS:
        # Timestamp tags may carry attributes, e.g. xsi:type="dcterms:W3CDTF"
        pattern = rf"(<{re.escape(tag)}[^>]*>)[^<]+(</{re.escape(tag)}>)"
        replacement = rf"\g<1>{DOCX_SENTINEL_DATE}\g<2>"
        new_text, n = re.subn(pattern, replacement, xml_text)
        if n > 0 and new_text != xml_text:
            subs.append(f"normalized {tag} ({n})")
            xml_text = new_text
    return xml_text, subs


# docx internal XML paths whose content is body text, headers, footers, comments,
# footnotes/endnotes, author attributes, and custom XML parts. Applying
# SCRUB_RULES to these catches personal identifiers in the document body —
# not just the property metadata.
DOCX_BODY_XML_PREFIXES = ("word/", "customXml/")


def scrub_docx(src: Path, dst: Path) -> list[str]:
    """Copy src.docx to dst.docx, scrubbing personal info from property metadata
    AND from body XML (word/*.xml, customXml/*.xml).
    """
    changes = []
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in ("docProps/core.xml", "docProps/app.xml"):
                text = data.decode("utf-8")
                new_text, subs = scrub_docx_metadata(text)
                if subs:
                    changes.append(f"{item.filename}: {', '.join(subs)}")
                data = new_text.encode("utf-8")
            elif (item.filename.endswith(".xml")
                  and any(item.filename.startswith(p) for p in DOCX_BODY_XML_PREFIXES)):
                text = data.decode("utf-8")
                new_text, rule_changes = scrub_text(text)
                if rule_changes:
                    changes.append(f"{item.filename}: scrubbed {len(rule_changes)} rule(s)")
                data = new_text.encode("utf-8")
            zout.writestr(item, data)
    return changes


def should_skip(src_file: Path, src_root: Path) -> bool:
    """Return True if this file should not be published."""
    if src_file.name in SKIP_FILES:
        return True
    if any(pat.search(src_file.name) for pat in SKIP_FILE_PATTERNS):
        return True
    # Any directory component (between src_root and the file) in SKIP_DIRS
    rel_parts = src_file.relative_to(src_root).parts[:-1]
    if any(part in SKIP_DIRS for part in rel_parts):
        return True
    return False


def copy_tree(src: Path, dst: Path, label: str, manifest: list[str], apply_rename: bool = True):
    """Copy a source directory to dst, applying scrub rules, renames, and skip rules.

    Used for both skills and agents. If apply_rename is False, file rename rules
    are not applied (useful for agents whose names shouldn't be transformed).
    """
    if not src.exists():
        manifest.append(f"WARNING: SKIP {label}: not found at {src}")
        return

    if dst.exists():
        shutil.rmtree(dst)

    manifest.append(f"\n--- {label} ---")

    for src_file in sorted(src.rglob("*")):
        if not src_file.is_file():
            continue
        if should_skip(src_file, src):
            manifest.append(f"  {src_file.relative_to(src)} (SKIPPED)")
            continue

        rel = src_file.relative_to(src)

        if apply_rename:
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
        elif src_file.suffix.lower() == ".docx":
            docx_changes = scrub_docx(src_file, dst_file)
            if docx_changes:
                manifest.append(f"  {rel} (docx scrubbed):")
                manifest.extend(f"    {c}" for c in docx_changes)
            else:
                manifest.append(f"  {rel} (docx copy, clean)")
        else:
            shutil.copy2(src_file, dst_file)
            manifest.append(f"  {rel} (binary copy)")


def copy_skill(source_name: str, dest_name: str, manifest: list[str]):
    """Copy a skill directory, applying scrub rules and file renames."""
    src = SOURCE_SKILLS_DIR / source_name
    dst = REPO_ROOT / dest_name
    copy_tree(src, dst, f"{source_name} -> {dest_name}", manifest, apply_rename=True)


def copy_agent(source_name: str, dest_name: str, manifest: list[str]):
    """Copy an agent directory, applying scrub rules. Agent filenames are not renamed."""
    src = SOURCE_AGENTS_DIR / source_name
    dst = AGENTS_OUTPUT_DIR / dest_name
    copy_tree(src, dst, f"agent: {source_name} -> agents/{dest_name}", manifest, apply_rename=False)


# --- Privacy verification ---

# Tokens that mark a string as a personal identifier. Used both to auto-derive
# the post-scrub verification set from SCRUB_RULES and to flag any scrub rule
# that mentions a token not yet covered.
PERSONAL_IDENTIFIER_TOKENS = ["Polk", "Wagner", "pwagner", "polkwagner", "polk@"]

# Infrastructure secrets that don't appear as SCRUB_RULES LHS (e.g. webhook id
# prefixes, signed URLs). Kept explicit because the derivation walks patterns.
EXTRA_PRIVATE_STRINGS = ["AKfycbw"]

# Optional private scrub rules loaded from OUTSIDE the repo. Third-party real
# names (colleagues, cited academics) that appear in source skills/fixtures must
# be sanitized in the published copy — but the mappings themselves are private,
# so they must NOT live in this file (publish.py is itself published). They load
# from a JSON file on the maintainer's machine; the public pipeline source shows
# only this loader. Schema: {"rules": [[pattern, repl], ...], "anchors": [str]}.
# Rules append AFTER the static SCRUB_RULES (so name→fictional runs before any
# rule that depends on the sanitized text). Anchors extend the post-scrub
# verification set. If the file is absent, main() emits a prominent warning and
# only the static (Polk-identity) scrub runs.
PRIVATE_SCRUB_PATH = Path.home() / ".claude" / "publish-private-scrub.json"
PRIVATE_SCRUB_LOADED = False
if PRIVATE_SCRUB_PATH.exists():
    _priv = json.loads(PRIVATE_SCRUB_PATH.read_text(encoding="utf-8"))
    SCRUB_RULES.extend((r[0], r[1]) for r in _priv.get("rules", []))
    EXTRA_PRIVATE_STRINGS.extend(_priv.get("anchors", []))
    PRIVATE_SCRUB_LOADED = True


def _literal_from_pattern(pat: str) -> str | None:
    """Best-effort extraction of a regex pattern's literal content.

    Returns None if the pattern has non-trivial regex metacharacters that
    would make the literal extraction unreliable. Used for auto-derivation;
    callers fall back to EXTRA_PRIVATE_STRINGS for complex patterns.
    """
    s = pat
    # Unescape the common escapes we use in SCRUB_RULES patterns
    s = s.replace(r"\.", ".").replace(r"\@", "@").replace(r"\b", "")
    # Any remaining regex metachars mean we can't safely extract a literal
    if re.search(r"[\\*+?()\[\]|{}^$]", s):
        return None
    return s


def derive_private_strings() -> list[str]:
    """Build the post-scrub verification set from SCRUB_RULES + extras.

    Any scrub pattern whose literal form contains a PERSONAL_IDENTIFIER_TOKENS
    entry is included. Patterns too complex to extract cleanly are skipped —
    they're expected to be covered by one of the simpler rules (e.g. the
    `\\bPolk\\b` catch-all covers substrings in the compound patterns).
    """
    strings = set(EXTRA_PRIVATE_STRINGS)
    for pattern, _ in SCRUB_RULES:
        literal = _literal_from_pattern(pattern)
        if literal is None:
            continue
        if any(tok in literal for tok in PERSONAL_IDENTIFIER_TOKENS):
            strings.add(literal)
    return sorted(strings)


def audit_scrub_coverage() -> list[str]:
    """Warn if any SCRUB_RULES pattern mentions a personal token that no
    verification string covers. Defense-in-depth against silent drift.
    """
    verification_set = derive_private_strings()
    warnings = []
    for pattern, _ in SCRUB_RULES:
        for token in PERSONAL_IDENTIFIER_TOKENS:
            if token not in pattern:
                continue
            if not any(token in vs for vs in verification_set):
                warnings.append(
                    f"SCRUB_RULES pattern '{pattern}' contains token '{token}' "
                    f"but no verification string covers it — post-scrub check will miss leaks"
                )
                break
    return warnings


def check_sync_drift() -> list[str]:
    """Flag published synced-skill files that differ from what the scrub
    would produce from their current source — i.e. in-repo hand edits that
    the next publish would silently overwrite.
    """
    findings = []
    for source_name, dest_name in SKILL_MAP.items():
        src = SOURCE_SKILLS_DIR / source_name
        dst = OUTPUT_ROOT / dest_name
        if not src.exists() or not dst.exists():
            continue
        for src_file in sorted(src.rglob("*")):
            if not src_file.is_file() or should_skip(src_file, src):
                continue
            if not is_text_file(src_file):
                continue
            rel = src_file.relative_to(src)
            new_name = rename_file(rel.name)
            if new_name != rel.name:
                rel = rel.with_name(new_name)
            dst_file = dst / rel
            if not dst_file.exists():
                continue
            expected, _ = scrub_text(src_file.read_text(encoding="utf-8"))
            actual = dst_file.read_text(encoding="utf-8")
            if expected != actual:
                findings.append(f"{dest_name}/{rel} — in-repo edit will be overwritten by next publish")
    return findings


def safety_check():
    """Verify no excluded skills would be committed to the output repo.

    Presence alone is not a failure — what matters is whether git would track
    the directory. If it's gitignored, it cannot leak on push. Only flag
    excluded skills that are NOT gitignored (i.e. actually reachable by git).
    """
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
    """Warn about unfilled placeholders in published skill / agent content.

    Scans every .md under published skill directories and the agents dir
    recursively — a forgotten OWNER/REPO_NAME in a nested SKILL.md would
    ship silently under a root-only check. Top-level repo docs (CLAUDE.md,
    README.md) are excluded: they legitimately reference the placeholder
    tokens when documenting the scrub pipeline itself.
    """
    problems = []
    scan_dirs = [OUTPUT_ROOT / n for n in SKILL_MAP.values()]
    scan_dirs += [AGENTS_OUTPUT_DIR]
    # Include repo-maintained skills (they're never under SKILL_MAP)
    for extra_skill in ["law-class-problems", "law-class-prep"]:
        extra = REPO_ROOT / extra_skill
        if extra.exists():
            scan_dirs.append(extra)
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for md_file in scan_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for placeholder in ["OWNER/REPO_NAME", "YOUR_WEBHOOK_URL"]:
                if placeholder in content:
                    rel = md_file.relative_to(OUTPUT_ROOT) if md_file.is_relative_to(OUTPUT_ROOT) else md_file.relative_to(REPO_ROOT)
                    problems.append(f"Unfilled placeholder '{placeholder}' in {rel}")
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


def validate_published_agent(dest_dir: Path) -> list[str]:
    """Validate a published agent's <name>.md against basic agent frontmatter rules.

    Agents use additional frontmatter fields (tools, model) beyond what the
    agentskills spec defines for skills, so validation here is intentionally
    looser: require name + description, require name matches directory.
    """
    agent_name = dest_dir.name
    agent_md = dest_dir / f"{agent_name}.md"
    if not agent_md.exists():
        return [f"{agent_name}.md not found"]

    text = agent_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not m:
        return ["No valid YAML frontmatter"]

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(fm, dict):
        return ["Frontmatter is not a YAML mapping"]

    errors = []
    name = fm.get("name")
    if not name:
        errors.append("Missing required field: name")
    elif name != agent_name:
        errors.append(f"name '{name}' does not match directory '{agent_name}'")
    if not fm.get("description"):
        errors.append("Missing required field: description")
    return errors


def run_preflight_tests() -> bool:
    """Run the test_publish.py suite as a pre-flight check.

    Returns True on success. These tests are cheap (~30ms) and are the last
    line of defense against scrub regressions. Any failure aborts publish.
    """
    import unittest
    test_path = Path(__file__).resolve().parent / "test_publish.py"
    if not test_path.exists():
        print("WARNING: test_publish.py not found — skipping pre-flight tests")
        return True
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_path.parent), pattern="test_publish.py")
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    global OUTPUT_ROOT, AGENTS_OUTPUT_DIR

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Write output to a temporary directory instead of the repo. "
             "Useful for previewing changes before committing.",
    )
    parser.add_argument(
        "--skip-tests", action="store_true",
        help="Skip the pre-flight test suite. Not recommended — tests guard "
             "against scrub-rule regressions.",
    )
    args = parser.parse_args()

    if not args.skip_tests:
        print("Running pre-flight tests...")
        if not run_preflight_tests():
            print("ERROR: Pre-flight tests failed. Fix them before publishing.")
            print("       Run `python3 scripts/test_publish.py` for details.")
            sys.exit(1)
        print("Pre-flight tests passed.")
        print()

    if args.dry_run:
        OUTPUT_ROOT = Path(tempfile.mkdtemp(prefix="publish-preview-"))
        AGENTS_OUTPUT_DIR = OUTPUT_ROOT / "agents"

    print("Publishing skills from", SOURCE_SKILLS_DIR)
    print("Publishing agents from", SOURCE_AGENTS_DIR)
    print("Destination:", OUTPUT_ROOT, "(DRY RUN)" if args.dry_run else "")
    if PRIVATE_SCRUB_LOADED:
        print(f"Private scrub rules: loaded from {PRIVATE_SCRUB_PATH}")
    else:
        print("*" * 70)
        print("WARNING: private scrub file not found:")
        print(f"  {PRIVATE_SCRUB_PATH}")
        print("  Third-party real names (colleagues, cited academics) will NOT be")
        print("  sanitized. Only the static Polk-identity scrub runs. Do not publish")
        print("  eddie or its agents without this file present.")
        print("*" * 70)
    print()

    if not SOURCE_SKILLS_DIR.exists():
        print(f"ERROR: Source skills directory not found: {SOURCE_SKILLS_DIR}")
        return
    if not SOURCE_AGENTS_DIR.exists():
        print(f"WARNING: Source agents directory not found: {SOURCE_AGENTS_DIR}")

    manifest = [
        "# Publish Manifest",
        f"Skills source: {SOURCE_SKILLS_DIR}",
        f"Agents source: {SOURCE_AGENTS_DIR}",
        f"Dest: {OUTPUT_ROOT}" + ("  [DRY RUN]" if args.dry_run else ""),
        "",
    ]
    has_errors = False

    # Sanity-check scrub coverage before doing anything else. If the scrub
    # rules mention a personal token the verification set can't catch, fail
    # fast — publishing with silent drift is worse than not publishing.
    coverage_warnings = audit_scrub_coverage()
    if coverage_warnings:
        manifest.append("--- Scrub coverage warnings ---")
        manifest.extend(f"  WARNING: {w}" for w in coverage_warnings)
        manifest.append("")

    # Detect in-repo edits to synced skills BEFORE overwriting them. We look
    # at the currently-published state, not what we're about to write — this
    # only runs in non-dry-run mode where OUTPUT_ROOT == REPO_ROOT.
    if not args.dry_run:
        drift = check_sync_drift()
        if drift:
            manifest.append("--- Sync-drift warnings ---")
            manifest.append(
                "  The following published files differ from what scrubbing "
                "their current source would produce. If these are hand edits, "
                "they will be overwritten. Edit at source instead."
            )
            manifest.extend(f"    - {d}" for d in drift)
            manifest.append("")

    for source_name, dest_name in SKILL_MAP.items():
        copy_skill(source_name, dest_name, manifest)

    if SOURCE_AGENTS_DIR.exists():
        for source_name, dest_name in AGENT_MAP.items():
            copy_agent(source_name, dest_name, manifest)

    # Fix name fields to match destination directories (safety net after scrub)
    manifest.append("\n--- Name field fixup ---")
    for dest_name in SKILL_MAP.values():
        dest_dir = OUTPUT_ROOT / dest_name
        if dest_dir.exists() and fix_name_field(dest_dir):
            manifest.append(f"  FIXED: {dest_name}/SKILL.md name field -> '{dest_name}'")
    manifest.append("  Done")

    # Validate published skills against agentskills spec
    manifest.append("\n--- Agentskills spec validation ---")
    for dest_name in SKILL_MAP.values():
        dest_dir = OUTPUT_ROOT / dest_name
        if not dest_dir.exists():
            continue
        errors = validate_published_skill(dest_dir)
        if errors:
            has_errors = True
            manifest.append(f"  FAIL: {dest_name}:")
            manifest.extend(f"    - {e}" for e in errors)
        else:
            manifest.append(f"  OK: {dest_name}")
    # Repo-maintained skills live in REPO_ROOT permanently; they aren't
    # written by the publish step but still need spec validation.
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

    # Validate published agents (looser rules than skills)
    manifest.append("\n--- Agent validation ---")
    for dest_name in AGENT_MAP.values():
        dest_dir = AGENTS_OUTPUT_DIR / dest_name
        if not dest_dir.exists():
            continue
        errors = validate_published_agent(dest_dir)
        if errors:
            has_errors = True
            manifest.append(f"  FAIL: agents/{dest_name}:")
            manifest.extend(f"    - {e}" for e in errors)
        else:
            manifest.append(f"  OK: agents/{dest_name}")

    # Safety check: excluded skills (always checks real REPO_ROOT's git state)
    problems = safety_check()
    if problems:
        has_errors = True
        manifest.append("\nSAFETY CHECK FAILURES:")
        manifest.extend(f"  - {p}" for p in problems)

    # Post-scrub verification (skills + agents, text files + docx metadata)
    # The verification set is derived from SCRUB_RULES so it can't drift.
    private_strings = derive_private_strings()
    manifest.append("\n--- Post-scrub verification ---")
    manifest.append(f"  (checking {len(private_strings)} private strings, auto-derived from SCRUB_RULES)")
    found_leaks = False
    scan_targets = [OUTPUT_ROOT / n for n in SKILL_MAP.values()]
    scan_targets += [AGENTS_OUTPUT_DIR / n for n in AGENT_MAP.values()]
    for dest_dir in scan_targets:
        if not dest_dir.exists():
            continue
        for f in dest_dir.rglob("*"):
            if not f.is_file():
                continue
            if is_text_file(f):
                content = f.read_text(encoding="utf-8")
                for s in private_strings:
                    if s in content:
                        manifest.append(f"  LEAK: '{s}' found in {f.relative_to(OUTPUT_ROOT)}")
                        found_leaks = True
                        has_errors = True
            elif f.suffix.lower() == ".docx":
                # Scan docx property XML for personal strings
                try:
                    with zipfile.ZipFile(f, "r") as zf:
                        for member in ("docProps/core.xml", "docProps/app.xml"):
                            if member in zf.namelist():
                                xml_text = zf.read(member).decode("utf-8")
                                for s in private_strings:
                                    if s in xml_text:
                                        manifest.append(
                                            f"  LEAK: '{s}' in {f.relative_to(OUTPUT_ROOT)} ({member})"
                                        )
                                        found_leaks = True
                                        has_errors = True
                except zipfile.BadZipFile:
                    pass
            else:
                # Defense-in-depth: any file that is neither text nor docx is
                # copied verbatim (never scrubbed) AND was previously never
                # verified — a silent leak path (see the .bak incident). Scan
                # its raw bytes for each private string. SKIP_FILE_PATTERNS
                # should already exclude backup cruft; this catches anything
                # that slips through with an unexpected extension.
                try:
                    raw = f.read_bytes()
                    for s in private_strings:
                        if s.encode("utf-8") in raw:
                            manifest.append(
                                f"  LEAK: '{s}' in {f.relative_to(OUTPUT_ROOT)} (non-text file)"
                            )
                            found_leaks = True
                            has_errors = True
                except OSError:
                    pass

    if not found_leaks:
        manifest.append("  OK: No private strings found in output")

    # Placeholder check (scans all published .md files recursively)
    placeholder_warnings = check_placeholders()
    if placeholder_warnings:
        manifest.append("\n--- Placeholder warnings ---")
        manifest.extend(f"  WARNING: {w}" for w in placeholder_warnings)

    print("\n".join(manifest))

    if args.dry_run:
        print()
        print(f"DRY RUN complete. Output at: {OUTPUT_ROOT}")
        print(f"To diff against the real repo:")
        print(f"  diff -ruN {REPO_ROOT} {OUTPUT_ROOT} | less")

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
