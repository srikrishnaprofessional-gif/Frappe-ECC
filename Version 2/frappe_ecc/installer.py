"""Install Frappe ECC into Claude Code (as a plugin) or Cursor (as rules)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

MARKETPLACE = "frappe-ecc"
PLUGIN_ID = f"frappe-ecc@{MARKETPLACE}"

# Files that installers before v3 copied into ~/.claude/commands.
LEGACY_COMMANDS = (
	"accessibility api audit auto bench build-and-push build-e2e chat-data client-script controller "
	"cron dashboard deploy doctype e2e-test fixtures gdpr heal help helpdesk hld hook i18n "
	"import-sheets lld manual-qa migrate notify ocr patch plan portal predict print-format "
	"prompt-to-app prototype pwa rbac report review saas security sla sop test tour training voice "
	"white-label wireframe workflow"
).split()


def plugin_root() -> Path:
	"""The plugin directory (contains .claude-plugin/plugin.json); this package lives inside it."""
	return Path(__file__).resolve().parent.parent


def marketplace_root() -> Path:
	"""The nearest directory at or above the plugin that holds .claude-plugin/marketplace.json."""
	for p in (plugin_root(), *plugin_root().parents):
		if (p / ".claude-plugin" / "marketplace.json").exists():
			return p
	raise SystemExit(
		f"No .claude-plugin/marketplace.json found at or above {plugin_root()}. "
		"Run the installer from a git clone of the Frappe ECC repo."
	)


def _claude(*args: str) -> subprocess.CompletedProcess:
	return subprocess.run(["claude", *args], capture_output=True, text=True)


def legacy_paths(home: Path) -> list[Path]:
	"""Leftovers from installers before v3, only where they are clearly ours."""
	found = []
	old_plugin = home / ".claude" / "plugins" / "frappe-ecc"
	if (old_plugin / "frappe_ecc_agents").is_dir() or (old_plugin / "bin" / "frappe_ecc_install.py").exists():
		found.append(old_plugin)
	commands = home / ".claude" / "commands"
	for name in LEGACY_COMMANDS:
		path = commands / f"frappe-{name}.md"
		if path.is_file() and re.search(rf"^# /frappe:{re.escape(name)}\s*$", path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE):
			found.append(path)
	return found


def remove_legacy(home: Path, dry_run: bool, out=print) -> None:
	for path in legacy_paths(home):
		out(f"  remove old install: {path}")
		if dry_run:
			continue
		if path.is_dir():
			shutil.rmtree(path)
		else:
			path.unlink()


def install_claude(scope: str, dry_run: bool, keep_legacy: bool, out=print) -> int:
	root = marketplace_root()
	if not shutil.which("claude"):
		out("Claude Code's `claude` command was not found. Inside Claude Code, run:")
		out(f"  /plugin marketplace add {root}")
		out(f"  /plugin install {PLUGIN_ID}")
		return 1

	if not keep_legacy:
		remove_legacy(Path.home(), dry_run, out)

	listed = _claude("plugin", "marketplace", "list").stdout
	steps = []
	if not re.search(rf"^\s*❯?\s*{re.escape(MARKETPLACE)}\b", listed, re.MULTILINE):
		steps.append(["plugin", "marketplace", "add", str(root), "--scope", scope])
	else:
		steps.append(["plugin", "marketplace", "update", MARKETPLACE])
	steps.append(["plugin", "install", PLUGIN_ID, "--scope", scope])

	for args in steps:
		out(f"  claude {' '.join(args)}")
		if dry_run:
			continue
		proc = _claude(*args)
		text = (proc.stdout + proc.stderr).strip()
		if proc.returncode != 0 and "already" not in text.lower():
			out(text)
			return proc.returncode
		if text:
			out("    " + text.replace("\n", "\n    "))
	out("Done. Restart Claude Code, then type /frappe-ecc: to see the commands.")
	return 0


def uninstall_claude(dry_run: bool, out=print) -> int:
	if not shutil.which("claude"):
		out(f"`claude` not found. Inside Claude Code run: /plugin uninstall {PLUGIN_ID}")
		return 1
	for args in (["plugin", "uninstall", PLUGIN_ID], ["plugin", "marketplace", "remove", MARKETPLACE]):
		out(f"  claude {' '.join(args)}")
		if not dry_run:
			proc = _claude(*args)
			out("    " + (proc.stdout + proc.stderr).strip())
	return 0


def install_cursor(project: Path, dry_run: bool, out=print) -> int:
	"""Write the rules and skills as Cursor project rules in <project>/.cursor/rules."""
	root = plugin_root()
	dest = project / ".cursor" / "rules"
	sources = sorted((root / "rules").glob("*.md")) + sorted((root / "skills").glob("*/SKILL.md"))
	for src in sources:
		text = src.read_text(encoding="utf-8")
		name = src.parent.name if src.name == "SKILL.md" else src.stem
		description, body = _split_frontmatter(text)
		globs = "**/*.py,**/*.js,**/*.json" if src.name != "SKILL.md" else ""
		always = "true" if src.name != "SKILL.md" else "false"
		mdc = f"---\ndescription: {description or name}\nglobs: {globs}\nalwaysApply: {always}\n---\n{body}"
		target = dest / f"{name}.mdc"
		out(f"  write {target}")
		if not dry_run:
			target.parent.mkdir(parents=True, exist_ok=True)
			target.write_text(mdc, encoding="utf-8")
	return 0


def _split_frontmatter(text: str) -> tuple[str, str]:
	if text.startswith("---\n"):
		end = text.find("\n---", 4)
		if end != -1:
			head = text[4:end]
			m = re.search(r"^description:\s*(.+)$", head, re.MULTILINE)
			return (m.group(1).strip() if m else ""), text[end + 4 :].lstrip("\n")
	return "", text


def doctor(out=print) -> int:
	ok = True

	def check(label: str, passed: bool, hint: str = "") -> None:
		nonlocal ok
		ok = ok and passed
		out(f"  [{'ok' if passed else '!!'}] {label}" + (f"\n       {hint}" if hint and not passed else ""))

	check(f"Python {sys.version.split()[0]} (3.10+)", sys.version_info >= (3, 10), "Install Python 3.10 or later.")
	check("bench on PATH", bool(shutil.which("bench")), "pip install frappe-bench")
	has_claude = bool(shutil.which("claude"))
	check("Claude Code (`claude`) on PATH", has_claude, "https://docs.anthropic.com/claude-code")
	if has_claude:
		plugins = _claude("plugin", "list").stdout
		check("frappe-ecc plugin installed", "frappe-ecc" in plugins, "Run: frappe-ecc install claude")
	legacy = legacy_paths(Path.home())
	check("no leftovers from the pre-v3 installer", not legacy, "Run: frappe-ecc install claude (removes them)")
	try:
		import yaml  # noqa: F401

		check("PyYAML available (for .yaml specs)", True)
	except ImportError:
		out("  [--] PyYAML not installed; use .json specs or pip install pyyaml")
	return 0 if ok else 1
