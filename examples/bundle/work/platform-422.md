---
type: work
title: Prove database network peering end to end on a test project
state: "done: all proof rounds passed; close-out comment posted"
stage: done
resource: https://github.com/acme/platform/issues/422
env: [dev]
systems: [database, network]
people: []
blocked_by: []
gh_state: open
gh_updated: 2026-09-16T13:00:00Z
last_actor: me
updated: 2026-09-16
---
# Prove database network peering end to end on a test project

Systems: [Database cluster](../systems/database.md) · [Network](../systems/network.md)

## Now

2026-09-16. Three proof rounds passed on a throwaway project: peering created from Terraform, routes visible both sides, a client in the ops network reached the cluster privately. Close-out comment posted; issue stays open until the parent decides.

## Next

1. Nothing; the parent (#431) carries the real work.

## Decisions

- 2026-09-15 peer over private endpoints rather than a VPN, cost

## Context

- proof round log: three rounds, all passed → ../../files/platform-422/rounds.md

## Log

- 2026-09-16 session 8ae135c0: 136 calls · `terraform apply` · `dig` from the ops client

