# Code Review Lenses

Rex evaluates code against 8 lenses:

## 1. Security
- Authentication and authorization gaps
- Input validation and sanitization
- Credential handling and exposure
- Injection vectors (SQL, command, XSS, etc.)
- Dependency risks, including maintenance, licensing, supply-chain expansion, and vulnerable transitive packages
- Sensitive-data handling: collection, retention, logging, redaction, and access boundaries

## 2. Correctness
- Does the code do what it claims? Logic errors, off-by-one errors, race conditions, incorrect algorithm choices, API misuse.
- Think like a user: what inputs will they provide? What states will the system be in?
- Concurrency: are shared resources protected? Can operations interleave in ways the author didn't consider?
- "Does this actually work?" is the question. Not "is it elegant" — does it produce the right output for every input?

## 3. Design Fitness
- Is this the right approach? Does this change belong here, or should it live somewhere else in the system?
- Could a simpler approach work? Is this solving the actual problem or a more general one nobody asked for?
- Does the approach fit the surrounding codebase, or does it introduce a foreign pattern?
- This is Google's #1 code review dimension: design comes before everything else.

## 4. Failure Modes
- What happens when external services are down?
- What happens with malformed input?
- What happens under load?
- What happens when disk is full, memory is exhausted, network drops?
- Are errors handled or swallowed?

## 5. Code Structure
- Single responsibility — does each function/module do one thing?
- Are abstractions at the right level?
- Is the control flow readable?
- Are there hidden dependencies or implicit ordering requirements?
- **Over-engineering** — Premature abstractions, unnecessary indirection, configurability nobody asked for, solving problems that don't exist yet. Three similar lines of code is better than a premature abstraction. If the flexibility isn't needed today, it's waste.

## 6. Test Quality
- Are tests testing behavior or implementation details? Tests coupled to internals break on every refactor.
- Will these tests actually fail when the code breaks? A test that always passes is worse than no test — it's false confidence.
- Are they brittle? Do they depend on ordering, timing, or environment details they shouldn't?
- Do they cover the edge cases that matter — the ones from the Correctness lens?
- Is new behavior covered? If the PR adds functionality without tests, that's a finding.

## 7. Extensibility and Maintainability
- Can this be modified without rewriting?
- Will the next developer understand why this code exists?
- Are there hardcoded values that should be configurable?
- Is there unnecessary coupling between components?

## 8. Operational Concerns
- Logging: can you diagnose a production issue from the logs?
- Monitoring: will you know when this breaks?
- Deployment: can this be rolled back?
- Data: are migrations reversible?
- Ownership: who receives and acts on an alert or failed job?
