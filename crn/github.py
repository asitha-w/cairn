"""github.py — crn sweep: the only place that talks to GitHub, read-only, through the user's own `gh` login.

Three searches: issues assigned to the user, PRs requesting the user's review, PRs the user authored.
Writes only gh_state, gh_updated and last_actor on existing work nodes; creates stub nodes only with --create.
A fixture file (see examples/github-fixture.json) stands in for GitHub in tests.
"""
import json, re, subprocess
from pathlib import Path
from .bundle import iwe, nodes, fm, key_of, die, TODAY, NOW, propose_priority, legend

ISSUE_URL = re.compile(r"github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)")
FIELDS = "repository,number,title,state,updatedAt,url,labels"


def _search(kind, *flags):
    try:
        p = subprocess.run(["gh", "search", kind, *flags, "--json", FIELDS, "--limit", "200"], capture_output=True, text=True)
    except FileNotFoundError:
        die("gh is not on PATH; see `crn doctor`")
    if p.returncode != 0: die(f"gh search {kind} failed: " + p.stderr.strip()[:200])
    rows = []
    for i in json.loads(p.stdout):
        owner, repo = i["repository"]["nameWithOwner"].split("/")
        rows.append({"owner": owner, "repo": repo, "number": i["number"], "title": i["title"], "state": i["state"].lower(),
                     "updated": i["updatedAt"], "last_actor": None, "url": i["url"], "labels": [l["name"] for l in i.get("labels") or []]})
    return rows


def fetch(cfg, fixture=None):
    """(issues {(owner, repo, n): item}, prs_review [items], prs_mine [items])."""
    if fixture:
        d = json.loads(Path(fixture).read_text())
        return {(i["owner"], i["repo"], int(i["number"])): i for i in d["items"]}, d.get("prs_review", []), d.get("prs_mine", [])
    gh = cfg.get("github", {}); org, user = gh.get("org"), gh.get("user")
    if not (org and user): die("cairn.toml needs [github] org and user for a live sweep (or use --fixture)")
    issues = {(i["owner"], i["repo"], int(i["number"])): i for i in _search("issues", "--owner", org, "--assignee", user, "--state", "open")}
    return issues, _search("prs", "--owner", org, "--review-requested", user, "--state", "open"), _search("prs", "--owner", org, "--author", user, "--state", "open")


def stub(it, prio=None):
    pr = f"priority: {prio}\npriority_by: sweep\n" if prio else ""
    return (f"---\ntype: work\ntitle: {json.dumps(it['title'], ensure_ascii=False)}\nstate: \"new from sweep, not yet triaged\"\nstage: active\n{pr}"
            f"resource: {it['url']}\nenv: []\nsystems: []\npeople: []\nblocked_by: []\ngh_state: {it['state']}\ngh_updated: {json.dumps(it['updated'])}\n"
            f"generated: {{ by: \"crn/sweep\", at: \"{NOW.isoformat(timespec='seconds')}\" }}\nupdated: {TODAY}\n---\n# {it['title']}\n\n"
            f"## Now\n\nCreated by `crn sweep` on {TODAY}; state not yet written.\n\n## Next\n\n1. Triage.\n\n## Decisions\n\n## Context\n\n## Log\n\n- {TODAY} created by sweep\n")


def sweep(bundle, cfg, fixture=None, create=False, as_json=False):
    issues, prs_review, prs_mine = fetch(cfg, fixture)
    work = nodes(bundle, "type: work"); seen, changed, created = set(), [], []
    for n in work:
        f = fm(n); m = ISSUE_URL.search(str(f.get("resource", "")))
        if not m: continue
        ident = (m.group(1), m.group(2), int(m.group(3))); seen.add(ident)
        it = issues.get(ident)
        if not it: continue
        sets = []
        if f.get("gh_state") != it["state"]: sets += ["--set", f"gh_state={it['state']}"]
        if str(f.get("gh_updated", ""))[:19] != str(it["updated"])[:19]: sets += ["--set", f"gh_updated={json.dumps(it['updated'])}"]
        if it.get("last_actor") and f.get("last_actor") != it["last_actor"]: sets += ["--set", f"last_actor={it['last_actor']}"]
        if not f.get("priority") and legend(cfg):
            pr = propose_priority(cfg, it["title"] + " " + " ".join(it.get("labels") or []))
            if pr: sets += ["--set", f"priority={pr}", "--set", "priority_by=sweep"]; it["proposed_priority"] = pr
        if sets:
            iwe(bundle, "update", "-k", key_of(n), "--expect", "1", *sets); changed.append({"key": key_of(n), **it})
    new = [it for ident, it in issues.items() if ident not in seen]
    if create:
        for it in new:
            pr = propose_priority(cfg, it["title"] + " " + " ".join(it.get("labels") or [])) if legend(cfg) else None
            k = f"work/{it['repo']}-{it['number']}"; iwe(bundle, "create", k, "-c", "-", inp=stub(it, pr)); created.append(k)
    noded = {str(fm(n).get("resource", "")).rstrip("/") for n in work}
    for p in prs_mine: p["has_node"] = p["url"].rstrip("/") in noded
    result = {"items": len(issues), "changed": changed, "new": new, "created": created,
              "prs_review": sorted(prs_review, key=lambda p: p["updated"], reverse=True),
              "prs_mine": sorted(prs_mine, key=lambda p: p["updated"], reverse=True)}
    (bundle / ".cairn").mkdir(exist_ok=True)
    (bundle / ".cairn" / "sweep.json").write_text(json.dumps({"at": NOW.isoformat(timespec="seconds"), **result}, ensure_ascii=False))
    from .graph import graph as _graph
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): _graph(bundle, cfg, "html")   # the picture follows the sweep
    result["graph"] = str(bundle / ".cairn" / "graph.html")
    if as_json: print(json.dumps(result, indent=1, ensure_ascii=False)); return 0
    print(f"sweep: {result['items']} items · {len(changed)} node(s) updated · {len(new)} without a node")
    for c in changed: print(f"  updated {c['key']}: gh_state={c['state']} gh_updated={str(c['updated'])[:10]}" + (f" priority P{c['proposed_priority']} (proposed)" if c.get("proposed_priority") else ""))
    for it in new: print(f"  new     {it['owner']}/{it['repo']}#{it['number']} {it['title'][:70]}")
    for k in created: print(f"          created {k}")
    if prs_review:
        print(f"review requested from you ({len(prs_review)}):")
        for p in result["prs_review"]: print(f"  {p['owner']}/{p['repo']}#{p['number']} {p['title'][:70]} · {str(p['updated'])[:10]}")
    if prs_mine:
        print(f"your open PRs ({len(prs_mine)}):")
        for p in result["prs_mine"]: print(f"  {p['owner']}/{p['repo']}#{p['number']} {p['title'][:70]} · {str(p['updated'])[:10]}{' · has node' if p['has_node'] else ''}")
    print(f"graph refreshed: {result['graph']}")
    return 0
