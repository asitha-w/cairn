"""verbs.py — the read and write verbs over nodes: find, open, pending, priority, systems, validate, state, stage, log, decide.

Reads print one screen (or --json). Writes are guarded iwe updates on exactly one node and stamp `updated`.
"""
import json
from .bundle import iwe, iwe_json, nodes, fm, key_of, resolve, node_fm, out, die, TODAY, STAGES, legend


def short(s, n): s = s or ""; return s if len(s) <= n else s[: n - 1] + "…"


# ---------------------------------------------------------------- reads
def find(bundle, words, as_json=False, limit=12):
    q = " ".join(words)
    rows = iwe_json(bundle, "find", "--lexical", q, "--fuzzy", q, "--limit", str(limit))
    hits = [{"key": key_of(n), "type": fm(n).get("type", "?"), "title": n.get("title", ""), "stage": fm(n).get("stage"), "state": fm(n).get("state")} for n in rows]
    # iwe indexes bodies, not frontmatter: a system whose aliases name the query is a hit too, first
    ql = [w.lower() for w in words]
    for n in nodes(bundle, "type: system"):
        al = [str(a).lower() for a in (fm(n).get("aliases") or [])] + [str(n.get("title", "")).lower(), key_of(n).split("/")[-1]]
        if any(w == a or (len(w) > 3 and (w in a or a in w)) for w in ql for a in al) and key_of(n) not in {h["key"] for h in hits}:
            hits.insert(0, {"key": key_of(n), "type": "system", "title": n.get("title", ""), "stage": None, "state": fm(n).get("access")})
    if not hits:
        print("no matches" if not as_json else "[]"); return 1
    def render(hs):
        L = []
        for h in hs:
            line = f"{h['type']:7s} {h['key']:34s} {short(h['title'], 60)}"
            if h["type"] == "work": line += f"\n        {h['stage'] or ''} · {short(str(h['state'] or ''), 90)}"
            L.append(line)
        return "\n".join(L)
    out(hits, as_json, render); return 0


def open_node(bundle, subject, as_json=False):
    k = resolve(bundle, subject)
    f = node_fm(bundle, k)
    body = iwe(bundle, "retrieve", "-k", k).rstrip()
    back = [b for b in iwe(bundle, "find", "--references", k, "--format", "keys").split() if b != k]
    if as_json:
        print(json.dumps({"key": k, "frontmatter": f, "body": body, "linked_from": back}, indent=1, ensure_ascii=False)); return 0
    if f.get("type") == "work":
        print(f"{k} · {f.get('stage')} · updated {str(f.get('updated', ''))[:10]} · gh {f.get('gh_state', '?')} {str(f.get('gh_updated', ''))[:10]} last {f.get('last_actor', '?')}")
        print(f"state: {f.get('state')}")
        meta = [f"{x} {', '.join(f[x])}" for x in ("env", "systems", "people", "blocked_by") if f.get(x)]
        if meta: print(" · ".join(meta))
        print()
    print(body)
    if back: print(f"\nlinked from ({len(back)}): " + " · ".join(back[:12]))
    return 0


STAGE_ORDER = {"active": 0, "blocked": 1, "parked": 2, "done": 3}


def pending(bundle, as_json=False, stage=None):
    want = (stage,) if stage else ("active", "parked", "blocked")
    rows = [n for n in nodes(bundle, "type: work") if fm(n).get("stage") in want]
    rows.sort(key=lambda n: str(fm(n).get("updated", "")), reverse=True)
    rows.sort(key=lambda n: (int(fm(n).get("priority") or 9), STAGE_ORDER.get(fm(n).get("stage"), 9)))   # stable: priority, stage, then newest
    hits = [{"key": key_of(n), "priority": fm(n).get("priority"), "stage": fm(n).get("stage"), "updated": str(fm(n).get("updated", ""))[:10],
             "state": fm(n).get("state"), "title": n.get("title")} for n in rows]
    if not hits: print("nothing pending" if not as_json else "[]"); return 0
    def pr(h): return f"P{h['priority']}" if h["priority"] else "  "
    out(hits, as_json, lambda hs: "\n".join(f"{pr(h)} {h['stage']:7s} {h['key']:34s} {h['updated']}  {short(str(h['state'] or ''), 76)}" for h in hs)); return 0


def priority(bundle, cfg, subject=None, value=None):
    """No node: print the legend. Node only: legend plus the node's current level. Node and value (number or legend word): set it."""
    lg = legend(cfg)
    if not lg: die("this bundle defines no priorities; add [priority].levels = [\"…\", …] to cairn.toml (1 is highest)")
    k = resolve(bundle, subject) if subject else None
    if value is None:
        cur = node_fm(bundle, k).get("priority") if k else None
        print(f"{len(lg)} levels" + (f" · {k} is P{cur}" if k and cur else f" · {k} has none" if k else ""))
        for i, l in lg: print(f"  P{i}  {l}")
        if k: print(f"set: crn priority {subject} <1-{len(lg)}>")
        return 0
    if value.isdigit() and 1 <= int(value) <= len(lg): lvl = int(value)
    else:
        hits = [i for i, l in lg if value.lower() in l.lower()]
        if len(hits) != 1: die(f"'{value}' does not name one level; use 1-{len(lg)} or a word from the legend (crn priority)")
        lvl = hits[0]
    iwe(bundle, "update", "-k", k, "--expect", "1", "--set", f"priority={lvl}", "--set", "priority_by=human", "--set", f"updated={TODAY}")
    print(f"{k}: P{lvl} {dict(lg)[lvl]}"); return 0


def systems(bundle, as_json=False):
    sysn = nodes(bundle, "type: system"); work = nodes(bundle, "type: work")
    hits = []
    for s in sorted(sysn, key=key_of):
        slug = key_of(s).split("/")[-1]
        hits.append({"key": key_of(s), "title": s.get("title", ""), "access": fm(s).get("access", ""),
                     "work": sum(1 for w in work if slug in (fm(w).get("systems") or []))})
    out(hits, as_json, lambda hs: "\n".join(f"{h['work']:3d} {h['key']:30s} {short(h['title'], 40):40s} {short(h['access'], 60)}" for h in hs)); return 0


def validate(bundle):
    v = iwe(bundle, "schema", "validate", check=False).rstrip()
    print(v or "valid"); return 1 if "›" in v else 0


# ---------------------------------------------------------------- writes
def _append(bundle, k, header, text):
    iwe(bundle, "update", "-k", k, "--expect", "1", "--set", f"updated={TODAY}",
        "--append", json.dumps({"$header": header, "content": f"- {TODAY} {text}"}))


def state(bundle, subject, text):
    k = resolve(bundle, subject)
    if len(text) < 3: die("state needs a sentence")
    iwe(bundle, "update", "-k", k, "--expect", "1", "--set", f"state={json.dumps(text, ensure_ascii=False)}", "--set", f"updated={TODAY}")
    print(f"{k}: state set"); return 0


def stage(bundle, subject, value):
    if value not in STAGES: die(f"stage must be one of {', '.join(STAGES)}")
    k = resolve(bundle, subject)
    iwe(bundle, "update", "-k", k, "--expect", "1", "--set", f"stage={value}", "--set", f"updated={TODAY}")
    print(f"{k}: stage {value}"); return 0


def log(bundle, subject, text):
    k = resolve(bundle, subject); _append(bundle, k, "Log", text); print(f"{k}: logged"); return 0


def decide(bundle, subject, text):
    k = resolve(bundle, subject); _append(bundle, k, "Decisions", text); print(f"{k}: decision recorded"); return 0
