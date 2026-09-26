"""Run the real bench pipeline against a generated app and report what happened.

verify() links the app into a bench, installs it on a site, migrates, and runs the
app's tests. Every step records the exact command, exit code and output tail, so
the report shows what ran rather than what was expected to run.
"""

from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlparse

OUTPUT_TAIL = 4000


@dataclass
class Step:
	name: str
	command: list[str]
	returncode: int | None = None
	seconds: float = 0.0
	output: str = ""
	skipped: bool = False

	@property
	def ok(self) -> bool:
		return self.skipped or self.returncode == 0


@dataclass
class Report:
	bench: str
	site: str
	app: str
	steps: list[Step] = field(default_factory=list)
	tests_run: int | None = None
	tests_failed: int | None = None
	error: str = ""

	@property
	def ok(self) -> bool:
		return not self.error and all(s.ok for s in self.steps)

	def to_dict(self) -> dict:
		d = asdict(self)
		d["ok"] = self.ok
		for s, step in zip(d["steps"], self.steps):
			s["ok"] = step.ok
		return d


class BenchError(Exception):
	pass


def find_bench(start: Path) -> Path | None:
	for p in (start, *start.parents):
		if (p / "apps").is_dir() and (p / "sites").is_dir():
			return p
	return None


def app_name_from_path(app_path: Path) -> str:
	pyproject = app_path / "pyproject.toml"
	if pyproject.exists():
		m = re.search(r'^name\s*=\s*"([^"]+)"', pyproject.read_text(), re.MULTILINE)
		if m:
			return m.group(1)
	hooks = list(app_path.glob("*/hooks.py"))
	if len(hooks) == 1:
		return hooks[0].parent.name
	raise BenchError(f"cannot tell the app name for {app_path}: no pyproject.toml name or single */hooks.py")


def _redis_urls(bench: Path) -> dict[str, str]:
	cfg_path = bench / "sites" / "common_site_config.json"
	try:
		cfg = json.loads(cfg_path.read_text())
	except (OSError, json.JSONDecodeError):
		return {}
	return {k: cfg[k] for k in ("redis_cache", "redis_queue") if isinstance(cfg.get(k), str)}


def _reachable(url: str) -> bool:
	parsed = urlparse(url)
	try:
		with socket.create_connection((parsed.hostname or "127.0.0.1", parsed.port or 6379), timeout=2):
			return True
	except OSError:
		return False


def preflight(bench: Path, site: str) -> list[str]:
	"""Problems that would make every bench command fail, in plain words."""
	problems = []
	if not shutil.which("bench"):
		problems.append("the 'bench' command is not on PATH (pip install frappe-bench)")
	if not (bench / "apps" / "frappe").is_dir():
		problems.append(f"{bench} has no apps/frappe; is it a bench directory?")
	if not (bench / "sites" / site / "site_config.json").exists():
		problems.append(
			f"site '{site}' does not exist in {bench}/sites. Create a throwaway one first:\n"
			f"  cd {bench} && bench new-site {site} --admin-password admin"
		)
	for key, url in _redis_urls(bench).items():
		if not _reachable(url):
			problems.append(
				f"{key} at {url} is not reachable. Start it with `bench start` in {bench}, "
				f"or run: redis-server {bench}/config/{key}.conf --daemonize yes"
			)
	return problems


def _run(step: Step, cwd: Path, timeout: int) -> Step:
	start = time.monotonic()
	try:
		proc = subprocess.run(
			step.command,
			cwd=cwd,
			capture_output=True,
			text=True,
			timeout=timeout,
		)
		step.returncode = proc.returncode
		out = (proc.stdout or "") + (proc.stderr or "")
	except subprocess.TimeoutExpired as e:
		step.returncode = -1
		out = f"timed out after {timeout}s\n" + (e.stdout or "" if isinstance(e.stdout, str) else "")
	except FileNotFoundError as e:
		step.returncode = -1
		out = str(e)
	step.seconds = round(time.monotonic() - start, 1)
	step.output = out[-OUTPUT_TAIL:]
	return step


_RAN = re.compile(r"Ran (\d+) tests? in")
_FAILED = re.compile(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?")


def parse_test_counts(output: str) -> tuple[int | None, int | None]:
	ran = _RAN.findall(output)
	total = sum(int(n) for n in ran) if ran else None
	failed = 0
	for failures, errors in _FAILED.findall(output):
		failed += int(failures or 0) + int(errors or 0)
	return total, (failed if total is not None else None)


def verify(
	bench: Path,
	site: str,
	app_path: Path,
	*,
	run_tests: bool = True,
	timeout: int = 1800,
	on_step=None,
) -> Report:
	bench = bench.resolve()
	app_path = app_path.resolve()
	app = app_name_from_path(app_path)
	report = Report(bench=str(bench), site=site, app=app)

	problems = preflight(bench, site)
	if problems:
		report.error = "\n".join(problems)
		return report

	installed_path = bench / "apps" / app
	if not (app_path / ".git").exists() and not installed_path.exists():
		report.error = (
			f"{app_path} is not a git repository, and `bench get-app` needs one. Run:\n"
			f"  cd {app_path} && git init -b main && git add -A && git commit -m 'Initial commit'"
		)
		return report
	steps: list[Step] = []
	if installed_path.exists() or installed_path.is_symlink():
		if installed_path.resolve() != app_path:
			report.error = (
				f"{installed_path} already exists and points to a different app. "
				"Remove it (bench remove-app) or use another bench."
			)
			return report
		steps.append(Step("link app into bench", ["bench", "get-app", "..."], skipped=True, output="already linked"))
	else:
		steps.append(
			Step("link app into bench", ["bench", "get-app", "--soft-link", "--skip-assets", str(app_path)])
		)

	installed_apps = _installed_apps(bench, site)
	if app in installed_apps:
		steps.append(Step("install app on site", ["bench", "--site", site, "install-app", app], skipped=True, output="already installed"))
	else:
		steps.append(Step("install app on site", ["bench", "--site", site, "install-app", app]))
	steps.append(Step("migrate", ["bench", "--site", site, "migrate"]))
	if run_tests:
		steps.append(Step("allow tests on site", ["bench", "--site", site, "set-config", "allow_tests", "true"]))
		steps.append(Step("run app tests", ["bench", "--site", site, "run-tests", "--app", app]))

	for step in steps:
		if not step.skipped:
			_run(step, bench, timeout)
		report.steps.append(step)
		if on_step:
			on_step(step)
		if not step.ok:
			break

	test_step = next((s for s in report.steps if s.name == "run app tests" and not s.skipped), None)
	if test_step:
		report.tests_run, report.tests_failed = parse_test_counts(test_step.output)
		if test_step.returncode == 0 and report.tests_run == 0:
			report.error = "run-tests exited 0 but ran no tests"
	return report


def _installed_apps(bench: Path, site: str) -> list[str]:
	try:
		proc = subprocess.run(
			["bench", "--site", site, "list-apps", "--format", "json"],
			cwd=bench,
			capture_output=True,
			text=True,
			timeout=120,
		)
		data = json.loads(proc.stdout[proc.stdout.find("{") :])
		return list(data.get(site, []))
	except (subprocess.SubprocessError, json.JSONDecodeError, ValueError, OSError):
		return []
