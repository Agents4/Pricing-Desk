"""Compile the canonical source into platform outputs. Generated files are never edited by hand.

Source (edit these)                         Generated
  core/skills/*, local/skills/*       -->   skills/            Gemini CLI extension (repo root is the extension)
  core/commands/<ns>/*.toml           -->   commands/<ns>/     hand-written commands, plus one generated per uncovered skill
  core/agents/*.md                    -->   agents/
  core/hooks/*                        -->   hooks/
  AGENTS.md (router and rules)        -->   GEMINI.md          AGENTS.md plus an extension note
  os.manifest.json + VERSION          -->   gemini-extension.json
  core/skills/*                       -->   .claude/skills/    Claude Code
  core/skills/*                       -->   .agents/skills/    Gemini CLI workspace scope, Codex, other Agent Skills clients
  core/skills/*                       -->   dist/gemini-app/   one zip per skill, for upload in the Gemini app and for Claude or Copilot

`pdos.py build --check` fails when generated files differ from what the source produces.
"""
from __future__ import annotations

import filecmp
import json
import os
import re
import shutil
import tempfile
import zipfile
from typing import Dict, List, Optional

from .skills import Skill, compile_skill, discover_skills, validate_collection

ALL_TARGETS = ["extension", "claude", "agents", "gemini-app", "notebook"]
ZIP_DATE = (2026, 1, 1, 0, 0, 0)
REPO_ONLY_RE = re.compile(r"<!--\s*repo-only:start\s*-->.*?<!--\s*repo-only:end\s*-->\s*", re.DOTALL)
JUNK_DIRS = {"__pycache__", ".DS_Store"}

EXTENSION_NOTE = """
## Running as a Gemini CLI extension

This context file ships with the Pricing Desk extension. Your project folder is the working folder.

- Skills are active by name. Slash commands live under `/pricing:`, for example `/pricing:deal-review`.
- Scripts sit inside each skill (`skills/<name>/scripts/`). Run them with `python3`, using the path your skill gives you. They read files you point them to and write only where you tell them.
- Company facts, thresholds and the Council live in your context library (`workspace/context-library/`). Run the setup skill to create and fill it. Nothing is written into the extension folder.
- Where a skill refers to `core/shared/...`, the same file is included inside the skill as `references/...`.
"""


def read_manifest(root: str) -> Dict:
    p = os.path.join(root, "os.manifest.json")
    if not os.path.isfile(p):
        raise SystemExit("os.manifest.json not found in %s" % root)
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_version(root: str) -> str:
    p = os.path.join(root, "VERSION")
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as fh:
            return fh.read().strip() or "0.0.0"
    return "0.0.0"


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def _toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=True)


def _dir_files(path: str) -> Dict[str, str]:
    out = {}
    for dirpath, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in JUNK_DIRS]
        for f in files:
            if f in JUNK_DIRS or f.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, f)
            out[os.path.relpath(full, path).replace(os.sep, "/")] = full
    return out


def diff_trees(expected: str, actual: str) -> List[str]:
    problems: List[str] = []
    fa = _dir_files(expected) if os.path.isdir(expected) else {}
    fb = _dir_files(actual) if os.path.isdir(actual) else {}
    for rel in sorted(set(fa) | set(fb)):
        if rel not in fb:
            problems.append("missing: %s" % rel)
        elif rel not in fa:
            problems.append("unexpected: %s" % rel)
        elif not filecmp.cmp(fa[rel], fb[rel], shallow=False):
            problems.append("changed: %s" % rel)
    return problems


def write_zip(path: str, files: Dict[str, bytes]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for arc in sorted(files):
            zi = zipfile.ZipInfo(arc, date_time=ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, files[arc])


# --------------------------------------------------------------------------- generators
def gen_skills(stage: str, rel: str, skills: List[Skill], core_dir: str) -> None:
    base = os.path.join(stage, rel)
    os.makedirs(base, exist_ok=True)
    for s in skills:
        compile_skill(s, core_dir, base)


def default_command(skill: Skill) -> str:
    desc = skill.description.strip()
    short = desc if len(desc) <= 160 else desc[:157].rstrip() + "..."
    body = (
        "Use the %s skill for this request. Follow the pricing desk rules in your context.\n\n"
        "Request and inputs: {{args}}\n\n"
        "If a needed input is missing, list it and stop. Recommend only; do not contact a customer or approve a price.\n" % skill.name
    )
    return "description = %s\nprompt = \"\"\"\n%s\"\"\"\n" % (_toml_str(short), body)


def gen_commands(stage: str, root: str, manifest: Dict, skills: List[Skill]) -> List[str]:
    ns = manifest.get("extension", {}).get("command_namespace", "pricing")
    names = [s.name for s in skills]
    covered = set()
    base = os.path.join(stage, "commands", ns)
    src = os.path.join(root, "core", "commands", ns)
    used = set()
    if os.path.isdir(src):
        for f in sorted(os.listdir(src)):
            if not f.endswith(".toml"):
                continue
            text = _read(os.path.join(src, f))
            _write(os.path.join(base, f), text)
            used.add(f[:-5])
            # A hand-written command covers the skill its prompt opens with ("Use the X skill"); a skill only mentioned
            # in passing (a pointer to another skill) still gets its own generated command.
            m = re.search(r"Use the ([a-z0-9-]+) skill", text)
            if m and m.group(1) in names:
                covered.add(m.group(1))
    notes: List[str] = []
    for s in skills:
        if s.name in covered:
            continue
        cmd = s.command
        if cmd in used:
            notes.append("command /%s:%s already exists; skill %s has no command" % (ns, cmd, s.name))
            continue
        _write(os.path.join(base, cmd + ".toml"), default_command(s))
        used.add(cmd)
    return notes


def gen_extension(stage: str, root: str, manifest: Dict, skills: List[Skill], core_dir: str, version: str) -> List[str]:
    ext = manifest.get("extension", {})
    gen_skills(stage, "skills", skills, core_dir)
    notes = gen_commands(stage, root, manifest, skills)
    for sub in ("agents", "hooks"):
        src = os.path.join(root, "core", sub)
        if os.path.isdir(src):
            dst = os.path.join(stage, sub)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*JUNK_DIRS, "*.pyc"))
    _write(os.path.join(stage, "gemini-extension.json"), json.dumps({
        "name": ext.get("name", manifest.get("slug")),
        "version": version,
        "description": ext.get("description", ""),
        "contextFileName": "GEMINI.md",
    }, indent=2) + "\n")
    rules = manifest.get("rules_file", "AGENTS.md")
    text = REPO_ONLY_RE.sub("", _read(os.path.join(root, rules)))
    _write(os.path.join(stage, "GEMINI.md"), text.rstrip() + "\n" + EXTENSION_NOTE)
    return notes


def gen_gemini_app(stage: str, skills: List[Skill], core_dir: str, version: str) -> None:
    base = os.path.join(stage, "dist", "gemini-app")
    tmp = tempfile.mkdtemp()
    sizes = {}
    try:
        for s in skills:
            files = compile_skill(s, core_dir, tmp)
            data = {rel: _read_bytes(os.path.join(tmp, s.name, rel)) for rel in files}
            zp = os.path.join(base, "zips", s.name + ".zip")
            write_zip(zp, data)
            sizes[s.name] = os.path.getsize(zp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lines = ["# Skill zips: Gemini app, Claude and Microsoft Copilot", "",
             "Version %s. Generated by `python3 tools/pdos.py build`. Do not edit." % version, "",
             "## How", "",
             "- **Gemini app** (gemini.google.com): Skills page, create, upload. Choose one `.zip`. SKILL.md sits at the zip root. Review, then Create.",
             "- **Gemini Enterprise**: an admin turns on skills and skill sharing in Feature Management first; then users upload and share the same zips.",
             "- **Claude** (Customize, Skills) and **Microsoft 365 Copilot Cowork**: upload the same `.zip` files, one skill per upload.",
             "- If a zip is rejected, upload the matching folder from `.agents/skills/<name>/` instead.",
             "- Uploads are plain text. Scripts in these skills cannot reach the internet; where a skill uses a script, it says what to do without one.",
             "- Skills do not sync between the Gemini app and Workspace apps. Upload in each place you want them.", "",
             "## All skills", "", "| Zip | Size |", "|---|---|"]
    for n in sorted(sizes):
        lines.append("| `zips/%s.zip` | %.1f KB |" % (n, sizes[n] / 1024.0))
    lines.append("")
    _write(os.path.join(base, "INSTALL.md"), "\n".join(lines))


# --------------------------------------------------------------------------- driver
MANAGED_DIRS = {
    "extension": ["skills", "commands", "agents", "hooks"],
    "claude": [".claude/skills"],
    "agents": [".agents/skills"],
    "gemini-app": ["dist/gemini-app"],
    "notebook": ["dist/notebook-packs/pricing-coach"],  # company and account packs live under workspace/outputs and are never touched by build
}
MANAGED_FILES = {"extension": ["gemini-extension.json", "GEMINI.md"], "claude": [".claude/settings.json"]}
GENERATED_MARK = "_generated_by"  # a settings file without this key is the user's own and is never overwritten


def build(root: str, targets: Optional[List[str]] = None, check: bool = False, quiet: bool = False) -> int:
    say = (lambda *a: None) if quiet else print
    targets = targets or ALL_TARGETS
    manifest = read_manifest(root)
    skills = discover_skills(root)
    issues = validate_collection(skills, root)
    errors = [i for i in issues if i.level == "error"]
    if not quiet:
        for i in issues:
            if i.level == "warn":
                say(str(i))
    if errors:
        for i in errors:
            say(str(i))
        say("\nbuild aborted: %d validation error(s)." % len(errors))
        return 1
    core_dir = os.path.join(root, "core")
    version = read_version(root)
    stage = tempfile.mkdtemp(prefix="pdos-stage-")
    try:
        notes: List[str] = []
        if "extension" in targets:
            notes += gen_extension(stage, root, manifest, skills, core_dir, version)
        if "claude" in targets:
            gen_skills(stage, ".claude/skills", skills, core_dir)
            cs = os.path.join(core_dir, "hooks", "claude-settings.json")
            if os.path.isfile(cs):
                _write(os.path.join(stage, ".claude", "settings.json"), _read(cs))
        if "agents" in targets:
            gen_skills(stage, ".agents/skills", skills, core_dir)
        if "gemini-app" in targets:
            gen_gemini_app(stage, skills, core_dir, version)
        if "notebook" in targets:
            from .notebook import build_coach_pack
            build_coach_pack(core_dir, skills, os.path.join(stage, "dist", "notebook-packs", "pricing-coach"), version)

        drift: List[str] = []
        for t in targets:
            for rel in MANAGED_DIRS.get(t, []):
                new, cur = os.path.join(stage, rel), os.path.join(root, rel)
                if check:
                    drift += ["%s: %s" % (rel, p) for p in diff_trees(new, cur)]
                else:
                    if os.path.isdir(cur):
                        shutil.rmtree(cur)
                    if os.path.isdir(new):
                        os.makedirs(os.path.dirname(cur), exist_ok=True)
                        shutil.copytree(new, cur)
            for rel in MANAGED_FILES.get(t, []):
                new, cur = os.path.join(stage, rel), os.path.join(root, rel)
                if not os.path.isfile(new):
                    continue
                if rel.endswith("settings.json") and os.path.isfile(cur) and GENERATED_MARK not in _read(cur):
                    notes.append("%s exists and is not generated by the build; left alone. Merge core/hooks/claude-settings.json into it by hand to turn on the guard hook." % rel)
                    continue
                if check:
                    if not os.path.isfile(cur) or _read(new) != _read(cur):
                        drift.append("%s: differs from generated" % rel)
                else:
                    shutil.copyfile(new, cur)
        for n in notes:
            say("note: " + n)
        if check:
            if drift:
                say("generated outputs are out of date (%d differences). Run: python3 tools/pdos.py build" % len(drift))
                for d in drift[:40]:
                    say("  " + d)
                return 2
            say("ok: generated outputs match source (%d skills)" % len(skills))
            return 0
        say("built %d skills -> %s" % (len(skills), ", ".join(sum((MANAGED_DIRS.get(t, []) + MANAGED_FILES.get(t, []) for t in targets), []))))
        return 0
    finally:
        shutil.rmtree(stage, ignore_errors=True)
