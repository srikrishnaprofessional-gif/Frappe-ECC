#!/usr/bin/env python3
"""
Frappe Shield — Static Analysis & Security Scanner for Frappe Framework Applications
Scans Frappe apps for SQL injection, transaction violations, insecure whitelisting, and anti-patterns.
"""

import ast
import os
import sys
import argparse
import json
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class IssueSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class FrappeShieldVisitor(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.issues = []
        self.current_function = None
        self.in_loop = False
        self.controller_methods = {
            "validate", "before_insert", "before_save", "on_update",
            "before_submit", "on_submit", "before_cancel", "on_cancel",
            "on_trash", "after_delete"
        }

    def add_issue(self, severity, line, title, description, recommendation):
        self.issues.append({
            "severity": severity,
            "file": str(self.filepath),
            "line": line,
            "title": title,
            "description": description,
            "recommendation": recommendation
        })

    def visit_FunctionDef(self, node):
        old_fn = self.current_function
        self.current_function = node
        
        # Check whitelist security
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, "attr", None) == "whitelist":
                # Check for allow_guest=True
                allow_guest = False
                for kw in decorator.keywords:
                    if kw.arg == "allow_guest" and getattr(kw.value, "value", False) is True:
                        allow_guest = True
                        break
                
                if allow_guest:
                    has_rate_limit = any(
                        isinstance(d, ast.Call) and getattr(d.func, "attr", None) == "rate_limit"
                        for d in node.decorator_list
                    )
                    if not has_rate_limit:
                        self.add_issue(
                            IssueSeverity.HIGH,
                            node.lineno,
                            "Unrestricted Guest Whitelist API",
                            f"Method '{node.name}' allows guest access without @frappe.rate_limit",
                            "Add @frappe.rate_limit(limit=10, seconds=60) and validate all inputs."
                        )

        self.generic_visit(node)
        self.current_function = old_fn

    def visit_For(self, node):
        prev = self.in_loop
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = prev

    def visit_While(self, node):
        prev = self.in_loop
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = prev

    def visit_Call(self, node):
        func = node.func
        
        # Check 1: frappe.db.commit() inside controller lifecycle
        if isinstance(func, ast.Attribute) and func.attr == "commit":
            if isinstance(func.value, ast.Attribute) and func.value.attr == "db":
                if self.current_function and self.current_function.name in self.controller_methods:
                    self.add_issue(
                        IssueSeverity.CRITICAL,
                        node.lineno,
                        "Manual DB Commit Inside Controller Hook",
                        f"frappe.db.commit() detected inside lifecycle method '{self.current_function.name}'",
                        "Remove frappe.db.commit(). Frappe manages transactions automatically."
                    )

        # Check 2: frappe.db.sql unparameterized formatting
        if isinstance(func, ast.Attribute) and func.attr == "sql":
            if isinstance(func.value, ast.Attribute) and func.value.attr == "db":
                if node.args:
                    first_arg = node.args[0]
                    # f-string formatting
                    if isinstance(first_arg, ast.JoinedStr):
                        self.add_issue(
                            IssueSeverity.CRITICAL,
                            node.lineno,
                            "SQL Injection: f-string in frappe.db.sql",
                            "Direct f-string query formatting detected in frappe.db.sql()",
                            "Use parameterized queries with values={'key': val} or use frappe.qb."
                        )
                    # % or .format() formatting
                    elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
                        self.add_issue(
                            IssueSeverity.CRITICAL,
                            node.lineno,
                            "SQL Injection: % formatting in frappe.db.sql",
                            "% string interpolation detected in frappe.db.sql()",
                            "Use parameterized queries with %(key)s and values parameter."
                        )
                    elif isinstance(first_arg, ast.Call) and getattr(first_arg.func, "attr", None) == "format":
                        self.add_issue(
                            IssueSeverity.CRITICAL,
                            node.lineno,
                            "SQL Injection: .format() in frappe.db.sql",
                            ".format() interpolation detected in frappe.db.sql()",
                            "Use parameterized queries or frappe.qb."
                        )

        # Check 3: frappe.get_doc inside loops (N+1 query)
        if isinstance(func, ast.Attribute) and func.attr == "get_doc":
            if self.in_loop:
                self.add_issue(
                    IssueSeverity.MEDIUM,
                    node.lineno,
                    "N+1 Query Bottleneck: frappe.get_doc in loop",
                    "frappe.get_doc() invoked inside a loop will severely degrade performance",
                    "Use frappe.get_all(..., filters={'name': ['in', id_list]}) or frappe.db.get_values()."
                )

        self.generic_visit(node)

    def visit_Assign(self, node):
        # Check direct assignment to docstatus = 1
        for target in node.targets:
            if isinstance(target, ast.Attribute) and target.attr == "docstatus":
                if isinstance(node.value, ast.Constant) and node.value.value in (1, 2):
                    self.add_issue(
                        IssueSeverity.HIGH,
                        node.lineno,
                        "Direct docstatus Manipulation",
                        f"Directly setting docstatus = {node.value.value} bypasses Frappe submission lifecycle",
                        "Use doc.submit() or doc.cancel() instead of directly setting docstatus."
                    )
        self.generic_visit(node)

def scan_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(filepath))
        visitor = FrappeShieldVisitor(filepath)
        visitor.visit(tree)
        return visitor.issues
    except Exception as e:
        return []

def scan_directory(target_path):
    all_issues = []
    target = Path(target_path)
    if target.is_file() and target.suffix == ".py":
        return scan_file(target)

    for root, _, files in os.walk(target):
        # Skip node_modules, env, venv, .git
        if any(skip in root for skip in ["node_modules", "env", "venv", ".git", "__pycache__"]):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                all_issues.extend(scan_file(file_path))
    return all_issues

def main():
    parser = argparse.ArgumentParser(description="Frappe Shield — Static Code Security Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Directory or file path to scan")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    issues = scan_directory(args.path)

    if args.json:
        print(json.dumps({"total_issues": len(issues), "issues": issues}, indent=2))
    else:
        print("=" * 60)
        print("🛡️  FRAPPE SHIELD — SECURITY & CODE QUALITY SCANNER")
        print("=" * 60)
        print(f"Scanning target: {os.path.abspath(args.path)}")
        print(f"Found {len(issues)} issue(s).\n")

        severity_colors = {
            IssueSeverity.CRITICAL: "\033[1;31m", # Red
            IssueSeverity.HIGH: "\033[1;33m",     # Yellow
            IssueSeverity.MEDIUM: "\033[1;34m",   # Blue
            IssueSeverity.LOW: "\033[0;37m"       # White
        }
        reset = "\033[0m"

        for idx, issue in enumerate(issues, 1):
            sev = issue["severity"]
            print(f"[{idx}] {severity_colors.get(sev, '')}{sev}{reset}: {issue['title']}")
            print(f"    File: {issue['file']}:{issue['line']}")
            print(f"    Issue: {issue['description']}")
            print(f"    Fix:   {issue['recommendation']}\n")

        print("=" * 60)
        if any(i["severity"] == IssueSeverity.CRITICAL for i in issues):
            print("❌ Scan FAILED: Critical security or transaction issues detected.")
            sys.exit(1)
        else:
            print("✅ Scan PASSED: No critical issues found.")

if __name__ == "__main__":
    main()
