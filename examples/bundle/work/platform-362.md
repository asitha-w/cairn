---
type: work
title: Upgrade both clusters to the next Kubernetes minor
state: "staging upgraded and soaked a week; prod waits for the edge allowlist change because the control plane IP moves"
stage: active
resource: https://github.com/vanaheim/platform/issues/362
env: [staging, prod]
systems: [cluster, ci]
people: []
blocked_by: [work/platform-408]
gh_state: open
gh_updated: 2026-09-16T09:00:00Z
last_actor: me
updated: 2026-09-16
---
# Upgrade both clusters to the next Kubernetes minor

[cluster](../systems/cluster.md) · [ci](../systems/ci.md) · blocked by [the edge change](platform-408.md)

## Now

2026-09-16. Staging has run the new minor for seven days with no regressions; the runbook was written from that roll. Prod cannot follow until the edge allowlist includes the new control plane range, which is part of the VPN CA rotation window.

## Next

1. After platform-408 lands: update the allowlist, then roll prod one node pool at a time per the runbook.
2. Verify CI runners reschedule after each pool.

## Decisions

- 2026-09-10 one minor at a time, never two; the vendor supports skipping but the ingress chart does not

## Context

## Log

- 2026-09-09 session a91f0c22: 61 calls · `kubectl drain` ×4 · `kubectl get nodes -w`
