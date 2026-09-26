"""
Frappe ECC Agents CLI Interface
Command-line runner to inspect, execute, and orchestrate all 53 Frappe AI agents.
"""

import sys
import os
import argparse
import json
from .base import AgentContext, AgentStatus
from .registry import registry
from .orchestrator import PipelineOrchestrator

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="frappe-agent",
        description="Frappe ECC Autonomous AI Agents CLI (53 Agents across 8 Pillars)"
    )
    parser.add_argument("--list", action="store_true", help="List all 53 registered Frappe AI agents")
    parser.add_argument("--agent", type=str, help="Execute a specific agent by name (e.g. frappe-prompt-to-app-builder)")
    parser.add_argument("--pipeline", choices=["autonomous", "all"], help="Execute a multi-agent pipeline")
    parser.add_argument("--app-name", type=str, default="loan_management", help="Application slug name")
    parser.add_argument("--app-title", type=str, default="Loan Management System", help="Human-readable app title")
    parser.add_argument("--prompt", type=str, default="Build an enterprise loan management and approval tracking system", help="Requirements prompt")
    parser.add_argument("--write-artifacts", action="store_true", help="Write generated deliverables to disk")
    parser.add_argument("--out-dir", type=str, default="./generated_app", help="Output directory when writing artifacts")

    args = parser.parse_args()

    if args.list:
        print(f"\nRegistered Frappe AI Agents: {registry.count()} across 8 Pillars\n")
        print(f"{'#':<4} {'Agent Name':<42} {'Pillar':<35}")
        print("-" * 85)
        for idx, agent in enumerate(registry.list_all(), 1):
            print(f"{idx:<4} {agent.name:<42} {agent.pillar.value:<35}")
        print("-" * 85)
        print(f"Total: {registry.count()} AI Agents verified.\n")
        return 0

    context = AgentContext(
        project_name=args.app_name,
        app_title=args.app_title,
        prompt=args.prompt
    )
    orchestrator = PipelineOrchestrator(context=context)

    if args.agent:
        print(f"\nExecuting single agent: {args.agent}...")
        result = orchestrator.run_agent(args.agent)
        print(f"Status: {result.status.value}")
        print(f"Execution Time: {result.execution_time_sec:.3f}s")
        print(f"Summary: {result.summary}")
        print(f"Deliverables generated: {len(result.deliverables)}")
        for d in result.deliverables:
            print(f"  - [{d.file_type.upper()}] {d.title} -> {d.file_path}")

        if args.write_artifacts:
            _write_deliverables(result.deliverables, args.out_dir)
        return 0 if result.status == AgentStatus.SUCCESS else 1

    if args.pipeline:
        if args.pipeline == "autonomous":
            summary = orchestrator.run_autonomous_build()
        else:
            summary = orchestrator.run_all_53_agents()

        if args.write_artifacts:
            all_delivs = []
            for res in summary["results"].values():
                all_delivs.extend(res.deliverables)
            _write_deliverables(all_delivs, args.out_dir)

        return 0 if summary["failed"] == 0 else 1

    parser.print_help()
    return 0


def _write_deliverables(deliverables, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for d in deliverables:
        target_path = os.path.join(out_dir, d.file_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(d.content)
    print(f"\nWrote {len(deliverables)} artifacts to: {os.path.abspath(out_dir)}")


if __name__ == "__main__":
    sys.exit(main())
