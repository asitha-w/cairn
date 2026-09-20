---
type: system
title: cluster
access: "kubeconfig from the platform repo, contexts staging and prod · read-only role by default; writes through PRs to vanaheim/platform · node pools and versions in platform/clusters/"
look_in: "platform/clusters/ · platform/apps/ · the upgrade runbook under the work folder"
env: [staging, prod]
aliases: [kubernetes, k8s, nodes, node pool, platform]
---
# cluster

The Kubernetes platform both environments run on. Upgrades roll one node pool at a time and need the edge change first.

## Gotchas

- The prod control plane is pinned to the edge VPN range; an upgrade that recreates the control plane IP breaks the VPN route until the edge allowlist is updated.

## Runbooks

- roll the cluster one node pool at a time, staging first, with the drain and verify steps per pool → ../../files/platform-362/upgrade-runbook.md
