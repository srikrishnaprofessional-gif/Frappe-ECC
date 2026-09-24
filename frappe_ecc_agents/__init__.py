"""
Frappe ECC Autonomous AI Agents Framework
53 Executable Python AI Agents across 8 Enterprise Pillars.
"""

from .base import (
    FrappeAIAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentPillar,
    AgentDeliverable,
)
from .engine import LLMEngine
from .registry import registry, ALL_AGENT_CLASSES
from .orchestrator import PipelineOrchestrator, AUTONOMOUS_BUILD_PIPELINE

__version__ = "2.1.0"
__all__ = [
    "FrappeAIAgent",
    "AgentContext",
    "AgentResult",
    "AgentStatus",
    "AgentPillar",
    "AgentDeliverable",
    "LLMEngine",
    "registry",
    "ALL_AGENT_CLASSES",
    "PipelineOrchestrator",
    "AUTONOMOUS_BUILD_PIPELINE",
]
