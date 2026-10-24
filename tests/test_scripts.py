"""Tests for the calculation scripts inside skills. Each runs the script as a user would."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "core", "skills")


def run(*args):
    return subprocess.run([sys.executable, "-I"] + list(args), capture_output=True, text=True, cwd=ROOT)


class TestHarvestScreen(unittest.TestCase):
    csv = os.path.join(SK, "api-access-request", "examples", "keys.csv")
    script = os.path.join(SK, "api-access-request", "scripts", "harvest_screen.py")

    def test_no_multiple_flags_nothing(self):
        r = run(self.script, "--in", self.csv, "--segment-median-l2b", "100")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Unknown (nothing flagged)", r.stdout)
        self.assertNotIn("possible data collection", r.stdout)
        self.assertIn("threshold Unknown", r.stdout)

    def test_multiple_flags_high_ratio(self):
        r = run(self.script, "--in", self.csv, "--segment-median-l2b", "20", "--multiple", "5")
        self.assertIn("possible data collection, to confirm", r.stdout)

    def test_zero_bookings_listed(self):
        r = run(self.script, "--in", self.csv, "--segment-median-l2b", "100", "--multiple", "5")
        self.assertIn("ratio undefined", r.stdout)


class TestTriage(unittest.TestCase):
    csv = os.path.join(SK, "deal-desk-triage", "examples", "requests.csv")
    script = os.path.join(SK, "deal-desk-triage", "scripts", "triage_rank.py")

    def test_band_unknown_without_flag(self):
        r = run(self.script, "--in", self.csv, "--today", "2026-10-24")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Unknown", r.stdout)

    def test_overdue_first(self):
        r = run(self.script, "--in", self.csv, "--today", "2026-10-24", "--band-pct", "15")
        first = [l for l in r.stdout.splitlines() if l.startswith("| 1 |")][0]
        self.assertIn("R-104", first)


class TestAccountWaterfall(unittest.TestCase):
    script = os.path.join(SK, "account-price-fit", "scripts", "account_waterfall.py")
    ex = os.path.join(SK, "account-price-fit", "examples", "atlas-example.json")

    def test_example_runs(self):
        r = run(self.script, "--in", self.ex)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Hold list", r.stdout)

    def test_missing_band_flagged(self):
        d = json.load(open(self.ex))
        d["discount_band_pct"] = None
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(d, f)
        try:
            r = run(self.script, "--in", f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Unknown", r.stdout)


if __name__ == "__main__":
    unittest.main()
