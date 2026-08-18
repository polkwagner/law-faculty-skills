# Density by Medium

Depth behind Step 3. Density is the Tufte principle most often misapplied,
because his density argument assumes a printed page read at arm's length.

## Why the split exists

Tufte's case for density — "say more per page," resist splitting one organized
graphic into five sparse ones — was made about *paper*. A reader controls the
distance, controls the time, and can re-read. None of that holds for a slide
projected in a room: distance is fixed, time is the speaker's, and there is no
second look.

His own *Cognitive Style of PowerPoint* makes the point from the other side —
the format's low resolution per slide is exactly why he thinks the handout beats
the deck. Both halves of his argument therefore point the same way: **when the
medium is projected, the answer is not to cram the page, it is to hand out the
page.**

So the density prescriptions and the legibility floor are not in conflict. They
apply to different media, and the first question is always: where will this be
read from?

## Projected slide

Legibility governs; density yields to it.

- **One idea, one comparison per slide.** If two comparisons are both essential,
  that is two slides, or one small-multiples grid that shows them at once.
- **Small multiples cap at about 6 panels.** Beyond that, panel labels and axis
  ticks fall below the legibility floor. Nine panels that cannot be read are
  worse than three that can.
- **Axis tick labels and annotations need to survive the room.** As a working
  floor at a 1280×720 check render, tick labels around 24px effective and
  annotations around 28px. If the chart only fits by going below that, the chart
  is too complex for the medium.
- **Direct labels rather than legends,** always. Legend round trips cost more
  when the audience cannot control pace.
- **Grey the context, colour the argument.** With the eye moving fast, one
  accent against neutrals does more than a full categorical palette.
- **The takeaway is the title.** State the finding in the title line, because
  some of the room will read only that.

**The escape hatch, and the right one: the handout.** When the material is
genuinely dense — a full results table, a nine-panel grid, a detailed schematic
— put it in a document the audience keeps and show a simplified view on screen.
This is Tufte's own recommendation, not a compromise against him.

## Print, PDF, handout

Density is the goal. This is the medium his argument was written for.

- **Do not split a coherent dense graphic across pages.** One organized page
  that rewards both a glance and a close read beats five sparse ones.
- **Small multiples can go wide** — 12, 20, 40 panels are legitimate when axes
  are identical and the grid is ordered meaningfully (by magnitude, by time, by
  geography — not alphabetically).
- **Tables belong here.** Exact values, many rows, read at the reader's pace.
- **Design for micro/macro reading.** A clear overall pattern at a glance, with
  enough resolution to read individual values on a stop.
- **Sparklines** — word-sized graphics set inline in a sentence or table cell —
  put the trend where the claim is, and cost almost no space.
- **Integrate the words.** Annotate directly on the graphic instead of writing a
  caption that describes what the reader is looking at.

## Web page, scrollable

Layered rather than uniformly dense; the reader controls pace but arrives fast.

- **Overview first, detail on the stop.** The top of a figure should carry the
  finding; supporting resolution can sit below.
- **Scroll is not a page break.** A long ordered sequence of small multiples
  works well here; a graphic split across a scroll boundary does not.
- **Responsive density is real.** A grid legible on a desktop collapses on a
  phone. Either reflow the panel grid or ship a simplified small-screen view —
  do not just let it shrink.
- **Wide graphics need their own horizontal scroll container,** never the page's.
- **Interaction is not a substitute for a good static view.** Tooltips that hide
  the only copy of a value fail any reader who does not hover, print, or use a
  pointer.

## Schematic and diagram

Governed by the mechanism being shown, not by an ink budget.

- **The layout should carry the structure.** Sequence left to right, hierarchy
  top to bottom, feedback as an explicit return path. A reader should infer the
  mechanism from the arrangement before reading a single label.
- **Label in place.** A diagram whose parts are keyed to a numbered list below
  makes the reader hold an index in their head.
- **Boxes only where there is real containment.** A box around every node is the
  diagram equivalent of a full table grid — ink that separates nothing.
- **One visual convention per meaning**, held consistently: if a dashed line
  means "optional" once, it cannot mean "asynchronous" later.
- **Show causality, not just adjacency.** Two boxes side by side assert nothing;
  an arrow asserts a mechanism. Do not draw the arrow unless you mean it.
