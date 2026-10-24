"""Tests for tools/pdos. Run: python3 -m unittest discover -s tests"""
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from pdos.build import build, diff_trees  # noqa: E402
from pdos.instance import new_instance  # noqa: E402
from pdos.lint import lint_text  # noqa: E402
from pdos.mdparse import split_frontmatter  # noqa: E402
from pdos.skills import discover_skills, validate_collection  # noqa: E402

GOOD = """# Weekly review
**Answer:** Realization fell 1.2 points (I) because of two credits.
**Decision and owner:** Which leaks to chase / pricing lead
Status: Draft      Handling: Internal      Date: 2026-10-24

| Item | Value | Tag |
|---|---|---|
| Realized vs list | 91.4% | F |

## Handoff
Done: review
Not done: root cause
You decide: chase
Watch: credits
"""


class LintTests(unittest.TestCase):
    def codes(self, text):
        return {i.code for i in lint_text(text, "x") if i.level == "error"}

    def test_good_output_has_no_errors(self):
        self.assertEqual(self.codes(GOOD), set())

    def test_missing_answer(self):
        self.assertIn("OL001", self.codes(GOOD.replace("**Answer:**", "Summary:")))

    def test_approved_status_is_an_error(self):
        self.assertIn("OL004", self.codes(GOOD.replace("Status: Draft", "Status: Approved")))

    def test_handoff_needs_four_parts(self):
        self.assertIn("OL007", self.codes(GOOD.replace("Watch: credits\n", "")))

    def test_analog_row_needs_url_and_date(self):
        bad = GOOD + "\n| Analog | Source URL | Accessed |\n|---|---|---|\n| X | none | never |\n"
        self.assertIn("OL008", self.codes(bad))
        ok = GOOD + "\n| Analog | Source URL | Accessed |\n|---|---|---|\n| X | https://example.com | 2026-10-24 |\n"
        self.assertNotIn("OL008", self.codes(ok))


class FrontmatterTests(unittest.TestCase):
    def test_nested_and_folded(self):
        fm, body, err = split_frontmatter("---\nname: a\nmetadata:\n  version: \"1\"\ndescription: >\n  one\n  two\n---\nbody\n")
        self.assertIsNone(err)
        self.assertEqual(fm["metadata"]["version"], "1")
        self.assertEqual(fm["description"], "one two")
        self.assertEqual(body, "body\n")


class RepoTests(unittest.TestCase):
    def test_skills_have_no_errors(self):
        issues = validate_collection(discover_skills(ROOT), ROOT)
        self.assertEqual([str(i) for i in issues if i.level == "error"], [])

    def test_generated_outputs_current(self):
        self.assertEqual(build(ROOT, check=True, quiet=True), 0)

    def test_new_instance_builds_and_protects(self):
        d = tempfile.mkdtemp()
        try:
            dest = os.path.join(d, "inst")
            self.assertEqual(new_instance(ROOT, dest, "Acme"), 0)
            self.assertTrue(os.path.isfile(os.path.join(dest, "workspace", "context-library", "pricing-governance.md")))
            marker = os.path.join(dest, "workspace", "context-library", "business-info.md")
            open(marker, "a").write("\nKEEP ME\n")
            from pdos.instance import upgrade_instance
            self.assertEqual(upgrade_instance(ROOT, dest), 0)
            self.assertIn("KEEP ME", open(marker).read())
            self.assertEqual(build(dest, check=True, quiet=True), 0)
        finally:
            shutil.rmtree(d, ignore_errors=True)



class TestThresholdLint(unittest.TestCase):
    def test_threshold_warning(self):
        import tempfile
        from pdos.skills import load_skill, validate_skill
        with tempfile.TemporaryDirectory() as td:
            d = os.path.join(td, "demo-skill")
            os.makedirs(d)
            open(os.path.join(d, "SKILL.md"), "w").write("---\nname: demo-skill\ndescription: A demo skill that checks things. Use when you test the threshold lint on the skill validator.\nmetadata:\n  version: \"1.0.0\"\n---\n\n# Demo\n\n## When to use\nx\n\n## Procedure\nReopen when costs move more than 20 percent.\n\n## Output\nx\n\n## Quality gate\nx\n")
            issues = validate_skill(load_skill(d), os.path.join(td, "core"))
            self.assertTrue(any(i.code == "SK090" for i in issues))


if __name__ == "__main__":
    unittest.main()
