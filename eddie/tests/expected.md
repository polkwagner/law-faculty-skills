# Eddie v2 Regression Fixtures — Expected Catches

> **This file lives in `tests/`, not `tests/fixtures/`, deliberately.** It is the answer key, and
> it used to sit in the same directory as the inputs. On 2026-07-27 `eddie-consistency-checker`
> found it, read it, and cited it in its own findings — "confirms these three are the fixture's
> intended catches" — which made that agent's calls on all three names worthless as independent
> evidence. The other agents were told not to read it and did not, so that run's headline results
> survived, but the only defense was a line in the dispatching prompt. Keeping the key out of the
> input directory is the structural fix. **Do not move it back, and do not put fixture inputs in
> `tests/` alongside it.**

> **The test registry is deliberately incomplete.** Two runs have proposed adding people to
> `tests/NAMES.md` — a curricular director (2026-07-27) and a fabrication row for the invented
> name in `personnel-drift.md` (2026-07-28). Both were declined, for the same reason each time:
> the *absence* is what the fixture tests. The missing curricular director is what forces
> fix-verification to drop an unsupported attribution rather than resolve it to a plausible
> name — the exact behavior worth testing. Registering the fabricated name would turn a catch
> that currently costs a 400-record directory enumeration into a free registry lookup, retiring
> the enumeration path from the suite entirely. A registry containing every answer tests only the
> registry. Before adding anyone here, ask which behavior their absence is currently forcing.

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

## institutional-sensitivity.md

**Test intent:** validate the Agent 2 / second-eyes split. Agent 2 surfaces findings without self-filtering; `eddie-second-eyes` applies the standing clearance rules. This fixture plants one finding that must survive and two that must be cleared. It is deliberately over 500 words so Eddie dispatches agents rather than taking the single-pass path.

**Must be caught (gating):**

- **P1 or P2 — institutional sensitivity** — "Between us, the Dean has already signaled he wants Rosalind Achebe-Farrar, so a third slot would be decorative" is a concrete exposure risk: it pre-decides an outcome, reveals a private steer, and would be damaging if forwarded or FOIAed. This must appear in the final report. If it does not, Agent 2 or second-eyes has over-corrected and the change is broken.
- **P2 or P3 — role/authority boundary** — "I've decided the committee will forward two names" asserts a decision that is the committee's to make. Expect a flag on the verb.
- **P3 — orphaned reference** — "As the clinical-appointments discussion above makes clear, this factor carries the least weight" refers to a clinical-appointments discussion that never occurs anywhere in the memo.

**Must be cleared, not suppressed upstream (gating):**

These two exist to prove the pipeline surfaces marginal findings and clears them *visibly*. Passing means either (a) they appear under "Considered but cleared" with the standing rule cited, or (b) they never appear at all. Failing means they appear as live findings in the final report.

- **Absence-as-implication** — all four workshop speakers are external. A speculative reviewer flags this as an unintended signal about internal faculty. The standing rule in `eddie-second-eyes` Sub-pass 1 says external speakers at internal workshops are routine; this clears.
- **Hypothetical inference** — "The subcommittee met twice in October" invites "a reader could infer the screen was rushed." No specific signal in the text supports that. The standing rule says hypothetical reader inferences with no grounding are speculation; this clears.

**Advisory (do not gate):**

- Structural discipline should fire somewhere on the Background section — four nested historical antecedents to explain an unchanged charge. Priority and phrasing will vary.
- "ensure" does not appear; voice/style findings here are incidental.
- The candidate ("Rosalind Achebe-Farrar") and the four workshop speakers are not in the test registry and may each draw an unknown-person flag at P2. That is expected noise orthogonal to this fixture's purpose, not a failure. The memo's author and contact ARE registered, so they should pass Stage 1c without flags.
- **Unplanted-but-real defects, confirmed 2026-07-27.** A second-eyes blind-spot scan found four genuine defects in this fixture's prose that were not deliberately planted. They are correct catches and should NOT be read as regressions. Recorded so future runs can distinguish them from new failures:
  - Logistics mandates distribution "through the committee's shared folder" and then instructs "do not remove files from the building" — the two controls are mutually unenforceable.
  - The subcommittee "met twice in October" but files do not circulate until March 20, an unexplained five-month gap.
  - "through the committee's shared folder rather than by email, as we did last cycle" — the trailing clause attaches to either side of "rather than", yielding opposite meanings.
  - Bertrand Oyelaran appears bare on first mention (Logistics) and with his title on second (closing), inverting the identify-then-shorten convention.
- **Quantum caution.** An adversarial pass described the Background section as "roughly a third" of the memo; it is closer to a quarter (~160 of ~640 words). Either characterization may appear; neither is a failure.
- **Standing-rule coverage is partial.** The absence-as-implication bait (all four workshop speakers external) did not provoke the intended reading in validation — the section was flagged for scope and for unrecorded informal candidate contact instead. That standing rule therefore remains untested by this fixture. Standing rule 3 (low-confidence marginal findings clear by default) IS exercised, via the P4/P5 findings the adversarial pass now ships rather than suppresses.

**Diagnostic value:** if both "must be cleared" items appear as live findings, second-eyes is not applying the standing rules — check that Task 10 Step 3's renumbering (step 5 → 6) did not disturb Sub-pass 1. If the "must be caught" exposure risk is missing, Agent 2 is still self-filtering — check that Task 10 Step 1 applied.

## clean.md

- **No P1 or P2 findings** — the document is clean.
- The word "ensure" appears in two places. The first ("the committee believes the package will ensure consistency") is in a non-quoted context. The second is inside a quoted policy ("the Committee shall ensure that...").
- voice-style-checker should flag the first "ensure" as banned phrase (P3).
- voice-style-checker should also initially flag the second "ensure" as banned phrase (P3).
- **eddie-second-eyes should clear the second "ensure"** via the test lessons.md calibration ("'ensure' is acceptable when used in a quoted policy"). The cleared item should appear in the "Considered but cleared" section with the lesson cited as the reason.
- "Maya Calloway" and "Diane Holloway" appear and match the registry — should pass Stage 1c without flag.

## static-site.md

- **P1 — static website** — The public link to `docs/accommodations.xlsx` exposes confidential accommodation information and must be removed or moved behind approved access control.
- **P2 — static website** — The text calls a Fall 2025 guide definitive for Fall 2026 courses; flag the stale semester claim.
- **P2 — static website** — The `example.invalid` external destination is not a usable resource link.
- **P3 — static website** — "Read more" is non-descriptive link text. The internal hash link itself should be checked, but not called broken solely because the fixture cannot prove the target page's markup.

## completed-plan.md

- A completed historical plan must be excluded from automatic plan reconciliation unless the user explicitly supplies it with `plan=`.
- The review report should disclose that the artifact was ignored only when its exclusion changes plan-reconciliation confidence.

## Validation protocol

Run for each fixture:

```
/eddie skills/eddie/tests/fixtures/<fixture>.md be aggressive lessons=skills/eddie/tests/lessons.md
```

Compare the produced report against the expected catches above. Document any divergence. If a fixture produces fewer catches than expected, the spec is wrong somewhere — fix the design before shipping.

If a fixture produces MORE catches than expected (false positives), that's also worth investigating — second-eyes should have removed them, or the fixture should be tightened.
