"""graph.py — crn graph: export the bundle as a graph with its dimensions, and a single-file local viewer.

Nodes: every work, system and person node with type, repo (from the resource URL), stage, priority, env, systems,
people, updated, log lines, state. Edges: frontmatter lists (systems, people, blocked_by) plus markdown links in the body
to other nodes. Formats: json, gexf (Gephi / Gephi Lite), html (self-contained viewer, opens from file://).
Writes under <bundle>/.cairn/ by default. Nothing leaves the machine.
"""
import json, re, html, posixpath
from pathlib import Path
from .bundle import iwe, nodes, fm, key_of, die, legend, HERE
from .github import ISSUE_URL

LINK = re.compile(r"\]\(([^)\s]+?\.md)\)")


def build(bundle, cfg, include_done=False):
    allnodes = nodes(bundle)
    keys = {key_of(n) for n in allnodes}
    out_nodes, edges, seen = [], [], set()
    lg = dict(legend(cfg))
    from datetime import date as _date
    stage_of = {key_of(n): fm(n).get("stage") for n in allnodes}
    today = _date.today()
    for n in allnodes:
        k = key_of(n); f = fm(n); t = f.get("type")
        if t not in ("work", "system", "person"): continue
        if t == "work" and f.get("stage") == "done" and not include_done: continue
        body = iwe(bundle, "retrieve", "-k", k, check=False)
        m = ISSUE_URL.search(str(f.get("resource", "")))
        repo = f"{m.group(1)}/{m.group(2)}" if m else ("local" if t == "work" else None)
        logs = sum(1 for ln in body.splitlines() if ln.startswith("- ") and "session" in ln)
        out_nodes.append({"id": k, "type": t, "title": n.get("title") or k.split("/")[-1], "repo": repo, "stage": f.get("stage"),
                          "priority": f.get("priority"), "priority_label": lg.get(f.get("priority")), "env": f.get("env") or [],
                          "systems": f.get("systems") or [], "people": f.get("people") or [], "updated": str(f.get("updated") or "")[:10],
                          "gh_updated": str(f.get("gh_updated") or "")[:10], "state": f.get("state") or f.get("access") or "", "logs": logs,
                          "resource": f.get("resource"), "blocked_by": f.get("blocked_by") or [],
                          "unblocked": bool(f.get("blocked_by")) and all(stage_of.get(b) == "done" for b in f.get("blocked_by") or []),
                          "gh_moved": bool(f.get("gh_updated")) and str(f.get("gh_updated"))[:10] > str(f.get("updated") or "")[:10],
                          "age": (today - _date.fromisoformat(str(f.get("updated"))[:10])).days if f.get("updated") else None})
        def edge(a, b, rel):
            if b in keys and (a, b, rel) not in seen: seen.add((a, b, rel)); edges.append({"s": a, "t": b, "rel": rel})
        for s in f.get("systems") or []: edge(k, f"systems/{s}", "about")
        for p in f.get("people") or []: edge(k, f"people/{p}", "waits_on")
        for b in f.get("blocked_by") or []: edge(k, b, "blocked_by")
        for l in LINK.findall(body):
            tgt = posixpath.normpath(l.lstrip("/")) if l.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(k), l))
            if tgt.startswith(".."): continue            # a link outside the bundle (an artifact) is not a graph edge
            tk = tgt[:-3] if tgt.endswith(".md") else tgt
            if tk in keys and tk != k: edge(k, tk, "links")
    # pull requests from the last sweep, if any: to review, and yours
    sw = bundle / ".cairn" / "sweep.json"; swept_at = None
    if sw.exists():
        d = json.loads(sw.read_text()); swept_at = d.get("at")
        by_res = {str(n.get("resource", "")).rstrip("/"): key_of(n) for n in allnodes if fm(n).get("type") == "work"}
        by_issue = {}   # (repo, number) -> work key, from resource URLs
        for n in allnodes:
            mm = ISSUE_URL.search(str(fm(n).get("resource", "")))
            if mm and fm(n).get("type") == "work": by_issue[(mm.group(2), int(mm.group(3)))] = key_of(n)
        REF = re.compile(r"(?:([A-Za-z0-9_.-]+)#|(?<![\w/])#)(\d+)\b")
        def pr_targets(p):
            out = set()
            wk = by_res.get(p["url"].rstrip("/"))
            if wk: out.add((wk, "is"))
            for repo_tok, num in REF.findall(p["title"]):
                num = int(num)
                if repo_tok:
                    hits = [k for (r, nn), k in by_issue.items() if nn == num and (r == repo_tok or r.endswith(repo_tok) or repo_tok in r)]
                else:
                    hits = [k for (r, nn), k in by_issue.items() if nn == num and r == p["repo"]]
                if len(hits) == 1: out.add((hits[0], "for"))
            return out
        for role, lst in (("review", d.get("prs_review", [])), ("mine", d.get("prs_mine", []))):
            for p in lst:
                pid = f"pr:{p['owner']}/{p['repo']}#{p['number']}"
                out_nodes.append({"id": pid, "type": "pr", "role": role, "title": f"PR #{p['number']} {p['title']}", "repo": f"{p['owner']}/{p['repo']}",
                                  "updated": str(p.get("updated", ""))[:10], "url": p["url"], "state": None, "logs": 0, "env": [], "systems": [], "people": []})
                for wk, rel in pr_targets(p): edges.append({"s": pid, "t": wk, "rel": rel})
    ids = {n["id"] for n in out_nodes}
    RANK = {"blocked_by": 0, "waits_on": 1, "is": 2, "for": 2, "about": 3, "links": 4}
    merged = {}
    for e in edges:
        if e["s"] not in ids or e["t"] not in ids: continue
        m = merged.setdefault((e["s"], e["t"]), {"s": e["s"], "t": e["t"], "rels": []})
        if e["rel"] not in m["rels"]: m["rels"].append(e["rel"])
    edges = []
    for m in merged.values():
        m["rels"].sort(key=lambda r: RANK.get(r, 9)); m["rel"] = m["rels"][0]; edges.append(m)
    return {"nodes": out_nodes, "edges": edges, "legend": lg, "generated_at": __import__("datetime").datetime.now().isoformat(timespec="minutes"), "swept_at": swept_at,
            "counts": {"work": sum(n["type"] == "work" for n in out_nodes), "systems": sum(n["type"] == "system" for n in out_nodes),
                       "people": sum(n["type"] == "person" for n in out_nodes), "prs": sum(n["type"] == "pr" for n in out_nodes), "edges": len(edges)}}


def gexf(g):
    def esc(s): return html.escape(str(s if s is not None else ""), quote=True)
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<gexf xmlns="http://gexf.net/1.3" version="1.3"><graph defaultedgetype="directed">',
         '<attributes class="node">'] + [f'<attribute id="{i}" title="{a}" type="string"/>' for i, a in enumerate(("type", "repo", "stage", "priority", "updated", "state"))] + ['</attributes><nodes>']
    for n in g["nodes"]:
        L.append(f'<node id="{esc(n["id"])}" label="{esc(n["title"])}"><attvalues>' + "".join(f'<attvalue for="{i}" value="{esc(n.get(a))}"/>' for i, a in enumerate(("type", "repo", "stage", "priority", "updated", "state"))) + "</attvalues></node>")
    L.append("</nodes><edges>")
    for i, e in enumerate(g["edges"]): L.append(f'<edge id="{i}" source="{esc(e["s"])}" target="{esc(e["t"])}" label="{esc(e["rel"])}"/>')
    L.append("</edges></graph></gexf>")
    return "\n".join(L)


def render_html(g):
    tpl = (HERE / "crn" / "viewer.html").read_text()
    return tpl.replace("/*GRAPH_JSON*/null", json.dumps(g, ensure_ascii=False))


def graph(bundle, cfg, fmt="html", out=None, include_done=False, open_browser=False):
    g = build(bundle, cfg, include_done)
    outdir = bundle / ".cairn"; outdir.mkdir(exist_ok=True)
    if fmt == "json": text, name = json.dumps(g, indent=1, ensure_ascii=False), "graph.json"
    elif fmt == "gexf": text, name = gexf(g), "graph.gexf"
    elif fmt == "html": text, name = render_html(g), "graph.html"
    else: die("format must be html, json or gexf")
    p = Path(out) if out else outdir / name
    p.write_text(text)
    c = g["counts"]
    print(f"graph: {c['work']} work · {c['systems']} systems · {c['people']} people · {c['prs']} PRs · {c['edges']} edges → {p}")
    if fmt == "html": print(f"open: file://{p.resolve()}")
    if open_browser:
        import webbrowser; webbrowser.open(f"file://{p.resolve()}")
    return 0
