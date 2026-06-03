# Eddie v2 Regression Fixtures — Expected Catches

Manual validation reference. After running `/eddie` against each fixture (with `skills/eddie/tests/NAMES.md` auto-discovered by the orchestrator's tree walk, and `skills/eddie/tests/lessons.md` passed via the `lessons=` invocation arg — full command: `/eddie skills/eddie/tests/fixtures/<fixture>.md be aggressive lessons=skills/eddie/tests/lessons.md`), the report should contain at least the catches listed below. Exact wording will vary; check for category and priority.

## personnel-drift.md

- **P1 — Personnel** — "Mark Calloway" should be flagged as first-name drift (registry has "Maya Calloway"). Stage 1c registry catch, no web verification.
- **P1 — Personnel** — "Kathy Lambert" should be flagged as known fabrication (registry's known-fabrications table maps to "Diane Holloway"). Stage 1c registry catch.
- **P1 or P2 — Personnel** — "Quentin Reynolds-Maxwell" should be flagged as unknown (not in registry). May resolve to unverifiable on web search; in which case P2 with note "Unknown person; consider adding to NAMES.md after verification."

## affiliations.md

- **P2 — extraction** — "Marco Delgado-Ruiz, Wharton School economist" should be extracted as a name+affiliation claim and routed to web verification; with a fictional name (public fixtures are sanitized) this resolves `unverifiable` → P2, not the real-name `contradicted`/P1 path.
- **P2 — extraction** — "Karen Whitfield Ellison, Yale Law School professor" should be extracted as a name+affiliation claim and routed to web verification; with a fictional name (public fixtures are sanitized) this resolves `unverifiable` → P2, not the real-name `contradicted`/P1 path.
- **P2 — extraction** — "Aaron Goldstein, Chicago Law professor" should be extracted as a name+affiliation claim and routed to web verification; with a fictional name (public fixtures are sanitized) this resolves `unverifiable` → P2, not the real-name `contradicted`/P1 path.

## quotes-and-citations.md

- **(may verify)** — Quote attributed to Justice Roberts ("Chevron is overruled") should be extracted by quote-extractor and verified against the public Supreme Court URL. The URL should resolve and the verification should confirm.
- **P1 (placeholder detected)** — The Westlaw URL is well-formed structurally but contains the placeholder strings "FAKE" and "EXAMPLE" in its path. The Wave 3 calibration to fact-verifier (placeholder-detection rule) flags this as `contradicted` P1 — a fabricated citation signal.
- **P1 (placeholder detected)** — The SSRN URL is well-formed structurally but the abstract_id `99999999` is all-9s, matching the placeholder-detection rule. Fact-verifier flags this `contradicted` P1.
- (Note: a paywalled URL with a plausible-looking ID — no FAKE/EXAMPLE/all-9s tokens — would correctly pass with no flag. The two fixture URLs intentionally exercise the placeholder-detection calibration; a legitimate paywalled citation would not trip it.)
- **P1 — AI patterns** — The example.com URL should fail to resolve (DNS or 404) → P1 broken citation.
- **P2 — AI patterns** — The unattributed environmental-regulation quote ("No source cited for this quotation") should be flagged by quote-extractor as a sourceless quotation → P2 citation-laundering risk.

## meta-error.md

**Test intent:** validate that fix-verifier (Wave 3) catches a wrong fix value. The fixture is designed so Eddie's natural Stage 1c registry catch ("Mark Calloway" → first-name drift) produces a suggested fix of "Maya Calloway." Fix-verifier should then cross-check that suggestion against the test NAMES.md and confirm it.

- **P1 — Personnel** — "Mark Calloway" should be flagged as first-name drift. Eddie's suggested fix should propose "Maya Calloway."
- **(fix-verifier)** — fix-verifier should cross-check "Maya Calloway" against `skills/eddie/tests/NAMES.md` → `Confidence: high`, citation = test NAMES.md path. The fix-verifier output should NOT downgrade the suggestion (the registry confirms it).
- The fixture's other claims (joined in 2010, Morgan Lewis 2002-2010, Yale 1995, Stanford 1998, Lindback Award 2024) are fictional. They will likely return `unverifiable` from web search — acceptable. Not the focus of this fixture; second-eyes priority calibration may demote them to P2 with "verify before applying."

**Failure signal:** if fix-verifier downgrades the "Maya Calloway" suggestion to `Confidence: low`, the agent isn't finding the test registry (likely the registry path isn't being passed through correctly — check Task 9 step 1's lessons-pass equivalent for NAMES.md).

## clean.md

- **No P1 or P2 findings** — the document is clean.
- The word "ensure" appears in two places. The first ("the committee believes the package will ensure consistency") is in a non-quoted context. The second is inside a quoted policy ("the Committee shall ensure that...").
- voice-style-checker should flag the first "ensure" as banned phrase (P3).
- voice-style-checker should also initially flag the second "ensure" as banned phrase (P3).
- **eddie-second-eyes should clear the second "ensure"** via the test lessons.md calibration ("'ensure' is acceptable when used in a quoted policy"). The cleared item should appear in the "Considered but cleared" section with the lesson cited as the reason.
- "Maya Calloway" and "Diane Holloway" appear and match the registry — should pass Stage 1c without flag.

## Validation protocol

Run for each fixture:

```
/eddie skills/eddie/tests/fixtures/<fixture>.md be aggressive lessons=skills/eddie/tests/lessons.md
```

Compare the produced report against the expected catches above. Document any divergence. If a fixture produces fewer catches than expected, the spec is wrong somewhere — fix the design before shipping.

If a fixture produces MORE catches than expected (false positives), that's also worth investigating — second-eyes should have removed them, or the fixture should be tightened.
