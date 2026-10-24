import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pdos(cwd, *args):
    return subprocess.run([sys.executable, os.path.join(ROOT, "tools", "pdos.py")] + list(args), capture_output=True, text=True, cwd=cwd)


class TestNotebook(unittest.TestCase):
    def test_coach_pack_built(self):
        d = os.path.join(ROOT, "dist", "notebook-packs", "pricing-coach")
        self.assertTrue(os.path.isfile(os.path.join(d, "chat-instructions.txt")))
        self.assertTrue(len(os.listdir(os.path.join(d, "sources"))) >= 4)
        self.assertLess(len(open(os.path.join(d, "chat-instructions.txt")).read()), 3000)

    def test_company_and_account_packs(self):
        with tempfile.TemporaryDirectory() as td:
            inst = os.path.join(td, "inst")
            r = pdos(ROOT, "new-instance", inst, "--client", "Test Co")
            self.assertEqual(r.returncode, 0, r.stderr)
            os.makedirs(os.path.join(inst, "workspace", "accounts", "atlas"), exist_ok=True)
            with open(os.path.join(inst, "workspace", "accounts", "atlas", "sheet.md"), "w") as f:
                f.write("# Atlas\nStatus: Draft\n")
            r = subprocess.run([sys.executable, os.path.join(inst, "tools", "pdos.py"), "notebook-pack", "--company"], capture_output=True, text=True, cwd=inst)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("deal desk", r.stdout)
            r = subprocess.run([sys.executable, os.path.join(inst, "tools", "pdos.py"), "notebook-pack", "--account", "atlas"], capture_output=True, text=True, cwd=inst)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            readme = open(os.path.join(inst, "workspace", "outputs", "notebook-packs", "account-atlas", "README.md")).read()
            self.assertIn("CONFIDENTIAL", readme)

    def test_missing_account_fails(self):
        with tempfile.TemporaryDirectory() as td:
            inst = os.path.join(td, "inst")
            pdos(ROOT, "new-instance", inst, "--client", "Test Co")
            r = subprocess.run([sys.executable, os.path.join(inst, "tools", "pdos.py"), "notebook-pack", "--account", "nope"], capture_output=True, text=True, cwd=inst)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
