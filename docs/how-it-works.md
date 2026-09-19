# How a session flows through Cairn

Everything that needs judgment stays with you and your agent. Everything mechanical is a `crn` call:
deterministic, read-only toward GitHub, writing only inside your bundle, never calling a model. The
agent's context receives one screen per step instead of a folder of notes.

```mermaid
flowchart LR
    classDef human fill:#1f2937,stroke:#7aa2f7,color:#e6e6e6
    classDef agent fill:#1f2937,stroke:#bb9af7,color:#e6e6e6
    classDef crn fill:#0f2f2a,stroke:#73daca,color:#e6e6e6
    classDef store fill:#2a2415,stroke:#e0af68,color:#e6e6e6
    classDef ext fill:#2a1a1e,stroke:#f7768e,color:#e6e6e6

    U(["you: let us work on peering"]):::human --> A1["agent turns words into a query"]:::agent
    A1 -->|"crn find peering"| C1[["crn: lexical and fuzzy search"]]:::crn
    C1 <--> B[("bundle: work, systems, people")]:::store
    C1 -->|"one screen: nodes and state lines"| A2["agent picks, or asks which"]:::agent
    A2 -->|"crn open 431"| C2[["crn: node and links"]]:::crn
    C2 <--> B
    C2 -->|"about 700 tokens: state, Now, Next, Log"| A3["agent verifies one dated claim"]:::agent
    A3 -->|"gh issue view"| GH[("GitHub")]:::ext
    A3 --> W["work: kubectl, terraform, PRs<br/>under your permissions"]:::agent
    W -->|"crn log, decide, state"| C3[["crn: guarded write"]]:::crn
    C3 --> B
    U2(["you close the session"]):::human -->|"SessionEnd hook"| C4[["crn trail"]]:::crn
    T[("transcripts")]:::ext --> C4
    C4 -->|"one Log line per node"| B
    S(["you: sweep"]):::human -->|"crn sweep"| C5[["crn: three gh searches"]]:::crn
    GH --> C5
    C5 -->|"gh fields, new issues, PRs"| B
    B -->|"crn graph"| V["viewer: graph, list, what to start now"]:::store
```

Legend: blue is you, purple is the agent (judgment, and the only thing that changes environments or
code), teal is `crn` (deterministic), amber is your bundle and the viewer built from it, red is
external sources read but never written.

What Cairn adds to the loop:

| Without Cairn | With Cairn |
|---|---|
| the agent greps notes, reads several files, guesses which thread you mean | one search call returns state lines; the agent picks or asks |
| resuming means re-reading a long note, often stale | one node, one screen, with what was actually run last time |
| what happened in a killed session is lost | the hook writes it into the node's Log from the transcript |
| GitHub state is re-fetched and re-summarised every time | the sweep writes `gh_*` fields once; nodes carry them |
| priorities live in someone's head | a field with your legend; the sweep proposes, you decide |
| the picture is in the agent's context, at token cost | `crn graph` renders it locally for free |

## What it looks like

```
$ crn pending
parked  work/platform-431   2026-09-18  parked, waiting on Sam for the tier, the container CIDR and whether users are cl
active  work/platform-362   2026-09-17  decision taken: renew one year; figures reconciled; purchase is user-run before
active  work/platform-419   2026-09-17  deletes done (5.6B documents); compact per node and the tier downsize remain
blocked work/manifests-894  2026-09-07  two PRs open, changes requested on the manifests one; waiting on my rebase

$ crn find peering
system  systems/network      Network
work    work/platform-431    Peer the dev database cluster to the ops network
        parked · parked, waiting on Sam for the tier, the container CIDR …

$ crn open 431
work/platform-431 · parked · updated 2026-09-18 · gh open 2026-09-18 last sam
state: parked, waiting on Sam for the tier, the container CIDR and whether users are cluster-scoped
env dev, ops · systems database, network · people sam · blocked_by work/platform-422
… the node's Now, Next, Decisions, Artifacts, Log …
linked from (2): work/platform-422 · systems/network

$ crn log 419 "compact pass A done on node 1"
$ crn sweep
sweep: 5 items · 1 node(s) updated · 1 without a node
  updated work/platform-431: gh_state=open gh_updated=2026-09-18
  new     acme/platform#512 Alert on backup freshness for the object store
```
