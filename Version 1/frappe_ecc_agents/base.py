"""
Frappe ECC Base Agent Architecture
Defines the base class FrappeAIAgent, execution contexts, agent responses, and data contracts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
from typing import Dict, Any, List, Optional


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WAITING_FEEDBACK = "WAITING_FEEDBACK"


class AgentPillar(str, Enum):
    INGESTION = "Pillar 1: Ingestion & Input Processing"
    ARCHITECTURE = "Pillar 2: Architecture & Analysis"
    WORKFLOWS = "Pillar 3: Workflows & Automations"
    ANALYTICS = "Pillar 4: Analytics, AI & Compliance"
    UI_UX = "Pillar 5: UI/UX & Frontends"
    DEVELOPMENT = "Pillar 6: Core Development & Engineering"
    QA_SECURITY = "Pillar 7: QA, Testing & Security"
    SAAS_OPS = "Pillar 8: Operations, SaaS & Support"


@dataclass
class AgentDeliverable:
    """Represents a generated artifact (code, document, schema, or config)."""
    title: str
    file_path: str
    content: str
    file_type: str  # python, javascript, json, markdown, html, css, yaml
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Standardized response object returned by every Frappe AI Agent."""
    agent_name: str
    pillar: str
    status: AgentStatus
    summary: str
    deliverables: List[AgentDeliverable] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    execution_time_sec: float = 0.0
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def add_log(self, message: str) -> None:
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def add_deliverable(self, title: str, file_path: str, content: str, file_type: str, **meta) -> None:
        self.deliverables.append(AgentDeliverable(
            title=title,
            file_path=file_path,
            content=content,
            file_type=file_type,
            metadata=meta
        ))


@dataclass
class AgentContext:
    """Shared execution state passed between agents in the pipeline."""
    project_name: str = "custom_app"
    app_title: str = "Custom Frappe Application"
    app_description: str = "Custom enterprise application built with Frappe Framework"
    prompt: str = ""
    doctypes: List[Dict[str, Any]] = field(default_factory=list)
    workflows: List[Dict[str, Any]] = field(default_factory=list)
    reports: List[Dict[str, Any]] = field(default_factory=list)
    client_scripts: List[Dict[str, Any]] = field(default_factory=list)
    server_scripts: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    git_repo: Optional[str] = None
    git_branch: str = "main"

    def record_step(self, agent_name: str, status: str, summary: str) -> None:
        self.execution_history.append({
            "timestamp": time.time(),
            "agent": agent_name,
            "status": status,
            "summary": summary
        })


class FrappeAIAgent(ABC):
    """
    Abstract Base Class for all 53 Frappe ECC AI Agents.
    Every agent supports dual execution:
    1. Live LLM reasoning (OpenAI, Claude, Gemini, Ollama) when available.
    2. High-fidelity deterministic reasoning fallback ensuring 100% offline operational guarantee.
    """

    def __init__(
        self,
        name: str,
        pillar: AgentPillar,
        description: str,
        capabilities: List[str],
        system_prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.2
    ):
        self.name = name
        self.pillar = pillar
        self.description = description
        self.capabilities = capabilities
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature

    def run(self, context: AgentContext) -> AgentResult:
        """Standard lifecycle runner handling timers, logging, and error boundaries."""
        start_time = time.time()
        result = AgentResult(
            agent_name=self.name,
            pillar=self.pillar.value,
            status=AgentStatus.RUNNING,
            summary=""
        )
        result.add_log(f"Initializing {self.name} under {self.pillar.value}...")

        try:
            # Step 1: Input Validation
            validation_error = self.validate_input(context)
            if validation_error:
                result.status = AgentStatus.FAILED
                result.error_message = validation_error
                result.add_log(f"Validation failed: {validation_error}")
                result.execution_time_sec = round(time.time() - start_time, 4)
                return result

            # Step 2: Agent Execution
            result.add_log(f"Executing reasoning engine for {self.name}...")
            self.execute(context, result)

            # Step 3: Mark Success
            result.status = AgentStatus.SUCCESS
            result.add_log(f"Completed execution with {len(result.deliverables)} deliverables.")

        except Exception as exc:
            result.status = AgentStatus.FAILED
            result.error_message = str(exc)
            result.add_log(f"Unhandled exception during execution: {exc}")

        finally:
            result.execution_time_sec = round(time.time() - start_time, 4)
            context.record_step(self.name, result.status.value, result.summary)

        return result

    def validate_input(self, context: AgentContext) -> Optional[str]:
        """Validates that prerequisite information is present. Returns None if valid, or error string."""
        if not context.project_name:
            return "Project name must not be empty."
        return None

    @abstractmethod
    def execute(self, context: AgentContext, result: AgentResult) -> None:
        """Core reasoning and artifact generation method to be implemented by each agent."""
        pass
