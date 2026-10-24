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

    def test_spelling_cannot_hide_a_bad_right_or_a_cliff(self):
        r = self.check(lambda rs: rs[0].update(conferred_right="Resell_Everything"), mode="release")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not one of the nine rights", r.stdout)
        # a recognised right in another case is read as that right, so its keeping terms are still demanded
        r = self.check(lambda rs: rs[1].update(conferred_right="Redistribution_Resale", minimum_commitment="", retention_term="", audit_right=""), mode="release")
        self.assertEqual(r.returncode, 1)
        self.assertIn("minimum_commitment", r.stdout)

    def test_tier_model_typo_and_case_variants(self):
        def cliff(rs, model):
            base = dict(rs[0])
            a, b = dict(base), dict(base)
            a.update(line_id="T1", tier_min="1", tier_max="1000", list_price="500", floor_price="400", tier_model=model)
            b.update(line_id="T2", tier_min="1001", tier_max="", list_price="499", floor_price="400", tier_model=model)
            del rs[:]
            rs.extend([a, b])
        r = self.check(lambda rs: cliff(rs, "All_Units"))
        self.assertIn("volume cliff", r.stdout)
        r = self.check(lambda rs: cliff(rs, "gradutaed"))
        self.assertIn("tier_model", r.stdout)

    def test_key_variants_do_not_hide_duplicates(self):
        def dup(rs):
            rs[1].update({k: rs[0][k] for k in ("product_id", "conferred_right", "delivery", "tier_min", "tier_max")})
            rs[1].update(unit=rs[0]["unit"].upper(), currency=rs[0]["currency"].lower(), term_months=rs[0]["term_months"] + ".0")
        r = self.check(dup)
        self.assertIn("duplicate line", r.stdout)

    def test_blank_product_id_and_shifted_columns(self):
        r = self.check(lambda rs: rs[0].update(product_id=""))
        self.assertEqual(r.returncode, 1)
        self.assertIn("product_id is blank", r.stdout)
        p = self.path("shift.csv")
        with open(self.EXAMPLE) as fh:
            lines = fh.read().splitlines()
        lines[1] = lines[1].replace("Air Shopping Market Insights", "Air Shopping, Market Insights")
        with open(p, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        r = run(self.CHECK, "--pricebook", p)
        self.assertEqual(r.returncode, 1)
        self.assertIn("more cells", r.stdout)

    def test_decimal_comma_is_refused_not_multiplied(self):
        r = self.check(lambda rs: rs[0].update(list_price="1,5"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("decimal comma", r.stdout)
        self.assertEqual(self.check(lambda rs: rs[0].update(list_price="3,000", floor_price="2,000")).returncode, 0)

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

    def test_name_variants_roll_up_to_one_customer(self):
        body = "".join("k%d,%s,500000,50,100,\n" % (i, n) for i, n in enumerate(("Acme Travel", "ACME Travel", "Acme Travel Inc."), 1))
        p = self.path("k.csv")
        with open(p, "w") as fh:
            fh.write("key_id,customer,searches,bookings\n" + "".join("k%d,%s,500000,50\n" % (i, n) for i, n in enumerate(("Acme Travel", "ACME Travel", "Acme Travel Inc."), 1)))
        r = run(self.SCRIPT, "--in", p, "--default-median", "20", "--multiple", "5", "--min-volume", "1000000")
        by_customer = r.stdout.split("## By key")[0]
        self.assertEqual(by_customer.count("| Acme Travel |"), 1)
        self.assertIn("pattern to confirm", by_customer)
        self.assertIn("treated as one customer", r.stdout)

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

    def test_gemini_before_tool_payload_gets_the_gemini_deny_shape(self):
        out = self.call({"hook_event_name": "BeforeTool", "tool_name": "write_file",
                         "tool_input": {"file_path": "workspace/outputs/x.md", "content": "Status: Approved"}})
        self.assertEqual(out.get("decision"), "deny")
        self.assertNotIn("hookSpecificOutput", out)

    def test_decided_is_the_councils_word_too(self):
        for content in ("Status: Decided\n", "**Status:** decided\n"):
            out = self.call({"tool_name": "Write", "tool_input": {"file_path": "workspace/outputs/x.md", "content": content}})
            self.assertTrue(self.denied(out), content)

    def test_other_ways_to_write_approved_are_denied(self):
        cases = {
            "workspace/price-book/pb.csv": ["line_id,status\nL1,Approved by Council\n", "line_id,Approval_Status\nL1,Council Approved\n",
                                            "line_id,status\nL1,Approved.\n", "line_id;price;status\nL1;5;Approved\n"],
            "workspace/outputs/x.md": ["| Status | Approved |\n", "Status - Approved\n", "- **Status**: Approved\n", "status = approved\n"],
            "workspace/outputs/x.json": ['{"\\u0073tatus": "approved"}', '{"approval_status": "Approved"}', '{"a": [{"status": "Decided"}]}'],
            "workspace/outputs/x.markdown": ["Status: Approved\n"],
            "workspace/outputs/NOTES": ["Status: Approved\n"],
        }
        for path, contents in cases.items():
            for content in contents:
                out = self.call({"tool_name": "Write", "tool_input": {"file_path": path, "content": content}})
                self.assertTrue(self.denied(out), (path, content))

    def test_swapping_which_row_is_approved_is_denied(self):
        p = self.path("workspace", "price-book", "pb.csv")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as fh:
            fh.write("line_id,status\nL1,Approved\nL2,Draft\n")
        out = self.call({"tool_name": "Write", "tool_input": {"file_path": p, "content": "line_id,status\nL1,Draft\nL2,Approved\n"}})
        self.assertTrue(self.denied(out))

    def test_symlink_with_an_innocent_name_is_judged_by_its_target(self):
        target = self.path("price-book.csv")
        with open(target, "w") as fh:
            fh.write("line_id,status\nL1,Draft\n")
        link = self.path("notes.csv")
        os.symlink(target, link)
        out = self.call({"tool_name": "Write", "tool_input": {"file_path": link, "content": "line_id,status\nL1,Approved\n"}})
        self.assertTrue(self.denied(out))

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

    def test_dist_is_refused_so_the_coach_pack_cannot_be_overwritten(self):
        inst = self.inst()
        os.makedirs(os.path.join(inst, "workspace", "accounts", "atlas"))
        with open(os.path.join(inst, "workspace", "accounts", "atlas", "s.md"), "w") as fh:
            fh.write("# Atlas\n")
        for out in (os.path.join(inst, "dist", "notebook-packs", "pricing-coach"), os.path.join(inst, "dist", "x")):
            self.assertNotEqual(inst_pdos(inst, "notebook-pack", "--account", "atlas", "--out", out).returncode, 0, out)

    def test_links_leading_outside_the_account_folder_are_not_packed(self):
        inst = self.inst()
        acc = os.path.join(inst, "workspace", "accounts", "atlas")
        os.makedirs(acc)
        with open(os.path.join(acc, "s.md"), "w") as fh:
            fh.write("# Atlas\n")
        secret = self.path("outside_secret.md")
        with open(secret, "w") as fh:
            fh.write("ZZZ-OUTSIDE-SECRET\n")
        os.symlink(secret, os.path.join(acc, "link.md"))
        r = inst_pdos(inst, "notebook-pack", "--account", "atlas")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        src = os.path.join(inst, "workspace", "outputs", "notebook-packs", "account-atlas", "sources")
        for f in os.listdir(src):
            self.assertNotIn("ZZZ-OUTSIDE-SECRET", read(os.path.join(src, f)))

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


class TestImporterHonesty(TmpCase):
    IMPORT = os.path.join(SK, "price-book-import", "scripts", "import_price_book.py")
    SRC = ("Product,Category,Type,Unit,Band,Price,Floor,License Type,FY Revenue,Accounts\n"
           "Fare Data,Data,Data License,per year,1-1000,EUR 5.00,3,Enterprise,1000,5\n"
           "Fare Data,Data,Data License,per year,1001-5000,\u20ac4.00,3,Enterprise,2000,6\n"
           "Search API,API,,per call,all,$0.10,,Internal Use Only,500,2\n"
           "Shop API,API,api,per call,all,0.20,,,-,1\n")

    def go(self, *extra):
        src = self.path("in.csv")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(self.SRC)
        out = self.path("out")
        r = run(self.IMPORT, "--in", src, "--out-dir", out, *extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(out, "price_book.csv"), newline="", encoding="utf-8") as fh:
            book = list(csv.DictReader(fh))
        with open(os.path.join(out, "product_rights_handoff.csv"), newline="", encoding="utf-8") as fh:
            hand = list(csv.DictReader(fh))
        with open(os.path.join(out, "import_report.md"), encoding="utf-8") as fh:
            report = fh.read()
        return book, hand, report

    def test_a_label_that_is_not_a_right_is_not_called_stated(self):
        book, _, report = self.go()
        fare = [b for b in book if b["product_id"] == "Fare Data"]
        self.assertTrue(all(b["conferred_right"] == "" and b["right_basis"] == "" for b in fare))
        self.assertIn("'Enterprise' is not one of the nine rights", report)

    def test_a_recognised_right_in_other_words_is_read(self):
        book, _, _ = self.go()
        search = [b for b in book if b["product_id"] == "Search API"][0]
        self.assertEqual((search["conferred_right"], search["right_basis"]), ("internal_use", "stated"))

    def test_currency_named_in_the_price_cell_is_kept(self):
        book, _, report = self.go()
        self.assertEqual({b["currency"] for b in book if b["product_id"] == "Fare Data"}, {"EUR"})
        search = [b for b in book if b["product_id"] == "Search API"][0]
        self.assertEqual(search["currency"], "")
        self.assertIn("no --default-currency", report)

    def test_data_license_type_reaches_the_rights_handoff(self):
        book, hand, _ = self.go()
        self.assertEqual({b["product_type"] for b in book if b["product_id"] == "Fare Data"}, {"data_license"})
        self.assertIn("Fare Data", {h["product_id"] for h in hand})

    def test_term_and_tier_model_are_not_invented(self):
        book, _, report = self.go()
        self.assertTrue(all(b["term_months"] == "" and b["tier_model"] == "" for b in book))
        self.assertIn("Unknown, not assumed", report)

    def test_revenue_that_differs_by_tier_row_is_kept_and_flagged(self):
        book, _, report = self.go()
        fare = [b for b in book if b["product_id"] == "Fare Data"]
        self.assertEqual([b["annual_revenue"] for b in fare], ["1000.0", "2000.0"])
        self.assertIn("revenue differs between tier rows", report)

    def test_bad_map_values_stop_the_run(self):
        src = self.path("in.csv")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(self.SRC)
        mp = self.path("map.json")
        with open(mp, "w") as fh:
            json.dump({"types": {"Fare Data": "feed"}}, fh)
        r = run(self.IMPORT, "--in", src, "--out-dir", self.path("o2"), "--map", mp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not one of the allowed values", r.stderr)


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

    def test_a_blank_discount_is_unknown_not_zero(self):
        r = self.go("R-1,Acme,API,standard,1000,,2026-10-20,2026-10-30,\n", "--band-pct", "10")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.row(r.stdout, "R-1")
        self.assertIn("Unknown", row)
        self.assertNotIn("quote from the price book", row)
        self.assertIn("ask the requester", row)

    def test_over_band_data_licence_gets_its_right_priced_first(self):
        r = self.go("R-1,Acme,Feed,data_licence,1000,30,2026-10-20,2026-10-30,\n", "--band-pct", "10")
        row = self.row(r.stdout, "R-1")
        self.assertIn("data-license-pricing", row)
        self.assertIn("deal-desk-review", row)

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

    def route_of(self, r, name):
        return [ln for ln in r.stdout.splitlines() if ln.startswith("| " + name + " |")][0]

    def test_a_concession_through_the_anchor_is_not_at_list(self):
        def mut(d):
            d["options"] = [{"name": "Quiet", "price": d["addon"]["list_price"], "incentive_change_annual": 300000,
                             "anchor_revenue_change_annual": -200000}]
        r = self.go(mut)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ESCALATE", self.route_of(r, "Quiet"))
        self.assertIn("concession through the anchor", r.stdout)

    def test_a_cap_that_cannot_be_checked_escalates(self):
        def mut(d):
            d["anchor"].pop("annual_list_value")
            d["options"] = [{"name": "Disc", "price": d["addon"]["list_price"] * 0.95, "incentive_change_annual": 0,
                             "gets": [{"name": "term", "annual_value": 10 ** 9}]}]
        r = self.go(mut)
        self.assertIn("ESCALATE", self.route_of(r, "Disc"))
        self.assertIn("cap cannot be checked", r.stdout)

    def test_a_get_with_no_value_is_not_called_a_give_tied_to_a_get(self):
        def mut(d):
            d["options"] = [{"name": "Disc", "price": d["addon"]["list_price"] * 0.95, "incentive_change_annual": 0, "gets": ["goodwill"]}]
        r = self.go(mut)
        self.assertNotIn("a give tied to a get", self.route_of(r, "Disc"))
        self.assertIn("NO VALUED GET", self.route_of(r, "Disc"))

    def test_product_type_and_currency_are_required(self):
        self.assertEqual(self.go(lambda d: d["addon"].pop("product_type")).returncode, 2)
        self.assertEqual(self.go(lambda d: d.pop("currency")).returncode, 2)

    def test_extra_ramp_entries_are_reported_not_dropped(self):
        def mut(d):
            d["options"] = [{"name": "Long", "price": d["addon"]["list_price"], "incentive_change_annual": 0, "ramp": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}]
        r = self.go(mut)
        self.assertIn("extra entries are ignored", r.stdout)

    def test_report_never_says_approved(self):
        r = self.go(lambda d: None)
        self.assertNotIn("Status: Approved", r.stdout)


class TestDiffAndRightsList(TmpCase):
    DIFF = os.path.join(SK, "price-book-release", "scripts", "price_book_diff.py")
    RIGHTS = os.path.join(SK, "rights-handoff", "scripts", "rights_list.py")
    HEAD = "line_id,product_id,product_type,%s,unit,tier_min,tier_max,list_price,floor_price,currency,term_months,status\n"

    def write(self, name, col, body):
        p = self.path(name)
        with open(p, "w") as fh:
            fh.write(self.HEAD % col + body)
        return p

    def test_legacy_use_right_column_changes_are_seen(self):
        old = self.write("o.csv", "use_right", "L1,P1,api_access,internal_use,call,1,,1,0.5,USD,12,Existing\n")
        new = self.write("n.csv", "use_right", "L1,P1,api_access,redistribution_resale,call,1,,1,0.5,USD,12,Existing\n")
        r = run(self.DIFF, "--old", old, "--new", new)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("conferred_right", r.stdout)
        self.assertIn("redistribution_resale", r.stdout)

    def test_blank_line_id_stops_the_comparison(self):
        old = self.write("o.csv", "conferred_right", "L1,P1,api_access,internal_use,call,1,,1,0.5,USD,12,Existing\n")
        new = self.write("n.csv", "conferred_right", ",P1,api_access,internal_use,call,1,,0.1,0.5,USD,12,Existing\n")
        r = run(self.DIFF, "--old", old, "--new", new)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("blank line_id", r.stderr)

    def test_spelling_only_changes_are_not_changes(self):
        old = self.write("o.csv", "conferred_right", "L1,P1,api_access,internal_use,call,1,,1,0.5,USD,12,Existing\n")
        new = self.write("n.csv", "conferred_right", "L1,P1,api_access,Internal_Use,call,1,,1.0,0.5,usd,12.0,existing\n")
        r = run(self.DIFF, "--old", old, "--new", new)
        self.assertIn("0 field change", r.stdout)

    def test_rights_list_flags_unusable_numbers_and_unknown_rights(self):
        p = self.path("pb.csv")
        with open(p, "w") as fh:
            fh.write("line_id,product_id,product_type,conferred_right,annual_revenue,customers\n"
                     "L1,P1,api_access,internal_use,nan,3\n"
                     "L2,P2,api_access,Resell_Everything,100,1\n")
        r = run(self.RIGHTS, "--pricebook", p)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("nan |", r.stdout)
        self.assertIn("not usable numbers", r.stdout)
        self.assertIn("not one of the nine rights", r.stdout)


class TestSmallGuards(TmpCase):
    def test_client_name_cannot_break_the_files(self):
        for bad in ('A"b', "A\nB", "A{{x}}", "A`b"):
            r = pdos(ROOT, "new-instance", self.path("i"), "--client", bad)
            self.assertNotEqual(r.returncode, 0, repr(bad))
        self.assertFalse(os.path.exists(self.path("i")))

    def test_valuation_needs_a_currency(self):
        src = os.path.join(SK, "data-product-valuation", "examples", "input.json")
        d = json.loads(read(src))
        d.pop("currency")
        p = self.path("v.json")
        with open(p, "w") as fh:
            json.dump(d, fh)
        r = run(os.path.join(SK, "data-product-valuation", "scripts", "valuation.py"), "--in", p)
        self.assertEqual(r.returncode, 2)
        self.assertIn("currency", r.stderr)


if __name__ == "__main__":
    unittest.main()
