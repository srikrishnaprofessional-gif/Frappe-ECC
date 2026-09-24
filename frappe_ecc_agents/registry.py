"""
Frappe ECC Agent Registry
Central catalog registering all 53 Frappe AI Agents with discovery, lookup, and metadata APIs.
"""

from typing import Dict, List, Optional, Type
from .base import FrappeAIAgent, AgentPillar

# Pillar 1
from .pillars.pillar1_ingestion import (
    FrappeAutonomousOrchestratorAgent,
    FrappePromptToAppBuilderAgent,
    FrappeExcelCsvAppConverterAgent,
    FrappeVoiceCommandCopilotAgent,
    FrappeOcrDocumentIngestorAgent,
)

# Pillar 2
from .pillars.pillar2_architecture import (
    FrappeProductManagerAgent,
    FrappeHldArchitectAgent,
    FrappeLldDesignerAgent,
    FrappePlannerAgent,
    FrappeArchitectAgent,
)

# Pillar 3
from .pillars.pillar3_workflows import (
    FrappeBpmnVisualWorkflowBuilderAgent,
    FrappeNotificationOmnichannelAgent,
    FrappeCronSchedulerOptimizerAgent,
    FrappeSlaEscalationManagerAgent,
    FrappeIntegrationsBrokerAgent,
    FrappeApiIntegratorAgent,
)

# Pillar 4
from .pillars.pillar4_analytics import (
    FrappeBiDashboardSynthesizerAgent,
    FrappeNaturalLanguageQueryAgent,
    FrappePredictiveAiForecasterAgent,
    FrappeAuditTrailForensicInspectorAgent,
    FrappeReportBuilderAgent,
)

# Pillar 5
from .pillars.pillar5_ui_ux import (
    FrappeUiUxDesignerAgent,
    FrappeWireframeBuilderAgent,
    FrappeInteractivePrototyperAgent,
    FrappeWhiteLabelBrandingThemerAgent,
    FrappeMobileAppPwaGeneratorAgent,
    FrappePortalEcommerceBuilderAgent,
    FrappeAccessibilityWcagComplianceAgent,
    FrappePrintFormatDesignerAgent,
)

# Pillar 6
from .pillars.pillar6_development import (
    FrappeFullstackDeveloperAgent,
    FrappeCustomAppGitBuilderAgent,
    FrappeBackendBuilderAgent,
    FrappeDeskBuilderAgent,
    FrappeDataSynthesizerAgent,
    FrappeMigrationPatcherAgent,
    FrappeSelfHealingDebuggerAgent,
)

# Pillar 7
from .pillars.pillar7_qa_security import (
    FrappeTddGuideAgent,
    FrappeManualQaAgent,
    FrappeAutomatedTesterAgent,
    FrappeCodeReviewerAgent,
    FrappeSecurityReviewerAgent,
    FrappeRbacComplianceGuardianAgent,
    FrappeGdprDataPrivacyOfficerAgent,
)

# Pillar 8
from .pillars.pillar8_saas_ops import (
    FrappeSaasMultitenancyOrchestratorAgent,
    FrappeMultilingualLocalizationAgent,
    FrappeDataMigrationConciergeAgent,
    FrappeInteractiveGuidedTourAuthorAgent,
    FrappeHelpdeskCustomerSupportCopilotAgent,
    FrappeTrainingVideoScriptwriterAgent,
    FrappeWorkingSopAuthorAgent,
    FrappeDocUpdaterAgent,
    FrappeBenchDevopsAgent,
    FrappeReleaseDevopsAgent,
)


ALL_AGENT_CLASSES: List[Type[FrappeAIAgent]] = [
    # Pillar 1: Ingestion & Input Processing (5)
    FrappeAutonomousOrchestratorAgent,
    FrappePromptToAppBuilderAgent,
    FrappeExcelCsvAppConverterAgent,
    FrappeVoiceCommandCopilotAgent,
    FrappeOcrDocumentIngestorAgent,

    # Pillar 2: Architecture & Analysis (5)
    FrappeProductManagerAgent,
    FrappeHldArchitectAgent,
    FrappeLldDesignerAgent,
    FrappePlannerAgent,
    FrappeArchitectAgent,

    # Pillar 3: Workflows & Automations (6)
    FrappeBpmnVisualWorkflowBuilderAgent,
    FrappeNotificationOmnichannelAgent,
    FrappeCronSchedulerOptimizerAgent,
    FrappeSlaEscalationManagerAgent,
    FrappeIntegrationsBrokerAgent,
    FrappeApiIntegratorAgent,

    # Pillar 4: Analytics, AI & Compliance (5)
    FrappeBiDashboardSynthesizerAgent,
    FrappeNaturalLanguageQueryAgent,
    FrappePredictiveAiForecasterAgent,
    FrappeAuditTrailForensicInspectorAgent,
    FrappeReportBuilderAgent,

    # Pillar 5: UI/UX & Frontends (8)
    FrappeUiUxDesignerAgent,
    FrappeWireframeBuilderAgent,
    FrappeInteractivePrototyperAgent,
    FrappeWhiteLabelBrandingThemerAgent,
    FrappeMobileAppPwaGeneratorAgent,
    FrappePortalEcommerceBuilderAgent,
    FrappeAccessibilityWcagComplianceAgent,
    FrappePrintFormatDesignerAgent,

    # Pillar 6: Core Development & Engineering (7)
    FrappeFullstackDeveloperAgent,
    FrappeCustomAppGitBuilderAgent,
    FrappeBackendBuilderAgent,
    FrappeDeskBuilderAgent,
    FrappeDataSynthesizerAgent,
    FrappeMigrationPatcherAgent,
    FrappeSelfHealingDebuggerAgent,

    # Pillar 7: QA, Testing & Security (7)
    FrappeTddGuideAgent,
    FrappeManualQaAgent,
    FrappeAutomatedTesterAgent,
    FrappeCodeReviewerAgent,
    FrappeSecurityReviewerAgent,
    FrappeRbacComplianceGuardianAgent,
    FrappeGdprDataPrivacyOfficerAgent,

    # Pillar 8: Operations, SaaS & Support (10)
    FrappeSaasMultitenancyOrchestratorAgent,
    FrappeMultilingualLocalizationAgent,
    FrappeDataMigrationConciergeAgent,
    FrappeInteractiveGuidedTourAuthorAgent,
    FrappeHelpdeskCustomerSupportCopilotAgent,
    FrappeTrainingVideoScriptwriterAgent,
    FrappeWorkingSopAuthorAgent,
    FrappeDocUpdaterAgent,
    FrappeBenchDevopsAgent,
    FrappeReleaseDevopsAgent,
]


class AgentRegistry:
    """Registry managing instances and cataloging of all 53 Frappe AI Agents."""

    _instance: Optional["AgentRegistry"] = None

    def __init__(self):
        self._agents: Dict[str, FrappeAIAgent] = {}
        self._initialize_all()

    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_all(self) -> None:
        for agent_cls in ALL_AGENT_CLASSES:
            agent = agent_cls()
            self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[FrappeAIAgent]:
        return self._agents.get(name)

    def list_all(self) -> List[FrappeAIAgent]:
        return list(self._agents.values())

    def count(self) -> int:
        return len(self._agents)

    def get_by_pillar(self, pillar: AgentPillar) -> List[FrappeAIAgent]:
        return [a for a in self._agents.values() if a.pillar == pillar]

    def get_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": a.name,
                "pillar": a.pillar.value,
                "description": a.description,
                "capabilities": a.capabilities,
                "model": a.model,
            }
            for a in self._agents.values()
        ]


# Global singleton instance
registry = AgentRegistry.get_instance()
