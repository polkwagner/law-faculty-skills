#!/usr/bin/env python3
"""Privacy-critical tests for publish.py.

These tests run before every publish in the normal workflow — they are the
last line of defense before private identifiers hit a public repo. They must
stay fast: no network, no real filesystem writes outside tempdirs.

Run as: python3 scripts/test_publish.py
Exit code is nonzero on any failure.

Notes on the brief:
- The brief asked for scrub coverage of "Best,\\nPolk" and "Best,\\n\\nPolk"
  (actual-newline sign-offs). The current SCRUB_RULES target the
  backslash-escaped literal form (as it appears inside documented examples
  within SKILL.md files). For real-newline sign-offs, the \\bPolk\\b catch-all
  replaces "Polk" with "[Your Name]" — not "[Your First Name]". The tests
  below verify both the documented-literal form (round-trips to
  [Your First Name]) and the real-newline form (falls through to the
  catch-all producing [Your Name]); either way, no "Polk" survives.
"""

import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish


# Minimal valid docx core.xml template with a dc:creator set to Polk Wagner.
# docx writers commonly omit most fields; core.xml + [Content_Types].xml + a
# minimal relationships file is enough for zipfile-level round-tripping.
CORE_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>R. Polk Wagner</dc:creator>
<cp:lastModifiedBy>Polk</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-04-06T00:23:18Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2026-04-06T00:23:18Z</dcterms:modified>
</cp:coreProperties>
"""

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>
"""


def build_minimal_docx(path: Path, core_xml: str = CORE_XML_TEMPLATE):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", RELS_XML)
        zf.writestr("docProps/core.xml", core_xml)


class ScrubTextTests(unittest.TestCase):
    """Fixture-based tests for scrub_text covering every leak class that has
    ever been shipped or nearly shipped.
    """

    FIXTURE = """---
name: polk-document
description: Polk Wagner's document style
---

# About

This skill produces documents for Polk Wagner, Deputy Dean for Academic Affairs and Innovation.
Contact: pwagner@law.upenn.edu.

Spawn the `foo-bar` agent to validate the output.

Sign off with:

"Best,
Polk"

And also the double-newline form:

"Best,

Polk"

Cross-reference: see the polk-document skill for shared formatting.
"""

    def test_name_is_replaced(self):
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertIn("[Your Name]", out)
        self.assertNotIn("Polk Wagner", out)

    def test_email_is_replaced(self):
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertIn("your-email@law.upenn.edu", out)
        self.assertNotIn("pwagner@law.upenn.edu", out)

    def test_title_is_replaced(self):
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertIn("[Your Title]", out)
        self.assertNotIn("Deputy Dean for Academic Affairs and Innovation", out)

    def test_real_newline_signoff(self):
        # Real-newline sign-offs are caught by the \bPolk\b catch-all, which
        # produces [Your Name] (not [Your First Name]). The critical property
        # is that "Polk" does not survive in any form.
        out, _ = publish.scrub_text('"Best,\nPolk"')
        self.assertNotIn("Polk", out)
        self.assertIn("Best,\n", out)

        out2, _ = publish.scrub_text('"Best,\n\nPolk"')
        self.assertNotIn("Polk", out2)
        self.assertIn("Best,\n\n", out2)

    def test_escaped_literal_signoff(self):
        # The documented-literal form (as it appears inside SKILL.md example
        # blocks) is handled by the specific "[Your First Name]" rule. Note
        # that the replacement in SCRUB_RULES uses non-raw strings, so the
        # \n in the output is an actual newline, not two characters. That's
        # an oddity of publish.py but still satisfies the privacy invariant.
        out, _ = publish.scrub_text(r'"Best,\nPolk"')
        self.assertNotIn("Polk", out)
        self.assertIn("[Your First Name]", out)

        out2, _ = publish.scrub_text(r'"Best,\n\nPolk"')
        self.assertNotIn("Polk", out2)
        self.assertIn("[Your First Name]", out2)

    def test_spawn_agent_made_conditional(self):
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertIn("If the `foo-bar` agent is available, spawn it", out)
        self.assertNotIn("Spawn the `foo-bar` agent", out)

    def test_polk_dir_reference_renamed(self):
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertIn("law-document", out)
        self.assertNotIn("polk-document", out)

    def test_no_polk_remains_anywhere(self):
        # Grep-sanity: the literal string "Polk" must not appear in the
        # scrubbed output at all. The fixture covers every known leak class,
        # so if this assertion ever fails a new leak class has been
        # introduced and needs its own scrub rule.
        out, _ = publish.scrub_text(self.FIXTURE)
        self.assertNotIn("Polk", out)
        self.assertNotIn("polk", out)


class ScrubDocxMetadataTests(unittest.TestCase):
    def test_creator_cleared(self):
        xml = "<root><dc:creator>R. Polk Wagner</dc:creator></root>"
        out, subs = publish.scrub_docx_metadata(xml)
        self.assertIn("<dc:creator/>", out)
        self.assertNotIn("Polk", out)
        self.assertTrue(any("dc:creator" in s for s in subs))

    def test_last_modified_by_cleared(self):
        xml = "<root><cp:lastModifiedBy>Polk</cp:lastModifiedBy></root>"
        out, _ = publish.scrub_docx_metadata(xml)
        self.assertIn("<cp:lastModifiedBy/>", out)
        self.assertNotIn("Polk", out)

    def test_created_timestamp_normalized(self):
        xml = (
            '<root><dcterms:created xsi:type="dcterms:W3CDTF">'
            '2026-04-06T00:23:18Z</dcterms:created></root>'
        )
        out, _ = publish.scrub_docx_metadata(xml)
        self.assertIn(
            '<dcterms:created xsi:type="dcterms:W3CDTF">'
            '2000-01-01T00:00:00Z</dcterms:created>',
            out,
        )
        self.assertNotIn("2026-04-06", out)

    def test_modified_timestamp_normalized(self):
        xml = (
            '<root><dcterms:modified xsi:type="dcterms:W3CDTF">'
            '2026-04-06T00:23:18Z</dcterms:modified></root>'
        )
        out, _ = publish.scrub_docx_metadata(xml)
        self.assertIn(
            '<dcterms:modified xsi:type="dcterms:W3CDTF">'
            '2000-01-01T00:00:00Z</dcterms:modified>',
            out,
        )

    def test_empty_creator_untouched(self):
        # Existing empty-form elements should pass through without being
        # flagged as a sub (no non-empty body to match).
        xml = "<root><dc:creator/></root>"
        out, subs = publish.scrub_docx_metadata(xml)
        self.assertEqual(out, xml)
        self.assertEqual(subs, [])


class ScrubDocxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "src.docx"
        self.dst = Path(self.tmp.name) / "dst.docx"
        build_minimal_docx(self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def test_end_to_end_scrub_removes_creator(self):
        publish.scrub_docx(self.src, self.dst)
        with zipfile.ZipFile(self.dst, "r") as zf:
            core = zf.read("docProps/core.xml").decode("utf-8")
        self.assertNotIn("Polk", core)
        self.assertNotIn("Wagner", core)
        self.assertIn("<dc:creator/>", core)
        self.assertIn("2000-01-01T00:00:00Z", core)

    def test_real_fixture_docx_scrubs_clean(self):
        # Fallback/integration: run the scrubber against a real repo fixture
        # and verify no private string survives in the output's core.xml.
        fixture = publish.REPO_ROOT / "law-memo" / "law-memo_sample.docx"
        if not fixture.exists():
            self.skipTest(f"fixture {fixture} missing")
        dst = Path(self.tmp.name) / "fixture-out.docx"
        publish.scrub_docx(fixture, dst)
        private = publish.derive_private_strings()
        with zipfile.ZipFile(dst, "r") as zf:
            for member in ("docProps/core.xml", "docProps/app.xml"):
                if member not in zf.namelist():
                    continue
                xml = zf.read(member).decode("utf-8")
                for s in private:
                    self.assertNotIn(s, xml, f"{s!r} leaked in {member}")


class DerivePrivateStringsTests(unittest.TestCase):
    def test_returns_list(self):
        result = publish.derive_private_strings()
        self.assertIsInstance(result, list)

    def test_includes_full_name(self):
        self.assertIn("Polk Wagner", publish.derive_private_strings())

    def test_includes_email(self):
        self.assertIn("pwagner@law.upenn.edu", publish.derive_private_strings())

    def test_includes_extra_private_strings(self):
        self.assertIn("AKfycbw", publish.derive_private_strings())

    def test_excludes_complex_regex_patterns(self):
        # The compound table-row pattern contains regex metachars that
        # _literal_from_pattern refuses to extract. It must not appear
        # literally in the verification set — otherwise the post-scrub scan
        # would look for a regex as a substring and find nothing.
        result = publish.derive_private_strings()
        for s in result:
            self.assertNotIn("\\s+", s)
            self.assertNotIn("\\*", s)
            self.assertFalse(s.startswith("|"))


class AuditScrubCoverageTests(unittest.TestCase):
    def test_current_rules_have_full_coverage(self):
        self.assertEqual(publish.audit_scrub_coverage(), [])

    def test_detects_drift_from_uncovered_token(self):
        # Simulate a maintainer adding a rule that mentions a new personal
        # token without updating the verification set. The audit should
        # catch it and return a non-empty warning list.
        original = list(publish.SCRUB_RULES)
        original_tokens = list(publish.PERSONAL_IDENTIFIER_TOKENS)
        original_extras = list(publish.EXTRA_PRIVATE_STRINGS)
        try:
            publish.PERSONAL_IDENTIFIER_TOKENS.append("NewSecret")
            publish.SCRUB_RULES.append((r"NewSecret\s+pattern", "REDACTED"))
            warnings = publish.audit_scrub_coverage()
            self.assertTrue(warnings, "expected a warning for uncovered token")
            self.assertTrue(any("NewSecret" in w for w in warnings))
        finally:
            publish.SCRUB_RULES[:] = original
            publish.PERSONAL_IDENTIFIER_TOKENS[:] = original_tokens
            publish.EXTRA_PRIVATE_STRINGS[:] = original_extras
        # Sanity: restoration worked.
        self.assertEqual(publish.audit_scrub_coverage(), [])


class ShouldSkipTests(unittest.TestCase):
    def _check(self, rel_path: str, expected: bool):
        root = Path("/fake/root")
        src_file = root / rel_path
        self.assertEqual(
            publish.should_skip(src_file, root),
            expected,
            f"should_skip({rel_path!r}) expected {expected}",
        )

    def test_plans_dir_skipped(self):
        self._check("foo/plans/x.md", True)

    def test_specs_dir_skipped(self):
        self._check("foo/specs/x.md", True)

    def test_archive_dir_skipped(self):
        self._check("foo/_archive/x.md", True)

    def test_v1_suffix_skipped(self):
        self._check("bar.v1.md", True)

    def test_v2_suffix_skipped(self):
        self._check("bar.v2.md", True)

    def test_ds_store_skipped(self):
        self._check(".DS_Store", True)

    def test_design_md_skipped(self):
        self._check("design.md", True)

    def test_skill_md_not_skipped(self):
        self._check("foo/SKILL.md", False)

    def test_asset_not_skipped(self):
        self._check("foo/assets/logo.png", False)

    def test_eddie_peer_helpers_skipped(self):
        for name in ("peer_review", "peer_command", "peer_decode", "peer_state"):
            self._check(f"scripts/{name}.py", True)
        self._check("references/peer-review-brief.md", True)

    def test_other_scripts_not_skipped(self):
        self._check("scripts/gen_docx.py", False)


class EddieCrossModelStripTests(unittest.TestCase):
    """The cross-vendor section is private-only: strip it and both markers."""

    SOURCE = (
        "Report contents.\n"
        "\n"
        "<!-- EDDIE_CROSS_MODEL_START -->\n"
        "## Cross-model routing\n"
        "\n"
        "Run scripts/peer_review.py probe.\n"
        "<!-- EDDIE_CROSS_MODEL_END -->\n"
        "\n"
        "## What Eddie Does Not Do\n"
        "\n"
        "Nothing.\n"
    )

    def test_section_and_markers_removed(self):
        out, _ = publish.transform(self.SOURCE, is_markdown=True)
        self.assertNotIn("Cross-model routing", out)
        self.assertNotIn("peer_review", out)
        self.assertNotIn("EDDIE_CROSS_MODEL", out)
        self.assertIn("Report contents.\n\n## What Eddie Does Not Do\n", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
