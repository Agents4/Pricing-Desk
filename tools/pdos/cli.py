"""Command line: validate, build, doctor, list."""
from __future__ import annotations

import argparse
import os
from typing import List, Optional

from . import __version__
from .build import ALL_TARGETS, build, read_version
from .doctor import doctor
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
    l = sub.add_parser("list", help="list skills and their slash commands")
    l.set_defaults(fn=cmd_list)
    args = p.parse_args(argv)
    return args.fn(args)
