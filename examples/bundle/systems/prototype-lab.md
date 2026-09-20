---
type: system
title: prototype-lab
access: "sandbox project vanaheim/lab · one namespace per prototype on the staging cluster · deploy by hand with make deploy, nothing here goes through CI"
look_in: "lab/<prototype>/ · the prototype notes under the work folder"
env: [staging]
aliases: [lab, prototype, poc, spike]
---
# prototype-lab

Where product-owner ideas get built to be looked at, not shipped. Nothing here is production, and nothing here is reviewed.

## Gotchas

- Namespaces are garbage-collected after 14 days without a deploy; a parked prototype vanishes and has to be redeployed from the notes.
