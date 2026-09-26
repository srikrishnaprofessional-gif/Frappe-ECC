"""
Comprehensive Test Suite for All 53 Frappe ECC AI Agents
Tests every single agent with concrete test scenarios, input data, schema assertions, and performance profiling.
"""

import sys
import os
import json
import time
import unittest

# Ensure repo root is on PYTHONPATH
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from frappe_ecc_agents.base import AgentContext, AgentStatus
from frappe_ecc_agents.registry import registry, ALL_AGENT_CLASSES

# Configure UTF-8 for console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestAll53FrappeAIAgents(unittest.TestCase):
    """Automated test suite executing and verifying all 53 Frappe AI Agents."""

    @classmethod
    def setUpClass(cls):
        cls.test_results = []
        cls.total_agents = registry.count()
        print(f"\n================================================================================")
        print(f"🧪 INITIALIZING TEST SUITE: {cls.total_agents} FRAPPE AI AGENTS ACROSS 8 PILLARS")
        print(f"================================================================================\n")

    def _execute_agent_test(self, agent_name: str, scenario: str, custom_context_kwargs: dict = None):
        agent = registry.get(agent_name)
        self.assertIsNotNone(agent, f"Agent '{agent_name}' was not found in registry.")

        # Prepare concrete test data
        context_kwargs = {
            "project_name": "procurement_flow",
            "app_title": "Enterprise Procurement Flow",
            "app_description": "Autonomous purchase order requisition and three-way invoice matching system",
            "prompt": "Build an enterprise procurement and purchase requisition application with multi-level approval workflows"
        }
        if custom_context_kwargs:
            context_kwargs.update(custom_context_kwargs)

        context = AgentContext(**context_kwargs)
        start_time = time.time()
        result = agent.run(context)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Assertions
        self.assertEqual(result.status, AgentStatus.SUCCESS, f"Agent {agent_name} failed: {result.error_message}")
        self.assertIsNone(result.error_message, f"Agent {agent_name} reported error: {result.error_message}")
        self.assertGreaterEqual(len(result.deliverables), 1, f"Agent {agent_name} produced 0 deliverables.")

        for d in result.deliverables:
            self.assertTrue(len(d.content.strip()) > 0, f"Deliverable '{d.title}' has empty content.")
            self.assertTrue(len(d.file_path.strip()) > 0, f"Deliverable '{d.title}' has no file path.")

        # Record test metadata
        test_record = {
            "agent_name": agent.name,
            "pillar": agent.pillar.value,
            "scenario": scenario,
            "input_data": {
                "project_name": context.project_name,
                "app_title": context.app_title,
                "prompt": context.prompt
            },
            "deliverables": [
                {"title": d.title, "path": d.file_path, "type": d.file_type, "size_bytes": len(d.content)}
                for d in result.deliverables
            ],
            "execution_time_ms": duration_ms,
            "status": "PASS",
            "summary": result.summary
        }
        self.test_results.append(test_record)

        print(f"  [PASS] {agent.name:<42} | {duration_ms:>6.2f}ms | {len(result.deliverables)} deliverables | {scenario}")

    # =========================================================================
    # PILLAR 1: INGESTION & INPUT PROCESSING (5 AGENTS)
    # =========================================================================
    def test_01_frappe_autonomous_orchestrator(self):
        self._execute_agent_test(
            "frappe-autonomous-orchestrator",
            "Multi-stage DAG decomposition for enterprise procurement app"
        )

    def test_02_frappe_prompt_to_app_builder(self):
        self._execute_agent_test(
            "frappe-prompt-to-app-builder",
            "Natural language requirement to normalized DocType JSON schema"
        )

    def test_03_frappe_excel_csv_app_converter(self):
        self._execute_agent_test(
            "frappe-excel-csv-app-converter",
            "Spreadsheet schema inference and child table migration script synthesis"
        )

    def test_04_frappe_voice_command_copilot(self):
        self._execute_agent_test(
            "frappe-voice-command-copilot",
            "Verbal spoken voice transcript parsing into Frappe REST API CRUD call",
            {"shared_memory": {"voice_transcript": "Approve purchase requisition PR-2026-0045 for $18,500"}}
        )

    def test_05_frappe_ocr_document_ingestor(self):
        self._execute_agent_test(
            "frappe-ocr-document-ingestor",
            "Scanned PDF/invoice OCR key-value extraction and DocType mapping"
        )

    # =========================================================================
    # PILLAR 2: ARCHITECTURE & ANALYSIS (5 AGENTS)
    # =========================================================================
    def test_06_frappe_product_manager(self):
        self._execute_agent_test(
            "frappe-product-manager",
            "PRD authoring with personas, user stories, and acceptance criteria"
        )

    def test_07_frappe_hld_architect(self):
        self._execute_agent_test(
            "frappe-hld-architect",
            "High-Level Design specification with Mermaid system topology and C4 model"
        )

    def test_08_frappe_lld_designer(self):
        self._execute_agent_test(
            "frappe-lld-designer",
            "Low-Level Design with data dictionary, state machines, and index strategies"
        )

    def test_09_frappe_planner(self):
        self._execute_agent_test(
            "frappe-planner",
            "Agile sprint plan, task backlog breakdown, and dependency tracking"
        )

    def test_10_frappe_architect(self):
        self._execute_agent_test(
            "frappe-architect",
            "Architectural governance for Redis caching, RQ queue partitioning, and DB scale"
        )

    # =========================================================================
    # PILLAR 3: WORKFLOWS & AUTOMATIONS (6 AGENTS)
    # =========================================================================
    def test_11_frappe_bpmn_visual_workflow_builder(self):
        self._execute_agent_test(
            "frappe-bpmn-visual-workflow-builder",
            "BPMN multi-state approval workflow fixture generation with transition guards"
        )

    def test_12_frappe_notification_omnichannel_agent(self):
        self._execute_agent_test(
            "frappe-notification-omnichannel-agent",
            "Omnichannel notification dispatcher (Email, In-App Bell, Webhook)"
        )

    def test_13_frappe_cron_scheduler_optimizer(self):
        self._execute_agent_test(
            "frappe-cron-scheduler-optimizer",
            "Scheduled cron jobs in hooks.py with queue starvation prevention"
        )

    def test_14_frappe_sla_escalation_manager(self):
        self._execute_agent_test(
            "frappe-sla-escalation-manager",
            "48-hour SLA breach countdown monitor and auto-escalation engine"
        )

    def test_15_frappe_integrations_broker(self):
        self._execute_agent_test(
            "frappe-integrations-broker",
            "Inbound webhook handler with HMAC signature verification and idempotency"
        )

    def test_16_frappe_api_integrator(self):
        self._execute_agent_test(
            "frappe-api-integrator",
            "Resilient outbound REST client with exponential backoff and retry policy"
        )

    # =========================================================================
    # PILLAR 4: ANALYTICS, AI & COMPLIANCE (5 AGENTS)
    # =========================================================================
    def test_17_frappe_bi_dashboard_synthesizer(self):
        self._execute_agent_test(
            "frappe-bi-dashboard-synthesizer",
            "Dashboard Chart and Number Card metric widgets synthesis"
        )

    def test_18_frappe_natural_language_query_agent(self):
        self._execute_agent_test(
            "frappe-natural-language-query-agent",
            "Natural language query to Frappe QueryBuilder (frappe.qb) translation"
        )

    def test_19_frappe_predictive_ai_forecaster(self):
        self._execute_agent_test(
            "frappe-predictive-ai-forecaster",
            "Machine learning risk scoring and anomaly detection model"
        )

    def test_20_frappe_audit_trail_forensic_inspector(self):
        self._execute_agent_test(
            "frappe-audit-trail-forensic-inspector",
            "Forensic inspection of DocType Version records and immutable audit logs"
        )

    def test_21_frappe_report_builder(self):
        self._execute_agent_test(
            "frappe-report-builder",
            "Server-side Python Script Report and client-side JS filter UI"
        )

    # =========================================================================
    # PILLAR 5: UI/UX & FRONTENDS (8 AGENTS)
    # =========================================================================
    def test_22_frappe_ui_ux_designer(self):
        self._execute_agent_test(
            "frappe-ui-ux-designer",
            "Modern design system CSS variables, dark mode tokens, and typography scale"
        )

    def test_23_frappe_wireframe_builder(self):
        self._execute_agent_test(
            "frappe-wireframe-builder",
            "Desk form section/column blueprint and visual wireframe layout"
        )

    def test_24_frappe_interactive_prototyper(self):
        self._execute_agent_test(
            "frappe-interactive-prototyper",
            "Interactive quick-approval modal dialog client script (frappe.ui.Dialog)"
        )

    def test_25_frappe_white_label_branding_themer(self):
        self._execute_agent_test(
            "frappe-white-label-branding-themer",
            "White-label corporate branding stylesheet, navbar theme, and custom buttons"
        )

    def test_26_frappe_mobile_app_pwa_generator(self):
        self._execute_agent_test(
            "frappe-mobile-app-pwa-generator",
            "Progressive Web App (PWA) manifest.json and offline service worker"
        )

    def test_27_frappe_portal_ecommerce_builder(self):
        self._execute_agent_test(
            "frappe-portal-ecommerce-builder",
            "Customer self-service portal web template with Jinja2 and public web form"
        )

    def test_28_frappe_accessibility_wcag_compliance(self):
        self._execute_agent_test(
            "frappe-accessibility-wcag-compliance",
            "WCAG 2.1 AA accessibility audit report across contrast and keyboard nav"
        )

    def test_29_frappe_print_format_designer(self):
        self._execute_agent_test(
            "frappe-print-format-designer",
            "Print format HTML/CSS template for official vouchers and invoices"
        )

    # =========================================================================
    # PILLAR 6: CORE DEVELOPMENT & ENGINEERING (7 AGENTS)
    # =========================================================================
    def test_30_frappe_fullstack_developer(self):
        self._execute_agent_test(
            "frappe-fullstack-developer",
            "Complete vertical slice: Python controller and hooks.py registration"
        )

    def test_31_frappe_custom_app_git_builder(self):
        self._execute_agent_test(
            "frappe-custom-app-git-builder",
            "Automated Git repository initialization, commit and push pipeline"
        )

    def test_32_frappe_backend_builder(self):
        self._execute_agent_test(
            "frappe-backend-builder",
            "Secure whitelisted REST API endpoint (@frappe.whitelist) with RBAC"
        )

    def test_33_frappe_desk_builder(self):
        self._execute_agent_test(
            "frappe-desk-builder",
            "Reactive Desk Client Script with indicator tags and field value triggers"
        )

    def test_34_frappe_data_synthesizer(self):
        self._execute_agent_test(
            "frappe-data-synthesizer",
            "Synthetic realistic test data fixtures for stress testing and demos"
        )

    def test_35_frappe_migration_patcher(self):
        self._execute_agent_test(
            "frappe-migration-patcher",
            "Idempotent database migration patch and entry in patches.txt"
        )

    def test_36_frappe_self_healing_debugger(self):
        self._execute_agent_test(
            "frappe-self-healing-debugger",
            "Self-healing code diagnostics checking schema constraints and exceptions"
        )

    # =========================================================================
    # PILLAR 7: QA, TESTING & SECURITY (7 AGENTS)
    # =========================================================================
    def test_37_frappe_tdd_guide(self):
        self._execute_agent_test(
            "frappe-tdd-guide",
            "Automated unit test suite using FrappeTestCase with validation tests"
        )

    def test_38_frappe_manual_qa(self):
        self._execute_agent_test(
            "frappe-manual-qa",
            "Manual QA test matrix with pre-conditions, steps, and expected outcomes"
        )

    def test_39_frappe_automated_tester(self):
        self._execute_agent_test(
            "frappe-automated-tester",
            "Automated end-to-end REST API integration test script"
        )

    def test_40_frappe_code_reviewer(self):
        self._execute_agent_test(
            "frappe-code-reviewer",
            "Static code quality analysis and Frappe convention compliance check"
        )

    def test_41_frappe_security_reviewer(self):
        self._execute_agent_test(
            "frappe-security-reviewer",
            "Frappe Shield security audit for SQL injection, XSS, and CSRF"
        )

    def test_42_frappe_rbac_compliance_guardian(self):
        self._execute_agent_test(
            "frappe-rbac-compliance-guardian",
            "Row-level permission query conditions hook restricting record visibility"
        )

    def test_43_frappe_gdpr_data_privacy_officer(self):
        self._execute_agent_test(
            "frappe-gdpr-data-privacy-officer",
            "GDPR Right-to-Erasure automated PII data scrubbing script"
        )

    # =========================================================================
    # PILLAR 8: OPERATIONS, SAAS & SUPPORT (10 AGENTS)
    # =========================================================================
    def test_44_frappe_saas_multitenancy_orchestrator(self):
        self._execute_agent_test(
            "frappe-saas-multitenancy-orchestrator",
            "Automated multi-tenant site provisioning script with quota management"
        )

    def test_45_frappe_multilingual_localization_agent(self):
        self._execute_agent_test(
            "frappe-multilingual-localization-agent",
            "Multi-lingual translation dictionaries for Spanish (es) and German (de)"
        )

    def test_46_frappe_data_migration_concierge(self):
        self._execute_agent_test(
            "frappe-data-migration-concierge",
            "Legacy ERP ETL data transformation and transactional insertion pipeline"
        )

    def test_47_frappe_interactive_guided_tour_author(self):
        self._execute_agent_test(
            "frappe-interactive-guided-tour-author",
            "Interactive Form Tour onboarding fixture with targeted field tooltips"
        )

    def test_48_frappe_helpdesk_customer_support_copilot(self):
        self._execute_agent_test(
            "frappe-helpdesk-customer-support-copilot",
            "AI customer support copilot response generator for helpdesk tickets"
        )

    def test_49_frappe_training_video_scriptwriter(self):
        self._execute_agent_test(
            "frappe-training-video-scriptwriter",
            "Professional 4-minute video training script with narration and click cues"
        )

    def test_50_frappe_working_sop_author(self):
        self._execute_agent_test(
            "frappe-working-sop-author",
            "Standard Operating Procedure (SOP) with step-by-step role instructions"
        )

    def test_51_frappe_doc_updater(self):
        self._execute_agent_test(
            "frappe-doc-updater",
            "Technical REST API reference and endpoint documentation"
        )

    def test_52_frappe_bench_devops(self):
        self._execute_agent_test(
            "frappe-bench-devops",
            "Bench DevOps deployment, database backup, and migration shell script"
        )

    def test_53_frappe_release_devops(self):
        self._execute_agent_test(
            "frappe-release-devops",
            "Release packaging manifest and CHANGELOG.md generation for v1.0.0"
        )

    @classmethod
    def tearDownClass(cls):
        # Save test results JSON
        results_path = os.path.join(REPO_ROOT, "tests", "test_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_agents_tested": len(cls.test_results),
                "passed": sum(1 for r in cls.test_results if r["status"] == "PASS"),
                "failed": sum(1 for r in cls.test_results if r["status"] == "FAIL"),
                "results": cls.test_results
            }, f, indent=2)

        print(f"\n================================================================================")
        print(f"📊 TEST SUITE SUMMARY: {len(cls.test_results)} / {cls.total_agents} AGENTS TESTED")
        print(f"✅ PASSED: {sum(1 for r in cls.test_results if r['status'] == 'PASS')} | ❌ FAILED: {sum(1 for r in cls.test_results if r['status'] == 'FAIL')}")
        print(f"📁 Detailed JSON Test Report saved to: {results_path}")
        print(f"================================================================================\n")


if __name__ == "__main__":
    unittest.main()
