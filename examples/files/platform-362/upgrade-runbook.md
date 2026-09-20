# Cluster upgrade runbook

Staging first. Per node pool: cordon, drain with the pod disruption budgets honoured, upgrade, uncordon, verify CI runners rescheduled and order-api is serving. Then the next pool. Prod only after the edge allowlist carries the new control plane range.
