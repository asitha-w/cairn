"""tidy.py — crn tidy: the periodic weed-out report. Read-only; it names what has outgrown its shape and what to do.

Checks: oversized nodes, long Logs, dangling or placeholder Context lines, work without systems, untriaged
stubs, stage that disagrees with GitHub, quiet active or parked work, orphan systems, unused people.
Thresholds come from cairn.toml [tidy]; every one has a default. Judgment (what to drop, where to split)
stays with the person; tidy only points.
"""
import re, posixpath
from datetime import date
from .bundle import nodes, fm, key_of, out, TODAY

DEFAULTS = {"max_tokens": 1000, "max_log": 15, "quiet_active_days": 30, "parked_days": 90, "untriaged_days": 14, "placeholders": []}
ADVICE = {
    "oversized":   "over the token budget: crn roll <node> for the Log, rewrite Now as one dated paragraph, or split the work",
    "long_log":    "Log past its budget (five for active and blocked, one for parked and done): crn roll <node>",
    "dangling":    "Context or Runbooks line whose file is missing: fix the path or drop the line",
    "placeholder": "Context line without a real finding: write the sentence, or drop the line",
    "no_systems":  "work node with no system: add the systems it touches",
    "untriaged":   "sweep stub still untriaged: write a state sentence, or mark it done if it is not yours",
    "gh_closed":   "GitHub says closed or merged, the node does not: crn stage <node> done",
    "quiet":       "active but silent for a while: still active, or parked",
    "long_parked": "parked for a long time: still worth keeping, or done",
    "orphan_system": "system with no work and no gotchas: merge into its owner or delete",
    "unused_person": "person no work waits on: delete, or link the work",
}


def _days(s):
    try: return (date.today() - date.fromisoformat(str(s)[:10])).days
    except Exception: return None


def _section(body, name):
    m = re.search(rf"^## {name}\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return [l for l in (m.group(1).splitlines() if m else []) if l.startswith("- ")]


def tidy(bundle, cfg, as_json=False, show_all=False):
    t = {**DEFAULTS, **(cfg.get("tidy") or {})}
    allnodes = nodes(bundle)
    work = [n for n in allnodes if fm(n).get("type") == "work"]
    systems = [n for n in allnodes if fm(n).get("type") == "system"]
    people = [n for n in allnodes if fm(n).get("type") == "person"]
    F = {k: [] for k in ADVICE}
    used_systems, used_people = set(), set()
    for n in work:
        k, f = key_of(n), fm(n)
        p = bundle / f"{k}.md"
        body = p.read_text() if p.exists() else ""
        toks = len(body) // 4
        logs = _section(body, "Log")
        if toks > t["max_tokens"]: F["oversized"].append((k, f"~{toks} tokens · {len(logs)} Log lines"))
        log_limit = 1 if f.get("stage") in ("parked", "done") else t["max_log"]
        if len(logs) > log_limit: F["long_log"].append((k, f"{len(logs)} Log lines · {f.get('stage')} keeps {log_limit}"))
        for l in _section(body, "Context"):
            if " → " not in l: F["placeholder"].append((k, l[2:60])); continue
            sent, path = l[2:].rsplit(" → ", 1)
            if any(ph.lower() in sent.lower() for ph in t["placeholders"]) or len(sent) < 25: F["placeholder"].append((k, sent[:60]))
            if not re.match(r"https?://", path):
                tgt = (bundle / posixpath.dirname(k) / path.strip())
                if not tgt.exists(): F["dangling"].append((k, path.strip()))
        used_systems.update(f.get("systems") or []); used_people.update(f.get("people") or [])
        if not f.get("systems"): F["no_systems"].append((k, str(f.get("title", ""))[:60]))
        age = _days(f.get("updated"))
        if str(f.get("state", "")).startswith("new from sweep") and age is not None and age > t["untriaged_days"]: F["untriaged"].append((k, f"{age}d"))
        if f.get("gh_state") in ("closed", "merged") and f.get("stage") != "done": F["gh_closed"].append((k, f"gh {f['gh_state']} · stage {f.get('stage')}"))
        if f.get("stage") == "active" and age is not None and age > t["quiet_active_days"]: F["quiet"].append((k, f"{age}d since updated"))
        if f.get("stage") == "parked" and age is not None and age > t["parked_days"]: F["long_parked"].append((k, f"{age}d parked"))
    for n in systems:
        k, f = key_of(n), fm(n); slug = k.split("/")[-1]
        p = bundle / f"{k}.md"; body = p.read_text() if p.exists() else ""
        for l in _section(body, "Context") + _section(body, "Runbooks"):
            if " → " in l:
                path = l.rsplit(" → ", 1)[1].strip()
                if not re.match(r"https?://", path) and not (bundle / "systems" / path).exists(): F["dangling"].append((k, path))
        if slug not in used_systems and not _section(body, "Gotchas"): F["orphan_system"].append((k, "no work, no gotchas"))
    for n in people:
        if key_of(n).split("/")[-1] not in used_people: F["unused_person"].append((key_of(n), "nothing waits on them"))
    total = sum(len(v) for v in F.values())
    if as_json:
        out({"date": TODAY, "thresholds": t, "findings": {k: [{"node": a, "detail": b} for a, b in v] for k, v in F.items() if v}, "total": total}, True, None); return 0
    print(f"tidy {TODAY}: {total} finding(s) over {len(work)} work · {len(systems)} systems · {len(people)} people" + ("" if total else " · nothing to weed"))
    for k, v in F.items():
        if not v: continue
        print(f"\n{k} ({len(v)}) — {ADVICE[k]}")
        for a, b in (v if show_all else v[:8]): print(f"  {a:40s} {b}")
        if not show_all and len(v) > 8: print(f"  … {len(v) - 8} more (--all)")
    return 0
