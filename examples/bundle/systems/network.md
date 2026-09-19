---
type: system
title: Network
access: "cloud CLI with the ops subscription · read-only role on this workstation · changes go through the infra repo"
look_in: "infra/network/ (peerings, NAT, NSGs)"
env: [prod, dev, ops]
aliases: [vnet, peering, nat, nsg, egress, firewall]
---
# Network

Virtual networks per environment, a NAT gateway on prod, peerings between ops and the rest.

## Gotchas

- A peering must exist on both sides before routes appear; one side alone looks green and routes nothing.

