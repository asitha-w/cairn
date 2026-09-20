# Image prompts

Two images in the README. Regenerate with these prompts; keep the palette and typography of `cairn-overview.png`
(white background, slate text, navy line work, one orange accent, rounded cards, dashed group frames,
monospace caption strip along the bottom).

## cairn-overview.png — overview

Three columns. The "Plain Markdown Files" chips read
`work · systems · people · context lines → files outside`; remove `records` and `artifacts`. The crn
chips read `find · open · pending · log · decide · priority · sweep · trail · graph`. Subtitle under the
logo: "Persistent work memory for humans and coding agents". Keep everything else.

## cairn-two-layers.png — structure

A clean architecture diagram, landscape 3:2, same style as cairn-overview.png. Title top-left: "Cairn · two
layers". Two horizontal bands stacked, labelled on the left edge.

Band one, "LAYER 1 · THE GRAPH": a small network of nodes. Five to seven round navy nodes labelled
`work/…` (for example `work/platform-431`), three larger light-blue nodes labelled `systems/database`,
`systems/network`, `systems/monitoring`. Thin lines from each work node to one or two systems. One small
violet node labelled `people/cato` with a violet line to one work node labelled "waits on". One ringed
violet node labelled `you` with lines coming in from two square nodes labelled `PR #894 · yours` and
`PR #901 · review`. Caption under the band: "nodes and edges, what `crn find` and `crn graph` see".

Band two, "LAYER 2 · CONTEXT", split into two side-by-side cards. Left card "inline · always loaded":
a stylised Markdown file for `work/platform-431.md` showing a frontmatter block (`state: one sentence`,
`stage: parked`, `systems: [database, network]`) and the section headers `## Now`, `## Next`,
`## Decisions`, `## Context`, `## Log`; a small orange tag "~700 tokens" on it. Right card "lazy · read only
on doubt": three plain document icons outside a dashed frame labelled "outside the bundle", named
`investigations/2026-09-18-cdc-drift.md`, `research/peering/README.md`, `runbooks/compact.md`; one thin
orange arrow from a single line in the `## Context` section of the left card to the first document, the
line reading "finding in one sentence → path". A small note under the right card: "never indexed, never
in search, never in the graph".

Two producers feed the left card from below, drawn as small labelled arrows: "sessions → `crn trail` →
## Log" and "GitHub → `crn sweep` → gh_* fields". Bottom caption strip in monospace: "OPEN A NODE, GET
ONE SCREEN. OPEN A FILE ONLY WHEN IN DOUBT."

No people, no photos, no 3D, no gradients heavier than the reference. Legible at 900 px wide.
