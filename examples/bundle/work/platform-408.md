---
type: work
title: Rotate the VPN certificate authority and close the legacy SSO endpoint
state: "change prepared and reviewed; blocked on Sindre approving a maintenance window, and on the two on-prem installs upgrading first"
stage: blocked
resource: https://github.com/vanaheim/platform/issues/408
env: [prod]
systems: [edge, secrets]
people: [sindre]
blocked_by: []
gh_state: open
gh_updated: 2026-09-14T10:00:00Z
last_actor: sindre
updated: 2026-09-14
priority: 2
priority_by: human
---
# Rotate the VPN certificate authority and close the legacy SSO endpoint

[edge](../systems/edge.md) · [secrets](../systems/secrets.md) · waits on [Sindre](../people/sindre.md)

## Now

2026-09-14. New CA issued and staged in the vault; the allowlist change for the cluster upgrade rides in the same window. Sindre wants the two on-prem customers confirmed on the new SSO flow before the legacy endpoint closes.

## Next

1. Get written confirmation from both on-prem installs.
2. Sindre approves the window; announce it.
3. Rotate the CA, update the allowlist, close the endpoint, verify VPN and SSO from outside.

## Decisions

- 2026-09-12 CA rotation and SSO closure share one window: one announcement, one rollback plan

## Context

## Log

- 2026-09-12 session 77b1e9d4: 14 calls · vault console · `gh issue comment`
