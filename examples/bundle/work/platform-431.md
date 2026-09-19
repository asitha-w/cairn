---
type: work
title: Peer the dev database cluster to the ops network
state: parked, waiting on Sam for the tier, the container CIDR and whether users are cluster-scoped
stage: parked
resource: https://github.com/acme/platform/issues/431
env:
- dev
- ops
systems:
- database
- network
people:
- sam
blocked_by:
- work/platform-422
gh_state: open
gh_updated: 2026-09-17T07:25:00Z
last_actor: me
updated: 2026-09-18
---
# Peer the dev database cluster to the ops network

Systems: [Database cluster](../systems/database.md) · [Network](../systems/network.md) · waits on [Sam](../people/sam.md) · blocked by [the PoC](platform-422.md)

## Now

2026-09-18. Filed and assigned to me and Sam. Nothing built. The peering plan is intact; a relocation question now sits in front of it: should dev share a vendor project with prod at all. Sequencing is recorded on the issue: if dev relocates, it happens before anything is peered.

## Next

1. Wait for Sam on tier and region, container CIDR, user scoping.
2. Settle the relocation question; the vendor guidance says split.
3. Subnet NSGs are the only unblocked step and can start any time.

## Decisions

- 2026-09-17 relocation, if any, happens before peering, because nothing is peered today

## Artifacts

- [peering plan draft](../artifacts/platform-431/peering-plan-2026-09-16.md)

## Log

- 2026-09-16 session 8ae135c0: 43 calls · `terraform plan` on the test project
- 2026-09-17 session e1d9e214: 1 call · read the note

