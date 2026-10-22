"""Behavioral checks: portable assets, safe creation, valid metadata and links."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "create-knowledge-hub"


class CreateHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_generator(self, destination, *extra, script=None):
        return subprocess.run(
            [sys.executable, "-B", str(script or SKILL / "scripts/create_hub.py"),
             "--dest", str(destination), "--id", "test-hub", "--title", "Test knowledge",
             "--kind", "company", "--owner", 'Acme "Turtle" Inc.', "--domain", "Marketing",
             "--hub-category", "competency",
             *extra], cwd=self.root, text=True, capture_output=True,
        )

    def test_portable_skill_produces_independent_hub_with_resolving_links(self):
        copied = self.root / "moved skill"
        shutil.copytree(SKILL, copied)
        destination = self.root / "hub with spaces"
        result = self.run_generator(destination, script=copied / "scripts/create_hub.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads((destination / "hub.json").read_text())
        self.assertEqual(config["owner"], 'Acme "Turtle" Inc.')
        self.assertEqual(config["policy"]["external_actions"], "disabled")
        self.assertEqual(config["policy"]["publication"], "explicit_acceptance")
        self.assertEqual(config["policy"]["remote_copy"], "required_after_validated_task")
        self.assertEqual(config["profile_version"], "0.4.0")
        self.assertEqual(config["policy"]["content_review"], "direct")
        self.assertEqual(config["hub_category"], "competency")
        self.assertRegex(config["hub_key"],
                         r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        self.assertEqual(config["quality"]["evidence_script"], "scripts/check_evidence.py")
        self.assertTrue((destination / "scripts/check_evidence.py").is_file())
        self.assertEqual(config["kind"], "company")
        self.assertIn(".venv/", (destination / ".gitignore").read_text().splitlines())
        self.assertFalse((destination / ".venv").exists())
        self.assertTrue((destination / config["bundle_root"]).is_dir())
        self.assertFalse((destination / config["bundle_root"] / "imports").exists())
        self.assertEqual(json.loads((destination / ".obsidian/app.json").read_text())
                         ["newLinkFormat"], "relative")
        # The generated hub must not retain a dependency on either installation path.
        for path in destination.rglob("*.md"):
            text = path.read_text()
            self.assertNotIn(str(SKILL), text)
            self.assertNotIn(str(copied), text)
            # Schema contains an explicitly illustrative, not-yet-created source path.
            if path.name == "SCHEMA.md":
                continue
            for href in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if not href.startswith(("https:", "http:", "#")):
                    self.assertTrue((path.parent / href).exists(), (path, href))

    def test_dry_run_does_not_create_parent_directories(self):
        destination = self.root / "absent" / "hub"
        result = self.run_generator(destination, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(destination.parent.exists())

    def test_generated_contract_is_self_contained_without_initializing_git(self):
        destination = self.root / 'hub'
        result = self.run_generator(destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('AGENTS.md', 'SCHEMA.md'):
            self.assertEqual((destination / name).read_bytes(),
                             (SKILL / 'assets/hub' / name).read_bytes())
        self.assertFalse((destination / '.git').exists())

    def test_existing_hub_is_preserved(self):
        destination = self.root / "hub"
        self.assertEqual(self.run_generator(destination).returncode, 0)
        before = {p.relative_to(destination): p.read_bytes()
                  for p in destination.rglob("*") if p.is_file()}
        result = self.run_generator(destination)
        self.assertNotEqual(result.returncode, 0)
        after = {p.relative_to(destination): p.read_bytes()
                 for p in destination.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_existing_empty_directory_is_also_refused(self):
        destination = self.root / "hub"
        destination.mkdir()
        self.assertNotEqual(self.run_generator(destination).returncode, 0)
        self.assertEqual(list(destination.iterdir()), [])

    def test_dangling_symlink_is_preserved(self):
        destination = self.root / "hub"
        target = self.root / "missing"
        destination.symlink_to(target, target_is_directory=True)
        self.assertNotEqual(self.run_generator(destination).returncode, 0)
        self.assertTrue(destination.is_symlink())
        self.assertFalse(target.exists())

    def test_invalid_id_and_multiline_metadata_fail_without_writes(self):
        destination = self.root / "hub"
        for extra in [("--id", "../other"), ("--owner", "first\nsecond")]:
            with self.subTest(extra=extra):
                self.assertNotEqual(self.run_generator(destination, *extra).returncode, 0)
                self.assertFalse(destination.exists())

    def test_each_generated_hub_gets_a_distinct_hub_key(self):
        first = self.root / "hub-one"
        second = self.root / "hub-two"
        self.assertEqual(self.run_generator(first).returncode, 0)
        self.assertEqual(self.run_generator(second).returncode, 0)
        key_one = json.loads((first / "hub.json").read_text())["hub_key"]
        key_two = json.loads((second / "hub.json").read_text())["hub_key"]
        self.assertNotEqual(key_one, key_two)

    def test_invalid_hub_category_is_refused(self):
        destination = self.root / "hub"
        result = self.run_generator(destination, "--hub-category", "client")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(destination.exists())

    def test_incomplete_skill_without_validator_is_refused(self):
        copied = self.root / "incomplete-skill"
        shutil.copytree(SKILL, copied)
        (copied / "assets/hub/scripts/validate_hub.py").unlink()
        destination = self.root / "hub"
        result = self.run_generator(destination, script=copied / "scripts/create_hub.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(destination.exists())

    def test_incomplete_skill_without_evidence_script_is_refused(self):
        copied = self.root / "incomplete-skill-evidence"
        shutil.copytree(SKILL, copied)
        (copied / "assets/hub/scripts/check_evidence.py").unlink()
        destination = self.root / "hub"
        result = self.run_generator(destination, script=copied / "scripts/create_hub.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
