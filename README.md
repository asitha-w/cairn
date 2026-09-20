# Cairn

Cairn gives coding agents persistent memory of your work across sessions, repositories and tools.

A coding-agent session dies and its context dies with it. The next morning you pay the onboarding tax
again: which issue was this, what did we decide, what did we actually run, who are we waiting on. Cairn
keeps the answer in a folder of plain Markdown you own, updated by deterministic tools, read by you and
by the agent in one screen. No database is the truth, no model is called, nothing leaves the machine.

## How it works

<p align="center"><img src="docs/cairn0.png" alt="Cairn overview: your work from GitHub, Claude Code, your CLI and notes flows through crn and iwe into plain Markdown files, read back by humans and coding agents" width="900"></p>

Your work arrives from GitHub, from agent transcripts and from you. `crn` (the work verbs) and
[`iwe`](https://github.com/iwe-org/iwe) (the graph engine) keep it as Markdown files. Humans read them in
an editor or the local viewer; agents read them through the CLI, one node at a time.

<p align="center"><img src="docs/cairn1.png" alt="Cairn structure: layer one is a graph of work and system nodes; layer two is context on each node, inline in the body or lazy as one line pointing at a file outside the bundle" width="900"></p>

Two layers. **Layer one is the graph**: work nodes (one piece of work each) linked to system nodes (one
thing you operate each), with people as small nodes for whoever work waits on. **Layer two is context**
and hangs off a node in two forms: *inline*, the node body, always loaded with it; and *lazy*, one line
in the body that carries a finding in one sentence and the path of a file outside the bundle, read only
when you or the agent are in doubt. Investigations, research, runbooks and plans stay where they are.
Sessions feed a node's Log through a hook; the sweep feeds its GitHub fields. Opening a node costs about
700 tokens and loads nothing else.

```
my-graph/
  cairn.toml                 who you are: GitHub org and user, where transcripts live
  work/platform-431.md       one piece of work: one-line state, Now, Next, Decisions, Context, Log
  systems/database.md        one thing you operate: how to reach it, where its config lives, gotchas, runbooks
  people/sam.md              someone work waits on
```

Every file is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
concept: YAML frontmatter plus markdown, linked with ordinary markdown links. The full session flow,
step by step, is in [docs/how-it-works.md](docs/how-it-works.md).

## Guide

### Install and try

```bash
# iwe: prebuilt binaries at https://github.com/iwe-org/iwe/releases (or brew install iwe-org/iwe/iwe)
git clone https://github.com/asitha-w/cairn && export PATH="$PWD/cairn/bin:$PATH"
export CAIRN_BUNDLE=$PWD/cairn/examples/bundle      # the mock bundle: one org, five pieces of work
crn pending
crn find peering
crn open 431
crn sweep --fixture cairn/examples/github-fixture.json --create
crn graph --open
bash cairn/tests/selftest.sh                         # PASS/FAIL, no network
```

Your own bundle: `crn init ~/my-graph` prints the steps and the Claude Code wiring; `crn doctor` tells
you what is still missing. Then `crn sweep --create` seeds work nodes from your open GitHub issues, and
you write one system node per thing you operate.

### A day

| Moment | You or the agent | What `crn` does |
|---|---|---|
| morning | `crn sweep`, `crn graph --open` | three `gh` searches, `gh_*` fields refreshed, priorities proposed from your words, the viewer rebuilt |
| picking up | `crn find peering` then `crn open 431` | ranked state lines, then one node: header, state, Now, Next, Decisions, Context, Log, backlinks |
| working | `gh`, `kubectl`, editors, under your permissions | nothing; the work is never `crn`'s business |
| a milestone | `crn log 431 "…"`, `crn decide`, `crn state`, `crn stage`, `crn priority` | one guarded, schema-validated write inside the node |
| closing | the SessionEnd hook runs `crn trail` | one Log line per session per node from the transcript, never prompts or output |

### Verbs

`crn --help` lists them, `crn <verb> --help` explains one, every read verb takes `--json`.

| Verb | What it does | Writes |
|---|---|---|
| `crn find <words>` | ranked search over titles, state lines and bodies | no |
| `crn open <node>` | one node with its links; `<node>` is a key, a bare issue number or a slug prefix | no |
| `crn pending` | work whose stage is active, parked or blocked, by priority then stage | no |
| `crn state` / `crn stage` / `crn priority` | set the one-line state, the stage, the priority level (your legend lives in `cairn.toml`) | the node |
| `crn log` / `crn decide` | append a dated line under Log or Decisions | the node |
| `crn sweep [--create]` | refresh `gh_*` fields; list issues without a node, PRs requesting your review, your open PRs; rebuild the viewer | `gh_*`, `.cairn/` |
| `crn trail` | fold new Claude Code transcripts into Log | Log only |
| `crn graph [--open]` | the local viewer, see below; `--format json` or `gexf` for other tools | `.cairn/` only |
| `crn validate` / `crn systems` / `crn init` / `crn doctor` | schema check; systems with their work counts; scaffold a bundle; check the wiring | no / no / a new bundle / no |

Two writers never touch the same field. You own `state`, `stage`, `Now`, `Next`, `Decisions`, `Context`,
`priority`. The producers own `gh_*` and `Log`; the sweep may propose a priority and never overwrites yours.

### The viewer

One HTML file, no dependencies, zero tokens. Group into sub-graphs by repo, system, stage, priority
(labelled with your legend's words) or people. Colour by priority or stage, size by activity. Click a
node for its card and its neighbours; "copy for Claude" gives the one `crn open` line. You are a node
too, ringed: PRs asking your review, your open PRs and work GitHub moved after your last update hang off
it, so "group by people" shows what waits on whom and what waits on you. A list mode and a "what to start
now" mode rank work by transparent rules and print the reason per row.

### A work node

```markdown
---
type: work
title: Peer the dev database cluster to the ops network
state: "parked, waiting on Sam for the tier, the container CIDR and whether users are cluster-scoped"
stage: parked                      # active | parked | blocked | done
resource: https://github.com/acme/platform/issues/431
env: [dev, ops]
systems: [database, network]       # slugs of systems/*.md
people: [sam]                      # slugs of people/*.md
blocked_by: [work/platform-422]
gh_state: open                     # written by crn sweep
gh_updated: 2026-09-17T07:25:00Z   # written by crn sweep
last_actor: me                     # written by crn sweep
updated: 2026-09-18
---
# Peer the dev database cluster to the ops network

Systems: [Database cluster](../systems/database.md) · [Network](../systems/network.md) · waits on [Sam](../people/sam.md)

## Now
One dated paragraph: what is true. The resume point.
## Next
1. Numbered steps.
## Decisions
- 2026-09-17 one line per decision
## Context
- peering plan draft: subnets, NSGs and the order of operations → ../../files/platform-431/peering-plan-2026-09-16.md
## Log
- 2026-09-16 session 8ae135c0: 43 calls · `terraform plan` on the test project
```

The `state` line is what search shows and what you read first: one sentence that lets you decide
whether to open the node. A finding that stays true after the work is done goes on the system node as a
Gotcha; one whose depth is in a file becomes a Context line. Files live outside the bundle, so `iwe`
never indexes them and they never appear in search or in the graph.

### With a coding agent

Everything is a CLI call: no MCP server, no tool schemas per session, and every call lands in the
transcript where `crn trail` can see it. `skills/cairn/SKILL.md` is the Claude Code skill (the five moves
and the rules); `commands/node.md` makes `/node 431` inject the node with zero tool calls. The rule the
design rests on: **anything that changes an environment or code stays with the agent under your
permissions; anything mechanical and read-only belongs in a tool.**

### Layout

```
crn/cli.py       argparse front: one subcommand per verb
crn/bundle.py    find the bundle, read cairn.toml, the iwe wrapper, resolve a node from what you typed
crn/verbs.py     find, open, pending, systems, validate, state, stage, log, decide
crn/github.py    sweep: the only code that talks to GitHub (read-only, via your gh login) or a fixture
crn/trail.py     transcripts → Log
crn/setup.py     init and doctor
crn/graph.py     graph export: json, gexf, and the html viewer (crn/viewer.html)
schemas/         work, system, person (iwe document schemas)
examples/        the mock bundle, its lazy files, a GitHub fixture, a cairn.toml template
skills/, commands/   the Claude Code skill and the /node command
tests/selftest.sh    PASS/FAIL, no network
```

## What Cairn is not

- Not a task tracker. GitHub (or whatever you use) stays the system of record; a node points at it.
- Not agent memory in the chat sense. It holds work, systems and people, not conversation.
- Not a database. For multi-hop queries build an index from `crn graph --format json` with an embedded
  graph database such as [LadybugDB](https://ladybugdb.com/) and throw it away. The markdown stays the truth.

## Status

v0.4: two layers; the CLI with per-verb help and `--json`; `init`, `doctor`, `priority`, `graph` with the
viewer; three schemas; the example bundle; the skill and command; the self-test. Not yet: `crn tidy` (the
periodic weed-out report), a scheduled sweep, converters from other note formats.

MIT.

---

*Cairn is pronounced KAIRN. A cairn is the pile of stones on a hill path that lets you pick the route up again when the fog comes in.*
