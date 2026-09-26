#!/usr/bin/env python3
"""
Frappe ECC Universal Setup Wizard & Installer (Python Native)
Installs, updates, and manages Frappe Engineering Coordination Center across AI code editors.
Zero external dependencies.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PKG_ROOT = Path(__file__).resolve().parent.parent

def get_antigravity_config_dir():
    home = Path.home()
    return home / ".gemini" / "config"

def get_claude_config_dir():
    home = Path.home()
    return home / ".claude"

def get_cursor_config_dir():
    return Path.cwd() / ".cursor"

def copy_tree_overwrite(src: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        d = dest / item.name
        if item.is_dir():
            copy_tree_overwrite(item, d)
        else:
            shutil.copy2(item, d)

def install_antigravity(profile: str, dry_run: bool = False):
    config_dir = get_antigravity_config_dir()
    plugin_dir = config_dir / "plugins" / "frappe-ecc"
    skills_target_dir = config_dir / "skills"
    rules_target_dir = config_dir / "rules"

    print(f"\n[*] Installing Frappe ECC for Antigravity (Profile: {profile})...")
    print(f"   Target Plugin: {plugin_dir}")
    print(f"   Target Skills: {skills_target_dir}")
    print(f"   Target Rules:  {rules_target_dir}")

    if dry_run:
        print("   [DRY-RUN] Would create plugin and copy skills, rules, and agents.")
        return

    # 1. Create directories
    plugin_dir.mkdir(parents=True, exist_ok=True)
    skills_target_dir.mkdir(parents=True, exist_ok=True)
    rules_target_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy skills to global skills directory
    skills_src = PKG_ROOT / "skills"
    if skills_src.exists():
        for skill in skills_src.iterdir():
            if skill.is_dir():
                dest_skill = skills_target_dir / skill.name
                copy_tree_overwrite(skill, dest_skill)
                print(f"   [+] Skill installed: {skill.name}")

    # 3. Copy plugin structure
    copy_tree_overwrite(PKG_ROOT / "agents", plugin_dir / "agents")
    copy_tree_overwrite(PKG_ROOT / "skills", plugin_dir / "skills")
    copy_tree_overwrite(PKG_ROOT / "rules", plugin_dir / "rules")
    copy_tree_overwrite(PKG_ROOT / "rules", rules_target_dir)
    copy_tree_overwrite(PKG_ROOT / "bin", plugin_dir / "bin")

    manifest = PKG_ROOT / "adapters" / "antigravity" / "plugin.json"
    if manifest.exists():
        shutil.copy2(manifest, plugin_dir / "plugin.json")

    print("\n   [SUCCESS] Antigravity installation completed successfully!")

def install_claude(profile: str, dry_run: bool = False):
    claude_dir = get_claude_config_dir()
    plugin_dir = claude_dir / "plugins" / "frappe-ecc"
    commands_dir = claude_dir / "commands"

    print(f"\n[*] Installing Frappe ECC for Claude Code (Profile: {profile})...")
    if dry_run:
        print(f"   [DRY-RUN] Would install to {plugin_dir} and {commands_dir}")
        return

    plugin_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    copy_tree_overwrite(PKG_ROOT, plugin_dir)
    copy_tree_overwrite(PKG_ROOT / "commands", commands_dir)
    print("   [SUCCESS] Claude Code installation completed successfully!")

def install_cursor(profile: str, dry_run: bool = False):
    cursor_dir = get_cursor_config_dir()
    print(f"\n[*] Installing Frappe ECC for Cursor (Profile: {profile})...")
    if dry_run:
        print(f"   [DRY-RUN] Would install to {cursor_dir}")
        return

    cursor_dir.mkdir(parents=True, exist_ok=True)
    copy_tree_overwrite(PKG_ROOT / "rules", cursor_dir / "rules")
    print("   [SUCCESS] Cursor installation completed successfully!")

def doctor():
    print("\nFRAPPE ECC DOCTOR - SYSTEM DIAGNOSTICS")
    print("=======================================")
    print(f"Python Version: {sys.version.split()[0]} - OK")
    print(f"Platform: {sys.platform}")

    ag_dir = get_antigravity_config_dir()
    status_ag = "EXISTS" if ag_dir.exists() else "NOT FOUND"
    print(f"Antigravity Config Path: {ag_dir} [{status_ag}]")

    cl_dir = get_claude_config_dir()
    status_cl = "EXISTS" if cl_dir.exists() else "NOT FOUND"
    print(f"Claude Code Config Path: {cl_dir} [{status_cl}]")
    print("\nDiagnostic Complete.")

def main():
    parser = argparse.ArgumentParser(description="Frappe ECC Universal Setup Wizard")
    parser.add_argument("command", nargs="?", default="setup", choices=["setup", "doctor", "uninstall"])
    parser.add_argument("--profile", default="minimal", choices=["minimal", "full"])
    parser.add_argument("--target", default="antigravity", choices=["antigravity", "claude", "cursor", "all"])
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without writing")
    args = parser.parse_args()

    if args.command == "doctor":
        doctor()
        return

    print("===========================================================")
    print("FRAPPE ECC (ENGINEERING COORDINATION CENTER) INSTALLER")
    print("===========================================================")
    print(f"Profile: {args.profile} | Target: {args.target} | DryRun: {args.dry_run}")

    if args.target == "antigravity":
        install_antigravity(args.profile, args.dry_run)
    elif args.target == "claude":
        install_claude(args.profile, args.dry_run)
    elif args.target == "cursor":
        install_cursor(args.profile, args.dry_run)
    elif args.target == "all":
        install_antigravity(args.profile, args.dry_run)
        install_claude(args.profile, args.dry_run)
        install_cursor(args.profile, args.dry_run)

    print("\nSetup finished! You can now use all Frappe ECC skills, agents, and commands.\n")

if __name__ == "__main__":
    main()
