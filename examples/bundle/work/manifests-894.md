---
type: work
title: Remove the retired event exporter
state: "two PRs open, changes requested on the manifests one; waiting on my rebase"
stage: blocked
resource: https://github.com/acme/manifests/issues/894
env: [dev, prod, ops]
systems: [monitoring]
people: [sam]
blocked_by: []
gh_state: open
gh_updated: 2026-09-12T10:00:00Z
last_actor: sam
updated: 2026-09-07
---
# Remove the retired event exporter

Systems: [Monitoring stack](../systems/monitoring.md) · reviewer [Sam](../people/sam.md)

## Now

2026-09-07. The exporter was replaced by the collector; two PRs remove its values files and its GitOps application. Sam requested changes on the manifests PR.

## Next

1. Rebase and address the review.
2. After merge, delete the two live applications by hand; removal from git alone leaves them running.

## Decisions

## Context

## Log

- 2026-09-07 session 5fec630f: 22 calls · `gh pr create` ×2

