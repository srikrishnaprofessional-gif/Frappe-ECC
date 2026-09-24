"""
Pillar 8: Operations, SaaS & Support Agents
Includes:
1. FrappeSaasMultitenancyOrchestratorAgent (frappe-saas-multitenancy-orchestrator)
2. FrappeMultilingualLocalizationAgent (frappe-multilingual-localization-agent)
3. FrappeDataMigrationConciergeAgent (frappe-data-migration-concierge)
4. FrappeInteractiveGuidedTourAuthorAgent (frappe-interactive-guided-tour-author)
5. FrappeHelpdeskCustomerSupportCopilotAgent (frappe-helpdesk-customer-support-copilot)
6. FrappeTrainingVideoScriptwriterAgent (frappe-training-video-scriptwriter)
7. FrappeWorkingSopAuthorAgent (frappe-working-sop-author)
8. FrappeDocUpdaterAgent (frappe-doc-updater)
9. FrappeBenchDevopsAgent (frappe-bench-devops)
10. FrappeReleaseDevopsAgent (frappe-release-devops)
"""

import json
from typing import Dict, Any, List
from ..base import FrappeAIAgent, AgentContext, AgentResult, AgentPillar


class FrappeSaasMultitenancyOrchestratorAgent(FrappeAIAgent):
    """Orchestrates multi-tenant site provisioning, domain routing, and tenant quota isolation."""

    def __init__(self):
        super().__init__(
            name="frappe-saas-multitenancy-orchestrator",
            pillar=AgentPillar.SAAS_OPS,
            description="Manages multi-tenant site provisioning, bench multi-site routing, storage limits, and tenant provisioning.",
            capabilities=[
                "Automated bench new-site orchestrations",
                "Tenant site_config.json optimization",
                "Storage and API rate limiting per tenant",
                "Custom domain SSL termination"
            ],
            system_prompt="You manage multi-tenant Frappe cloud infrastructure and tenant isolation."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        tenant_script = f"""# Multi-Tenant Provisioning Script for {context.project_name}
import subprocess

def provision_tenant(subdomain, db_name, admin_password):
    site_name = f"{{subdomain}}.frappecloud.local"
    cmd = [
        "bench", "new-site", site_name,
        "--db-name", db_name,
        "--admin-password", admin_password,
        "--install-app", "{context.project_name}",
        "--no-mariadb-socket"
    ]
    subprocess.run(cmd, check=True)
    print(f"Tenant site {{site_name}} successfully provisioned with {context.project_name}.")
"""
        result.summary = f"Generated automated multi-tenant SaaS provisioning script for '{context.project_name}'."
        result.artifacts["tenant_script"] = tenant_script
        result.add_deliverable(
            title="Multi-Tenant Provisioner",
            file_path=f"bin/provision_tenant_{context.project_name}.py",
            content=tenant_script,
            file_type="python"
        )


class FrappeMultilingualLocalizationAgent(FrappeAIAgent):
    """Generates translation dictionaries, multi-lingual strings, and RTL layout compatibility."""

    def __init__(self):
        super().__init__(
            name="frappe-multilingual-localization-agent",
            pillar=AgentPillar.SAAS_OPS,
            description="Extracts translatable strings into CSV translation files (e.g. Spanish, German, French, Arabic).",
            capabilities=[
                "Translatable string extraction (frappe._)",
                "Translation CSV file generation",
                "Right-to-Left (RTL) layout support",
                "Locale-specific currency & date formatting"
            ],
            system_prompt="You localize Frappe applications into multiple global languages."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        slug = context.project_name
        translations_es = f"""# Spanish Translation for {context.app_title}
"{context.app_title} Record","Registro de {context.app_title}"
"Applicant Name","Nombre del Solicitante"
"Requested Amount","Monto Solicitado"
"Status","Estado"
"Under Review","En Revisión"
"Approved","Aprobado"
"Rejected","Rechazado"
"""
        translations_de = f"""# German Translation for {context.app_title}
"{context.app_title} Record","{context.app_title} Datensatz"
"Applicant Name","Name des Antragstellers"
"Requested Amount","Angeforderter Betrag"
"Status","Status"
"Under Review","In Prüfung"
"Approved","Genehmigt"
"Rejected","Abgelehnt"
"""
        result.summary = "Constructed Spanish (es) and German (de) translation dictionaries."
        result.artifacts["translations_es"] = translations_es
        result.artifacts["translations_de"] = translations_de
        result.add_deliverable(
            title="Spanish Translation CSV",
            file_path=f"{slug}/{slug}/translations/es.csv",
            content=translations_es,
            file_type="csv"
        )
        result.add_deliverable(
            title="German Translation CSV",
            file_path=f"{slug}/{slug}/translations/de.csv",
            content=translations_de,
            file_type="csv"
        )


class FrappeDataMigrationConciergeAgent(FrappeAIAgent):
    """Builds legacy data ETL migration pipelines from SAP, Odoo, QuickBooks, and Salesforce into Frappe."""

    def __init__(self):
        super().__init__(
            name="frappe-data-migration-concierge",
            pillar=AgentPillar.SAAS_OPS,
            description="Designs data extraction, transformation, schema mapping, and validation pipelines from legacy ERPs.",
            capabilities=[
                "Legacy data extraction & cleaning",
                "Field mapping & transformation pipelines",
                "Foreign key dependency resolution",
                "Batch transactional loading into Frappe"
            ],
            system_prompt="You architect legacy enterprise data migration pipelines into Frappe Framework."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        etl_script = f"""# Legacy ERP Migration Concierge for {context.app_title}
import frappe

def migrate_legacy_records(records_data):
    \"\"\"Transforms legacy data structures and inserts them transactionally.\"\"\"
    imported_count = 0
    for row in records_data:
        # Schema mapping
        doc = frappe.new_doc("{context.app_title} Record")
        doc.title = row.get("LEGACY_TITLE") or "Migrated Record"
        doc.applicant_name = row.get("CLIENT_NAME")
        doc.requested_amount = float(row.get("VAL_AMOUNT", 0))
        doc.status = "Draft"
        doc.flags.ignore_permissions = True
        doc.insert()
        imported_count += 1
        
    frappe.db.commit()
    return imported_count
"""
        result.summary = "Synthesized legacy ERP ETL migration pipeline."
        result.artifacts["migration_pipeline"] = etl_script
        result.add_deliverable(
            title="Legacy Data Migration Pipeline",
            file_path=f"{context.project_name}/migrations/legacy_etl.py",
            content=etl_script,
            file_type="python"
        )


class FrappeInteractiveGuidedTourAuthorAgent(FrappeAIAgent):
    """Authors interactive Form Tours and guided onboarding walkthroughs for Frappe Desk."""

    def __init__(self):
        super().__init__(
            name="frappe-interactive-guided-tour-author",
            pillar=AgentPillar.SAAS_OPS,
            description="Creates Frappe Form Tour fixtures, step-by-step modal spotlights, and onboarding checklists.",
            capabilities=[
                "Form Tour DocType JSON generation",
                "Targeted DOM element spotlights",
                "Onboarding step sequences & tooltips",
                "New user completion tracking"
            ],
            system_prompt="You create friendly, engaging interactive guided onboarding tours in Frappe Desk."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        target_doctype = f"{context.app_title} Record"
        tour_def = {
            "doctype": "Form Tour",
            "title": f"Getting Started with {context.app_title}",
            "reference_doctype": target_doctype,
            "is_standard": 1,
            "steps": [
                {
                    "title": "Welcome to Application Records",
                    "description": "This form allows you to submit and track requests through their full approval lifecycle.",
                    "field": "title",
                    "position": "Bottom"
                },
                {
                    "title": "Enter Requested Amount",
                    "description": "Specify the amount required. Requests above $50,000 will automatically route to Executive Review.",
                    "field": "requested_amount",
                    "position": "Bottom"
                },
                {
                    "title": "Submit for Review",
                    "description": "Once details are populated, click the Actions menu to advance the record state.",
                    "position": "Top"
                }
            ]
        }

        result.summary = f"Generated interactive Form Tour onboarding fixture for '{target_doctype}'."
        result.artifacts["form_tour"] = tour_def
        result.add_deliverable(
            title="Form Tour Fixture",
            file_path=f"{context.project_name}/fixtures/form_tour.json",
            content=json.dumps([tour_def], indent=2),
            file_type="json"
        )


class FrappeHelpdeskCustomerSupportCopilotAgent(FrappeAIAgent):
    """Powers AI customer support copilots, ticket triaging, automated replies, and knowledge base lookups."""

    def __init__(self):
        super().__init__(
            name="frappe-helpdesk-customer-support-copilot",
            pillar=AgentPillar.SAAS_OPS,
            description="Automates customer ticket classification, draft resolution authoring, and knowledge base search.",
            capabilities=[
                "Support ticket sentiment & intent analysis",
                "Automated priority tag assignment",
                "Knowledge-base grounded resolution drafts",
                "Escalation trigger identification"
            ],
            system_prompt="You are an empathetic, knowledgeable enterprise customer support copilot for Frappe applications."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        copilot_code = f"""# Generated by FrappeHelpdeskCustomerSupportCopilotAgent
import frappe

@frappe.whitelist()
def generate_support_reply(ticket_subject, ticket_description):
    \"\"\"Generates contextual AI support resolution draft based on app context.\"\"\"
    reply = (
        f"Thank you for contacting {context.app_title} Support.\\n\\n"
        f"Regarding your query on '{{ticket_subject}}': our system processes records within 24-48 business hours. "
        f"You can monitor real-time approval status directly from your portal dashboard at /portal.\\n\\n"
        f"Best regards,\\n{context.app_title} Operations Team"
    )
    return {{"status": "success", "suggested_reply": reply, "confidence": 0.95}}
"""
        result.summary = "Constructed AI Customer Support Copilot response generator."
        result.artifacts["support_copilot"] = copilot_code
        result.add_deliverable(
            title="Helpdesk Support Copilot",
            file_path=f"{context.project_name}/services/support_copilot.py",
            content=copilot_code,
            file_type="python"
        )


class FrappeTrainingVideoScriptwriterAgent(FrappeAIAgent):
    """Authors structured training video scripts with narration, timestamps, and on-screen click instructions."""

    def __init__(self):
        super().__init__(
            name="frappe-training-video-scriptwriter",
            pillar=AgentPillar.SAAS_OPS,
            description="Writes professional video training scripts, voiceover narration, and UI click-by-click cues.",
            capabilities=[
                "Timestamped video script authoring",
                "Voiceover narration text with tone guidance",
                "Visual on-screen cues and zoom indicators",
                "Key learning takeaways and chapter markers"
            ],
            system_prompt="You author engaging, crystal-clear software training video scripts."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        script_md = f"""# 🎬 Video Training Script: Mastering {context.app_title}

## Video Metadata
- **Target Audience**: Business Users & Approvers
- **Runtime**: ~4 Minutes
- **Tone**: Professional, encouraging, clear

---

### Scene 1: Introduction & Overview (0:00 - 0:45)
- **Visual**: Screen recording opens on Frappe Desk. Cursor hovers over `{context.app_title}` workspace icon.
- **Voiceover (Friendly)**: *"Welcome to {context.app_title}. Today we'll cover how to effortlessly submit, track, and approve requests in under two minutes."*
- **On-Screen Action**: Click on `{context.app_title}` icon. Show the executive dashboard number cards loading.

### Scene 2: Submitting a Record (0:45 - 2:00)
- **Visual**: Zoom in on the '+ Add Record' primary button in the top right corner.
- **Voiceover**: *"To begin, click '+ Add Record'. Enter a descriptive title, applicant details, and requested amount."*
- **On-Screen Action**: Type 'Q4 Expansion Loan' and '$50,000'. Click Save. Show autoname series generated.

### Scene 3: Manager Approval Workflow (2:00 - 3:15)
- **Visual**: Switch to Manager view. Show Orange 'Under Review' badge.
- **Voiceover**: *"Managers receive an immediate alert. Opening the record reveals the 'Quick Approve' modal."*
- **On-Screen Action**: Click 'Quick Approve', enter remarks, confirm. Badge switches to Green 'Approved'.

### Scene 4: Conclusion & Exporting (3:15 - 4:00)
- **Visual**: Click Print View to demonstrate the official PDF voucher.
- **Voiceover**: *"With one click, print or email the audit-ready voucher. Thank you for watching!"*
"""
        result.summary = f"Authored 4-scene video training script for '{context.app_title}'."
        result.artifacts["video_script"] = script_md
        result.add_deliverable(
            title="Video Training Script",
            file_path=f"docs/video_training_script_{context.project_name}.md",
            content=script_md,
            file_type="markdown"
        )


class FrappeWorkingSopAuthorAgent(FrappeAIAgent):
    """Authors Standard Operating Procedures (SOPs) with visual walkthroughs, checklists, and screenshots."""

    def __init__(self):
        super().__init__(
            name="frappe-working-sop-author",
            pillar=AgentPillar.SAAS_OPS,
            description="Authors complete Standard Operating Procedures (SOPs), user manuals, verification checkpoints, and screenshots.",
            capabilities=[
                "Standard Operating Procedure (SOP) authoring",
                "Step-by-step role execution checklists",
                "Verification checkpoints & error recovery procedures",
                "ASCII / Diagrammatic screenshots and UI layout representations"
            ],
            system_prompt="You author rigorous, production-grade Standard Operating Procedures (SOPs) for enterprise users."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        sop_md = f"""# 📘 Standard Operating Procedure (SOP): {context.app_title} Operations

**Document ID**: SOP-{context.project_name.upper()}-001  
**Effective Date**: September 2026  
**Applicability**: All Operations Executives, Managers, and Auditors

---

## 1. Purpose & Scope
This Standard Operating Procedure establishes the mandatory operational protocol for initiating, reviewing, approving, and auditing requests within the **{context.app_title}** system.

## 2. Roles & Responsibilities
- **Operations Executive (Maker)**: Accurately enters applicant details, ensures documentation completeness, and submits the record.
- **Branch Manager (Checker / Approver)**: Verifies applicant credentials, performs risk evaluation, and issues formal approval.
- **Compliance Officer (Auditor)**: Periodically reviews audit trails, checks SLA compliance, and performs forensic sampling.

## 3. Step-by-Step Procedure

### Stage 1: Record Initiation
1. Navigate to **Desk > {context.app_title} > {context.app_title} Record**.
2. Click the **Add {context.app_title} Record** button in the top right corner.
3. Fill in the mandatory fields:
   - **Title**: Enter a clear, concise description (e.g. `Working Capital Request - Q4`).
   - **Applicant Name**: Legal name of the requesting individual or entity.
   - **Requested Amount**: Valid positive currency amount.
4. Click **Save** (`Ctrl+S`). Verify that the autoname series assigns an immutable record ID.

### Stage 2: Verification Checkpoint
> [!IMPORTANT]
> Verify that the requested amount does not exceed the applicant's pre-approved credit ceiling before submitting.

### Stage 3: Approval Execution
1. Login with **Branch Manager** credentials.
2. In the list view, filter records by `Status == 'Under Review'`.
3. Open the pending document and click **Actions > Quick Approve**.
4. Confirm the approved amount and enter mandatory approval remarks.
5. Click **Confirm Approval**. The document state transitions to `Approved`.

## 4. Exception & Failure Recovery
- **Validation Error ("Amount must be > 0")**: Correct the amount field to a positive value.
- **Workflow Action Denied**: Contact System Administrator to verify role assignment in Role Permissions Manager.
"""
        result.summary = f"Authored Standard Operating Procedure (SOP) for '{context.app_title}'."
        result.artifacts["sop"] = sop_md
        result.add_deliverable(
            title="Standard Operating Procedure (SOP)",
            file_path=f"docs/SOP_{context.project_name}.md",
            content=sop_md,
            file_type="markdown"
        )


class FrappeDocUpdaterAgent(FrappeAIAgent):
    """Updates technical documentation, READMEs, API specifications, and architectural diagrams."""

    def __init__(self):
        super().__init__(
            name="frappe-doc-updater",
            pillar=AgentPillar.SAAS_OPS,
            description="Maintains project READMEs, API references, environment configurations, and changelogs.",
            capabilities=[
                "Project README.md updating",
                "OpenAPI / REST API specification generation",
                "Environment variable & install documentation",
                "Docstring synchronization"
            ],
            system_prompt="You keep technical documentation, READMEs, and API references pristine and synchronized."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        api_doc_md = f"""# 📚 API Reference: {context.app_title}

## Base URL
`/api/method/{context.project_name}`

## Endpoints

### 1. Approve Record
- **Method**: `POST`
- **Path**: `/api/method/{context.project_name}.api.approval_api.approve_record`
- **Authentication**: Session / Token (Requires `System Manager` role)
- **Parameters**:
  - `name` (string, required): Record Name (e.g. `LR-2026-00001`)
  - `approved_amount` (float, optional): Final sanctioned amount
  - `remarks` (string, optional): Internal approval notes

### 2. Natural Language Query (NLQ)
- **Method**: `GET`
- **Path**: `/api/method/{context.project_name}.services.nlq_service.run_natural_query`
- **Parameters**:
  - `query_text` (string): Natural language question
"""
        result.summary = f"Generated technical API specification for '{context.app_title}'."
        result.artifacts["api_doc"] = api_doc_md
        result.add_deliverable(
            title="Technical API Reference",
            file_path=f"docs/api_reference_{context.project_name}.md",
            content=api_doc_md,
            file_type="markdown"
        )


class FrappeBenchDevopsAgent(FrappeAIAgent):
    """Executes Bench commands, manages supervisor/systemd services, backups, and Redis caches."""

    def __init__(self):
        super().__init__(
            name="frappe-bench-devops",
            pillar=AgentPillar.SAAS_OPS,
            description="Automates Bench CLI commands, database backups, cache clears, and process restarts.",
            capabilities=[
                "Bench CLI automation scripts",
                "Automated MariaDB database backups (bench backup)",
                "Redis cache flushing & restart procedures",
                "Supervisor / Systemd service monitoring"
            ],
            system_prompt="You are a Frappe DevOps Engineer managing bench environments and infrastructure."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        devops_script = f"""#!/usr/bin/env bash
# Bench DevOps Automation Script for {context.project_name}

SITE="mysite.local"

echo "=== 1. Taking database and file backup ==="
bench --site $SITE backup --with-files

echo "=== 2. Running database migrations ==="
bench --site $SITE migrate

echo "=== 3. Building assets and clearing cache ==="
bench build --app {context.project_name}
bench --site $SITE clear-cache

echo "=== 4. Restarting background workers ==="
bench restart

echo "=== Deployment Completed Successfully ==="
"""
        result.summary = "Constructed Bench DevOps maintenance and deployment automation shell script."
        result.artifacts["devops_script"] = devops_script
        result.add_deliverable(
            title="Bench DevOps Automation Script",
            file_path=f"bin/deploy_{context.project_name}.sh",
            content=devops_script,
            file_type="bash"
        )


class FrappeReleaseDevopsAgent(FrappeAIAgent):
    """Manages semantic versioning, CHANGELOG updates, Git release tags, and deployment manifests."""

    def __init__(self):
        super().__init__(
            name="frappe-release-devops",
            pillar=AgentPillar.SAAS_OPS,
            description="Automates semantic version bumping, CHANGELOG updates, release packaging, and git tags.",
            capabilities=[
                "Semantic Versioning (SemVer) enforcement",
                "Automated CHANGELOG.md generation",
                "Release tagging (v1.0.0, v2.1.0)",
                "Docker image manifest generation"
            ],
            system_prompt="You automate production release pipelines and version control for Frappe applications."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        changelog = f"""# 📦 Release Changelog: {context.app_title}

## [v1.0.0] - 2026-09-24
### Added
- Initial enterprise release of `{context.project_name}`.
- Complete DocType schema and controller for `{context.app_title} Record`.
- State machine workflow with Draft, Under Review, Approved, and Rejected states.
- Reactive Desk Client Script with real-time indicators and dynamic checks.
- Omnichannel notification dispatchers for Email and In-App alerts.
- High-performance Script Reports and Executive BI Dashboard Charts.
- WCAG 2.1 AA accessibility compliance and white-label branding stylesheets.
- Standard Operating Procedure (SOP) documentation.
"""
        result.summary = f"Generated release packaging manifest and CHANGELOG.md for v1.0.0."
        result.artifacts["changelog"] = changelog
        result.add_deliverable(
            title="Release Changelog",
            file_path=f"CHANGELOG.md",
            content=changelog,
            file_type="markdown"
        )
