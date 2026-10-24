"""Adversarial tests for the fixes made after the four independent reviews of PR #7.
Each test feeds a script or tool the bad input a real user could produce and checks it fails loudly, or refuses."""
import copy
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "core", "skills")
PDOS = os.path.join(ROOT, "tools", "pdos.py")
HOOK = os.path.join(ROOT, "core", "hooks", "guard_pricing_files.py")
sys.path.insert(0, ROOT)


def run(*args, cwd=None, env=None, stdin=None):
    return subprocess.run([sys.executable, "-I"] + list(args), capture_output=True, text=True, cwd=cwd or ROOT, env=env, input=stdin)


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def pdos(cwd, *args):
    return subprocess.run([sys.executable, PDOS] + list(args), capture_output=True, text=True, cwd=cwd)


def inst_pdos(inst, *args):
    """Run the instance's own copy of the tool, as a company would (the tool works on the folder it lives in)."""
    return subprocess.run([sys.executable, os.path.join(inst, "tools", "pdos.py")] + list(args), capture_output=True, text=True, cwd=inst)


class TmpCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = self._td.name
        self.addCleanup(self._td.cleanup)

    def path(self, *p):
        return os.path.join(self.td, *p)


class TestPriceBookChecker(TmpCase):
    CHECK = os.path.join(SK, "price-book-builder", "scripts", "check_price_book.py")
    EXAMPLE = os.path.join(SK, "price-book-builder", "examples", "price-book-example.csv")

    def rows(self):
        with open(self.EXAMPLE, newline="") as fh:
            rd = csv.DictReader(fh)
            return list(rd), rd.fieldnames

    def check(self, mutate, mode="strategy"):
        rows, fields = self.rows()
        mutate(rows)
        p = self.path("pb.csv")
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fields)
            w.writeheader()
            w.writerows(rows)
        return run(self.CHECK, "--pricebook", p, "--mode", mode)

    def test_example_passes(self):
        r = run(self.CHECK, "--pricebook", self.EXAMPLE)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_duplicate_line_id_is_an_error(self):
        r = self.check(lambda rs: rs[1].update(line_id=rs[0]["line_id"]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("duplicated", r.stdout)

    def test_negative_price_is_an_error(self):
        r = self.check(lambda rs: rs[0].update(list_price="-5"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("positive", r.stdout)

    def test_text_and_nan_prices_are_errors(self):
        for bad in ("abc", "nan", "inf"):
            r = self.check(lambda rs, b=bad: rs[0].update(list_price=b))
            self.assertEqual(r.returncode, 1, bad)
            self.assertIn("list_price", r.stdout)

    def test_floor_above_list_is_an_error(self):
        r = self.check(lambda rs: rs[0].update(floor_price="999999"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("above list", r.stdout)

    def test_unknown_right_is_flagged(self):
        r = self.check(lambda rs: rs[0].update(conferred_right="made_up_right"))
        self.assertIn("not one of the nine rights", r.stdout)

    def test_release_mode_rejects_a_right_that_is_only_assumed(self):
        r = self.check(lambda rs: rs[0].update(right_basis="assumed"), mode="release")
        self.assertEqual(r.returncode, 1)
        self.assertIn("assumed", r.stdout)

    def test_missing_file_is_a_clean_error(self):
        r = run(self.CHECK, "--pricebook", self.path("nope.csv"))
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("Cannot read", r.stderr)


class TestImporterAndDiffFailCleanly(TmpCase):
    IMPORT = os.path.join(SK, "price-book-import", "scripts", "import_price_book.py")
    DIFF = os.path.join(SK, "price-book-release", "scripts", "price_book_diff.py")
    NEW = os.path.join(SK, "price-book-release", "examples", "price-book-new.csv")

    def test_importer_missing_file(self):
        r = run(self.IMPORT, "--in", self.path("nope.csv"), "--out-dir", self.path("out"))
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)

    def test_diff_missing_file(self):
        r = run(self.DIFF, "--old", self.path("nope.csv"), "--new", self.NEW)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)

    def test_diff_file_without_line_id(self):
        p = self.path("bad.csv")
        with open(p, "w") as fh:
            fh.write("sku,price\nA,1\n")
        r = run(self.DIFF, "--old", p, "--new", self.NEW)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("line_id", r.stderr)


class TestCorridorRequiresCompanyValues(TmpCase):
    SCRIPT = os.path.join(SK, "data-price-setting", "scripts", "price_corridor.py")
    EXAMPLE = os.path.join(SK, "data-price-setting", "examples", "air-shopping-insights.json")

    def go(self, mutate):
        with open(self.EXAMPLE) as fh:
            d = json.load(fh)
        mutate(d)
        p = self.path("in.json")
        with open(p, "w") as fh:
            json.dump(d, fh)
        return run(self.SCRIPT, "--in", p)

    def test_example_runs(self):
        self.assertEqual(self.go(lambda d: None).returncode, 0)

    def test_each_required_value_stops_the_run(self):
        cases = {"min_margin_pct": lambda d: d["cost"].pop("min_margin_pct"),
                 "royalty_pct": lambda d: d["cost"].pop("royalty_pct"),
                 "cannibalization_per_unit": lambda d: d["cost"].pop("cannibalization_per_unit"),
                 "max_capture_share": lambda d: d["value"].pop("max_capture_share")}
        for name, mut in cases.items():
            r = self.go(mut)
            self.assertEqual(r.returncode, 2, name)
            self.assertIn(name, r.stderr)

    def test_royalty_plus_margin_at_or_above_one_is_refused(self):
        def mut(d):
            d["cost"]["royalty_pct"], d["cost"]["min_margin_pct"] = 0.6, 0.4
        r = self.go(mut)
        self.assertEqual(r.returncode, 2)
        self.assertIn("below 1", r.stderr)

    def test_nan_and_negative_costs_are_refused(self):
        r = self.go(lambda d: d["cost"].update(variable_per_unit=-1))
        self.assertEqual(r.returncode, 2)
        r = self.go(lambda d: d["cost"].update(annual_fixed="lots"))
        self.assertEqual(r.returncode, 2)


class TestHarvestInputErrors(TmpCase):
    SCRIPT = os.path.join(SK, "api-access-request", "scripts", "harvest_screen.py")

    def screen(self, body, *extra):
        p = self.path("keys.csv")
        with open(p, "w") as fh:
            fh.write("key_id,customer,searches,bookings\n" + body)
        return run(self.SCRIPT, "--in", p, "--default-median", "20", *extra)

    def test_blank_count_is_not_zero(self):
        r = self.screen("K1,Acme,,5\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("blank is not zero", r.stderr)

    def test_negative_and_impossible_counts_stop(self):
        self.assertEqual(self.screen("K1,Acme,-5,0\n").returncode, 2)
        r = self.screen("K1,Acme,10,50\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("exceed", r.stderr)

    def test_no_threshold_means_nothing_is_flagged(self):
        r = self.screen("K1,Acme,100000,1\n")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("pattern to confirm", r.stdout)

    def test_flag_wording_never_alleges_misuse(self):
        r = self.screen("K1,Acme,100000,1\n", "--multiple", "5")
        self.assertIn("pattern to confirm with the account owner", r.stdout)
        for word in ("scrap", "abuse", "violat", "fraud"):
            self.assertNotIn(word, r.stdout.lower())


GUARD_CASES = [
    ("workspace/price-book/price-book.csv", "line_id,status\nL1,Approved\n"),
    ("/home/claude/pricing-desk/workspace/outputs/memo.md", "Title\n\nStatus: Approved\n"),
    ("outputs/council-pack.md", "**Status:** Approved\n"),
]


class TestGuardHook(TmpCase):
    def call(self, payload, env=None, raw=None):
        e = dict(os.environ)
        e.pop("PRICING_DESK_COUNCIL", None)
        e.update(env or {})
        r = subprocess.run([sys.executable, HOOK], input=raw if raw is not None else json.dumps(payload),
                           capture_output=True, text=True, env=e, cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    @staticmethod
    def denied(out):
        return out.get("decision") == "deny" or out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    def test_claude_code_write_is_denied(self):
        for path, content in GUARD_CASES:
            out = self.call({"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": path, "content": content}})
            self.assertTrue(self.denied(out), path)
            self.assertIn("hookSpecificOutput", out)

    def test_gemini_write_file_is_denied(self):
        out = self.call({"tool_name": "write_file", "tool_input": {"file_path": "workspace/outputs/x.md", "content": "Status: Approved"}})
        self.assertEqual(out["decision"], "deny")

    def test_edit_and_multiedit_that_add_approved_are_denied(self):
        p = self.path("workspace", "outputs", "pack.md")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as fh:
            fh.write("Status: Draft\nbody\n")
        edit = {"tool_name": "Edit", "tool_input": {"file_path": p, "old_string": "Status: Draft", "new_string": "Status: Approved"}}
        self.assertTrue(self.denied(self.call(edit)))
        multi = {"tool_name": "MultiEdit", "tool_input": {"file_path": p, "edits": [{"old_string": "body", "new_string": "more"},
                                                                                   {"old_string": "Status: Draft", "new_string": "status: approved"}]}}
        self.assertTrue(self.denied(self.call(multi)))
        gem = {"tool_name": "replace", "tool_input": {"file_path": p, "old_string": "Status: Draft", "new_string": "Status: Approved"}}
        self.assertTrue(self.denied(self.call(gem)))

    def test_editing_other_text_of_an_approved_record_is_allowed(self):
        p = self.path("workspace", "outputs", "decision-log.md")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as fh:
            fh.write("Status: Approved\nnote one\n")
        edit = {"tool_name": "Edit", "tool_input": {"file_path": p, "old_string": "note one", "new_string": "note two"}}
        self.assertFalse(self.denied(self.call(edit)))

    def test_product_source_and_unrelated_files_are_not_guarded(self):
        for path in ("/home/claude/pricing-desk/core/templates/council-pack.md", "docs/security-and-governance.md", "tools/notes.md",
                     "src/readme.md"):
            out = self.call({"tool_name": "Write", "tool_input": {"file_path": path, "content": "Status: Approved"}})
            self.assertFalse(self.denied(out), path)

    def test_council_override(self):
        out = self.call({"tool_name": "Write", "tool_input": {"file_path": "workspace/price-book/price-book.csv", "content": "line_id,status\nL1,Approved\n"}},
                        env={"PRICING_DESK_COUNCIL": "1"})
        self.assertFalse(self.denied(out))

    def test_garbage_input_allows_rather_than_blocks(self):
        for raw in ("", "not json", "[]", "null", '{"tool_name": "Write"}'):
            out = self.call(None, raw=raw)
            self.assertFalse(self.denied(out), raw)

    def test_draft_and_proposed_are_allowed(self):
        out = self.call({"tool_name": "Write", "tool_input": {"file_path": "workspace/outputs/x.md", "content": "Status: Draft\nStatus: For decision\n"}})
        self.assertFalse(self.denied(out))


class TestInstanceTooling(TmpCase):
    def make(self):
        inst = self.path("inst")
        r = pdos(ROOT, "new-instance", inst, "--client", "Test Co")
        self.assertEqual(r.returncode, 0, r.stderr)
        return inst

    def test_upgrade_refuses_the_product_folder_itself(self):
        r = pdos(ROOT, "upgrade-instance", ROOT)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("product folder", r.stdout + r.stderr)

    def test_upgrade_keeps_workspace_and_local_and_writes_a_backup(self):
        inst = self.make()
        mark = self.path("inst", "workspace", "context-library", "mine.md")
        with open(mark, "w") as fh:
            fh.write("company fact\n")
        lk = self.path("inst", "local", "skills", "mine")
        os.makedirs(lk)
        with open(os.path.join(lk, "SKILL.md"), "w") as fh:
            fh.write("---\nname: mine\ndescription: Use when testing.\n---\n")
        with open(self.path("inst", "core", "shared", "operating-rules.md"), "a") as fh:
            fh.write("\nLOCAL TAMPER\n")
        r = pdos(ROOT, "upgrade-instance", inst)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(read(mark), "company fact\n")
        self.assertTrue(os.path.isfile(os.path.join(lk, "SKILL.md")))
        self.assertNotIn("LOCAL TAMPER", read(self.path("inst", "core", "shared", "operating-rules.md")))
        backups = self.path("inst", ".upgrade-backups")
        self.assertTrue(os.path.isdir(backups) and os.listdir(backups))

    def test_build_leaves_company_notebook_packs_alone(self):
        inst = self.make()
        packs = self.path("inst", "workspace", "outputs", "notebook-packs", "company-playbook")
        os.makedirs(packs)
        keep = os.path.join(packs, "keep.txt")
        with open(keep, "w") as fh:
            fh.write("do not delete\n")
        r = inst_pdos(inst, "build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.isfile(keep))

    def test_local_skill_never_reaches_the_coach_pack(self):
        inst = self.make()
        lk = self.path("inst", "local", "skills", "secret-floor")
        os.makedirs(lk)
        with open(os.path.join(lk, "SKILL.md"), "w") as fh:
            fh.write("---\nname: secret-floor\ndescription: Use when testing the coach pack leak.\nmetadata:\n  layer: pricing\n---\n# Secret\nZZZ-COMPANY-FLOOR-9999\n")
        r = inst_pdos(inst, "build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # positive control: the local skill is built for the company's own agent, just not into the shared pack
        self.assertIn("ZZZ-COMPANY-FLOOR-9999", read(self.path("inst", "skills", "secret-floor", "SKILL.md")))
        src = self.path("inst", "dist", "notebook-packs", "pricing-coach", "sources")
        self.assertTrue(os.listdir(src))
        for f in os.listdir(src):
            self.assertNotIn("ZZZ-COMPANY-FLOOR-9999", read(os.path.join(src, f)))

    def test_every_compiled_skill_ships_the_closing_check(self):
        for name in os.listdir(os.path.join(ROOT, "skills")):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "skills", name, "references", "output-check.md")), name)

    def test_every_skill_has_a_slash_command(self):
        base = os.path.join(ROOT, "commands", "pricing")
        text = "\n".join(read(os.path.join(base, f)) for f in os.listdir(base) if f.endswith(".toml"))
        for name in os.listdir(os.path.join(ROOT, "skills")):
            self.assertIn("Use the %s skill" % name, text, name)


class TestNotebookGuards(TmpCase):
    def inst(self):
        inst = self.path("inst")
        self.assertEqual(pdos(ROOT, "new-instance", inst, "--client", "Test Co").returncode, 0)
        return inst

    def test_bad_account_slugs_are_refused(self):
        inst = self.inst()
        for bad in ("../../etc", "a/b", "/abs", "..", "Upper", ""):
            r = inst_pdos(inst, "notebook-pack", "--account", bad)
            self.assertNotEqual(r.returncode, 0, bad)

    def test_out_must_be_inside_outputs_or_dist(self):
        inst = self.inst()
        os.makedirs(os.path.join(inst, "workspace", "accounts", "atlas"))
        with open(os.path.join(inst, "workspace", "accounts", "atlas", "s.md"), "w") as fh:
            fh.write("# Atlas\n")
        for bad in (self.path("elsewhere"), os.path.join(inst, "workspace", "context-library"), os.path.join(inst, "workspace", "outputs"),
                    os.path.join(inst, "workspace", "outputs", "..", "accounts")):
            r = inst_pdos(inst, "notebook-pack", "--account", "atlas", "--out", bad)
            self.assertNotEqual(r.returncode, 0, bad)
        self.assertTrue(os.path.isdir(os.path.join(inst, "workspace", "context-library")))

    def test_non_empty_foreign_folder_is_not_cleared(self):
        inst = self.inst()
        os.makedirs(os.path.join(inst, "workspace", "accounts", "atlas"))
        with open(os.path.join(inst, "workspace", "accounts", "atlas", "s.md"), "w") as fh:
            fh.write("# Atlas\n")
        target = os.path.join(inst, "workspace", "outputs", "mine")
        os.makedirs(os.path.join(target, "sources"))
        keep = os.path.join(target, "sources", "important.md")
        with open(keep, "w") as fh:
            fh.write("keep\n")
        r = inst_pdos(inst, "notebook-pack", "--account", "atlas", "--out", target)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(os.path.isfile(keep))

    def test_rerun_replaces_stale_sources(self):
        inst = self.inst()
        acc = os.path.join(inst, "workspace", "accounts", "atlas")
        os.makedirs(acc)
        with open(os.path.join(acc, "s.md"), "w") as fh:
            fh.write("# Atlas\n")
        self.assertEqual(inst_pdos(inst, "notebook-pack", "--account", "atlas").returncode, 0)
        out = os.path.join(inst, "workspace", "outputs", "notebook-packs", "account-atlas", "sources")
        stale = os.path.join(out, "99-stale.md")
        with open(stale, "w") as fh:
            fh.write("old\n")
        self.assertEqual(inst_pdos(inst, "notebook-pack", "--account", "atlas").returncode, 0)
        self.assertFalse(os.path.exists(stale))


class TestLintAndSkillRules(TmpCase):
    def test_lint_of_a_missing_file_is_an_error(self):
        r = pdos(ROOT, "lint", self.path("nope.md"))
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)

    def test_include_paths_must_stay_inside_core(self):
        from tools.pdos.skills import safe_include
        for bad in ("../secrets.md", "/etc/passwd", "a/../../b", "C:\\x", "..\\x"):
            self.assertFalse(safe_include(bad), bad)
        for ok in ("shared/operating-rules.md", "templates/deal-package.md", "rubrics/output-check.md"):
            self.assertTrue(safe_include(ok), ok)

    def test_script_numeric_defaults_are_caught(self):
        from tools.pdos.skills import SCRIPT_DEFAULT_RE
        self.assertTrue(SCRIPT_DEFAULT_RE.search('ap.add_argument("--multiple", type=float, default=5)'))
        self.assertTrue(SCRIPT_DEFAULT_RE.search('x = cfg.get("max_discount", 15)'))
        self.assertFalse(SCRIPT_DEFAULT_RE.search('x = cfg.get("count", 0)'))
        self.assertFalse(SCRIPT_DEFAULT_RE.search('ap.add_argument("--in", required=True)'))

    def test_body_threshold_lint_catches_new_phrasings(self):
        from tools.pdos.skills import THRESHOLD_RE
        for line in ("escalate above 20 percent", "keep at least 3 deals", "a 2x multiple", "within 14 days", "top 10 customers"):
            self.assertTrue(THRESHOLD_RE.search(line), line)


class TestTriageFailsClosed(TmpCase):
    SCRIPT = os.path.join(SK, "deal-desk-triage", "scripts", "triage_rank.py")
    HEAD = "request_id,account,product,request_type,tcv,requested_discount_pct,received,due,anchor_deal\n"

    def go(self, body, *extra):
        p = self.path("r.csv")
        with open(p, "w") as fh:
            fh.write(self.HEAD + body)
        return run(self.SCRIPT, "--in", p, "--today", "2026-10-24", *extra)

    def row(self, out, rid):
        return [ln for ln in out.splitlines() if "| " + rid + " |" in ln][0]

    def test_no_band_sends_every_discount_to_review(self):
        r = self.go("R-1,Acme,API,standard,1000,5%,2026-10-20,2026-10-30,\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NO BAND ON FILE", r.stdout)
        self.assertIn("deal-desk-review", self.row(r.stdout, "R-1"))
        self.assertNotIn("quote from the price book", self.row(r.stdout, "R-1"))

    def test_a_standard_label_cannot_skip_review_when_over_band(self):
        r = self.go("R-1,Acme,API,standard,1000,22,2026-10-20,2026-10-30,\n", "--band-pct", "10")
        self.assertIn("deal-desk-review", self.row(r.stdout, "R-1"))
        self.assertIn("exceeds band", self.row(r.stdout, "R-1"))

    def test_anchor_deal_goes_through_account_price_fit(self):
        r = self.go("R-1,Acme,API,non_standard_quote,1000,5,2026-10-20,2026-10-30,yes\n", "--band-pct", "10")
        self.assertIn("account-price-fit", self.row(r.stdout, "R-1"))

    def test_bad_rows_are_listed_not_dropped(self):
        r = self.go("R-1,Acme,API,standard,lots,5,2026-10-20,2026-10-30,\nR-2,Acme,API,standard,1000,0,2026-10-20,2026-10-30,\n", "--band-pct", "10")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("R-1", r.stdout)
        self.assertIn("R-2", r.stdout)

    def test_bad_date_and_missing_columns_stop(self):
        p = self.path("r.csv")
        with open(p, "w") as fh:
            fh.write("request_id,account\nR-1,Acme\n")
        self.assertEqual(run(self.SCRIPT, "--in", p, "--today", "2026-10-24").returncode, 2)
        self.assertEqual(run(self.SCRIPT, "--in", p, "--today", "24/10/2026").returncode, 2)


class TestAccountWaterfallFailsClosed(TmpCase):
    SCRIPT = os.path.join(SK, "account-price-fit", "scripts", "account_waterfall.py")
    EXAMPLE = os.path.join(SK, "account-price-fit", "examples", "atlas-example.json")

    def go(self, mutate):
        with open(self.EXAMPLE) as fh:
            d = json.load(fh)
        mutate(d)
        p = self.path("in.json")
        with open(p, "w") as fh:
            json.dump(d, fh)
        return run(self.SCRIPT, "--in", p)

    def test_example_runs(self):
        self.assertEqual(self.go(lambda d: None).returncode, 0)

    def test_zero_or_missing_term_stops(self):
        for mut in (lambda d: d.pop("term_months"), lambda d: d.update(term_months=0), lambda d: d.update(term_months="three")):
            self.assertEqual(self.go(mut).returncode, 2)

    def test_not_a_number_stops(self):
        r = self.go(lambda d: d["anchor"].update(annual_revenue="lots"))
        self.assertEqual(r.returncode, 2)

    def test_report_never_says_approved(self):
        r = self.go(lambda d: None)
        self.assertNotIn("Status: Approved", r.stdout)


if __name__ == "__main__":
    unittest.main()
