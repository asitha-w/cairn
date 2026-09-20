---
type: work
title: Reserved instances expire 2026-10-02 with auto-renew off
state: "decision taken: renew one year; figures reconciled; purchase is user-run before the cliff"
stage: active
resource: https://github.com/acme/platform/issues/362
env: [prod]
systems: []
people: [alex]
blocked_by: []
gh_state: open
gh_updated: 2026-09-16T09:00:00Z
last_actor: alex
updated: 2026-09-17
---
# Reserved instances expire 2026-10-02 with auto-renew off

Waits on [Alex](../people/alex.md) for the purchase.

## Now

2026-09-17. Ten reservations lapse on 2026-10-02 and would fall to pay-as-you-go at about 9.7k a month more. The observer work found no better node type in the region; the decision is a one-year renewal.

## Next

1. Alex places the purchase before 2026-10-01.
2. Confirm the new reservation ids on the issue.

## Decisions

- 2026-09-10 one-year term, not three; the exchange rules change on 2027-02-01

## Context

- reservation plan: one-year term, figures reconciled → ../../files/platform-362/plan.md

## Log

- 2026-09-17 session 047c5303: 12 calls · `az reservations` reads

