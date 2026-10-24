"""Source packs for Gemini Notebook (formerly NotebookLM).

A notebook cannot run skills or scripts, so it gets structured source documents plus chat instructions and a
Studio prompt cookbook. Three packs:
  pricing-coach   static: rules, spine, rhythms, frameworks, skill procedures (built by `build`)
  company         from workspace/context-library, decision log and price book tables
  account         from workspace/accounts/<slug>

The source limits are Google's and change; verify them before relying on them (adapters/google/platform-facts.md).
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import re
from typing import List, Optional, Tuple

DEFAULT_MAX_WORDS = 120000
CHAT_SOFT_LIMIT = 3000
LIMITS_NOTE = ("Source limits are Google's and change: verify them on Google's usage-limits page before relying on them. "
               "Sales-OS notes about 50 sources per notebook on the consumer tier and 300 sources with 500,000 words or 500 MB per source on Enterprise (not re-verified here).")
CONF_NOTE = ("CONFIDENTIAL: company and account packs can contain floors, discount bands, incentives and customer prices. "
             "Everyone with access to a notebook can read its sources. Share only with the deal desk and the Pricing Council.")


def words(t: str) -> int:
    return len(t.split())


def _read(p: str) -> str:
    with open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def _strip_fm(t: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", t, flags=re.DOTALL)


def split_words(text: str, max_words: int) -> List[str]:
    if words(text) <= max_words:
        return [text]
    parts, cur, n = [], [], 0
    for para in re.split(r"\n{2,}", text):
        w = words(para)
        if cur and n + w > max_words:
            parts.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(para)
        n += w
    if cur:
        parts.append("\n\n".join(cur))
    return parts


def assemble(title: str, chunks: List[Tuple[str, str]], note: str = "") -> str:
    out = ["# %s" % title, ""]
    if note:
        out += [note, ""]
    for label, text in chunks:
        out += ["---", "", "## Document: %s" % label, "", _strip_fm(text).strip(), ""]
    return "\n".join(out).rstrip() + "\n"


PACK_MARK = ".pdos-notebook-pack"


def prepare_out(out_dir: str) -> None:
    """Create out_dir for a pack. An existing folder is reused only if it is empty or is one of our packs (then its
    sources/ are cleared, so stale files from an older run cannot linger). Anything else is refused."""
    if os.path.isdir(out_dir) and os.listdir(out_dir):
        if not os.path.isfile(os.path.join(out_dir, PACK_MARK)):
            raise SystemExit("%s exists, is not empty and is not a notebook pack made by this tool; choose another --out" % out_dir)
        src = os.path.join(out_dir, "sources")
        if os.path.isdir(src):
            for f in os.listdir(src):
                if f.endswith(".md"):
                    os.remove(os.path.join(src, f))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, PACK_MARK), "w", encoding="utf-8") as fh:
        fh.write("Made by pdos notebook-pack. This folder may be cleared and rewritten by the next run.\n")


def write_sources(out_dir: str, sources: List[Tuple[str, str]], max_words: int = DEFAULT_MAX_WORDS) -> List[Tuple[str, int]]:
    prepare_out(out_dir)
    os.makedirs(os.path.join(out_dir, "sources"), exist_ok=True)
    written, n = [], 0
    for title, text in sources:
        parts = split_words(text, max_words)
        for i, part in enumerate(parts, 1):
            n += 1
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "source"
            fn = "%02d-%s%s.md" % (n, slug, "" if len(parts) == 1 else "-part%d" % i)
            with open(os.path.join(out_dir, "sources", fn), "w", encoding="utf-8") as fh:
                fh.write(part)
            written.append((fn, words(part)))
    return written


def _copy(src: str, dest: str, subst: Optional[dict] = None) -> int:
    t = _read(src)
    for k, v in (subst or {}).items():
        t = t.replace("{{%s}}" % k, v)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(t)
    return len(t)


def write_readme(out_dir: str, title: str, desc: str, written: List[Tuple[str, int]], confidential: bool) -> None:
    lines = ["# %s" % title, "", desc, ""]
    if confidential:
        lines += [CONF_NOTE, ""]
    lines += ["## Upload steps", "",
              "1. Create a new notebook in Gemini Notebook (or Gemini Notebook Enterprise).",
              "2. Add everything in `sources/`. Importing them as Google Docs first lets you use sync with Drive when they change.",
              "3. Open the chat settings, choose a custom conversational style and paste `chat-instructions.txt`.",
              "4. Use `studio-prompts.md` for overviews, reports, quizzes, flashcards, slide decks and mind maps.", "",
              "## Sources (%d)" % len(written), "", "| File | Words |", "|---|---|"]
    lines += ["| `%s` | %d |" % (f, w) for f, w in written]
    lines += ["", LIMITS_NOTE, "",
              "A notebook is a snapshot unless its sources are synced Google Docs. Regenerate after meaningful changes and replace only the changed sources.", ""]
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _finish(out_dir: str, pack_dir: str, subst: dict) -> None:
    for fn in ("chat-instructions.txt", "studio-prompts.md"):
        src = os.path.join(pack_dir, fn)
        if os.path.isfile(src):
            n = _copy(src, os.path.join(out_dir, fn), subst)
            if fn.endswith(".txt") and n > CHAT_SOFT_LIMIT:
                print("  warn: chat instructions are %d chars (soft limit %d)" % (n, CHAT_SOFT_LIMIT))


def build_coach_pack(core_dir: str, skills, out_dir: str, version: str = "") -> List[Tuple[str, int]]:
    rules = [(f, _read(os.path.join(core_dir, f))) for f in ("shared/operating-rules.md", "shared/output-conventions.md")]
    method = [(f, _read(os.path.join(core_dir, f))) for f in ("methodology/spine.md", "methodology/rhythms.md")]
    frame = [("methodology/frameworks.md", _read(os.path.join(core_dir, "methodology/frameworks.md")))]
    # Only the product's own skills: a company's local skills can hold company facts and must never reach a shared coach pack.
    core_sk = [s for s in skills if getattr(s, "origin", "core") == "core"]
    sk = [(s.name, s.raw) for s in core_sk if s.metadata.get("layer") == "pricing"]
    sys_sk = [(s.name, s.raw) for s in core_sk if s.metadata.get("layer") != "pricing"]
    sources = [("Operating rules and output conventions", assemble("Operating rules and output conventions", rules)),
               ("Spine and rhythms", assemble("The pricing spine and rhythms", method)),
               ("Frameworks and sources", assemble("Frameworks and sources", frame)),
               ("Skill procedures", assemble("Pricing skill procedures", sk, "What each skill does, step by step. A notebook cannot run these skills or their scripts.")),
               ("System skill procedures", assemble("System skill procedures", sys_sk))]
    written = write_sources(out_dir, sources)
    _finish(out_dir, os.path.join(core_dir, "notebook-packs", "pricing-coach"), {})
    write_readme(out_dir, "Pricing coach (version %s)" % version,
                 "Method questions, quizzes and onboarding for the pricing desk. Contains no company data.", written, False)
    return written


def _md_files(base: str) -> List[str]:
    out = []
    if not os.path.isdir(base):
        return out
    for dp, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for f in sorted(files):
            if f.endswith(".md") and not f.startswith(".") and f.lower() != "readme.md":
                out.append(os.path.join(dp, f))
    return out


def _csv_table(path: str, max_rows: int = 400) -> str:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return ""
    head, body = rows[0], rows[1:max_rows + 1]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join((c.replace("|", "/") for c in r)) + " |" for r in body]
    if len(rows) - 1 > max_rows:
        out.append("\n(%d more rows not shown)" % (len(rows) - 1 - max_rows))
    return "\n".join(out)


def build_company_pack(root: str, core_dir: str, out_dir: str) -> List[Tuple[str, int]]:
    cl = os.path.join(root, "workspace", "context-library")
    if not os.path.isdir(cl):
        raise SystemExit("workspace/context-library not found")
    rel = lambda p, b: os.path.relpath(p, b)
    sources = []
    top = [os.path.join(cl, f) for f in sorted(os.listdir(cl)) if f.endswith(".md")]
    if top:
        sources.append(("Company context", assemble("Company context", [(rel(f, cl), _read(f)) for f in top],
                                                    "Files still marked status: template hold no company facts; every value in them is Unknown.")))
    an = _md_files(os.path.join(cl, "analogs"))
    if an:
        sources.append(("Analogs", assemble("Analog library", [(rel(f, cl), _read(f)) for f in an])))
    pb = os.path.join(root, "workspace", "price-book")
    tables = []
    if os.path.isdir(pb):
        for f in sorted(os.listdir(pb)):
            if f.endswith(".csv"):
                tables.append((f, _csv_table(os.path.join(pb, f))))
    if tables:
        sources.append(("Price book", assemble("Price book (tables from CSV)", tables)))
    dl = os.path.join(root, "workspace", "outputs", "decision-log.md")
    if os.path.isfile(dl):
        sources.append(("Decision log", assemble("Decision log", [("decision-log.md", _read(dl))])))
    if not sources:
        raise SystemExit("nothing to pack in workspace/")
    written = write_sources(out_dir, sources)
    _finish(out_dir, os.path.join(core_dir, "notebook-packs", "company-playbook"), {})
    write_readme(out_dir, "Company pricing playbook", "Company context, price book and decisions for desk Q&A and onboarding.", written, True)
    return written


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def valid_slug(account: str) -> bool:
    return bool(SLUG_RE.match(account)) and ".." not in account


def build_account_pack(root: str, core_dir: str, account: str, out_dir: str) -> List[Tuple[str, int]]:
    if not valid_slug(account):
        raise SystemExit("account %r is not a folder slug (lower-case letters, digits, dot, dash, underscore; no path separators)" % account)
    ad = os.path.join(root, "workspace", "accounts", account)
    if not os.path.isdir(ad):
        raise SystemExit("account folder not found: workspace/accounts/%s" % account)
    files = _md_files(ad)
    if not files:
        raise SystemExit("no markdown files in workspace/accounts/%s" % account)
    today = dt.date.today().isoformat()
    sources = [("Account material", assemble("%s: account pricing material" % account, [(os.path.relpath(f, ad), _read(f)) for f in files],
                                             "Compiled %s from workspace/accounts/%s." % (today, account)))]
    written = write_sources(out_dir, sources)
    _finish(out_dir, os.path.join(core_dir, "notebook-packs", "account-room"), {"account": account, "date": today})
    write_readme(out_dir, "Account room: %s" % account, "Pricing material for one account, compiled %s." % today, written, True)
    return written
