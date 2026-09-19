"""trail.py — crn trail: fold Claude Code transcripts into the nodes' ## Log, one line per session per node.

Reads ~/.claude/projects/<prefix>*/*.jsonl (prefix from cairn.toml [trail]). A tool call belongs to a node when
its input names the node's key, slug, issue ref or issue number. Keeps: date, session id, call count, up to
three command heads. Never keeps tool output, prompts or file contents. Idempotent via .cairn/trail-state.json.
"""
import json, os, re
from pathlib import Path
from .bundle import iwe, nodes, fm, key_of, die, TODAY
from .github import ISSUE_URL


def patterns(work):
    pats = {}
    for k, f in work.items():
        m = ISSUE_URL.search(str(f.get("resource", "")))
        rx = [re.escape(k), re.escape(k.split("/")[-1])]
        if m:
            rx += [re.escape(f"{m.group(2)}#{m.group(3)}"), re.escape(f"{m.group(1)}/{m.group(2)}#{m.group(3)}"), rf"/{m.group(3)}\b"]
        pats[k] = re.compile("|".join(rx))
    return pats


def scan(path, pats):
    """{node_key: [command heads]} plus the session's first timestamp."""
    per, first = {}, None
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "assistant": continue
        first = first or d.get("timestamp")
        for c in (d.get("message") or {}).get("content", []) or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"): continue
            inp = c.get("input", {}); text = json.dumps(inp)[:3000]
            head = (inp.get("command") or inp.get("file_path") or c.get("name")) if isinstance(inp, dict) else c.get("name")
            head = re.sub(r"\s+", " ", str(head)).split("<<")[0][:90]
            for k, rx in pats.items():
                if rx.search(text): per.setdefault(k, []).append(head)
    return per, first


def trail(bundle, cfg, dry_run=False):
    tr = cfg.get("trail", {}); root = Path(os.path.expanduser(tr.get("transcripts", "~/.claude/projects"))); prefix = tr.get("prefix", "")
    if not prefix: die("cairn.toml needs [trail] prefix (the encoded project dir, e.g. -home-me-work-repo)")
    if not root.exists(): print(f"trail: {root} does not exist; nothing to fold"); return 0
    state_p = bundle / ".cairn" / "trail-state.json"
    state = json.loads(state_p.read_text()) if state_p.exists() else {"done": {}}
    logged = state["done"].setdefault("__logged__", {})
    work = {key_of(n): fm(n) for n in nodes(bundle, "type: work")}
    pats = patterns(work)
    files = [p for d in root.iterdir() if d.is_dir() and d.name.startswith(prefix) for p in d.glob("*.jsonl")]
    added = 0
    for p in sorted(files, key=lambda p: p.stat().st_mtime):
        sig = f"{p.stat().st_size}:{int(p.stat().st_mtime)}"
        if state["done"].get(p.stem) == sig: continue
        per, first = scan(p, pats)
        for k, heads in per.items():
            if k in logged.get(p.stem, []): continue
            uniq = list(dict.fromkeys(heads))[-3:]
            line = f"- {(first or '')[:10] or TODAY} session {p.stem[:8]}: {len(heads)} call(s) · " + " · ".join(f"`{h}`" for h in uniq)
            if dry_run: print(f"{k}: {line}")
            else:
                iwe(bundle, "update", "-k", k, "--expect", "1", "--append", json.dumps({"$header": "Log", "content": line}))
                logged.setdefault(p.stem, []).append(k)
            added += 1
        if not dry_run: state["done"][p.stem] = sig
    if not dry_run:
        state_p.parent.mkdir(exist_ok=True); state_p.write_text(json.dumps(state, indent=1))
    print(f"trail: {len(files)} transcript(s) scanned · {added} log line(s) {'would be ' if dry_run else ''}added"); return 0
