"""Instances: a product snapshot plus workspace/ (company data) and local/ (company-only skills).

Upgrades replace product folders and never touch workspace/ or local/.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import tarfile
from typing import Optional

from .build import ALL_TARGETS, build, read_version

PRODUCT_DIRS = ["core", "tools", "evals", "docs", "adapters", "design"]
PRODUCT_FILES = ["AGENTS.md", "CLAUDE.md", "VERSION", "os.manifest.json", ".gitignore", "README.md", "CHANGELOG.md"]
META = ".pricing-desk-instance.json"
JUNK = shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc")


def _copy_product(src: str, dest: str) -> None:
    for d in PRODUCT_DIRS:
        s = os.path.join(src, d)
        if os.path.isdir(s):
            t = os.path.join(dest, d)
            if os.path.isdir(t):
                shutil.rmtree(t)
            shutil.copytree(s, t, ignore=JUNK)
    for f in PRODUCT_FILES:
        s = os.path.join(src, f)
        if os.path.isfile(s):
            shutil.copyfile(s, os.path.join(dest, f))


def _scaffold_workspace(src: str, dest: str, client: str) -> None:
    scaf = os.path.join(src, "core", "scaffold", "workspace")
    today = dt.date.today().isoformat()
    for dirpath, dirs, files in os.walk(scaf):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            s = os.path.join(dirpath, f)
            t = os.path.join(dest, "workspace", os.path.relpath(s, scaf))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            if os.path.exists(t):
                continue  # never overwrite company data
            try:
                text = open(s, "r", encoding="utf-8").read()
            except UnicodeDecodeError:
                shutil.copyfile(s, t)
                continue
            with open(t, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.replace("{{client}}", client).replace("{{date}}", today))


def new_instance(src: str, dest: str, client: str) -> int:
    dest = os.path.abspath(dest)
    if os.path.exists(dest) and os.listdir(dest):
        print("destination %s exists and is not empty" % dest)
        return 1
    os.makedirs(dest, exist_ok=True)
    _copy_product(src, dest)
    os.makedirs(os.path.join(dest, "local", "skills"), exist_ok=True)
    with open(os.path.join(dest, "local", "README.md"), "w", encoding="utf-8") as fh:
        fh.write("# local/\n\nCompany-only skills go in `local/skills/<name>/SKILL.md`. They are built with the core skills and survive upgrades. See `core/shared/skill-authoring.md`.\n")
    _scaffold_workspace(src, dest, client)
    meta = {"client": client, "created": dt.date.today().isoformat(), "product_version": read_version(src)}
    with open(os.path.join(dest, META), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    rc = build(dest, targets=ALL_TARGETS)
    if rc == 0:
        print("\ninstance ready: %s\nnext: open it in your agent and say \"set up the pricing desk\" (runs pd-setup, one question at a time)." % dest)
    return rc


def upgrade_instance(src: str, dest: str) -> int:
    dest = os.path.abspath(dest)
    meta_path = os.path.join(dest, META)
    if not os.path.isfile(meta_path):
        print("%s is not a Pricing Desk instance (no %s)" % (dest, META))
        return 1
    meta = json.load(open(meta_path, "r", encoding="utf-8"))
    agents = os.path.join(dest, "AGENTS.md")
    if os.path.isfile(agents):
        shutil.copyfile(agents, agents + ".bak-" + dt.date.today().isoformat())
    _copy_product(src, dest)
    _scaffold_workspace(src, dest, meta.get("client", "Company"))  # adds new scaffold files only
    old = meta.get("product_version")
    meta["product_version"] = read_version(src)
    meta["upgraded"] = dt.date.today().isoformat()
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    print("upgraded %s: %s -> %s (workspace/ and local/ untouched; old AGENTS.md saved as .bak)" % (dest, old, meta["product_version"]))
    return build(dest, targets=ALL_TARGETS)


def release(root: str, out_dir: Optional[str] = None) -> str:
    version = read_version(root)
    out_dir = out_dir or os.path.join(root, "dist", "releases")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "pricing-desk-%s.tar.gz" % version)

    def keep(ti: tarfile.TarInfo):
        if any(p in ("__pycache__", ".DS_Store") for p in ti.name.split("/")) or ti.name.endswith(".pyc"):
            return None
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = ""
        ti.mtime = 0
        return ti

    with tarfile.open(path, "w:gz") as tar:
        for item in sorted(PRODUCT_DIRS + PRODUCT_FILES):
            p = os.path.join(root, item)
            if os.path.exists(p):
                tar.add(p, arcname="pricing-desk-%s/%s" % (version, item), filter=keep)
    return path
