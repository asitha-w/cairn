---
name: cairn
description: "crn — the user's work graph in plain markdown (Cairn). Use when the user names a piece of work or a system to pick up ('let's work on X', 'state of Y'), asks what is pending, wants a milestone recorded, or asks for a GitHub sweep. Everything is a CLI call, deterministic, no model: crn find, crn open, crn pending, crn state, crn log, crn decide, crn sweep, crn trail. Never read the bundle's files directly when a crn verb answers the question."
---

# Cairn

The bundle is a folder of markdown nodes: `work/`, `systems/`, `people/`. `crn` is on the PATH and
finds the bundle from `$CAIRN_BUNDLE`. Every verb prints one screen; print it as-is, then act.

## The five moves

| The user says | Run | Then |
|---|---|---|
| "let's work on peering" | `crn find peering` | one or more work nodes with their one-line state. If two are live, show the two state lines and ask which. |
| picks one | `crn open work/<key>` | read Now and Next; open at most one artifact if needed. Do not read other nodes. |
| we work | the work itself (gh, kubectl, editors) | anything that changes an environment or code stays with you and the user's permissions |
| a milestone lands | `crn log <key> "what landed"`; a decision: `crn decide <key> "…"`; a new truth: `crn state <key> "one sentence"` | say that you recorded it |
| "what should I pick up" | `crn pending` | the list, as printed. Do not summarise or re-rank. |
| "do a sweep" | `crn sweep` (`--create` to add nodes for new issues) | list the new and changed items; the user decides what becomes a node |

## Rules

- A claim on screen with a date or an owner is verified with one read of the source (`gh issue view`),
  never assumed. Nodes lag; `gh_*` fields say when GitHub last moved.
- `crn` writes only inside the bundle. GitHub comments, PRs and any environment change are yours,
  by hand, with the user's permissions.
- Do not grep the bundle or read `work/*.md` in bulk. If a word does not resolve, the fix is an
  `aliases` entry on the system node or a better `state` sentence, not a wider search.
- `crn validate` after editing a node by hand; the schema is the contract.
