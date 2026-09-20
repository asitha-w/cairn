---
type: system
title: order-api
access: "repo vanaheim/product, service order-api · staging via the cluster kubeconfig, namespace orders · logs and traces in the observability stack under service=order-api · prod deploys through CI only"
look_in: "product/services/order-api/ · platform/apps/order-api/ for the manifests"
env: [staging, prod]
aliases: [orders, order service, checkout, backend]
---
# order-api

The backend service that takes orders. Owned by the engineer, deployed by CI, watched by everyone.

## Gotchas

- Submit is not idempotent below v2.3; a client retry on a slow network creates a second order. Fixed by the idempotency key in PR #440.
- Staging shares the payments sandbox with the prototype lab; sandbox rate limits show up as 429s that look like our bug.
