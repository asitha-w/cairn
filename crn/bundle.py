"""bundle.py — where the bundle is, what its config says, and the one wrapper around the iwe binary.

Every other module goes through here: find_bundle(), config(), iwe(), nodes(), resolve().
"""
import json, os, subprocess, sys, tomllib
from datetime import datetime, timezone, date
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # the cairn checkout
TODAY = date.today().isoformat()
NOW = datetime.now(timezone.utc)
STAGES = ("active", "parked", "blocked", "done")


class CrnError(SystemExit):
    def __init__(self, msg, rc=2):
        print(f"crn: {msg}", file=sys.stderr); super().__init__(rc)


def die(msg, rc=2): raise CrnError(msg, rc)


def find_bundle():
    """$CAIRN_BUNDLE, else the nearest parent of the cwd that holds cairn.toml."""
    if os.environ.get("CAIRN_BUNDLE"):
        b = Path(os.environ["CAIRN_BUNDLE"]).expanduser().resolve()
        if not (b / "cairn.toml").exists(): die(f"CAIRN_BUNDLE={b} has no cairn.toml")
        return b
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "cairn.toml").exists(): return d
    die("no bundle: set CAIRN_BUNDLE or run inside a directory with cairn.toml (crn init <dir>)")


def config(bundle):
    with open(bundle / "cairn.toml", "rb") as f: return tomllib.load(f)


def iwe(bundle, *args, check=True, inp=None):
    """Run the iwe binary inside the bundle. Dies with iwe's own message on failure."""
    try:
        p = subprocess.run(["iwe", *args], cwd=bundle, capture_output=True, text=True, input=inp)
    except FileNotFoundError:
        die("iwe is not on PATH; see `crn doctor`")
    if check and p.returncode != 0:
        die(f"iwe {' '.join(args[:2])} failed: {(p.stderr or p.stdout).strip()[:400]}", p.returncode)
    return p.stdout


def iwe_json(bundle, *args):
    out = iwe(bundle, *args, "--format", "json")
    return json.loads(out) if out.strip() else []


def nodes(bundle, flt=None):
    args = ["find", "--limit", "0"]
    if flt: args += ["--filter", flt]
    return iwe_json(bundle, *args)


def fm(n):
    """Frontmatter of an iwe find result, whichever shape iwe used."""
    return n.get("frontmatter") or n.get("fm") or {k: v for k, v in n.items() if k not in ("key", "title", "content", "$content")}


def key_of(n): return n.get("key") or n.get("$key")


def resolve(bundle, s):
    """A node from what a person types: full key, bare issue number, owner/repo#n, or a slug prefix."""
    s = s.strip().rstrip("/")
    allk = {key_of(n): n for n in nodes(bundle)}
    if s in allk: return s
    for pre in ("work/", "systems/", "people/"):
        if pre + s in allk: return pre + s
    if s.isdigit() or "#" in s:
        num = s.split("#")[-1]
        hits = [k for k, n in allk.items() if k.startswith("work/") and
                (str(fm(n).get("resource", "")).rstrip("/").endswith("/" + num) or k.endswith("-" + num))]
        if len(hits) == 1: return hits[0]
    hits = [k for k in allk if k.split("/")[-1].startswith(s)]
    if len(hits) == 1: return hits[0]
    if len(hits) > 1: die("ambiguous: " + ", ".join(sorted(hits)[:8]), 1)
    die(f"no node matches '{s}'; try: crn find {s}", 1)


def node_fm(bundle, k):
    return next((fm(n) for n in nodes(bundle) if key_of(n) == k), {})


def out(rows, as_json, render):
    """Print rows as JSON or through render(rows)."""
    if as_json: print(json.dumps(rows, indent=1, ensure_ascii=False))
    else: print(render(rows))
