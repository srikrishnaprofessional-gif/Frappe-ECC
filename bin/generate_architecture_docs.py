#!/usr/bin/env python3
"""
Generates the comprehensive FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx
and converts it to FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf.
Covers:
- AI Foundation & Cognitive Architecture
- 20-Agent Catalog with Inputs, Processing, Outputs, and Downstream Consumers
- Multi-Agent Data Pipelines & Contract-First Handoff Models
- Case Study: equipment_loan End-to-End Pipeline Execution
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

def add_callout(doc, text, title="NOTE", alert_type="note"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
    
    border_colors = {"note": "1F4E79", "warning": "D83B01", "tip": "107C41", "brand": "4F46E5"}
    bg_colors = {"note": "F0F4F8", "warning": "FFF4CE", "tip": "EDF7ED", "brand": "EEF2FF"}
    
    fill_hex = bg_colors.get(alert_type, "F0F4F8")
    b_color = border_colors.get(alert_type, "1F4E79")
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

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(code_text.strip())
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(36, 41, 46)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_docx(output_path):
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        header = section.header
        hp = header.paragraphs[0]
        hp.text = "MULTI-AGENT COGNITIVE ARCHITECTURE & PIPELINE SPECIFICATION | FRAPPE ECC"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp.style.font.name = "Calibri"
        hp.style.font.size = Pt(8.5)
        hp.style.font.color.rgb = RGBColor(128, 128, 128)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = "Document ID: ARCH-SPEC-FRAPPE-ECC-001  |  Version 1.0.0  |  Engineering Standard"
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fp.style.font.name = "Calibri"
        fp.style.font.size = Pt(8.5)
        fp.style.font.color.rgb = RGBColor(128, 128, 128)

    # Document Header
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("MULTI-AGENT COGNITIVE ARCHITECTURE & PIPELINE SPECIFICATION")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(20)
    run_title.font.color.rgb = RGBColor(31, 78, 121)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    run_sub = p_sub.add_run("Engineering Coordination Center for Frappe Framework & ERPNext (Frappe ECC)")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12.5)
    run_sub.font.color.rgb = RGBColor(89, 89, 89)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Document ID", "ARCH-SPEC-FRAPPE-ECC-001"),
        ("System Release", "Frappe ECC v1.1.0 (20 Autonomous Agents • 18 Skills • 20 Commands)"),
        ("Effective Date", "2026-09-21"),
        ("Target Runtimes", "Frappe Framework v14/v15/v16, ERPNext, Antigravity IDE, Claude Code, Cursor, Codex")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.0)
        c1.width = Inches(4.7)
        set_cell_background(c0, "E9EEF4")
        set_cell_margins(c0, 45, 45, 75, 75)
        set_cell_margins(c1, 45, 45, 75, 75)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(9)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_sec_heading(text, level=1):
        h = doc.add_heading(text, level=level)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        return h

    # Section 1
    add_sec_heading("1. Executive Summary & AI Foundation", level=1)
    doc.add_paragraph(
        "The Frappe Engineering Coordination Center (Frappe ECC) establishes a specialized multi-agent cognitive architecture "
        "designed specifically for developing, testing, securing, and maintaining Frappe Framework and ERPNext applications. "
        "Rather than relying on generic, monolithic LLM code generation, Frappe ECC decomposes the entire software engineering "
        "lifecycle into 20 specialized autonomous agents operating across 6 synchronized pipeline stages."
    ).paragraph_format.space_after = Pt(6)

    add_callout(
        doc,
        "Frappe ECC combines non-deterministic reasoning from Frontier LLMs (Gemini 1.5 Pro, Claude 3.5 Sonnet, GPT-4o) with "
        "deterministic verification tools (Frappe Shield AST static analyzer, Playwright E2E browser automation, and FrappeTestCase) "
        "to provide a zero-hallucination, zero-placeholder engineering standard.",
        title="CORE AI PARADIGM",
        alert_type="brand"
    )

    doc.add_paragraph(
        "The system rests upon four technical pillars:\n"
        "1. Role-Specialized Cognitive Decomposition: 20 agents constrained by dedicated persona guardrails.\n"
        "2. Retrieval-Augmented Skill Loading (RAG): On-demand injection of 18 Frappe-specific skills into agent context.\n"
        "3. Deterministic AST Security Analysis: Python Abstract Syntax Tree scanning via Frappe Shield to verify SQL injection defense, transaction boundaries, and authorization checks.\n"
        "4. Automated Self-Correction Loops: Runtime test errors and AST scan failures are piped directly back to the agent for iterative self-healing."
    ).paragraph_format.space_after = Pt(6)

    # Section 2
    add_sec_heading("2. Multi-Agent Data Pipeline Architecture", level=1)
    doc.add_paragraph(
        "Frappe ECC enforces a Contract-First, Test-Driven Handoff Model. Upstream agents generate formal, structured artifacts "
        "(Markdown specifications with Mermaid diagrams, JSON schemas, or Python test suites) that serve as the strict input contract "
        "for downstream agents:"
    ).paragraph_format.space_after = Pt(6)

    pipeline_ascii = (
        "[Phase 1: Architecture]    [Phase 2: UX & Prototype]       [Phase 3: TDD & QA]          [Phase 4: Implementation]\n"
        "  frappe-hld-architect      frappe-ui-ux-designer            frappe-tdd-guide             frappe-fullstack-developer\n"
        "  frappe-lld-designer  -->  frappe-wireframe-builder  -->    frappe-manual-qa       -->   frappe-backend-builder\n"
        "  frappe-planner            frappe-interactive-prototyper    frappe-automated-tester      frappe-desk-builder\n"
        "                                                                                          frappe-api-integrator\n"
        "                                                                                                   │\n"
        "                                                                                                   ▼\n"
        "                               [Phase 6: Quality & Security]   <--   [Phase 5: DevOps & Migrations]\n"
        "                                 frappe-code-reviewer                  frappe-architect\n"
        "                                 frappe-security-reviewer              frappe-bench-devops\n"
        "                                 (Frappe Shield AST Engine)            frappe-migration-patcher\n"
        "                                                                       frappe-doc-updater"
    )
    add_code_block(doc, pipeline_ascii)

    # Section 3
    add_sec_heading("3. Comprehensive 20-Agent Catalog & Operational Specs", level=1)
    doc.add_paragraph(
        "The following matrix outlines each agent's system role, exact inputs received, internal cognitive processing, "
        "generated output artifact, and downstream consumer agents:"
    ).paragraph_format.space_after = Pt(6)

    # Agent Table
    agent_table = doc.add_table(rows=21, cols=5)
    agent_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Specialist Agent", "Primary Input", "Cognitive Processing", "Output Artifact", "Downstream Consumer"]
    for col_idx, h in enumerate(headers):
        cell = agent_table.rows[0].cells[col_idx]
        set_cell_background(cell, "1F4E79")
        set_cell_margins(cell, 50, 50, 60, 60)
        cp = cell.paragraphs[0]
        cr = cp.add_run(h)
        cr.bold = True
        cr.font.name = "Calibri"
        cr.font.color.rgb = RGBColor(255, 255, 255)
        cr.font.size = Pt(8.5)

    agents_data = [
        ("frappe-hld-architect", "Business PRD, feature request", "C4 container modeling, queue topology, Redis caching strategy", "HLD_<feature>.md", "frappe-lld-designer, frappe-planner"),
        ("frappe-lld-designer", "HLD.md", "Entity modeling, field datatypes, state transition matrices, API contracts", "LLD_<feature>.md", "frappe-ui-ux-designer, frappe-planner, frappe-tdd-guide"),
        ("frappe-planner", "HLD.md + LLD.md", "Taxonomy mapping, autonaming rules, DocType scaffolding", "DocType JSON blueprints", "frappe-fullstack-developer, frappe-tdd-guide"),
        ("frappe-ui-ux-designer", "LLD.md state machine & fields", "Desk layout ergonomics, visual tokens, responsive form specs", "UI/UX design guidelines", "frappe-wireframe-builder"),
        ("frappe-wireframe-builder", "UI/UX guidelines + field schemas", "Layout wireframing, child table grid design, modal dialog mockups", "wireframes.md", "frappe-interactive-prototyper"),
        ("frappe-interactive-prototyper", "wireframes.md + sample fixtures", "Single-file Vue 3/Tailwind interactive prototype synthesis", "interactive_prototype.html", "Stakeholder Sign-Off, frappe-desk-builder"),
        ("frappe-tdd-guide", "LLD.md validation rules", "Red-Green-Refactor test scaffolding; exception assertions", "test_<doctype>.py", "frappe-fullstack-developer"),
        ("frappe-manual-qa", "Prototype & Controller rules", "Boundary condition analysis, exploratory charters, QA matrices", "test_scenarios.md & test_data.json", "frappe-automated-tester, QA Engineers"),
        ("frappe-automated-tester", "Form DOM selectors & QA scenarios", "Headless Playwright script generation; form entry & state assertions", "test_e2e_playwright.py", "CI/CD Runner, Bench test runner"),
        ("frappe-fullstack-developer", "Prototype + LLD.md + Failing tests", "Vertical slice code synthesis with zero placeholders", "<doctype>/ (.json, .py, .js)", "frappe-backend-builder, frappe-desk-builder"),
        ("frappe-backend-builder", "Controller draft & business rules", "Lifecycle hooks (validate, on_submit), QueryBuilder (frappe.qb)", "Production <doctype>.py", "frappe-security-reviewer, frappe-code-reviewer"),
        ("frappe-desk-builder", "Prototype interactions", "Desk form client scripts (frappe.ui.form.on), dynamic dialogs", "<doctype>.js", "frappe-code-reviewer"),
        ("frappe-api-integrator", "LLD.md API contracts", "Whitelisted REST endpoints, rate limiting, authentication", "<api_name>.py", "External clients, frappe-security-reviewer"),
        ("frappe-report-builder", "Query specs & KPI metrics", "Script Reports (Python aggregator + JS visual filter chart)", "<report>.py & <report>.js", "Executive Dashboards"),
        ("frappe-architect", "System-wide events & requirements", "Hook registration (doc_events, cron schedulers, class overrides)", "Updated hooks.py", "frappe-bench-devops"),
        ("frappe-bench-devops", "Site config & worker errors", "Multi-tenancy diagnostics, worker tuning (Redis RQ), site provisioning", "Bench execution commands", "System Administrators"),
        ("frappe-migration-patcher", "Schema diffs between versions", "Idempotent database patches; column conversions without data loss", "patches/<patch>.py & patches.txt", "Bench migrate workflow"),
        ("frappe-doc-updater", "Schemas, APIs, and controllers", "API documentation synchronization and end-user manuals", "README.md, developer docs", "Technical Writers & End Users"),
        ("frappe-code-reviewer", "Git diff of implemented code", "Fresh-context review for Frappe anti-patterns and N+1 query loops", "Structured code review report", "Software Engineers"),
        ("frappe-security-reviewer", "Full application codebase", "AST static analysis (SQLi, CSRF, IDOR, transaction leaks)", "Security audit report (frappe-shield)", "Release Managers & CI/CD")
    ]

    for idx, row_data in enumerate(agents_data):
        row = agent_table.rows[idx + 1]
        bg_color = "FFFFFF" if idx % 2 == 0 else "F8FAFC"
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, 35, 35, 50, 50)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(31, 78, 121)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section 4
    add_sec_heading("4. Concrete Pipeline Execution Case Study: IT Equipment Loan System", level=1)
    doc.add_paragraph(
        "The IT Equipment Loan & Return System (equipment_loan) implemented in this repository serves as the benchmark "
        "demonstration of the multi-agent pipeline executing seamlessly from PRD to production commit:"
    ).paragraph_format.space_after = Pt(6)

    case_study_steps = [
        ("Step 1: HLD Architecture", "frappe-hld-architect synthesized HLD_Equipment_Loan.md defining C4 container boundaries, submittable document lifecycle, Redis queue integration, and 30-day corporate SLA limits."),
        ("Step 2: LLD & Entity Modeling", "frappe-lld-designer ingested HLD and formulated LLD_Equipment_Loan.md with Mermaid erDiagram connecting Loanable Asset (Master), Equipment Loan (Parent Submittable), and Equipment Loan Item (Child Table)."),
        ("Step 3: MAANG-Grade Prototyping", "frappe-wireframe-builder and frappe-interactive-prototyper produced interactive_prototype.html, a standalone Vue 3/Tailwind experience featuring dynamic badge states, live 30-day SLA meters, inventory checks, command palette (Ctrl+K), and modal return dialogs."),
        ("Step 4: TDD & QA Matrix Scaffolding", "frappe-tdd-guide and frappe-manual-qa drafted test_data.json, test_scenarios.md (10 comprehensive cases), and test_equipment_loan.py prior to controller implementation."),
        ("Step 5: Turnkey Fullstack Synthesis", "frappe-fullstack-developer implemented equipment_loan.json schema, equipment_loan.py controller, equipment_loan.js Desk script, and loan_api.py whitelisted REST endpoint with zero placeholders."),
        ("Step 6: Automated Browser Verification", "frappe-automated-tester created test_e2e_playwright.py driving Desk login, form entry, child table insertion, and document submission."),
        ("Step 7: AST Security Audit", "frappe-security-reviewer executed bin/frappe-shield.py across the test project, certifying 0 critical and 0 high issues, guaranteeing absence of SQL injection and docstatus bypasses."),
        ("Step 8: Remote Repository Sync", "All assets, test results, and prototypes were staged, committed (59096f3), and pushed to https://github.com/srikrishnaprofessional-gif/Frappe-ECC.")
    ]

    for title, desc in case_study_steps:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        rt = p.add_run(f"• {title}: ")
        rt.bold = True
        rt.font.name = "Calibri"
        rt.font.size = Pt(9)
        rt.font.color.rgb = RGBColor(31, 78, 121)
        rd = p.add_run(desc)
        rd.font.name = "Calibri"
        rd.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section 5
    add_sec_heading("5. Architectural Governance & Quality Guarantees", level=1)
    doc.add_paragraph(
        "Frappe ECC guarantees enterprise software delivery through three core constraints:\n"
        "1. Zero Hallucination Guarantee: Downstream agents strictly inherit schemas, datatypes, and relation links defined upstream in HLD/LLD.\n"
        "2. Deterministic AST Security: All generated Python code is checked by Frappe Shield's Abstract Syntax Tree analyzer before merge approval.\n"
        "3. Zero-Placeholder Policy: All generated DocTypes, controllers, client scripts, and tests are turnkey and 100% executable with no '# TODO' shortcuts."
    ).paragraph_format.space_after = Pt(6)

    doc.save(str(output_path))
    print(f"[SUCCESS] Built Word document: {output_path}")

def convert_to_pdf(docx_path, pdf_path):
    ps_script = f"""
    $ErrorActionPreference = "Stop"
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $docx = "{str(docx_path.resolve())}"
    $pdf = "{str(pdf_path.resolve())}"
    try {{
        $doc = $word.Documents.Open($docx)
        $doc.SaveAs([ref]$pdf, [ref]17)
        $doc.Close()
        Write-Output "SUCCESS"
    }} finally {{
        $word.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    }}
    """
    
    ps_file = DOCS_DIR / "_convert_tmp.ps1"
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(ps_script)
        
    try:
        res = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[SUCCESS] PDF generated: {pdf_path}")
    finally:
        if ps_file.exists():
            ps_file.unlink()

def main():
    docx_path = DOCS_DIR / "FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx"
    pdf_path = DOCS_DIR / "FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf"
    
    build_docx(docx_path)
    convert_to_pdf(docx_path, pdf_path)
    
    user_downloads = Path.home() / "Downloads"
    if user_downloads.exists():
        import shutil
        shutil.copy2(docx_path, user_downloads / "FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx")
        shutil.copy2(pdf_path, user_downloads / "FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf")
        print(f"[SUCCESS] Copied to Downloads: {user_downloads / 'FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf'}")

if __name__ == "__main__":
    main()
