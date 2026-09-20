---
type: system
title: ci
access: "GitHub Actions in vanaheim/product and vanaheim/platform · runners in the staging cluster · prod deploy needs the release environment approval"
look_in: ".github/workflows/ in each repo · platform/runners/"
env: [staging, prod]
aliases: [pipeline, actions, build, deploy]
---
# ci

The pipelines. Everything that reaches prod goes through here, including the platform changes.

## Gotchas

- The cache key includes the lockfile hash; a dependency bump invalidates every cache and the first run after it takes three times longer. Not a regression.
