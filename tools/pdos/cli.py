"""Command line: validate, build, doctor, list."""
from __future__ import annotations

import argparse
import os
from typing import List, Optional

from . import __version__
from .build import ALL_TARGETS, build, read_version
from .doctor import doctor
from .instance import new_instance, release, upgrade_instance
from .lint import lint_file
from .skills import discover_skills, validate_collection


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cmd_validate(args) -> int:
    root = repo_root()
    skills = discover_skills(root)
    issues = validate_collection(skills, root)
    errors = [i for i in issues if i.level == "error"]
    for i in issues:
        if i.level == "error" or not args.errors_only:
            print(i)
    print("%d skills, %d error(s), %d warning(s)" % (len(skills), len(errors), len(issues) - len(errors)))
    return 1 if errors or (args.strict and len(issues) > len(errors)) else 0


def cmd_build(args) -> int:
    targets = args.target or ALL_TARGETS
    return build(repo_root(), targets=targets, check=args.check)


def cmd_doctor(args) -> int:
    return doctor(repo_root())


def cmd_lint(args) -> int:
    worst = 0
    for path in args.files:
        issues = lint_file(path)
        for i in issues:
            print(i)
        errs = [i for i in issues if i.level == "error"]
        print("%s: %d error(s), %d warning(s)" % (path, len(errs), len(issues) - len(errs)))
        worst = max(worst, 1 if errs else 0)
    return worst


def cmd_evals(args) -> int:
    root = repo_root()
    names = {s.name for s in discover_skills(root)}
    base = os.path.join(root, "evals", "cases")
    bad = 0
    cases = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))) if os.path.isdir(base) else []
    covered = set()
    for c in cases:
        d = os.path.join(base, c)
        for f in ("input.md", "expected.md"):
            if not os.path.isfile(os.path.join(d, f)):
                print("FAIL %s: missing %s" % (c, f))
                bad += 1
        ep = os.path.join(d, "expected.md")
        if os.path.isfile(ep):
            first = open(ep, encoding="utf-8").readline().strip()
            sk = first[len("Skill:"):].strip() if first.startswith("Skill:") else ""
            if sk not in names:
                print("FAIL %s: first line must be `Skill: <existing skill>`, got %r" % (c, first))
                bad += 1
            else:
                covered.add(sk)
            checks = [l for l in open(ep, encoding="utf-8").read().splitlines() if l.startswith("- ")]
            if not checks:
                print("FAIL %s: no checks (lines starting with '- ')" % c)
                bad += 1
    print("%d case(s), %d skill(s) covered of %d, %d problem(s)" % (len(cases), len(covered), len(names), bad))
    uncovered = sorted(names - covered)
    if uncovered and args.coverage:
        print("no eval case: " + ", ".join(uncovered))
    return 1 if bad else 0


def cmd_new_instance(args) -> int:
    return new_instance(repo_root(), args.dest, args.client)


def cmd_upgrade(args) -> int:
    return upgrade_instance(repo_root(), args.dest)


def cmd_release(args) -> int:
    print(release(repo_root(), args.out))
    return 0


def _inside(path: str, base: str) -> bool:
    path, base = os.path.realpath(path), os.path.realpath(base)
    return path == base or path.startswith(base + os.sep)


def cmd_notebook_pack(args) -> int:
    from .notebook import build_account_pack, build_company_pack, valid_slug
    root = os.path.abspath(args.workspace) if args.workspace else (os.getcwd() if os.path.isdir(os.path.join(os.getcwd(), "workspace")) else repo_root())
    core = os.path.join(repo_root(), "core")
    packs = os.path.join(root, "workspace", "outputs", "notebook-packs")
    if args.account:
        if not valid_slug(args.account):
            print("account %r is not a folder slug (lower-case letters, digits, dot, dash, underscore)" % args.account)
            return 1
        out = os.path.abspath(args.out) if args.out else os.path.join(packs, "account-" + args.account)
    elif args.company:
        out = os.path.abspath(args.out) if args.out else os.path.join(packs, "company-playbook")
    else:
        print("choose --account <slug> or --company")
        return 1
    if not (_inside(out, os.path.join(root, "workspace", "outputs")) or _inside(out, os.path.join(root, "dist"))) or os.path.realpath(out) in (
            os.path.realpath(os.path.join(root, "workspace", "outputs")), os.path.realpath(os.path.join(root, "dist"))):
        print("--out must be a new folder inside workspace/outputs/ or dist/ (it may be cleared and rewritten): %s" % out)
        return 1
    try:
        written = build_account_pack(root, core, args.account, out) if args.account else build_company_pack(root, core, out)
    except SystemExit as e:
        print(e)
        return 1
    print("wrote %d source file(s) to %s" % (len(written), out))
    for fn, w in written:
        print("  %-48s %7d words" % (fn, w))
    print("These packs can hold floors and customer prices. Share only with the deal desk and the Pricing Council.")
    return 0


def cmd_list(args) -> int:
    for s in discover_skills(repo_root()):
        print("%-30s %-5s /%s" % (s.name, s.origin, s.command))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="pdos.py", description="Pricing Desk OS tool (version %s, repo version %s)" % (__version__, read_version(repo_root())))
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="validate every skill")
    v.add_argument("--strict", action="store_true", help="treat warnings as failures")
    v.add_argument("--errors-only", action="store_true", help="print errors only")
    v.set_defaults(fn=cmd_validate)
    b = sub.add_parser("build", help="generate platform outputs from core/")
    b.add_argument("--check", action="store_true", help="fail if generated outputs are out of date")
    b.add_argument("--target", action="append", choices=ALL_TARGETS, help="limit to a target (repeatable)")
    b.set_defaults(fn=cmd_build)
    d = sub.add_parser("doctor", help="health checks")
    d.set_defaults(fn=cmd_doctor)
    li = sub.add_parser("lint", help="check pricing outputs against the checkable operating rules")
    li.add_argument("files", nargs="+")
    li.set_defaults(fn=cmd_lint)
    e = sub.add_parser("evals", help="check eval cases are well formed and name real skills")
    e.add_argument("--coverage", action="store_true", help="list skills without an eval case")
    e.set_defaults(fn=cmd_evals)
    ni = sub.add_parser("new-instance", help="create a company instance (product + workspace + local)")
    ni.add_argument("dest")
    ni.add_argument("--client", required=True)
    ni.set_defaults(fn=cmd_new_instance)
    up = sub.add_parser("upgrade-instance", help="upgrade an instance; workspace/ and local/ untouched")
    up.add_argument("dest")
    up.set_defaults(fn=cmd_upgrade)
    rl = sub.add_parser("release", help="write a release tarball")
    rl.add_argument("--out")
    rl.set_defaults(fn=cmd_release)
    nb = sub.add_parser("notebook-pack", help="compile a Gemini Notebook source pack from the workspace")
    nb.add_argument("--account", help="account folder slug under workspace/accounts")
    nb.add_argument("--company", action="store_true", help="company pack from the context library, price book and decision log")
    nb.add_argument("--out")
    nb.add_argument("--workspace", help="folder that contains workspace/")
    nb.set_defaults(fn=cmd_notebook_pack)
    l = sub.add_parser("list", help="list skills and their slash commands")
    l.set_defaults(fn=cmd_list)
    args = p.parse_args(argv)
    return args.fn(args)
