---
type: system
title: edge
access: "firewall and VPN in the vendor console, user-run · SSO in the identity provider admin · allowlists and VPN CA declared in platform/edge/, applied by hand in a maintenance window Sindre approves"
look_in: "platform/edge/ · the identity provider's audit log for SSO"
env: [prod]
aliases: [firewall, vpn, sso, network, perimeter, identity]
---
# edge

The perimeter: firewall, VPN and single sign-on. Every change needs a window and a security officer.

## Gotchas

- The legacy SSO endpoint is still called by two on-prem installs; closing it without their upgrade locks them out on Monday morning.
