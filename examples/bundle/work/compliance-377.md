---
type: work
title: ISO 27001 surveillance audit evidence pack
state: "eleven of fourteen controls have dated evidence; waiting on Cato for the access-review export, due 2026-10-10"
stage: active
resource: https://github.com/vanaheim/compliance/issues/377
env: [prod]
systems: [iso-evidence, edge, cluster]
people: [cato, sindre]
blocked_by: []
gh_state: open
gh_updated: 2026-09-13T12:00:00Z
last_actor: me
updated: 2026-09-13
priority: 2
priority_by: human
---
# ISO 27001 surveillance audit evidence pack

[iso-evidence](../systems/iso-evidence.md) · [edge](../systems/edge.md) · [cluster](../systems/cluster.md) · waits on [Cato](../people/cato.md) · sign-off [Sindre](../people/sindre.md)

## Now

2026-09-13. The checklist maps fourteen controls to an export each. Eleven are in the evidence store and dated inside the period. Missing: the quarterly access review (Cato's export), the edge change log (after platform-408 lands), and the backup restore test.

## Next

1. Cato exports the access review; file it under A.9.
2. Run and record the backup restore test.
3. After the edge window: export the change log.
4. Sindre signs the pack; hand it to the auditor.

## Decisions

- 2026-09-13 evidence is exported from the system it describes, never written by hand

## Context

- evidence checklist: the fourteen controls, the export for each, and what is still missing → ../../files/compliance-377/evidence-checklist.md

## Log

- 2026-09-13 session 3b7d2a10: 27 calls · `gh api` exports · evidence store commits
