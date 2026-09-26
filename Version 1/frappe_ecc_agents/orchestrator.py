"""
Frappe ECC Multi-Agent Orchestrator
Coordinates multi-agent pipelines, dependencies, shared state passing, and execution tracing.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from .base import AgentContext, AgentResult, AgentStatus
from .registry import registry

logger = logging.getLogger("frappe_ecc_agents.orchestrator")


# Canonical autonomous build pipeline executing essential agents across the 8 pillars
AUTONOMOUS_BUILD_PIPELINE = [
    # Phase 1: Ingestion & PRD
    "frappe-autonomous-orchestrator",
    "frappe-prompt-to-app-builder",
    "frappe-product-manager",

    # Phase 2: Architecture & Schemas
    "frappe-hld-architect",
    "frappe-lld-designer",

    # Phase 3: Core Development
    "frappe-fullstack-developer",
    "frappe-desk-builder",
    "frappe-backend-builder",

    # Phase 4: Workflows & Automations
    "frappe-bpmn-visual-workflow-builder",
    "frappe-notification-omnichannel-agent",

    # Phase 5: Analytics & UI/UX
    "frappe-bi-dashboard-synthesizer",
    "frappe-ui-ux-designer",

    # Phase 6: QA, Security & Privacy
    "frappe-tdd-guide",
    "frappe-security-reviewer",
    "frappe-gdpr-data-privacy-officer",

    # Phase 7: SOP, Docs & Git Push
    "frappe-working-sop-author",
    "frappe-custom-app-git-builder",
]


class PipelineOrchestrator:
    """Coordinates phased execution across multiple Frappe AI Agents."""

    def __init__(self, context: Optional[AgentContext] = None):
        self.context = context or AgentContext()
        self.results: Dict[str, AgentResult] = {}

    def run_agent(self, agent_name: str) -> AgentResult:
        """Executes a single agent within the current pipeline context."""
        agent = registry.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in registry.")

        res = agent.run(self.context)
        self.results[agent_name] = res
        return res

    def run_pipeline(self, agent_names: List[str]) -> Dict[str, Any]:
        """Executes an ordered list of agents, passing shared context forward."""
        pipeline_start = time.time()
        successful = 0
        failed = 0
        total_deliverables = 0

        print(f"\n=================================================================")
        print(f"🚀 Launching Frappe AI Agent Pipeline: {len(agent_names)} Agents")
        print(f"Project: {self.context.app_title} ({self.context.project_name})")
        print(f"=================================================================\n")

        for idx, name in enumerate(agent_names, 1):
            agent = registry.get(name)
            if not agent:
                print(f"[{idx}/{len(agent_names)}] ⚠️ Agent '{name}' not found. Skipping.")
                failed += 1
                continue

            print(f"[{idx}/{len(agent_names)}] 🤖 Executing: {agent.name} ({agent.pillar.value})...")
            res = agent.run(self.context)
            self.results[name] = res

            if res.status == AgentStatus.SUCCESS:
                successful += 1
                total_deliverables += len(res.deliverables)
                print(f"    ✅ Succeeded in {res.execution_time_sec:.3f}s | {len(res.deliverables)} deliverables")
            else:
                failed += 1
                print(f"    ❌ Failed: {res.error_message}")

        total_time = round(time.time() - pipeline_start, 3)
        print(f"\n=================================================================")
        print(f"🏁 Pipeline Execution Finished in {total_time}s")
        print(f"Success: {successful} | Failed: {failed} | Total Deliverables: {total_deliverables}")
        print(f"=================================================================\n")

        return {
            "project_name": self.context.project_name,
            "total_agents": len(agent_names),
            "successful": successful,
            "failed": failed,
            "total_deliverables": total_deliverables,
            "execution_time_sec": total_time,
            "results": self.results
        }

    def run_all_53_agents(self) -> Dict[str, Any]:
        """Topological execution of all 53 registered agents."""
        all_agent_names = [a.name for a in registry.list_all()]
        return self.run_pipeline(all_agent_names)

    def run_autonomous_build(self) -> Dict[str, Any]:
        """Runs the canonical end-to-end autonomous build pipeline."""
        return self.run_pipeline(AUTONOMOUS_BUILD_PIPELINE)
