# Rex v2 Regression Fixtures

## critical-auth-diff.md

- **Blocker, verified:** Removing `isAdmin` authorization allows every authenticated user to reach an account-deletion endpoint.
- The finding must identify the changed condition and the guarded endpoint as evidence.

## docs-only-plan.md

- No migration, rollback, scaling, or database finding solely because those headings are absent.
- A link-check or publication-validation gap may be a finding only if the stated workflow makes it consequential.

## unverified-query-risk.md

- Do not state that the change creates an N+1 query.
- A `Needs verification` finding may identify the exact query, call volume, and benchmark or trace needed before assigning a severity.

## Clean review

- A clean review must end with `No material findings` and state the reviewed scope and coverage limits.
