---
type: system
title: Database cluster
access: "read: db-ro MCP servers per cluster · metrics: job db-metrics in the metrics store · writes and resizes: user-run in the vendor console"
look_in: "manifests/db/ · the backfill job repo for connection secrets"
env: [prod, dev]
aliases: [db, mongo, cluster, atlas]
---
# Database cluster

Managed document database, one cluster per environment. Storage does not shrink after deletes; reclaiming space is a compact per node followed by a tier change.

## Gotchas

- Egress from the app network to the database is billed twice: once by the cloud NAT, once by the vendor.
- The metrics job needs the vendor scrape credential; without it the dashboard is empty, not red.

