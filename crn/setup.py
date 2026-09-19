"""setup.py — crn init and crn doctor: make a bundle, and say what is missing on this machine.

init writes: .iwe/ (via iwe init --okf), the three Cairn schemas and their bindings, cairn.toml, .cairn/,
.hooks/session-end.sh, .gitignore. Then it prints the four lines that wire Claude Code to the bundle.
doctor checks: python, iwe, gh auth, CAIRN_BUNDLE, cairn.toml fields, schema validity, hook, skill, command.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path
from .bundle import HERE, iwe, die

HOOK = """#!/usr/bin/env bash
# SessionEnd / PreCompact hook: fold the session that just ended into the nodes' ## Log. No GitHub, no model, no state edits.
export PATH="$HOME/.local/bin:$PATH" CAIRN_BUNDLE="{bundle}"
crn trail >/dev/null 2>&1 || true
exit 0
"""


def init(target):
    d = Path(target).expanduser().resolve(); d.mkdir(parents=True, exist_ok=True)
    if (d / "cairn.toml").exists(): die(f"{d} already has cairn.toml")
    try:
        subprocess.run(["iwe", "init", "--okf", "--auto"], cwd=d, check=True, capture_output=True)
    except FileNotFoundError:
        die("iwe is not on PATH; install it first (https://github.com/iwe-org/iwe/releases) then rerun")
    sd = d / ".iwe" / "schemas"
    for s in ("work", "system", "person", "record"): shutil.copy(HERE / "schemas" / f"{s}.yaml", sd / f"{s}.yaml")
    cfg = d / ".iwe" / "config.toml"
    cfg.write_text(cfg.read_text() + '\n[schemas.work]\nmatch = "work/**"\n\n[schemas.system]\nmatch = "systems/**"\n\n[schemas.person]\nmatch = "people/**"\n\n[schemas.record]\nmatch = "records/**"\n')
    for sub in ("work", "systems", "people", "records", "artifacts", ".cairn", ".hooks"): (d / sub).mkdir(exist_ok=True)
    (d / "cairn.toml").write_text((HERE / "examples" / "cairn.example.toml").read_text())
    (d / ".hooks" / "session-end.sh").write_text(HOOK.format(bundle=d)); (d / ".hooks" / "session-end.sh").chmod(0o755)
    (d / ".gitignore").write_text(".cairn/\n")
    hook = {"type": "command", "command": f"bash {d}/.hooks/session-end.sh", "async": True, "timeout": 60}
    print(f"""bundle ready: {d}

1. edit {d}/cairn.toml           github org + user, transcript prefix
2. export CAIRN_BUNDLE={d}        put it in your shell profile or in .claude/settings.json "env"
3. crn sweep --create             one work node per open issue assigned to you
4. write systems/<slug>.md        one per thing you operate: access, look_in, aliases, Gotchas
5. records/<slug>.md, optional   one pointer per investigation, research write-up or runbook you want findable

Claude Code wiring (optional, zero tokens at startup):
  ln -sfn {HERE}/skills/cairn ~/.claude/skills/cairn
  ln -sfn {HERE}/commands/node.md ~/.claude/commands/node.md
  settings.json → "hooks": {json.dumps({"SessionEnd": [{"matcher": "", "hooks": [hook]}], "PreCompact": [{"matcher": "", "hooks": [hook]}]})}

then: crn doctor""")
    return 0


def _ok(label, good, detail=""):
    print(f"{'ok  ' if good else 'MISS'} {label:24s} {detail}"); return good


def doctor(bundle_hint=None):
    good = True
    good &= _ok("python", sys.version_info >= (3, 11), sys.version.split()[0])
    iwe_path = shutil.which("iwe")
    v = subprocess.run(["iwe", "--version"], capture_output=True, text=True).stdout.strip() if iwe_path else ""
    good &= _ok("iwe on PATH", bool(iwe_path), v or "install from https://github.com/iwe-org/iwe/releases")
    good &= _ok("crn on PATH", bool(shutil.which("crn")), shutil.which("crn") or f"ln -sfn {HERE}/bin/crn ~/.local/bin/crn")
    gh = shutil.which("gh")
    auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True).returncode == 0 if gh else False
    good &= _ok("gh authenticated", auth, "" if auth else "gh auth login (only needed for crn sweep)")
    env = os.environ.get("CAIRN_BUNDLE")
    b = Path(env).expanduser() if env else (Path(bundle_hint) if bundle_hint else None)
    good &= _ok("CAIRN_BUNDLE", bool(env), env or "export CAIRN_BUNDLE=<bundle dir>")
    if not (b and (b / "cairn.toml").exists()):
        _ok("bundle", False, "no cairn.toml found; crn init <dir>"); print("RESULT FAIL"); return 1
    import tomllib
    with open(b / "cairn.toml", "rb") as f: cfg = tomllib.load(f)
    gh_ok = bool(cfg.get("github", {}).get("org")) and bool(cfg.get("github", {}).get("user")) and cfg["github"]["org"] != "acme"
    good &= _ok("cairn.toml [github]", gh_ok, "org + user set" if gh_ok else "edit org and user (still the template values)")
    tr_ok = bool(cfg.get("trail", {}).get("prefix")) and cfg["trail"]["prefix"] != "-home-me-work"
    good &= _ok("cairn.toml [trail]", tr_ok, cfg.get("trail", {}).get("prefix", "") if tr_ok else "set prefix to your encoded project dir")
    v = iwe(b, "schema", "validate", check=False)
    good &= _ok("bundle validates", "›" not in v, f"{sum(1 for _ in (b / 'work').glob('*.md'))} work · {sum(1 for _ in (b / 'systems').glob('*.md'))} systems")
    hook = b / ".hooks" / "session-end.sh"
    good &= _ok("session-end hook file", hook.exists(), str(hook) if hook.exists() else "crn init writes it; copy from another bundle")
    skill = Path.home() / ".claude" / "skills" / "cairn"; cmd = Path.home() / ".claude" / "commands" / "node.md"
    _ok("claude skill installed", skill.exists(), str(skill) if skill.exists() else f"ln -sfn {HERE}/skills/cairn {skill}")
    _ok("claude /node command", cmd.exists(), str(cmd) if cmd.exists() else f"ln -sfn {HERE}/commands/node.md {cmd}")
    print("RESULT " + ("PASS" if good else "FAIL")); return 0 if good else 1
