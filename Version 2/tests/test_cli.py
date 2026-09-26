import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from frappe_ecc import bench, installer
from frappe_ecc.cli import main

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "clinic_management.json"


def run(*argv):
	out, err = io.StringIO(), io.StringIO()
	with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
		code = main(list(argv))
	return code, out.getvalue(), err.getvalue()


class TestCli(unittest.TestCase):
	def test_validate_ok_and_json(self):
		code, out, _ = run("validate", str(EXAMPLE))
		self.assertEqual(code, 0)
		self.assertIn("5 DocType(s)", out)
		code, out, _ = run("validate", str(EXAMPLE), "--json")
		self.assertEqual(json.loads(out)["ok"], True)

	def test_validate_reports_errors(self):
		with tempfile.TemporaryDirectory() as tmp:
			bad = Path(tmp) / "bad.json"
			bad.write_text(json.dumps({"app": {"name": "Bad Name"}, "modules": []}))
			code, _, err = run("validate", str(bad))
			self.assertEqual(code, 1)
			self.assertIn("snake_case", err)
			bad.write_text("{not json")
			code, _, err = run("validate", str(bad))
			self.assertEqual(code, 2)
			self.assertIn("not valid JSON", err)

	def test_new_then_shield_generated_app_is_clean(self):
		with tempfile.TemporaryDirectory() as tmp:
			code, out, _ = run("new", str(EXAMPLE), "--dest", tmp)
			self.assertEqual(code, 0, out)
			app = Path(tmp) / "clinic_management"
			code, out, _ = run("shield", str(app))
			self.assertEqual(code, 0, out)
			self.assertIn("no findings", out)
			code, _, err = run("new", str(EXAMPLE), "--dest", tmp)
			self.assertEqual(code, 1)
			self.assertIn("already exists", err)

	def test_shield_fails_on_high(self):
		with tempfile.TemporaryDirectory() as tmp:
			(Path(tmp) / "api.py").write_text('import frappe\nfrappe.db.sql(f"select {x}")\n')
			code, out, _ = run("shield", tmp)
			self.assertEqual(code, 1)
			self.assertIn("sql-string-building", out)
			code, _, _ = run("shield", tmp, "--fail-on", "critical")
			self.assertEqual(code, 0)

	def test_hook_check_ignores_bad_input(self):
		import sys

		stdin = sys.stdin
		try:
			sys.stdin = io.StringIO("not json")
			self.assertEqual(run("hook-check")[0], 0)
		finally:
			sys.stdin = stdin


class TestBenchHelpers(unittest.TestCase):
	def test_parse_test_counts(self):
		out = "....\nRan 12 tests in 3.2s\n\nFAILED (failures=1, errors=2)\n"
		self.assertEqual(bench.parse_test_counts(out), (12, 3))
		self.assertEqual(bench.parse_test_counts("Ran 4 tests in 1s\n\nOK"), (4, 0))
		self.assertEqual(bench.parse_test_counts("boom"), (None, None))

	def test_app_name_from_generated_app(self):
		with tempfile.TemporaryDirectory() as tmp:
			run("new", str(EXAMPLE), "--dest", tmp)
			self.assertEqual(bench.app_name_from_path(Path(tmp) / "clinic_management"), "clinic_management")

	def test_preflight_reports_missing_site(self):
		with tempfile.TemporaryDirectory() as tmp:
			(Path(tmp) / "apps" / "frappe").mkdir(parents=True)
			(Path(tmp) / "sites").mkdir()
			problems = bench.preflight(Path(tmp), "nosuch.localhost")
			self.assertTrue(any("does not exist" in p for p in problems))


class TestInstaller(unittest.TestCase):
	def test_cursor_rules(self):
		with tempfile.TemporaryDirectory() as tmp:
			installer.install_cursor(Path(tmp), dry_run=False, out=lambda *_: None)
			rules = sorted(p.name for p in (Path(tmp) / ".cursor" / "rules").glob("*.mdc"))
			self.assertIn("frappe-doctypes.mdc", rules)
			text = (Path(tmp) / ".cursor" / "rules" / "frappe-doctypes.mdc").read_text()
			self.assertTrue(text.startswith("---\ndescription: Design Frappe DocTypes"))

	def test_legacy_detection_only_matches_old_files(self):
		with tempfile.TemporaryDirectory() as tmp:
			home = Path(tmp)
			commands = home / ".claude" / "commands"
			commands.mkdir(parents=True)
			(commands / "frappe-doctype.md").write_text("\n# /frappe:doctype\n")
			(commands / "frappe-mine.md").write_text("# /frappe:mine\n")
			(commands / "frappe-api.md").write_text("my own notes")
			found = installer.legacy_paths(home)
			self.assertEqual([p.name for p in found], ["frappe-doctype.md"])


class TestPluginLayout(unittest.TestCase):
	def test_plugin_and_package_versions_match(self):
		from frappe_ecc import __version__

		plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
		self.assertEqual(plugin["version"], __version__)

	def test_agents_and_commands_reference_existing_skills(self):
		import re

		skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
		agents = {p.stem for p in (ROOT / "agents").glob("*.md")}
		for path in list((ROOT / "agents").glob("*.md")) + list((ROOT / "commands").glob("*.md")):
			text = path.read_text()
			for ref in re.findall(r"skills/([a-z0-9-]+)/SKILL\.md", text):
				self.assertIn(ref, skills, f"{path.name} references missing skill {ref}")
			for ref in re.findall(r"\*\*(frappe-[a-z-]+)\*\* agent", text):
				self.assertIn(ref, agents, f"{path.name} references missing agent {ref}")


if __name__ == "__main__":
	unittest.main()
