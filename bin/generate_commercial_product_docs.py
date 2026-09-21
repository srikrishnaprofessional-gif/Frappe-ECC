#!/usr/bin/env python3
"""
Generates the executive FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.docx and .pdf.
Presents Frappe Autonomous Enterprise Studio (Frappe AES):
The Complete Autonomous No-Code & Low-Code Product Platform (52 Agents, 18 Skills, 50 Commands).
"""

import os
import sys
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text, title="COMMERCIAL VALUE PROPOSITION", alert_type="brand"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
    
    border_colors = {"brand": "0D9488", "warning": "D97706", "success": "16A34A", "note": "2563EB"}
    bg_colors = {"brand": "F0FDFA", "warning": "FFFBEB", "success": "F0FDF4", "note": "EFF6FF"}
    
    fill_hex = bg_colors.get(alert_type, "F0FDFA")
    b_color = border_colors.get(alert_type, "0D9488")
    set_cell_background(cell, fill_hex)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{b_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"[{title}] ")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = RGBColor.from_string(b_color)
    
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_row(row, bg_hex, text_color="333333", is_header=False):
    for cell in row.cells:
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(8.5 if not is_header else 9)
                r.font.color.rgb = RGBColor.from_string(text_color)
                if is_header:
                    r.bold = True

def build_commercial_product_doc():
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("FRAPPE AUTONOMOUS ENTERPRISE STUDIO (AES)")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(13, 148, 136) # Teal
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("The Turnkey No-Code / Low-Code AI Operating Platform for Global Enterprises\n52 Specialized Autonomous Agents | 18 Production Skills | 50 Slash Commands")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_heading("1. Executive Summary & Market Paradigm Shift", level=1)
    doc.add_paragraph(
        "Frappe Autonomous Enterprise Studio (Frappe AES) eliminates the multi-month engineering backlog and "
        "prohibitive per-seat licensing of legacy low-code platforms (ServiceNow, OutSystems, Mendix, Salesforce). "
        "By orchestrating 52 domain-specialist AI agents on top of the open-source Frappe Framework and ERPNext engine, "
        "it delivers a complete, autonomous no-code environment where non-technical executives and teams create, "
        "customize, translate, monetize, and audit mission-critical enterprise applications in under 5 minutes."
    )
    
    add_callout(
        doc,
        "Commercial Differentiation: Traditional low-code suites charge $150 to $300 per user per month with closed proprietary "
        "runtime lock-in. Frappe AES operates on open-source standards with $0 per-seat licensing, unlimited users, and 100% "
        "data sovereignty on-premises, cloud, or hybrid.",
        title="COMMERCIAL ADVANTAGE",
        alert_type="brand"
    )
    
    doc.add_heading("2. Market Benchmark: Frappe AES vs. Legacy Platforms", level=1)
    
    comp_tbl = doc.add_table(rows=1, cols=6)
    comp_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = comp_tbl.rows[0]
    headers = ["Metric / Feature", "ServiceNow", "OutSystems", "Mendix", "Salesforce", "Frappe AES"]
    for i, title in enumerate(headers):
        hdr.cells[i].paragraphs[0].text = title
    format_row(hdr, "0D9488", "FFFFFF", is_header=True)
    
    comp_data = [
        ("Foundation", "Proprietary", "Proprietary PaaS", "Mendix Runtime", "Force.com Cloud", "Open-Source Frappe"),
        ("Seat Pricing", "$100-$250/u/mo", "$1,500+/mo base", "$2,000+/mo base", "$150-$300/u/mo", "$0 Per-Seat Fees"),
        ("Lock-In", "100% Locked", "High", "100% Locked", "100% Locked", "Zero Lock-In"),
        ("App Creation", "Complex Studio", "Visual Studio IDE", "Low-Code Modeler", "Complex Setup", "Prompt/Excel/Voice/OCR"),
        ("Autonomous AI", "Assistive Only", "Copilot Suggestions", "Basic Bots", "Agentforce ($$$)", "52 Coordinated Agents"),
        ("Deployment", "SaaS Only", "Cloud/Hybrid", "Cloud/Hybrid", "SaaS Only", "Self-Hosted / Cloud / Air-Gap"),
        ("Time-to-Market", "3-9 Months", "2-6 Months", "2-6 Months", "4-12 Months", "Under 5 Minutes"),
    ]
    for row_idx, data in enumerate(comp_data):
        row = comp_tbl.add_row()
        for c_idx, val in enumerate(data):
            row.cells[c_idx].paragraphs[0].text = val
        bg = "F0FDFA" if row_idx % 2 == 0 else "FFFFFF"
        format_row(row, bg, "333333")
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    doc.add_heading("3. The 8 Enterprise Architectural Pillars (52 Agents)", level=1)
    doc.add_paragraph(
        "Frappe AES organizes its 52 autonomous agents into 8 tightly-integrated enterprise pillars that span the entire "
        "application lifecycle from non-technical ingestion to continuous post-launch customer support:"
    )
    
    pillars = [
        ("Pillar 1: No-Code Front Door & Ingestion", [
            ("frappe-autonomous-orchestrator", "Master director coordinating prompt-to-production DAG execution pipelines."),
            ("frappe-prompt-to-app-builder", "Pure natural language prompt to complete relational Frappe application in 60s."),
            ("frappe-excel-csv-app-converter", "Ingests messy spreadsheets, normalizes 3NF schemas, creates child tables, and seeds records."),
            ("frappe-voice-command-copilot", "Audio-to-action engine for voice navigation, spoken record creation, and audio KPI briefings."),
            ("frappe-ocr-document-ingestor", "Vision/OCR pipeline extracting structured data from scanned invoices, receipts, and PDFs.")
        ]),
        ("Pillar 2: Product Architecture & System Design", [
            ("frappe-product-manager", "Domain discovery, PRD specification & user story acceptance criteria."),
            ("frappe-hld-architect", "High-Level Design (HLD) with Mermaid C4 architecture diagrams."),
            ("frappe-lld-designer", "Low-Level Design (LLD) with Mermaid ER diagrams and state machines."),
            ("frappe-planner", "Architectural blueprinting, DocType taxonomy & build sequence."),
            ("frappe-architect", "System-level design, bench multi-tenancy & RQ queue topology.")
        ]),
        ("Pillar 3: Visual Workflows & Omnichannel Automations", [
            ("frappe-bpmn-visual-workflow-builder", "Visual BPMN 2.0 drag-and-drop state machines and approval hierarchies."),
            ("frappe-notification-omnichannel-agent", "Real-time alerts across WhatsApp, Twilio SMS, Slack, Email, and MS Teams."),
            ("frappe-cron-scheduler-optimizer", "Visual background recurring tasks and Redis RQ queue load balancing."),
            ("frappe-sla-escalation-manager", "Real-time SLA breach detection, countdown timers, and automated supervisory escalation."),
            ("frappe-integrations-broker", "Pre-built connectors for Stripe, PayPal, S3/GCS, and external ERPs."),
            ("frappe-api-integrator", "REST APIs, webhooks, and third-party event listeners.")
        ]),
        ("Pillar 4: Enterprise Analytics, BI & AI Intelligence", [
            ("frappe-bi-dashboard-synthesizer", "Interactive executive workspaces, KPI scorecards, funnel charts, and board deck exports."),
            ("frappe-natural-language-query-agent", "Conversational ERP AI ('Chat with your ERP Data' text-to-SQL/QueryBuilder)."),
            ("frappe-predictive-ai-forecaster", "ML time-series demand forecasting, cash flow prediction, and anomaly detection."),
            ("frappe-audit-trail-forensic-inspector", "Tamper-proof audit logger, fraud detector, and Segregation of Duties (SoD) scanner."),
            ("frappe-report-builder", "Script Reports (Python + JS) and custom analytical queries.")
        ]),
        ("Pillar 5: UI/UX, Multi-Experience & Theming", [
            ("frappe-ui-ux-designer", "UI/UX design, desk ergonomics, workspace dashboards, and mobile UX."),
            ("frappe-wireframe-builder", "Visual ASCII, Markdown, and SVG wireframe mockups."),
            ("frappe-interactive-prototyper", "Clickable standalone interactive HTML/Vue prototypes."),
            ("frappe-white-label-branding-themer", "1-click corporate visual identity customizer (logos, palettes, typography, custom CSS)."),
            ("frappe-mobile-app-pwa-generator", "Mobile Progressive Web App (PWA) with offline sync and camera barcode scanner."),
            ("frappe-portal-ecommerce-builder", "Customer and supplier self-service web portals, catalogs, and extranets."),
            ("frappe-accessibility-wcag-compliance", "WCAG 2.1 AA accessibility auditing and screen reader compliance."),
            ("frappe-print-format-designer", "Print-ready Jinja2 invoices, vouchers, and QR barcode labels.")
        ]),
        ("Pillar 6: Turnkey Development & Autonomous Healing", [
            ("frappe-fullstack-developer", "Turnkey end-to-end fullstack feature synthesis without placeholders."),
            ("frappe-backend-builder", "Python DocType controllers, lifecycle hooks & QueryBuilder."),
            ("frappe-desk-builder", "Desk client scripts, form UI events, dialogs & buttons."),
            ("frappe-data-synthesizer", "Domain-accurate seed fixtures and relational test data."),
            ("frappe-migration-patcher", "Database schema migrations and idempotent patches.txt scripts."),
            ("frappe-self-healing-debugger", "Automated root-cause isolation and surgical patch repair for test crashes.")
        ]),
        ("Pillar 7: Enterprise QA, Security & Governance", [
            ("frappe-tdd-guide", "Test-driven development with FrappeTestCase unit tests."),
            ("frappe-manual-qa", "Comprehensive manual test plans, edge-case matrices, and sign-offs."),
            ("frappe-automated-tester", "Playwright E2E browser automation & REST API regression tests."),
            ("frappe-code-reviewer", "Fresh-context reviewer detecting Frappe anti-patterns."),
            ("frappe-security-reviewer", "Static security analyzer detecting SQLi, CSRF, and broken access control."),
            ("frappe-rbac-compliance-guardian", "Role-based access control, Custom DocPerms, and permission query filters."),
            ("frappe-gdpr-data-privacy-officer", "PII anonymization, GDPR Right-to-be-Forgotten, and consent audit logs.")
        ]),
        ("Pillar 8: Commercial SaaS, Support & Continuous Operations", [
            ("frappe-saas-multitenancy-orchestrator", "Multi-tenant site provisioning, Stripe subscription tiers, and seat metering."),
            ("frappe-multilingual-localization-agent", "100+ language localization, auto-translation, and RTL layout support."),
            ("frappe-data-migration-concierge", "Legacy ERP migration wizards (SAP, Odoo, QuickBooks, Zoho, Salesforce)."),
            ("frappe-interactive-guided-tour-author", "In-app interactive guided walkthroughs (Driver.js / Shepherd.js)."),
            ("frappe-helpdesk-customer-support-copilot", "24/7 AI-powered customer support bot trained on system docs & SOPs."),
            ("frappe-training-video-scriptwriter", "Structured video narration scripts, quizzes, and certification rubrics."),
            ("frappe-working-sop-author", "Visual Working SOPs & operator manuals with embedded UI screenshots."),
            ("frappe-doc-updater", "Auto-documentation for DocTypes, APIs, and hooks registries."),
            ("frappe-bench-devops", "Bench CLI operations, Redis/RQ worker tuning, and site repair."),
            ("frappe-release-devops", "CI/CD GitHub Actions workflows, Docker packaging, and cloud deployment.")
        ])
    ]
    
    for p_name, agent_list in pillars:
        p_hdr = doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(8)
        p_hdr.paragraph_format.space_after = Pt(2)
        r_ph = p_hdr.add_run(f"■ {p_name} ({len(agent_list)} Agents)")
        r_ph.bold = True
        r_ph.font.name = "Segoe UI"
        r_ph.font.size = Pt(11)
        r_ph.font.color.rgb = RGBColor(13, 148, 136)
        
        p_tbl = doc.add_table(rows=1, cols=2)
        p_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_p = p_tbl.rows[0]
        hdr_p.cells[0].paragraphs[0].text = "Autonomous Agent"
        hdr_p.cells[1].paragraphs[0].text = "Operational Mission & Enterprise Deliverables"
        format_row(hdr_p, "0D9488", "FFFFFF", is_header=True)
        
        for r_idx, (ag_name, ag_desc) in enumerate(agent_list):
            row = p_tbl.add_row()
            row.cells[0].paragraphs[0].text = ag_name
            row.cells[1].paragraphs[0].text = ag_desc
            bg = "F0FDFA" if r_idx % 2 == 0 else "FFFFFF"
            format_row(row, bg, "333333")
            
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        
    doc.add_heading("4. Commercial Monetization & Licensing Model", level=1)
    
    tier_tbl = doc.add_table(rows=1, cols=4)
    tier_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_tier = tier_tbl.rows[0]
    h_tier.cells[0].paragraphs[0].text = "Licensing Tier"
    h_tier.cells[1].paragraphs[0].text = "Commercial Price"
    h_tier.cells[2].paragraphs[0].text = "Target Audience"
    h_tier.cells[3].paragraphs[0].text = "Included Platform Capabilities"
    format_row(h_tier, "0D9488", "FFFFFF", is_header=True)
    
    tiers = [
        ("Community Edition", "Free / Open Source", "Developers & Solo Founders", "Core 29 dev agents, CLI commands, basic scaffolding, community support."),
        ("Professional Studio", "$499 / site / month", "Fast-growing SMEs & Startups", "All 52 agents, No-Code Front Door, WhatsApp notifications, Executive BI dashboards."),
        ("Enterprise Autonomous Fabric", "$2,499 / cluster / mo", "Mid-to-Large Enterprises", "Unlimited users, White-Labeling, Mobile PWA, Multi-Tenancy, GDPR, WCAG, 24/7 AI Helpdesk."),
        ("Global SI & Agency Partner", "$9,999 / year", "System Integrators & Agencies", "White-label reselling rights, unlimited client app generation, custom agent authoring engine.")
    ]
    for r_idx, (t_name, t_price, t_target, t_incl) in enumerate(tiers):
        row = tier_tbl.add_row()
        row.cells[0].paragraphs[0].text = t_name
        row.cells[1].paragraphs[0].text = t_price
        row.cells[2].paragraphs[0].text = t_target
        row.cells[3].paragraphs[0].text = t_incl
        bg = "F0FDFA" if r_idx % 2 == 0 else "FFFFFF"
        format_row(row, bg, "333333")
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    doc.add_heading("5. Verification & Launch Readiness", level=1)
    doc.add_paragraph(
        "Frappe Autonomous Enterprise Studio has been fully validated with an end-to-end IT Equipment Loan & Return "
        "reference project, featuring live interactive prototypes, unit and Playwright E2E test suites, whitelisted REST APIs, "
        "and published Working SOPs with embedded UI screenshots. The platform is ready for commercial enterprise deployment."
    )
    
    add_callout(
        doc,
        "System Status: 52 Autonomous Agents, 18 Production Skills, and 50 Slash Commands are registered and "
        "operational across Antigravity, Claude Code, Cursor, and Codex CLI runtimes.",
        title="SYSTEM STATUS: PRODUCTION READY",
        alert_type="success"
    )
    
    output_docx = DOCS_DIR / "FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.docx"
    doc.save(str(output_docx))
    print(f"[SUCCESS] Built Commercial Product Word document: {output_docx}")
    return output_docx

def convert_docx_to_pdf(docx_path):
    pdf_path = docx_path.with_suffix(".pdf")
    ps_cmd = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{docx_path}')
    $doc.SaveAs([ref]'{pdf_path}', [ref]17)
    $doc.Close()
    Write-Host "PDF_CONVERT_SUCCESS"
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}} finally {{
    $word.Quit()
}}
"""
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60)
        if "PDF_CONVERT_SUCCESS" in res.stdout:
            print(f"[SUCCESS] Commercial Product PDF generated: {pdf_path}")
            return pdf_path
        else:
            print(f"[WARNING] Word COM conversion returned: {res.stdout} / {res.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to run Word COM conversion: {e}")
        return None

def main():
    docx_path = build_commercial_product_doc()
    pdf_path = convert_docx_to_pdf(docx_path)
    
    downloads_dir = Path(r"C:\Users\srikrishna.rg_quanti\Downloads")
    if downloads_dir.exists():
        import shutil
        if docx_path.exists():
            shutil.copy2(str(docx_path), str(downloads_dir / docx_path.name))
            print(f"[SUCCESS] Copied Commercial Product DOCX to Downloads: {downloads_dir / docx_path.name}")
        if pdf_path and pdf_path.exists():
            shutil.copy2(str(pdf_path), str(downloads_dir / pdf_path.name))
            print(f"[SUCCESS] Copied Commercial Product PDF to Downloads: {downloads_dir / pdf_path.name}")

if __name__ == "__main__":
    main()
