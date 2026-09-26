import tempfile
import textwrap
import unittest
from pathlib import Path

from frappe_ecc import shield


def rules(code, suffix=".py"):
	code = textwrap.dedent(code)
	path = Path("sample" + suffix)
	found = shield.scan_python(path, code) if suffix == ".py" else shield.scan_js(path, code)
	return [f.rule for f in found]


class TestPythonRules(unittest.TestCase):
	def test_sql_string_building(self):
		for query in ('f"select * from tabX where name={name}"', '"select %s" % name', '"a {}".format(x)', '"select " + name'):
			with self.subTest(query):
				self.assertIn("sql-string-building", rules(f"import frappe\nfrappe.db.sql({query})"))

	def test_parameterised_sql_is_fine(self):
		code = 'frappe.db.sql("select name from tabX where a=%(a)s", {"a": a})\nfrappe.db.sql("select " "name")'
		self.assertEqual(rules(code), [])

	def test_commit_in_controller_hook_only(self):
		code = """
		class Foo(Document):
			def validate(self):
				frappe.db.commit()

		def background_job():
			frappe.db.commit()
		"""
		self.assertEqual(rules(code), ["commit-in-controller"])

	def test_guest_api(self):
		code = """
		@frappe.whitelist(allow_guest=True)
		def signup(email):
			frappe.get_doc({"doctype": "Lead", "email": email}).insert(ignore_permissions=True)
		"""
		self.assertEqual(sorted(rules(code)), ["guest-api-no-rate-limit", "guest-ignore-permissions"])
		limited = """
		@frappe.whitelist(allow_guest=True)
		@frappe.rate_limit(limit=5, seconds=60)
		def ping():
			return "pong"
		"""
		self.assertEqual(rules(limited), [])

	def test_ignore_permissions_in_api(self):
		code = """
		@frappe.whitelist()
		def close(name):
			frappe.get_doc("ToDo", name).save(ignore_permissions=True)
		"""
		self.assertEqual(rules(code), ["api-ignore-permissions"])

	def test_queries_in_loops(self):
		code = """
		for n in names:
			frappe.get_doc("ToDo", n)
		rows = [frappe.db.get_value("ToDo", n, "status") for n in names]
		"""
		self.assertEqual(rules(code), ["query-in-loop", "query-in-loop"])

	def test_loop_outside_function_does_not_leak_into_it(self):
		code = """
		for n in names:
			def helper():
				return frappe.get_doc("ToDo", "x")
		"""
		self.assertEqual(rules(code), [])

	def test_misc(self):
		self.assertEqual(rules("doc.docstatus = 1"), ["docstatus-assignment"])
		self.assertEqual(rules("eval(user_input)"), ["eval-exec"])
		self.assertEqual(rules("subprocess.run(cmd, shell=True)"), ["subprocess-shell"])
		self.assertEqual(rules('api_key = "sk_live_1234567890"'), ["hardcoded-secret"])
		self.assertEqual(rules("try:\n\tx()\nexcept Exception:\n\tpass"), ["swallowed-exception"])

	def test_ignore_marker(self):
		self.assertEqual(rules("eval(expr)  # shield: ignore"), [])

	def test_syntax_error_is_reported(self):
		self.assertEqual(rules("def broken(:\n"), ["syntax-error"])


class TestJsRules(unittest.TestCase):
	def test_js(self):
		self.assertEqual(rules("eval(x);", ".js"), ["js-eval"])
		self.assertEqual(rules("el.innerHTML = data.name;", ".js"), ["js-unescaped-html"])
		self.assertEqual(rules("// eval(x)", ".js"), [])
		self.assertEqual(rules("if (a.innerHTML == b) {}", ".js"), [])


class TestScanDirectory(unittest.TestCase):
	def test_skips_vendor_dirs_but_not_names_containing_env(self):
		with tempfile.TemporaryDirectory() as tmp:
			root = Path(tmp)
			(root / "node_modules").mkdir()
			(root / "node_modules" / "x.js").write_text("eval(a)")
			(root / "environment_tools").mkdir()
			(root / "environment_tools" / "a.py").write_text("eval(a)")
			found = shield.scan(root)
			self.assertEqual([Path(f.file).parent.name for f in found], ["environment_tools"])

	def test_threshold(self):
		findings = [shield.Finding("r", s, "f", 1, "m", "x") for s in shield.SEVERITIES]
		self.assertEqual(len(shield.at_or_above(findings, "high")), 2)


if __name__ == "__main__":
	unittest.main()
