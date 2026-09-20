---
type: system
title: secrets
access: "vault at the platform level, read through the cluster's secret store · rotation is a PR to platform/secrets/ plus a manual step in the vault console"
look_in: "platform/secrets/ · rotation history in the vault audit log"
env: [staging, prod]
aliases: [vault, credentials, keys, certificates]
---
# secrets

Credentials, certificates and the VPN certificate authority.

## Gotchas

- The VPN CA expiry is not monitored; the last one expired on a Saturday. The rotation issue is the reminder.
