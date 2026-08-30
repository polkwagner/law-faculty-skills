# Course themes and prior-exam checking

Extracted from `law-essay-generator/SKILL.md` to keep the skill body small; this file loads only when read.

## Course Themes

Course themes are recurring ideas, philosophies, or cross-cutting questions
that run through the course and connect individual doctrines into a larger
intellectual framework. They are not doctrines themselves — they are the
*reasons* doctrines exist and the *tensions* that make them interesting.

### How to Identify Themes

While reading the course materials (especially the syllabus framing, slide
introductions, transcript discussions, and cross-doctrinal class problems),
look for:

- **Recurring questions** that appear across multiple doctrinal areas (e.g.,
  "how do we balance incentives for creators against public access?")
- **Cross-regime comparisons** the professor draws (e.g., "how does patent
  disclosure compare to trade secret secrecy?")
- **Channeling logic** — how the law steers different types of intellectual
  creations into different IP regimes based on their characteristics
- **Policy tensions** that are revisited throughout the course (e.g.,
  "when does IP protection become anticompetitive?")
- **Structural parallels** across regimes (e.g., "every IP regime has a
  functionality limitation — why?")

### How to Use Themes

Present the identified themes to the user and ask:
1. "I identified these course themes — are these right?"
2. "Are there other themes I should consider?"

Course themes should **influence but not dictate** essay design:
- When choosing which doctrines to test, prefer combinations that engage a
  course theme (e.g., a fact pattern testing trade secret and patent on the
  same information engages the channeling theme)
- When designing cross-doctrinal synthesis issues (Extended Abstract SOLO
  level), frame them around course themes — these are the issues where the
  A student demonstrates thematic understanding
- Do NOT create issues that test themes in the abstract (that's a policy
  essay). Themes should emerge from the doctrinal analysis, not replace it.
- Policy considerations (the goals underlying a doctrine) can appear in the
  rubric as **quality indicators** — arguments that strengthen an otherwise
  doctrinally-grounded analysis. They should never be **required elements**.
  A student who makes a strong doctrinal argument without mentioning policy
  gets full credit; a student who adds a policy rationale gets a stronger
  answer but not more points. Policy without doctrine earns nothing.

### IP Course Theme Examples

For the IP preset, common course themes include (confirm with the user):
- **Channeling** — how IP law channels different intellectual creations into
  different regimes (trade secret vs. patent for inventions, copyright vs.
  trademark for designs, etc.)
- **The disclosure bargain** — the tradeoff between exclusive rights and
  public knowledge (patent disclosure, copyright's limited term, trade
  secret's requirement of secrecy)
- **Functionality limits** — why every IP regime excludes functional features
  from protection (patent's utility requirement, copyright's
  idea/expression, trademark's functionality doctrine)
- **Incentives vs. access** — balancing the incentive to create against the
  public's interest in using intellectual goods
- **IP in the digital environment** — how technology (AI, DRM, platforms)
  challenges traditional IP frameworks

## Prior Exam Check

If the user provides prior exam essay questions, read them before designing
the new essay. This is not just a best practice — it is a compliance
requirement:

> **Policy:** "An instructor of a course or a seminar may not give an
> examination question or problem in a course or seminar if a substantially
> identical examination question or problem has been given by that instructor
> as part of the examination in a prior course or seminar."

The goal is to produce an exam that is clearly not "substantially identical"
to any prior exam — not to avoid the same doctrinal areas (which would be
impossible), but to avoid repeating the same *question design*.

### What to Check

For each prior essay, extract:
- The **scenario type** (industry, setting, character archetypes)
- The **issue set** (which specific doctrines were tested together)
- The **cross-cutting asset** (what single thing was analyzable under
  multiple regimes — e.g., "a recipe" or "a product design")
- The **discrimination features** (what was buried, ambiguous, or a red
  herring)

### Novelty Requirements

The new essay must differ from each prior essay on **at least 3 of 5**
dimensions:

| Dimension | What to Compare |
|---|---|
| **Doctrinal areas tested** | Which IP regimes does the question touch? The same areas can repeat across years (these are the course's core content), but the specific combination and breadth should vary. |
| **Scenario type** | Industry, setting, and character archetypes. If a prior exam used a restaurant, don't use a restaurant. |
| **Issue set** | The specific legal issues tested. Individual doctrines can repeat, but the specific *combination* should not. If a prior exam tested trade secret misappropriation + §101 eligibility + fair use, don't test that exact trio again. |
| **Cross-cutting asset** | The central asset that sits at the intersection of regimes. If a prior exam centered on a recipe, don't center on a recipe. |
| **Discrimination features** | The buried facts, ambiguous facts, and red herrings should test different doctrinal traps. If a prior exam buried an NDA consideration issue, don't bury the same issue. |

### How to Read Prior Exams

If the user provides a folder path:
1. Look for an INDEX.md file. If present, read it first — it contains YAML
   frontmatter for each exam file (topics, points, word limits, scenario
   descriptions) and a topic-by-year matrix.
2. Parse the YAML frontmatter from each exam file listed in the index for
   structured comparison data.
3. If no INDEX.md exists, read each exam file directly and extract the
   5 dimensions manually.

### How to Use

- Read prior exams early (step 2) so the constraint informs all design
  decisions
- Run the 5-dimension novelty check automatically and present a **novelty
  matrix** to the user: rows = prior questions, columns = dimensions,
  cells = same/different. The new essay must differ on >= 3 of 5 dimensions
  from every prior question.
- When presenting the essay plan (step 7), explicitly note how the new
  essay differs from each prior exam
- Include a "Prior exam differentiation" section in the Quality Analysis
  (Output 4) documenting the comparison

### When No Prior Exams Are Available

If the user says no prior exams exist, skip this check. Do not ask repeatedly.
