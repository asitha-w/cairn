---
type: system
title: Monitoring stack
access: "grafana CLI (view role) · every metrics query needs a cluster= label"
look_in: "manifests/monitoring/ (collector, rules, alert routing)"
env: [ops]
aliases: [alerts, alerting, metrics, logs, grafana, dashboards]
---
# Monitoring stack

Central metrics, logs and alerting in the ops cluster; prod and dev ship into it.

## Gotchas

- An alert that depends on a target existing fires on both evaluators when the target is gone; guard with a count of the target first.

