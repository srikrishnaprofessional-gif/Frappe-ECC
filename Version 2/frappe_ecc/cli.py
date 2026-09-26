"""frappe-ecc command line.

  frappe-ecc validate SPEC                 check a spec against Frappe's DocType rules
  frappe-ecc new SPEC [--dest DIR]         generate an installable app from a spec
  frappe-ecc add-doctypes SPEC APP_PATH    add the spec's DocTypes to an existing app
  frappe-ecc shield [PATH]                 scan Python/JS for security and transaction mistakes
  frappe-ecc verify APP_PATH --site SITE   install, migrate and test the app on a real bench
  frappe-ecc install claude|cursor         install the Claude Code plugin or Cursor rules
  frappe-ecc uninstall claude
  frappe-ecc doctor                        check the local toolchain
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from frappe_ecc import __version__, bench, generator, installer, shield, spec


def _reconfigure_stdio() -> None:
	for stream in (sys.stdout, sys.stderr):
		if hasattr(stream, "reconfigure"):
			stream.reconfigure(encoding="utf-8", errors="replace")


def _load_and_validate(path: str, quiet: bool = False) -> tuple[dict | None, spec.ValidationResult | None]:
	try:
		raw = spec.load_spec(path)
	except spec.SpecError as e:
		print(f"error: {e}", file=sys.stderr)
		return None, None
	normalised = spec.normalise(raw)
	result = spec.validate(normalised)
	if not quiet:
		for w in result.warnings:
			print(f"warning: {w}", file=sys.stderr)
		for e in result.errors:
			print(f"error: {e}", file=sys.stderr)
	return normalised, result


def cmd_validate(args) -> int:
	normalised, result = _load_and_validate(args.spec, quiet=args.json)
	if result is None:
		return 2
	if args.json:
		print(json.dumps({"ok": result.ok, "errors": result.errors, "warnings": result.warnings}, indent=2))
	elif result.ok:
		count = sum(1 for _ in spec.iter_doctypes(normalised))
		print(f"OK: {normalised['app']['name']} with {count} DocType(s), {len(result.warnings)} warning(s)")
	return 0 if result.ok else 1


def cmd_new(args) -> int:
	normalised, result = _load_and_validate(args.spec)
	if result is None or not result.ok:
		print("Fix the errors above, then run again.", file=sys.stderr)
		return 1
	dest = Path(args.dest).resolve()
	try:
		written = generator.generate_app(normalised, dest, with_ci=args.ci, force=args.force)
	except generator.GenerateError as e:
		print(f"error: {e}", file=sys.stderr)
		return 1
	root = dest / normalised["app"]["name"]
	print(f"Created {root} ({len(written)} files)")
	if not args.no_git:
		try:
			if generator.init_git(root, normalised["app"]["publisher"], normalised["app"]["email"]):
				print("Initialised a git repository with the generated files as the first commit.")
			else:
				print("git not found: run `git init` in the app before `bench get-app`, which needs a git repo.")
		except generator.GenerateError as e:
			print(f"warning: {e}", file=sys.stderr)
	print("Next: frappe-ecc verify", root, "--bench <bench-dir> --site <site>")
	return 0


def cmd_add_doctypes(args) -> int:
	normalised, result = _load_and_validate(args.spec)
	if result is None or not result.ok:
		print("Fix the errors above, then run again.", file=sys.stderr)
		return 1
	app_root = Path(args.app_path).resolve()
	try:
		expected = bench.app_name_from_path(app_root)
	except bench.BenchError as e:
		print(f"error: {e}", file=sys.stderr)
		return 1
	if expected != normalised["app"]["name"]:
		print(f"error: spec app.name is '{normalised['app']['name']}' but {app_root} is '{expected}'", file=sys.stderr)
		return 1
	try:
		written = generator.add_doctypes(normalised, app_root, overwrite=args.force)
	except generator.GenerateError as e:
		print(f"error: {e}", file=sys.stderr)
		return 1
	for path in written:
		print(f"  {path.relative_to(app_root)}")
	print(f"Wrote {len(written)} files. Run `bench --site <site> migrate` to sync them.")
	return 0


def cmd_shield(args) -> int:
	target = Path(args.path)
	if not target.exists():
		print(f"error: {target} does not exist", file=sys.stderr)
		return 2
	findings = shield.scan(target)
	failing = shield.at_or_above(findings, args.fail_on) if args.fail_on != "none" else []
	if args.json:
		print(json.dumps(shield.to_dict(findings), indent=2))
	else:
		for f in findings:
			print(f"{f.severity:8} {f.file}:{f.line}  [{f.rule}] {f.message}\n         fix: {f.fix}")
		counts = shield.to_dict(findings)["counts"]
		summary = ", ".join(f"{n} {s.lower()}" for s, n in counts.items() if n) or "no findings"
		print(f"\nFrappe Shield: {summary}.")
		if failing:
			print(f"FAILED: {len(failing)} finding(s) at {args.fail_on.upper()} or above.")
	return 1 if failing else 0


def cmd_hook_check(args) -> int:
	"""Claude Code PostToolUse hook: report HIGH/CRITICAL findings in the edited file.

	Exit code 2 sends stderr back to Claude so it can fix the problem; 0 stays silent.
	"""
	try:
		payload = json.load(sys.stdin)
	except (json.JSONDecodeError, ValueError):
		return 0
	path = Path(((payload.get("tool_input") or {}).get("file_path")) or "")
	if path.suffix not in (".py", ".js") or not path.is_file():
		return 0
	findings = shield.at_or_above(shield.scan(path), "high")
	if not findings:
		return 0
	print(f"Frappe Shield found {len(findings)} issue(s) in {path}:", file=sys.stderr)
	for f in findings:
		print(f"- line {f.line} [{f.severity}] {f.message}. Fix: {f.fix}", file=sys.stderr)
	print("Fix these, or add '# shield: ignore' on the line if the code is intentional.", file=sys.stderr)
	return 2


def cmd_verify(args) -> int:
	app_path = Path(args.app_path).resolve()
	bench_dir = Path(args.bench).resolve() if args.bench else bench.find_bench(Path.cwd())
	if not bench_dir:
		print("error: not inside a bench; pass --bench <bench-dir>", file=sys.stderr)
		return 2

	def show(step: bench.Step) -> None:
		if args.json:
			return
		status = "skip" if step.skipped else ("ok" if step.ok else "FAIL")
		print(f"  [{status:4}] {step.name} ({step.seconds}s): {' '.join(step.command)}")
		if not step.ok:
			print("         " + step.output.strip().replace("\n", "\n         "))

	try:
		report = bench.verify(bench_dir, args.site, app_path, run_tests=not args.skip_tests, timeout=args.timeout, on_step=show)
	except bench.BenchError as e:
		print(f"error: {e}", file=sys.stderr)
		return 2

	if args.report:
		Path(args.report).write_text(json.dumps(report.to_dict(), indent=2))
	if args.json:
		print(json.dumps(report.to_dict(), indent=2))
		return 0 if report.ok else 1

	if report.error:
		print(f"\n{report.error}")
	if report.tests_run is not None:
		print(f"\nTests: {report.tests_run} ran, {report.tests_failed} failed or errored.")
	print("VERIFIED" if report.ok else "NOT VERIFIED", f"- {report.app} on {report.site}")
	return 0 if report.ok else 1


def cmd_install(args) -> int:
	if args.target == "claude":
		return installer.install_claude(args.scope, args.dry_run, args.keep_legacy)
	return installer.install_cursor(Path(args.project).resolve(), args.dry_run)


def cmd_uninstall(args) -> int:
	return installer.uninstall_claude(args.dry_run)


def cmd_doctor(args) -> int:
	print(f"Frappe ECC {__version__}")
	return installer.doctor()


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="frappe-ecc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("--version", action="version", version=f"frappe-ecc {__version__}")
	sub = parser.add_subparsers(dest="command", required=True)

	p = sub.add_parser("validate", help="check a spec")
	p.add_argument("spec")
	p.add_argument("--json", action="store_true")
	p.set_defaults(func=cmd_validate)

	p = sub.add_parser("new", help="generate an app from a spec")
	p.add_argument("spec")
	p.add_argument("--dest", default=".", help="directory to create the app in (default: current)")
	p.add_argument("--ci", action="store_true", help="add a GitHub Actions workflow that runs the tests")
	p.add_argument("--force", action="store_true", help="overwrite files in an existing app directory")
	p.add_argument("--no-git", action="store_true", help="don't initialise a git repository")
	p.set_defaults(func=cmd_new)

	p = sub.add_parser("add-doctypes", help="add a spec's DocTypes to an existing app")
	p.add_argument("spec")
	p.add_argument("app_path")
	p.add_argument("--force", action="store_true", help="overwrite existing DocType files")
	p.set_defaults(func=cmd_add_doctypes)

	p = sub.add_parser("shield", help="scan code for security and transaction mistakes")
	p.add_argument("path", nargs="?", default=".")
	p.add_argument("--json", action="store_true")
	p.add_argument(
		"--fail-on",
		default="high",
		choices=["critical", "high", "medium", "low", "none"],
		help="exit 1 when a finding is at or above this severity (default: high)",
	)
	p.set_defaults(func=cmd_shield)

	p = sub.add_parser("verify", help="install, migrate and test an app on a real bench site")
	p.add_argument("app_path")
	p.add_argument("--site", required=True, help="a throwaway site; tests write data to it")
	p.add_argument("--bench", help="bench directory (default: the bench containing the current directory)")
	p.add_argument("--skip-tests", action="store_true")
	p.add_argument("--timeout", type=int, default=1800, help="seconds per step")
	p.add_argument("--report", help="also write the JSON report to this file")
	p.add_argument("--json", action="store_true")
	p.set_defaults(func=cmd_verify)

	p = sub.add_parser("install", help="install into Claude Code or Cursor")
	p.add_argument("target", choices=["claude", "cursor"])
	p.add_argument("--scope", default="user", choices=["user", "project", "local"], help="Claude Code scope")
	p.add_argument("--project", default=".", help="project directory for Cursor rules")
	p.add_argument("--keep-legacy", action="store_true", help="leave files from pre-v3 installers in place")
	p.add_argument("--dry-run", action="store_true")
	p.set_defaults(func=cmd_install)

	p = sub.add_parser("uninstall", help="remove the Claude Code plugin")
	p.add_argument("target", choices=["claude"])
	p.add_argument("--dry-run", action="store_true")
	p.set_defaults(func=cmd_uninstall)

	p = sub.add_parser("hook-check", help=argparse.SUPPRESS)
	p.set_defaults(func=cmd_hook_check)

	p = sub.add_parser("doctor", help="check the local toolchain")
	p.set_defaults(func=cmd_doctor)
	return parser


def main(argv: list[str] | None = None) -> int:
	_reconfigure_stdio()
	args = build_parser().parse_args(argv)
	return args.func(args)
