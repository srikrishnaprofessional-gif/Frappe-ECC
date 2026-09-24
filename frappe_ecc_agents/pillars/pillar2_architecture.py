"""
Pillar 2: Architecture & Analysis Agents
Includes:
1. FrappeProductManagerAgent (frappe-product-manager)
2. FrappeHldArchitectAgent (frappe-hld-architect)
3. FrappeLldDesignerAgent (frappe-lld-designer)
4. FrappePlannerAgent (frappe-planner)
5. FrappeArchitectAgent (frappe-architect)
"""

import json
from typing import Dict, Any, List
from ..base import FrappeAIAgent, AgentContext, AgentResult, AgentPillar


class FrappeProductManagerAgent(FrappeAIAgent):
    """Produces comprehensive Product Requirement Documents (PRDs), personas, and user stories."""

    def __init__(self):
        super().__init__(
            name="frappe-product-manager",
            pillar=AgentPillar.ARCHITECTURE,
            description="Authors comprehensive PRDs, defining target personas, functional requirements, user journeys, and acceptance criteria.",
            capabilities=[
                "PRD authoring",
                "User persona definition",
                "User story mapping with Gherkin scenarios",
                "Success metrics and KPI definition"
            ],
            system_prompt="You are a senior Product Manager specializing in enterprise ERP and Frappe Framework applications."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        app_title = context.app_title
        app_name = context.project_name

        prd_content = f"""# 📋 Product Requirement Document (PRD): {app_title}

## 1. Executive Summary
{app_title} (`{app_name}`) is designed to streamline and automate end-to-end business operations with zero manual friction, role-based workflows, and real-time observability.

## 2. Target Personas
1. **Business Administrator / Approver**: Needs a holistic birds-eye view of incoming requests, approvals, and compliance flags.
2. **Operations Executive / Maker**: Submits records, attaches supporting documentation, and tracks life-cycle progression.
3. **Auditor / Compliance Inspector**: Requires read-only access to immutable audit trails, change logs, and SLA timelines.

## 3. Core Functional Requirements
- **FR-01**: Multi-tiered record submission with dynamic form validation.
- **FR-02**: Automated multi-stage approval workflow with SLA timers.
- **FR-03**: Omnichannel notifications (Email, In-Desk Notifications, Webhooks).
- **FR-04**: Role-Based Access Control (RBAC) with field-level permissions.
- **FR-05**: Interactive Analytics Dashboard with Drill-down capabilities.

## 4. Non-Functional Requirements
- **NFR-01**: Response time under 250ms for 95% of standard REST API transactions.
- **NFR-02**: 100% adherence to Frappe Shield SQL injection prevention standards (`frappe.qb` or parameterized SQL).
- **NFR-03**: Full WCAG 2.1 AA accessibility compliance across Desk and Portal interfaces.
"""
        result.summary = f"Synthesized Product Requirement Document (PRD) for '{app_title}'."
        result.artifacts["prd"] = prd_content
        result.add_deliverable(
            title="Product Requirement Document",
            file_path=f"docs/PRD_{app_name}.md",
            content=prd_content,
            file_type="markdown"
        )


class FrappeHldArchitectAgent(FrappeAIAgent):
    """Authors enterprise High-Level Design (HLD) specifications with Mermaid diagrams and system topology."""

    def __init__(self):
        super().__init__(
            name="frappe-hld-architect",
            pillar=AgentPillar.ARCHITECTURE,
            description="Authors complete High-Level Design (HLD) specifications including Mermaid C4 and container diagrams.",
            capabilities=[
                "High-Level Architecture authoring",
                "Mermaid topology and data flow diagramming",
                "System integration boundary definition",
                "Scalability and tier modeling"
            ],
            system_prompt="You are a Principal Enterprise Architect designing resilient Frappe Framework architectures."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        app_title = context.app_title
        app_name = context.project_name

        hld_content = f"""# 🏛️ High-Level Design (HLD): {app_title}

## 1. System Architecture Diagram

```mermaid
graph TD
    User([Enterprise User / Browser]) -->|HTTPS / WSS| NGINX[NGINX Reverse Proxy]
    NGINX -->|HTTP| Gunicorn[Frappe Web Server / Gunicorn :8000]
    NGINX -->|Socket.IO| NodeWS[Socket.IO Push Service :9000]
    
    subgraph Frappe Application Core
        Gunicorn --> ORM[Frappe Document ORM / QueryBuilder]
        Gunicorn --> Hooks[hooks.py / Event Handlers]
        Hooks --> RedisQueue[Redis Queue RQ :11000]
        RedisQueue --> BackgroundWorkers[RQ Background Workers: default / short / long]
    end
    
    subgraph Data & Storage Persistence
        ORM --> MariaDB[(MariaDB / MySQL Database :3306)]
        Gunicorn --> RedisCache[(Redis Cache :13000)]
        BackgroundWorkers --> MariaDB
        Gunicorn --> ObjectStore[(Encrypted Files / S3 / Local)]
    end
```

## 2. Component Responsibilities
- **Presentation Tier**: Frappe Desk (Vue 3 / Vanilla JS Desk) + PWA Web Portal.
- **Application Tier**: Python 3.10+ Frappe Controller classes and `@frappe.whitelist()` REST endpoints.
- **Background Job Engine**: Redis RQ handling asynchronous calculations, bulk email dispatches, and third-party webhooks.
- **Data Persistence**: MariaDB with InnoDB engine, utf8mb4 collation, and strict indexing.
"""
        result.summary = f"Generated High-Level Design (HLD) specification with Mermaid diagrams."
        result.artifacts["hld"] = hld_content
        result.add_deliverable(
            title="High-Level Design Specification",
            file_path=f"docs/HLD_{app_name}.md",
            content=hld_content,
            file_type="markdown"
        )


class FrappeLldDesignerAgent(FrappeAIAgent):
    """Authors precise Low-Level Design (LLD) specifications, data dictionaries, and state machine diagrams."""

    def __init__(self):
        super().__init__(
            name="frappe-lld-designer",
            pillar=AgentPillar.ARCHITECTURE,
            description="Authors Low-Level Design (LLD) specifications, field data dictionaries, validation triggers, and state machines.",
            capabilities=[
                "Low-Level Design authoring",
                "DocType Schema Data Dictionary",
                "State Transition State Machine modeling",
                "Database Indexing Strategy"
            ],
            system_prompt="You are a Frappe Database Specialist creating granular LLDs and database schemas."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        app_title = context.app_title
        app_name = context.project_name

        lld_content = f"""# 📐 Low-Level Design (LLD): {app_title}

## 1. DocType Schema Dictionary: `{app_title} Record`
| Fieldname | Fieldtype | Mandatory | Description / Validation | Index |
|:---|:---|:---|:---|:---|
| `naming_series` | Select | Yes | Auto-naming prefix (`LR-.YYYY.-.#####`) | Clustered Primary |
| `title` | Data | Yes | Human-readable title (max 140 chars) | B-Tree |
| `status` | Select | Yes | Workflow state: Draft, Under Review, Approved, Rejected | B-Tree |
| `applicant_name` | Data | Yes | Submitting entity or person | - |
| `requested_amount` | Currency | Yes | Precision: 2 decimal places. Must be > 0. | - |
| `approved_amount` | Currency | No | Set upon manager approval | - |
| `submission_date` | Date | No | Default to today's date | - |
| `approval_date` | Datetime | No | Populated upon state transition | - |

## 2. State Machine Transition Diagram
```mermaid
stateDiagram-v2
    [*] --> Draft : User Creates Record
    Draft --> Under_Review : Submit for Review
    Under_Review --> Approved : Manager Approves
    Under_Review --> Rejected : Manager Rejects
    Approved --> Completed : Fulfill / Disburse
    Rejected --> Draft : Reopen for Corrections
    Completed --> [*]
```
"""
        result.summary = f"Produced Low-Level Design (LLD) schema dictionary and state machine."
        result.artifacts["lld"] = lld_content
        result.add_deliverable(
            title="Low-Level Design Specification",
            file_path=f"docs/LLD_{app_name}.md",
            content=lld_content,
            file_type="markdown"
        )


class FrappePlannerAgent(FrappeAIAgent):
    """Builds phased sprint backlogs, dependency graphs, and resource estimates for Frappe builds."""

    def __init__(self):
        super().__init__(
            name="frappe-planner",
            pillar=AgentPillar.ARCHITECTURE,
            description="Generates Work Breakdown Structures (WBS), sprint milestones, critical path dependencies, and effort estimates.",
            capabilities=[
                "Sprint backlog creation",
                "Critical path dependency analysis",
                "Effort estimation in story points / hours",
                "Risk register & mitigation plans"
            ],
            system_prompt="You are an Agile Technical Delivery Planner specializing in rapid Frappe application synthesis."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        plan_content = f"""# 📅 Implementation Plan & Sprint Backlog: {context.app_title}

## Sprint Breakdown
- **Sprint 1: Core Foundation & DocTypes (Days 1-2)**
  - Task 1.1: Initialize app scaffolding via Bench (`{context.project_name}`).
  - Task 1.2: Generate DocType JSON schemas and controllers.
  - Task 1.3: Configure permissions and autoname series.
- **Sprint 2: Workflows, Automations & Scripts (Days 3-4)**
  - Task 2.1: Implement state machine workflow and transitions.
  - Task 2.2: Add Client Scripts for real-time validation and calculation.
  - Task 2.3: Configure automated omnichannel notification hooks.
- **Sprint 3: Analytics, QA & Deployment (Days 5-6)**
  - Task 3.1: Generate Script Reports and Dashboard charts.
  - Task 3.2: Run automated test suite with 100% code coverage.
  - Task 3.3: Publish SOP documentation and push to GitHub.
"""
        result.summary = f"Constructed 3-sprint implementation plan and task backlog."
        result.artifacts["sprint_plan"] = plan_content
        result.add_deliverable(
            title="Sprint Implementation Plan",
            file_path=f"docs/sprint_plan_{context.project_name}.md",
            content=plan_content,
            file_type="markdown"
        )


class FrappeArchitectAgent(FrappeAIAgent):
    """Ensures architectural rigor, caching patterns, background queue routing, and multi-app compatibility."""

    def __init__(self):
        super().__init__(
            name="frappe-architect",
            pillar=AgentPillar.ARCHITECTURE,
            description="Audits and guides architectural decisions, caching policies, queue partitioning, and benchmark scalability.",
            capabilities=[
                "Frappe hooks and monkey-patching governance",
                "Redis caching tier design (frappe.cache)",
                "Queue routing optimization (default, short, long)",
                "Database connection pool optimization"
            ],
            system_prompt="You are a Chief Enterprise Architect validating Frappe Framework design patterns."
        )

    def execute(self, context: AgentContext, result: AgentResult) -> None:
        arch_guidelines = f"""# 🏛️ Architecture Governance & System Guidelines: {context.app_title}

## 1. Caching Policy (`frappe.cache`)
- Cache frequently queried metadata using keys formatted as: `{context.project_name}:metadata:{{docname}}`.
- Invalidate cache entries deterministically in the `on_update` and `on_trash` controller lifecycle methods.

## 2. Background Queue Strategy
- **Short Queue (`timeout=300`)**: Real-time webhook notifications, single document PDF generation.
- **Default Queue (`timeout=600`)**: Standard batch processing and external REST API sync.
- **Long Queue (`timeout=1500`)**: Heavy monthly reconciliations, big data CSV exports.

## 3. Database Integrity
- Enforce strict foreign keys via Frappe `Link` fieldtypes.
- Never execute raw SQL without query parameters. Always utilize `frappe.qb` (PyPika QueryBuilder).
"""
        result.summary = "Produced Architectural Governance guidelines for caching, queues, and DB integrity."
        result.artifacts["architecture_guidelines"] = arch_guidelines
        result.add_deliverable(
            title="Architecture Governance Guidelines",
            file_path=f"docs/architecture_governance_{context.project_name}.md",
            content=arch_guidelines,
            file_type="markdown"
        )
