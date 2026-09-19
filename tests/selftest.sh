#!/usr/bin/env bash
# selftest.sh — does crn work end to end against the example bundle? PASS/FAIL + exit code. No network.
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd); export PATH="$HERE/bin:$HOME/.local/bin:$PATH"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT; cp -r "$HERE/examples/bundle" "$T/b"; export CAIRN_BUNDLE="$T/b"; fail=0
t() { local name=$1; shift; if "$@" >/dev/null 2>&1; then echo "PASS $name"; else echo "FAIL $name"; fail=1; fi; }
t "iwe on PATH"                        command -v iwe
t "crn --version"                      bash -c "crn --version | grep -q '^crn 0'"
t "crn --help lists verbs"             bash -c "crn --help | grep -q sweep"
t "per-verb --help"                    bash -c "crn sweep --help | grep -q fixture"
t "pending --json"                     bash -c "crn pending --json | python3 -c 'import json,sys;assert json.load(sys.stdin)[0][\"key\"]'"
t "find --json"                        bash -c "crn find peering --json | python3 -c 'import json,sys;assert any(r[\"key\"]==\"work/platform-431\" for r in json.load(sys.stdin))'"
t "trail --dry-run runs"               bash -c "crn trail --dry-run | grep -q '^trail:'"
t "init scaffolds a bundle"            bash -c "crn init $T/fresh | grep -q 'bundle ready' && test -f $T/fresh/.hooks/session-end.sh && test -f $T/fresh/.iwe/schemas/work.yaml"
t "doctor runs"                        bash -c "CAIRN_BUNDLE=$T/b crn doctor | grep -q '^RESULT'"
t "bundle validates"                   bash -c "crn validate | grep -qiv 'error\|violation' "
t "find by system alias"               bash -c "crn find peering | grep -q 'work/platform-431'"
t "find by state words"                bash -c "crn find compact | grep -q 'platform-419'"
t "open by number"                     bash -c "crn open 431 | grep -q '^## Now'"
t "open by slug prefix"                bash -c "crn open platform-4 2>&1 | grep -q ambiguous"
t "open shows backlinks"               bash -c "crn open systems/database | grep -q 'linked from'"
t "pending excludes done"              bash -c "crn pending | grep -q platform-431 && ! crn pending | grep -q platform-422"
t "log appends under ## Log"           bash -c "crn log 419 'selftest line' && grep -q 'selftest line' $T/b/work/platform-419.md && grep -q 'updated: $(date +%F)' $T/b/work/platform-419.md"
t "decide appends under ## Decisions"  bash -c "crn decide 431 'selftest decision' && awk '/^## Decisions/,/^## Artifacts/' $T/b/work/platform-431.md | grep -q 'selftest decision'"
t "state sets one sentence"            bash -c "crn state 362 'selftest state' && grep -q 'state: selftest state' $T/b/work/platform-362.md"
t "sweep updates gh fields (fixture)"  bash -c "crn sweep --fixture $HERE/examples/github-fixture.json | grep -q 'updated work/platform-431'"
t "sweep lists issues without a node"  bash -c "crn sweep --fixture $HERE/examples/github-fixture.json | grep -q 'new .*platform#512'"
t "sweep lists review requests and my PRs" bash -c "crn sweep --fixture $HERE/examples/github-fixture.json | grep -q 'review requested from you (1)' && crn sweep --fixture $HERE/examples/github-fixture.json | grep -q 'your open PRs (1)'"
t "sweep --create makes a valid node"  bash -c "crn sweep --fixture $HERE/examples/github-fixture.json --create >/dev/null && test -f $T/b/work/platform-512.md && crn validate | grep -qiv 'error\|violation'"
t "priority legend prints"             bash -c "crn priority | grep -q 'P1  Outage'"
t "priority set by word"               bash -c "crn priority 431 security && grep -q 'priority: 2' $T/b/work/platform-431.md && grep -q 'priority_by: human' $T/b/work/platform-431.md"
t "priority bad word exits 1"          bash -c "! crn priority 431 urgent"
t "pending sorts P1 first"             bash -c "crn priority 419 1 >/dev/null && crn pending | head -1 | grep -q 'P1 .*platform-419'"
t "sweep proposes, never overwrites"   bash -c "crn sweep --fixture $HERE/examples/github-fixture.json --create >/dev/null && grep -q 'priority: 3' $T/b/work/platform-512.md || grep -q 'priority_by: sweep' $T/b/work/platform-512.md; grep -q 'priority: 2' $T/b/work/platform-431.md"
t "unknown node exits 1"               bash -c "! crn open nothing-here-xyz"
t "still valid after writes"           bash -c "crn validate | grep -qiv 'error\|violation'"
[ $fail -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"; exit $fail
