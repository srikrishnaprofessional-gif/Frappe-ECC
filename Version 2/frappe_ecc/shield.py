"""Frappe Shield: static checks for security and transaction mistakes in Frappe apps.

Python files are parsed with `ast`; JavaScript files get a few line-based checks.
A finding on a line ending with `# shield: ignore` (or `// shield: ignore`) is skipped.
Shield catches common patterns; it does not prove code is secure.
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "env", "venv", ".venv", "dist", "build", ".tox"}
IGNORE_MARKER = re.compile(r"(#|//)\s*(shield:\s*ignore|nosec)\b")

CONTROLLER_HOOKS = {
	"validate",
	"before_validate",
	"before_insert",
	"after_insert",
	"before_save",
	"on_update",
	"before_submit",
	"on_submit",
	"before_cancel",
	"on_cancel",
	"on_trash",
	"after_delete",
	"on_change",
	"before_rename",
	"after_rename",
	"autoname",
	"before_update_after_submit",
	"on_update_after_submit",
}
SQL_METHODS = {"sql", "multisql", "sql_list", "sql_ddl"}
SECRET_NAME = re.compile(r"(api_?key|secret|password|passwd|token|private_?key)$", re.IGNORECASE)


@dataclass
class Finding:
	rule: str
	severity: str
	file: str
	line: int
	message: str
	fix: str


def _dotted(node: ast.AST) -> str:
	"""'frappe.db.sql' for the call target, '' if not a plain attribute chain."""
	parts = []
	while isinstance(node, ast.Attribute):
		parts.append(node.attr)
		node = node.value
	if isinstance(node, ast.Name):
		parts.append(node.id)
		return ".".join(reversed(parts))
	return ""


def _is_whitelist(dec: ast.AST) -> tuple[bool, bool]:
	"""(is @frappe.whitelist, allow_guest=True)"""
	target = dec.func if isinstance(dec, ast.Call) else dec
	if _dotted(target) not in ("frappe.whitelist", "whitelist"):
		return False, False
	guest = isinstance(dec, ast.Call) and any(
		kw.arg == "allow_guest" and isinstance(kw.value, ast.Constant) and kw.value.value is True
		for kw in dec.keywords
	)
	return True, guest


def _has_rate_limit(decorators: list[ast.expr]) -> bool:
	for dec in decorators:
		target = dec.func if isinstance(dec, ast.Call) else dec
		if _dotted(target).endswith("rate_limit"):
			return True
	return False


def _builds_string(node: ast.AST) -> str | None:
	"""Name the kind of dynamic string building in `node`, or None if it is a plain literal."""
	if isinstance(node, ast.JoinedStr) and any(isinstance(v, ast.FormattedValue) for v in node.values):
		return "an f-string"
	if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
		return "% formatting"
	if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
		if not (_is_literal_str(node.left) and _is_literal_str(node.right)):
			return "string concatenation"
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
		return ".format()"
	return None


def _is_literal_str(node: ast.AST) -> bool:
	if isinstance(node, ast.Constant) and isinstance(node.value, str):
		return True
	if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
		return _is_literal_str(node.left) and _is_literal_str(node.right)
	return False


class _Visitor(ast.NodeVisitor):
	def __init__(self, path: str, lines: list[str]):
		self.path = path
		self.lines = lines
		self.findings: list[Finding] = []
		self.functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
		self.class_depth = 0
		self.loop_depth = 0
		self.whitelisted: list[tuple[bool, bool]] = []  # (whitelisted, guest) per enclosing function

	def add(self, node: ast.AST, rule: str, severity: str, message: str, fix: str) -> None:
		line = getattr(node, "lineno", 0)
		if 0 < line <= len(self.lines) and IGNORE_MARKER.search(self.lines[line - 1]):
			return
		self.findings.append(Finding(rule, severity, self.path, line, message, fix))

	# --- scopes ---
	def visit_ClassDef(self, node: ast.ClassDef) -> None:
		self.class_depth += 1
		self.generic_visit(node)
		self.class_depth -= 1

	def _visit_function(self, node) -> None:
		wl, guest = False, False
		for dec in node.decorator_list:
			w, g = _is_whitelist(dec)
			wl, guest = wl or w, guest or g
		if guest and not _has_rate_limit(node.decorator_list):
			self.add(
				node,
				"guest-api-no-rate-limit",
				"HIGH",
				f"'{node.name}' is callable without login and has no rate limit",
				"Add @rate_limit(limit=..., seconds=...) (from frappe.rate_limiter import rate_limit) and validate every argument.",
			)
		self.functions.append(node)
		self.whitelisted.append((wl, guest))
		outer_loops, self.loop_depth = self.loop_depth, 0
		self.generic_visit(node)
		self.loop_depth = outer_loops
		self.whitelisted.pop()
		self.functions.pop()

	visit_FunctionDef = _visit_function
	visit_AsyncFunctionDef = _visit_function

	def _visit_loop(self, node) -> None:
		self.loop_depth += 1
		self.generic_visit(node)
		self.loop_depth -= 1

	visit_For = _visit_loop
	visit_AsyncFor = _visit_loop
	visit_While = _visit_loop

	visit_ListComp = _visit_loop
	visit_SetComp = _visit_loop
	visit_DictComp = _visit_loop
	visit_GeneratorExp = _visit_loop

	@property
	def in_controller_hook(self) -> bool:
		return bool(self.functions) and self.class_depth > 0 and self.functions[-1].name in CONTROLLER_HOOKS

	@property
	def in_whitelisted(self) -> tuple[bool, bool]:
		return self.whitelisted[-1] if self.whitelisted else (False, False)

	# --- checks ---
	def visit_Call(self, node: ast.Call) -> None:
		name = _dotted(node.func)
		attr = node.func.attr if isinstance(node.func, ast.Attribute) else name

		if name == "frappe.db.commit" and self.in_controller_hook:
			self.add(
				node,
				"commit-in-controller",
				"CRITICAL",
				f"frappe.db.commit() inside '{self.functions[-1].name}' breaks the request's transaction",
				"Remove it. Frappe commits at the end of the request and rolls back on errors.",
			)

		if attr in SQL_METHODS and (name.startswith("frappe.db.") or name.endswith(f"db.{attr}")) and node.args:
			kind = _builds_string(node.args[0])
			if kind:
				self.add(
					node,
					"sql-string-building",
					"HIGH",
					f"SQL passed to {name}() is built with {kind}",
					"Pass values separately: frappe.db.sql(query, {'key': value}) with %(key)s, or use frappe.qb.",
				)
			if self.loop_depth:
				self.add(
					node,
					"query-in-loop",
					"MEDIUM",
					f"{name}() runs once per loop iteration",
					"Fetch all rows in one query before the loop.",
				)

		if name in ("frappe.get_doc", "frappe.get_cached_doc", "frappe.db.get_value") and self.loop_depth:
			self.add(
				node,
				"query-in-loop",
				"MEDIUM",
				f"{name}() runs once per loop iteration (N+1 queries)",
				"Fetch in bulk with frappe.get_all(..., filters={'name': ['in', names]}).",
			)

		for kw in node.keywords:
			if kw.arg == "ignore_permissions" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
				wl, guest = self.in_whitelisted
				if guest:
					self.add(
						node,
						"guest-ignore-permissions",
						"HIGH",
						"ignore_permissions=True in an API that guests can call",
						"Check exactly what the guest may do before bypassing permissions, or require login.",
					)
				elif wl:
					self.add(
						node,
						"api-ignore-permissions",
						"MEDIUM",
						"ignore_permissions=True in a whitelisted API",
						"Call frappe.has_permission()/doc.check_permission() first, or drop ignore_permissions.",
					)
			if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
				if name.startswith("subprocess."):
					self.add(
						node,
						"subprocess-shell",
						"HIGH",
						f"{name}(shell=True) can run injected shell commands",
						"Pass the command as a list and drop shell=True.",
					)

		if name in ("eval", "exec"):
			self.add(
				node,
				"eval-exec",
				"HIGH",
				f"{name}() runs arbitrary code",
				"Use frappe.safe_eval() for expressions, or parse the input explicitly.",
			)

		self.generic_visit(node)

	def visit_Assign(self, node: ast.Assign) -> None:
		for target in node.targets:
			if (
				isinstance(target, ast.Attribute)
				and target.attr == "docstatus"
				and isinstance(node.value, ast.Constant)
				and node.value.value in (1, 2)
			):
				self.add(
					node,
					"docstatus-assignment",
					"HIGH",
					f"docstatus set to {node.value.value} directly, skipping submit/cancel hooks and checks",
					"Call doc.submit() or doc.cancel().",
				)
			tname = target.id if isinstance(target, ast.Name) else getattr(target, "attr", "")
			if (
				tname
				and SECRET_NAME.search(tname)
				and isinstance(node.value, ast.Constant)
				and isinstance(node.value.value, str)
				and len(node.value.value) >= 8
			):
				self.add(
					node,
					"hardcoded-secret",
					"HIGH",
					f"'{tname}' looks like a hard-coded secret",
					"Read it from site config (frappe.conf) or a Password field instead.",
				)
		self.generic_visit(node)

	def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
		if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
			if node.type is None or _dotted(node.type) in ("Exception", "BaseException"):
				self.add(
					node,
					"swallowed-exception",
					"LOW",
					"exception caught and ignored",
					"Catch the specific exception, or log it with frappe.log_error().",
				)
		self.generic_visit(node)


JS_RULES = [
	(
		re.compile(r"\beval\s*\(|new\s+Function\s*\("),
		"js-eval",
		"HIGH",
		"eval()/new Function() runs arbitrary code",
		"Parse the data instead of evaluating it.",
	),
	(
		re.compile(r"\.innerHTML\s*=(?!=)|\.html\(\s*[^)'\"`\s]"),
		"js-unescaped-html",
		"MEDIUM",
		"HTML inserted without escaping may allow XSS",
		"Escape values with frappe.utils.escape_html() or set textContent.",
	),
]


def scan_python(path: Path, text: str | None = None) -> list[Finding]:
	text = path.read_text(encoding="utf-8", errors="replace") if text is None else text
	try:
		tree = ast.parse(text, filename=str(path))
	except SyntaxError as e:
		return [Finding("syntax-error", "HIGH", str(path), e.lineno or 0, f"cannot parse: {e.msg}", "Fix the syntax error.")]
	visitor = _Visitor(str(path), text.splitlines())
	visitor.visit(tree)
	return visitor.findings


def scan_js(path: Path, text: str | None = None) -> list[Finding]:
	text = path.read_text(encoding="utf-8", errors="replace") if text is None else text
	findings = []
	for lineno, line in enumerate(text.splitlines(), 1):
		stripped = line.strip()
		if stripped.startswith("//") or IGNORE_MARKER.search(line):
			continue
		for pattern, rule, severity, message, fix in JS_RULES:
			if pattern.search(line):
				findings.append(Finding(rule, severity, str(path), lineno, message, fix))
	return findings


def iter_files(target: Path):
	if target.is_file():
		yield target
		return
	for root, dirs, files in os.walk(target):
		dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
		for name in sorted(files):
			if name.endswith((".py", ".js")) and not name.endswith(".min.js"):
				yield Path(root) / name


def scan(target: str | Path) -> list[Finding]:
	findings: list[Finding] = []
	for path in iter_files(Path(target)):
		if path.suffix == ".py":
			findings += scan_python(path)
		elif path.suffix == ".js":
			findings += scan_js(path)
	findings.sort(key=lambda f: (SEVERITIES.index(f.severity), f.file, f.line))
	return findings


def at_or_above(findings: list[Finding], threshold: str) -> list[Finding]:
	limit = SEVERITIES.index(threshold.upper())
	return [f for f in findings if SEVERITIES.index(f.severity) <= limit]


def to_dict(findings: list[Finding]) -> dict:
	counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES}
	return {"total": len(findings), "counts": counts, "findings": [asdict(f) for f in findings]}
