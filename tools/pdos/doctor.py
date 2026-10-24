"""Health checks for the repository or an instance of it."""
from __future__ import annotations

import json
import os
import re
import sys
from typing import List, Tuple

from .build import build, read_manifest, read_version
from .skills import discover_skills, validate_collection


def check_registries(root: str, manifest: dict, skills) -> Tuple[List[str], List[str]]:
    """Registries are hand-kept files that must change when a skill is added.
    lists_skills: every core skill name appears in the file.
    skill_count: every number matched by `pattern` equals the core skill count."""
    names = sorted(s.name for s in skills if s.origin == "core")
    problems: List[str] = []
    notes: List[str] = []
    for reg in manifest.get("registries", []):
        kind = reg.get("check")
        if not kind:
            continue
        rel = reg.get("file", "")
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            notes.append("registry %s not found" % rel)
            continue
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        if kind == "lists_skills":
            missing = [n for n in names if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), text)]
            if missing:
                problems.append("%s does not mention: %s. %s" % (rel, ", ".join(missing), reg.get("update", "")))
        elif kind == "skill_count":
            found = re.findall(reg.get("pattern", r"(\d+) skills"), text)
            wrong = sorted(set(f for f in found if int(f) != len(names)))
            if not found:
                notes.append("%s: no skill count found by pattern %s" % (rel, reg.get("pattern")))
            elif wrong:
                problems.append("%s states %s skills; there are %d. %s" % (rel, "/".join(wrong), len(names), reg.get("update", "")))
        else:
            notes.append("registry %s: unknown check %r" % (rel, kind))
    return problems, notes


def doctor(root: str) -> int:
    problems = 0
    warns = 0

    def ok(m):
        print("  ok    " + m)

    def bad(m):
        nonlocal problems
        problems += 1
        print("  FAIL  " + m)

    def note(m):
        nonlocal warns
        warns += 1
        print("  warn  " + m)

    print("Pricing Desk OS doctor  (%s)" % root)
    if sys.version_info < (3, 8):
        bad("Python 3.8+ required, found %s" % sys.version.split()[0])
    else:
        ok("python %s" % sys.version.split()[0])
    for rel in ("os.manifest.json", "AGENTS.md", "core/skills", "tools/pdos.py", "VERSION"):
        (ok if os.path.exists(os.path.join(root, rel)) else bad)(rel + (" present" if os.path.exists(os.path.join(root, rel)) else " missing"))
    try:
        manifest = read_manifest(root)
    except (SystemExit, ValueError) as e:
        bad("os.manifest.json unreadable: %s" % e)
        print("\n%d problem(s), %d warning(s)" % (problems, warns))
        return 1

    unreadable = []
    count = 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for f in files:
            count += 1
            try:
                with open(os.path.join(dirpath, f), "rb") as fh:
                    fh.read(512)
            except OSError as e:
                unreadable.append((os.path.relpath(os.path.join(dirpath, f), root), e.strerror))
    if unreadable:
        bad("%d file(s) cannot be read. On Google Drive for desktop this means cloud-only placeholders; set the folder to Available offline:" % len(unreadable))
        for rel, why in unreadable[:15]:
            print("          - %s: %s" % (rel, why))
    else:
        ok("all %d files readable" % count)

    skills = discover_skills(root)
    issues = validate_collection(skills, root)
    errs = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warn"]
    (bad if errs else ok)("%d skills, %d error(s), %d warning(s)" % (len(skills), len(errs), len(warnings)))
    for i in errs[:10]:
        print("          " + str(i))

    rp, rn = check_registries(root, manifest, skills)
    if rp:
        for m in rp:
            bad("registry: " + m)
    else:
        ok("registries in os.manifest.json are consistent with the skills")
    for m in rn:
        note(m)

    names = {s.name for s in skills}
    ns = manifest.get("extension", {}).get("command_namespace", "pricing")
    cdir = os.path.join(root, "core", "commands", ns)
    if os.path.isdir(cdir):
        orphan = []
        for f in sorted(os.listdir(cdir)):
            if f.endswith(".toml"):
                text = open(os.path.join(cdir, f), encoding="utf-8").read()
                if not any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), text) for n in names):
                    orphan.append(f)
        (bad if orphan else ok)("hand-written commands each name a skill" if not orphan else "commands naming no skill: " + ", ".join(orphan))

    cs = os.path.join(root, ".claude", "settings.json")
    if os.path.isfile(cs):
        txt = open(cs, encoding="utf-8").read()
        if "guard_pricing_files" in txt:
            ok("Claude Code guard hook is wired in .claude/settings.json")
        else:
            note(".claude/settings.json exists but does not run the guard hook (guard_pricing_files.py): Approved statuses are not blocked in Claude Code. Merge the hooks block from core/hooks/claude-settings.json")
    else:
        note("no .claude/settings.json: the guard hook is not wired for Claude Code (run build)")

    a = os.path.join(root, "AGENTS.md")
    if os.path.isfile(a):
        n = len(open(a, encoding="utf-8").read().splitlines())
        (note if n > 220 else ok)("AGENTS.md is %d lines%s" % (n, " (keep it a router, under about 200)" if n > 220 else ""))
    if os.path.isfile(os.path.join(root, ".pricing-desk-instance.json")):
        for rel in manifest.get("protect", []):
            if not os.path.isdir(os.path.join(root, rel)):
                note("protected folder %s does not exist" % rel)
        gov = os.path.join(root, "workspace", "context-library", "pricing-governance.md")
        if os.path.isfile(gov) and "status: template" in open(gov, encoding="utf-8").read():
            note("pricing-governance.md is still a template: run pd-setup before relying on approval routes")

    v = read_version(root)
    gp = os.path.join(root, "gemini-extension.json")
    if os.path.isfile(gp):
        gv = json.load(open(gp, encoding="utf-8")).get("version")
        (ok if gv == v else note)("extension version %s %s VERSION %s" % (gv, "matches" if gv == v else "differs from", v))
    cl = os.path.join(root, "CHANGELOG.md")
    if os.path.isfile(cl):
        (ok if v in open(cl, encoding="utf-8").read() else note)("CHANGELOG %s version %s" % ("mentions" if v in open(cl, encoding="utf-8").read() else "does not mention", v))

    rc = build(root, check=True, quiet=True)
    if rc == 0:
        ok("generated outputs are current")
    elif rc == 2:
        note("generated outputs are out of date: run `python3 tools/pdos.py build`")
    else:
        bad("build check failed (validation errors)")
    print("\n%d problem(s), %d warning(s)" % (problems, warns))
    return 1 if problems else 0
