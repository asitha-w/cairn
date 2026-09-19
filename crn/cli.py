"""cli.py — argparse front: one subcommand per verb, each with its own --help. `crn <verb> --help` for details."""
import argparse, sys
from . import __version__
from .bundle import find_bundle, config, CrnError

EPILOG = """examples:
  crn find peering                 ranked search over titles, state lines and bodies
  crn open 431                     one node by issue number (also a key or a slug prefix)
  crn pending                      work whose stage is active, parked or blocked
  crn log 419 "compact pass A done on node 1"
  crn priority                     the bundle's priority legend; crn priority 419 2 sets one
  crn sweep --create               refresh gh_* fields; create nodes for assigned issues that have none
  crn doctor                       what is missing on this machine

The bundle is $CAIRN_BUNDLE, else the nearest parent of the cwd with cairn.toml.
crn never calls a model, writes only inside the bundle, and reads GitHub read-only through your own gh login."""


def build():
    p = argparse.ArgumentParser(prog="crn", description="Cairn: your work as a graph of markdown nodes. iwe does the graph; crn adds the work verbs.",
                                epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"crn {__version__}")
    sp = p.add_subparsers(dest="verb", metavar="<verb>")

    def add(name, help_, **kw):
        s = sp.add_parser(name, help=help_, description=help_, formatter_class=argparse.RawDescriptionHelpFormatter, **kw); return s

    s = add("init", "Scaffold a new bundle: iwe --okf, the Cairn schemas, cairn.toml, the session-end hook. Prints the wiring steps.")
    s.add_argument("dir", help="directory to create (your graph; make it a private git repo)")

    s = add("doctor", "Check this machine: python, iwe, crn, gh auth, CAIRN_BUNDLE, cairn.toml fields, schema validity, hook, skill, command. PASS/FAIL.")

    s = add("find", "Ranked search over nodes: BM25 on title and body fused with fuzzy title/key match. Work nodes show stage and state.")
    s.add_argument("words", nargs="+"); s.add_argument("--json", action="store_true"); s.add_argument("--limit", type=int, default=12)

    s = add("open", "One node with its links. <node> is a key (work/platform-431), a bare issue number (431), owner/repo#n, or a slug prefix.")
    s.add_argument("node"); s.add_argument("--json", action="store_true")

    s = add("pending", "Work nodes whose stage is active, parked or blocked: by priority (1 first, unset last), then stage, then most recently updated.")
    s.add_argument("--json", action="store_true"); s.add_argument("--stage", choices=["active", "parked", "blocked", "done"], help="only this stage")

    s = add("systems", "System nodes with how many work nodes point at each, and their access line.")
    s.add_argument("--json", action="store_true")

    s = add("validate", "iwe schema validate over the whole bundle. Exit 1 on any violation.")

    s = add("state", "Set the one-line state of a work node: what is true right now, in one sentence. Stamps updated.")
    s.add_argument("node"); s.add_argument("text", nargs="+")

    s = add("stage", "Move a work node between active, parked, blocked and done.")
    s.add_argument("node"); s.add_argument("value", choices=["active", "parked", "blocked", "done"])

    s = add("priority", "Priorities as the bundle defines them (cairn.toml [priority].levels, 1 highest). No node: print the legend. Node only: legend plus the node's level. Node and value: set it (a number or a word from the legend).")
    s.add_argument("node", nargs="?"); s.add_argument("value", nargs="?")

    s = add("log", "Append a dated line under ## Log. Use it when a milestone lands.")
    s.add_argument("node"); s.add_argument("text", nargs="+")

    s = add("decide", "Append a dated line under ## Decisions. One line per decision, with the reason.")
    s.add_argument("node"); s.add_argument("text", nargs="+")

    s = add("sweep", "Read GitHub (or a fixture): refresh gh_state/gh_updated/last_actor on work nodes; list assigned issues with no node, PRs requesting your review, your open PRs.")
    s.add_argument("--fixture", metavar="FILE", help="JSON standing in for GitHub; see examples/github-fixture.json")
    s.add_argument("--create", action="store_true", help="create a stub work node for each assigned issue that has none")
    s.add_argument("--json", action="store_true")

    s = add("trail", "Fold new Claude Code transcripts into ## Log: one line per session per node it touched. Idempotent; run by the session-end hook.")
    s.add_argument("--dry-run", action="store_true", help="print the lines instead of writing them")
    return p


def main(argv=None):
    p = build(); a = p.parse_args(argv)
    if not a.verb: p.print_help(); return 2
    try:
        if a.verb == "init":
            from .setup import init; return init(a.dir)
        if a.verb == "doctor":
            from .setup import doctor; return doctor()
        bundle = find_bundle(); cfg = config(bundle)
        from . import verbs
        if a.verb == "find": return verbs.find(bundle, a.words, a.json, a.limit)
        if a.verb == "open": return verbs.open_node(bundle, a.node, a.json)
        if a.verb == "pending": return verbs.pending(bundle, a.json, a.stage)
        if a.verb == "systems": return verbs.systems(bundle, a.json)
        if a.verb == "validate": return verbs.validate(bundle)
        if a.verb == "state": return verbs.state(bundle, a.node, " ".join(a.text))
        if a.verb == "stage": return verbs.stage(bundle, a.node, a.value)
        if a.verb == "priority": return verbs.priority(bundle, cfg, a.node, a.value)
        if a.verb == "log": return verbs.log(bundle, a.node, " ".join(a.text))
        if a.verb == "decide": return verbs.decide(bundle, a.node, " ".join(a.text))
        if a.verb == "sweep":
            from .github import sweep; return sweep(bundle, cfg, a.fixture, a.create, a.json)
        if a.verb == "trail":
            from .trail import trail; return trail(bundle, cfg, a.dry_run)
    except CrnError as e:
        return e.code
    p.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
