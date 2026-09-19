---
type: work
title: Compact the telemetry collection to reclaim freed space
state: deletes done (5.6B documents); compact per node and the tier downsize remain, both user-run
stage: active
resource: https://github.com/acme/platform/issues/419
env:
- prod
systems:
- database
people:
- sam
blocked_by: []
gh_state: open
gh_updated: 2026-09-17T15:00:00Z
last_actor: me
updated: 2026-09-19
---

# Compact the telemetry collection to reclaim freed space

Systems: [Database cluster](../systems/database.md) · waits on [Sam](../people/sam.md)

## Now

2026-09-17. The delete campaign finished 2026-09-12: 100 weeks, 5.61 billion documents, no failures. Disk is unchanged at 73 percent because the engine frees pages inside files and never shrinks them. The whole saving lands at compact plus tier downsize, estimated 250 to 330 GiB per node.

## Next

1. Run the compact, evening, outside the snapshot window, one node at a time, secondaries first.
2. Post the free-storage figure on the issue; replaces the estimate.
3. Downsize the storage tier after all three nodes.

## Decisions

- 2026-09-12 no replay of the three unreadable buckets; filed separately

## Artifacts

- [compact runbook](../artifacts/platform-419/compact-runbook.md)
- [free-storage ask sheet](../artifacts/platform-419/collstats-request.md)

## Log

- 2026-09-12 session 914fa4fd: 53 calls · `q-db.sh` counts · `gh issue create` for the buckets
- 2026-09-17 session e1d9e214: 19 calls · `kubectl get cronjob` · `q-db.sh` week states

