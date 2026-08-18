# Chart Decisions: Encoding and Integrity

Depth behind Steps 1 and 2 of the skill. Read when choosing a chart type, or
when checking one for distortion.

## Part 1 — Encoding

### The hierarchy

Cleveland and McGill (1984) measured how accurately people extract quantities
from each visual channel. The ranking is the closest thing information design
has to a physical constant:

1. Position along a common scale
2. Position along non-aligned scales
3. Length, direction, angle
4. Area
5. Volume, curvature
6. Shading, colour saturation

**The rule:** encode the quantity that carries your argument on the highest
channel the data structure allows. Push secondary quantities down the list.

### Applied to chart choice

| You want to show | Default | Why |
|---|---|---|
| Values across categories | Horizontal bar or dot plot | Rank 1; horizontal fits long labels |
| Change over time, one or few series | Line | Rank 1 for value, direction reads the trend |
| Parts of a whole | Bar, or a stacked bar **only if** parts ≤3 | Pie is ranks 3–4; a stack floats all but the first segment |
| The same relationship across groups | Small multiples, identical axes | Restores rank 1 within every panel |
| Two variables, many points | Scatter | Both on rank 1 |
| Three variables, many points | Scatter + small multiples, not bubble size | Bubble area is rank 4 |
| Distribution | Histogram, box plot, or strip plot | Rank 1 |
| Ranking that changes over time | Slope chart | Position plus direction, both high |
| Geographic pattern | Choropleth, knowing the limits | Colour is rank 6 — pattern only, never precise values |
| One number | A sentence | A chart of one number is a chart of nothing |

### When a lower channel is right

The hierarchy ranks *accuracy of value extraction*. That is not always the job.

- **Pattern over precision.** A heatmap of 400 cells communicates a shape no
  rank-1 encoding fits on the page. Correct, so long as no argument depends on
  reading an individual cell. Add the numbers if one does.
- **Geography is fixed.** A map's positions encode place, not quantity, so
  quantity falls to colour. Accept rank 6 and label the values that matter.
- **Familiarity has real value.** Two or three parts of a whole in a pie are
  read reliably by everyone. The pie's failure is at five-plus slices, where
  angle comparison collapses.
- **Nesting is the point.** A treemap encodes hierarchy in a way no bar chart
  does. Use it for structure, not for comparing leaf values.

State the trade when you take it: "colour here shows the pattern; exact values
are labelled."

### Series count and labelling

- **≤5 series: label directly** at the end of each line or inside each bar.
  Direct labels remove a round trip to the legend on every read.
- **6+ series:** you probably have small multiples, not one chart. If the lines
  genuinely belong together, grey all but the one being argued about and label
  that one.
- **Never** a legend *and* data labels *and* a title all naming the same thing.

## Part 2 — Integrity

Do this while the source numbers are in scope. A rendered image cannot be
integrity-checked afterwards, because it no longer carries its data.

### Lie factor

    lie factor = size of effect shown in graphic ÷ size of effect in data

Tufte flags <0.95 or >1.05 as substantial distortion. Worked example, his own:
a fuel-economy graphic where the data rose 53% while the drawn effect rose
783% — a lie factor of 14.8.

Compute it whenever a graphical element is *scaled* to represent a value. When
a chart uses common-scale position with a zero baseline, the lie factor is 1.0
by construction, which is the argument for that encoding.

### The baseline rules

**Bars and areas start at zero. No exception.** The mark's length is the
encoding; cut the baseline and you have re-encoded every value. Correll,
Bertini and Franconeri (2020) found the exaggeration of subjective effect size
persists **even when the design explicitly signals the truncation** — so axis
breaks, jagged marks, and "note: axis does not start at zero" do not repair it.
If the differences are too small to see against a zero baseline, that *is* the
finding. Say it in words.

**Lines may truncate.** A line encodes value by position and trend by direction;
showing fine variation often requires a narrow range, and forcing zero can hide
a real signal. Two obligations follow: label the axis range plainly, and — since
labelling does not neutralize the perception — **state the effect size in
words**. A line that visually doubles while the data moved 4.6 points needs
"up 4.6 points" on the slide.

**Never scale a 2D shape by height to encode a 1D value.** Doubling an icon's
height quadruples its area; the reader sees the area. Either scale area to the
value, or use a bar.

**Dual axes distort by default.** Two series on two scales lets the designer
choose where they cross. Prefer indexing both to a base period on one axis, or
small multiples. If dual axes are unavoidable, say what the alignment implies.

### Disclosure

On the graphic, in small print, near the data — not in an appendix or a
speaker note:

- Source and date of the data
- Sample size, where inference depends on it
- Any normalization: per capita, inflation-adjusted, seasonally adjusted,
  indexed to a base year, excluding a category
- Any exclusion or truncation of the data itself, as distinct from the axis

A normalization the reader cannot see is a distortion they cannot correct for.

### When you did not make the chart

If a figure arrives pre-rendered and the underlying numbers are unavailable,
you can check what is visible — baseline, 3D, disclosure lines, scaling of
iconography — and nothing else. Record the limit explicitly:

> Figure supplied pre-rendered; baseline and disclosure verified from the image.
> Underlying data not available, so the lie factor was not computed.

Silence about an unperformed check reads as a passed check.

## Part 3 — Tables

Tables are not a lesser chart. They win whenever readers need exact values,
whenever the categories are few and the numbers are the point, and whenever the
document will be read rather than projected.

- **Right-align numbers, decimal-aligned.** Digit places must line up vertically
  or the column cannot be scanned.
- **Rules sparingly.** A header rule and a bottom rule are usually enough. Full
  grids box every cell and add ink that separates nothing.
- **No vertical rules.** Column spacing already separates columns.
- **Sort by a meaningful column,** not alphabetically, unless readers will look
  up a known row.
- **Significant digits, not spreadsheet defaults.** Trailing noise digits imply
  a precision the data does not have and make columns harder to compare.
- **Numbers first, labels close.** A wide gap between a row label and its values
  forces the eye to track across whitespace; keep the columns tight.
