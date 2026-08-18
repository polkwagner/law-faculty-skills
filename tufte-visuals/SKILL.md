---
name: tufte-visuals
description: >
  Information-design judgment for charts, diagrams, tables, and decks:
  encoding choice, data honesty, density by medium. Use when building or
  reviewing any data-bearing visual.
license: CC-BY-4.0
---

# Information Design for Data-Bearing Visuals

Judgment for any visual that carries data, comparison, or quantitative claim —
a chart, a table, a schematic, a timeline, a slide, a figure in a document, a
page on a website. Use it when building one and when reviewing one.

## What this skill is not

**It does not draw the chart.** If a `dataviz` skill is available, that one owns
the rendering system: palette construction, colour accessibility, light/dark
behaviour, mark specifications, stat tiles, legend and axis mechanics. Read it
for *how the thing is drawn*, and substitute your institution's brand tokens
where it asks for them.

This skill owns the layer above: **is this the right comparison, is the encoding
honest, and is the density right for where it will be seen.** The two compose —
consult this one first to decide what to build, then that one to build it.

Order of operations: **decide here → render there.**

## The first question

Before choosing a chart type, answer Tufte's opening move from *Beautiful
Evidence*: **compared with what?** A number alone is not evidence. A visual
earns its place by showing a contrast, a difference, a change, or a mechanism.

His six principles of analytical design, in the order they apply:

1. **Show comparisons, contrasts, differences.** The fundamental analytical act.
2. **Show causality, mechanism, structure.** Not just that it moved — why.
3. **Show more than one or two variables.** Real questions are multivariate.
4. **Integrate words, numbers, images, and diagrams.** Do not separate a chart
   from its explanation; annotate in place.
5. **Document the evidence.** Sources, normalization, method, on the graphic.
6. **Content counts most.** No design move rescues a claim not worth making.

If a visual fails 1 and 2, no amount of chart-craft saves it. Consider a
sentence instead — a number stated plainly often beats a chart of one number.

## Step 1 — Choose the encoding

Chart type is not a matter of taste. Cleveland and McGill (1984) ranked how
accurately people read quantities from each visual channel. Use the highest
channel the data allows:

| Rank | Channel | Reads as |
|---|---|---|
| 1 | Position along a common scale | most accurate |
| 2 | Position along non-aligned scales | |
| 3 | Length, direction, angle | |
| 4 | Area | |
| 5 | Volume, curvature | |
| 6 | Shading, colour saturation | least accurate |

This makes the usual advice derivable rather than dogmatic:

- **A dot plot or bar chart beats a pie chart** — pies encode with angle and
  area (ranks 3–4) what a bar encodes with common-scale position (rank 1).
- **Grouped bars beat stacked bars** for comparing segments — only the bottom
  segment of a stack sits on a common scale; the rest float on non-aligned ones.
- **A small-multiples grid beats a bubble chart** — identical axes across panels
  restore rank-1 position where bubbles force rank-4 area.
- **Colour saturation is for pattern, not for reading values.** A heatmap shows
  *where* something is concentrated; it cannot show *how much* precisely. Pair
  it with numbers if exact values matter.

Full guidance, including when a lower channel is the right call:
[references/chart-decisions.md](references/chart-decisions.md).

## Step 2 — Check integrity, while the data is still in scope

**This check happens when the chart is generated, not when it is reviewed.**
A rendered image does not carry its own source numbers, so the central integrity
test is uncomputable downstream. Do it now or it does not get done.

**Lie factor** = size of effect shown in the graphic ÷ size of effect in the
data. Tufte treats anything below 0.95 or above 1.05 as substantial distortion —
beyond what production inaccuracy explains. Compute it whenever a visual element
is scaled to represent a quantity.

Three rules that follow:

- **Bars and areas start at zero. No exception.** Length *is* the encoding, so a
  truncated baseline changes the encoded value. Correll, Bertini and Franconeri
  (2020) confirm the exaggeration, and found it **persists even when the design
  explicitly cues that truncation occurred** — so an axis break or a label does
  not fix it.
- **Lines may truncate**, and often must, to show fine variation. But since
  cueing the truncation does not neutralize the perceived exaggeration, **state
  the actual effect size in words** near the chart: "up 4.6 points" alongside a
  line that visually doubles.
- **Never scale a 2D shape by height to encode a 1D value.** Area grows as the
  square; a barrel icon drawn twice as tall reads as four times as much. This is
  the classic lie-factor failure.

**Document on the graphic, not in an appendix.** Source, date, sample size, and
any normalization — per capita, inflation-adjusted, seasonally adjusted, indexed
to a base year — belong in small print beside the chart. A normalization the
reader cannot see is a distortion they cannot correct for.

**If you did not generate the chart** and cannot see the underlying data, say so
rather than implying the check passed. "Figure supplied; underlying data not
available for integrity check" is an honest note. Silence reads as verification.

## Step 3 — Set density by medium

Density is the principle most often applied wrongly, because Tufte's density
argument assumes a page read at arm's length. **A projected slide is a different
medium with a hard legibility floor, and the same layout is right in one and
wrong in the other.**

| Medium | Density posture |
|---|---|
| Projected slide | Legibility governs. One idea, one comparison. Small multiples cap at ~6 panels. |
| Print, PDF, handout | Density is the goal. Tables and dense multiples belong here. |
| Web page, scrollable | Layered: overview reads at a glance, detail rewards a stop. |
| Schematic / diagram | Governed by the mechanism shown, not by ink budget. |

Specifics, floors, and the projected-vs-print split:
[references/medium-guide.md](references/medium-guide.md).

## Step 4 — Remove what distorts; keep what helps recall

Tufte's data-ink argument says delete every pixel that is not data. Take the
*distortion* half and leave the ascetic half — the evidence does not support the
strong version:

- Inbar, Tractinsky and Meyer (2007) had 87 participants compare a standard bar
  chart with a minimalist version of the same data and found a clear preference
  for the standard one.
- Bateman et al. (2010) found embellished charts were read no less accurately
  than plain ones, and recalled **significantly better** two to three weeks on.

Read those honestly: Inbar measured preference, which is not comprehension, and
Bateman used few data points with unlimited viewing time. But when the goal is
that an audience remembers a finding weeks later — teaching, most of all — the
ascetic version is arguing against the evidence.

**Delete, always** — these distort or mislead:
- 3D effects on bars, pies, or lines. They add no information and corrupt
  magnitude judgments.
- Drop shadows on data marks, which detach the mark from its baseline.
- Moiré patterns and heavy cross-hatching as fills.
- Gridlines heavy enough to compete with the data line.
- A legend duplicating information already on the marks.

**Keep or add, when it helps** — these aid reading or recall:
- Direct labels on lines and bars with ≤5 series. The eye stays on the data
  instead of round-tripping to a key.
- An annotation naming the inflection point, placed at it.
- An image or motif that carries the subject, provided it never encodes a value
  and never sits between the reader and a number.

The dividing line is **whether it touches the quantity.** Decoration adjacent to
the data is a recall aid. Decoration that *is* the data, or that obscures it, is
a defect.

## Step 5 — Layer with weight and position, not boxes

Separate data from annotation using type weight, size, colour, and placement —
not boxes, borders, and rules. Restrict colour to **one accent for the series
being argued about, neutrals for context.** A different colour per category is
right only when the categories themselves are the argument.

Give the visual a **takeaway title that states the finding**, not a label naming
the axes: "MCQ scores rose 14 points with materials; essays did not move" beats
"Scores by condition." A reader who takes only the title should still get the
point.

Where the claim is analytical rather than a list, write the sentence. Fragments
strip out the causal and conditional connections that make a claim a claim.

## Reviewing an existing visual

In order. Stop at the first failure — later checks are moot if the data is wrong.

1. **Integrity.** Baseline, scaling, lie factor, undisclosed normalization. A
   correctness defect, not a style note. If the underlying data is unavailable,
   record what could not be checked.
2. **Comparison.** Compared with what? Is that the comparison the argument needs?
3. **Encoding.** Could a higher channel carry this? Pie, stacked bar, bubble, or
   value-bearing colour are the usual downgrades.
4. **Distortion.** 3D, shadows, moiré, competing gridlines, redundant legend.
5. **Density for its medium.** Illegible projected, or wastefully sparse in print.
6. **Title.** A finding, or a label?

Report integrity failures separately from design suggestions. The first is a
correction; the second is an opinion.

## Sources

- Tufte, *The Visual Display of Quantitative Information* (1983; 2nd ed. 2001) —
  lie factor, data-ink, chartjunk, data density.
- Tufte, *Envisioning Information* (1990) — layering and separation, small multiples.
- Tufte, *Beautiful Evidence* (2006) — the six principles of analytical design.
- Tufte, *The Cognitive Style of PowerPoint* (2003; 2nd ed. 2006) — the bullet-outline critique.
- Cleveland & McGill, "Graphical Perception," *JASA* 79:387 (1984) — the encoding hierarchy.
- Correll, Bertini & Franconeri, "Truncating the Y-Axis: Threat or Menace?" CHI 2020.
- Bateman et al., "Useful Junk?" CHI 2010.
- Inbar, Tractinsky & Meyer, "Minimalism in Information Visualization," ECCE 2007.
