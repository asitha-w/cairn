---
type: work
title: Usage-based pricing prototype for the product owner
state: "prototype deployed to the lab and demoed; parked until Ingrid picks a metering model"
stage: parked
resource: https://github.com/vanaheim/product/issues/419
env: [staging]
systems: [prototype-lab, order-api]
people: [ingrid]
blocked_by: []
gh_state: open
gh_updated: 2026-09-15T15:00:00Z
last_actor: me
updated: 2026-09-15
---
# Usage-based pricing prototype for the product owner

[prototype-lab](../systems/prototype-lab.md) · [order-api](../systems/order-api.md) · waits on [Ingrid](../people/ingrid.md)

## Now

2026-09-15. Three metering models built side by side in the lab (per order, per seat, per volume tier) with last quarter's real order data replayed through them. Demoed to Ingrid; she wants to see the per-seat numbers against the two largest accounts before deciding.

## Next

1. Wait for Ingrid's decision on the metering model.
2. Redeploy the lab namespace if it has been collected before she decides.
3. When decided: write the product issue for the real implementation; this node is done.

## Decisions

- 2026-09-15 the prototype replays real data but never writes to order-api; pricing stays a read-only view until a model is chosen

## Context

- pricing notes: the three models, the replay method and the per-account numbers shown at the demo → ../../files/product-419/pricing-notes.md
- earlier Log, 1 session line(s) 2026-09-12 to 2026-09-12 → ../../files/product-419/log.md

## Log

- 2026-09-15 session 2c1a77b0: 9 calls · demo prep
