---
type: work
title: order-api creates a second order on a client retry
state: "reproduced on staging with a throttled client; fix is the idempotency key in PR #440, waiting on Cato's review"
stage: active
resource: https://github.com/vanaheim/product/issues/431
env: [staging, prod]
systems: [order-api, ci]
people: [cato]
blocked_by: []
gh_state: open
gh_updated: 2026-09-18T07:25:00Z
last_actor: cato
updated: 2026-09-17
---
# order-api creates a second order on a client retry

[order-api](../systems/order-api.md) · [ci](../systems/ci.md) · reviewer [Cato](../people/cato.md)

## Now

2026-09-17. Two customers reported double orders after a slow checkout. Reproduced on staging by throttling the client to 3G: the retry lands after the first request has committed. PR #440 adds an idempotency key on submit and a 24-hour dedupe table. Cato has the review.

## Next

1. Address Cato's review, merge, let CI take it to staging.
2. Replay the two customer cases against staging before the prod deploy.
3. Prod deploy through the release environment; watch the duplicate-order metric for a day.

## Decisions

- 2026-09-17 dedupe on an idempotency key, not on payload hash: two identical orders in a row are legal

## Context

- reproduction log: the throttled-client steps, the two requests and the timestamps → ../../files/product-431/repro-2026-09-17.md

## Log

- 2026-09-16 session 8ae135c0: 43 calls · `kubectl -n orders logs` · `make test`
- 2026-09-17 session e1d9e214: 19 calls · `gh pr create` · `curl` against staging
