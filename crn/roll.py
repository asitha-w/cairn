"""roll.py — crn roll: move a work node's older Log lines into a file outside the bundle and leave one Context line.

The Log is the only part of a node that grows by itself. Rolling keeps the last sessions inline (five for
active and blocked work, one for parked and done: a parked node only needs to say when it was last touched)
and parks the rest under the files directory (cairn.toml [files].dir, relative to the bundle root), one
file per node, appended on every roll. The node keeps a single Context line pointing at it.
"""
import re
from pathlib import Path
from .bundle import resolve, node_fm, die, iwe

LOG_DATE = re.compile(r"^- (\d{4}-\d{2}-\d{2})")


KEEP = {"active": 5, "blocked": 5, "parked": 1, "done": 1}


def keep_for(stage): return KEEP.get(stage, 5)


def roll(bundle, cfg, subject, keep=None):
    k = resolve(bundle, subject)
    f = node_fm(bundle, k)
    if f.get("type") != "work": die(f"{k} is not a work node")
    if keep is None: keep = keep_for(f.get("stage"))
    p = bundle / f"{k}.md"; s = p.read_text()
    m = re.search(r"^## Log\n(.*?)(?=^## |\Z)", s, re.S | re.M)
    if not m: die(f"{k} has no ## Log section")
    lines = [l for l in m.group(1).splitlines() if l.startswith("- ")]
    if len(lines) <= keep: print(f"{k}: {len(lines)} Log line(s), nothing to roll (keep {keep})"); return 0
    old, kept = lines[:-keep], lines[-keep:]
    files_dir = (cfg.get("files") or {}).get("dir") or "../files"
    slug = k.split("/", 1)[1]
    target = (bundle / files_dir / slug / "log.md").resolve()
    title = node_fm(bundle, k).get("title") or k
    header = f"# {title}: Log archive\n\nRolled out of {k} by crn roll. Newest at the bottom.\n\n"
    archive_text = (target.read_text().rstrip("\n") + "\n" if target.exists() else header) + "\n".join(old) + "\n"
    # the Context line: relative to the node's folder, one per archive file
    rel = Path(*([".."] * len(Path(k).parts[:-1]))) / files_dir / slug / "log.md"
    rel = str(rel).replace("\\", "/")
    archived = [l for l in archive_text.splitlines() if LOG_DATE.match(l)]
    dates = sorted(LOG_DATE.match(l).group(1) for l in archived)
    sentence = f"earlier Log, {len(archived)} session line(s) {dates[0]} to {dates[-1]}"
    ctx_line = f"- {sentence} → {rel}"
    s = s[:m.start()] + "## Log\n\n" + "\n".join(kept) + "\n" + s[m.end():]
    cm = re.search(r"^## Context\n(.*?)(?=^## |\Z)", s, re.S | re.M)
    if cm and rel in cm.group(1):
        s = s[:cm.start()] + re.sub(rf"^- [^\n]*→ {re.escape(rel)}[ \t]*$", ctx_line, cm.group(0), flags=re.M) + s[cm.end():]
    elif cm:
        body = cm.group(1).rstrip("\n"); body = (body + "\n" if body.strip() else "\n") + ctx_line + "\n"
        s = s[:cm.start()] + "## Context\n" + (body if body.startswith("\n") else "\n" + body) + ("\n" if cm.end() < len(s) else "") + s[cm.end():]
    else:
        s = s[:m.start()] + "## Context\n\n" + ctx_line + "\n\n" + s[m.start():]
    s = re.sub(r"\n{3,}", "\n\n", s)
    backup = p.read_text(); p.write_text(s)
    v = iwe(bundle, "schema", "validate", check=False)
    if "›" in v and k in v: p.write_text(backup); die(f"{k}: roll would break the schema, reverted:\n{v}")
    target.parent.mkdir(parents=True, exist_ok=True); target.write_text(archive_text)
    print(f"{k}: rolled {len(old)} Log line(s) → {rel} · kept {len(kept)} · {sentence}"); return 0
