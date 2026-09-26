#!/usr/bin/env python3
"""
Generates the executive FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.docx and .pdf.
Presents the complete Frappe Autonomous Enterprise Studio (Frappe AES) Project Report
in plain, non-technical English with corporate executive styling.
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

def add_callout(doc, text, title="EXECUTIVE TAKEAWAY", alert_type="brand"):
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

def build_executive_report_doc():
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
    r_title = p_title.add_run("FRAPPE AUTONOMOUS ENTERPRISE STUDIO")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(13, 148, 136)
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Complete Project Report for Non-Technical Leaders, Executives & Business Owners\nHow a 52-Agent Digital Factory Replaces Months of Costly Software Development")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_heading("1. The Big Problem: Why Building Business Software Is Painful Today", level=1)
    doc.add_paragraph(
        "Every modern business needs custom software to run operations — whether it is tracking asset loans, managing patient "
        "care, dispatching rental fleets, or processing purchase orders. Yet, traditional software engineering is notoriously slow, "
        "expensive, and frustrating:"
    )
    doc.add_paragraph(
        "• It Takes Too Long: Typical enterprise software takes 6 to 12 months from first meeting to deployment.\n"
        "• It Costs a Fortune: Engineering teams, designers, and testers cost $150,000 to $500,000+ per custom app.\n"
        "• Extortionate Licensing: Platforms like ServiceNow and Salesforce charge $100 to $300 per employee every month. "
        "A 500-employee company pays over $1,000,000 every single year just for software permissions!"
    )
    
    add_callout(
        doc,
        "The Solution: Frappe Autonomous Enterprise Studio (Frappe AES) eliminates human developer bottlenecks and per-seat fees "
        "by introducing 52 autonomous AI specialists who design, code, test, and deploy complete applications in under 60 seconds.",
        title="CORE VALUE PROPOSITION",
        alert_type="brand"
    )
    
    doc.add_heading("2. What Is Frappe AES? The Digital Software Factory Explained", level=1)
    doc.add_paragraph(
        "Think of Frappe AES as a state-of-the-art digital software factory. You don't need to know how to write code. "
        "You simply interact using the methods you already use every day:"
    )
    doc.add_paragraph(
        "1. Type a Sentence: 'Build an equipment loan tracking app with serial verification and return condition checklists.'\n"
        "2. Drop an Excel Spreadsheet: Upload an existing spreadsheet, and the factory turns it into a relational database.\n"
        "3. Speak Into Your Microphone: Voice dictation transcribes and extracts business logic automatically.\n"
        "4. Scan a Paper Form: The vision OCR engine reads receipts and paper documents directly into verified transactions."
    )
    
    doc.add_heading("3. The 8 Departments of the Factory (The 8 Pillars)", level=1)
    
    dept_tbl = doc.add_table(rows=1, cols=3)
    dept_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = dept_tbl.rows[0]
    hdr.cells[0].paragraphs[0].text = "Department"
    hdr.cells[1].paragraphs[0].text = "Specialist Staff"
    hdr.cells[2].paragraphs[0].text = "Everyday Responsibility"
    format_row(hdr, "0D9488", "FFFFFF", is_header=True)
    
    depts = [
        ("1. The Front Desk", "5 Ingestion Agents", "Welcomes you, reads prompts, spreadsheets, voice, and scanned paper forms."),
        ("2. The Master Architects", "5 Design Agents", "Draws visual blueprints and ensures all database connections make sense."),
        ("3. The Automation Team", "6 Workflow Agents", "Connects WhatsApp alerts, SMS reminders, and multi-tier approval chains."),
        ("4. The Intelligence Unit", "5 BI & ML Agents", "Builds executive charts, predicts cash flow, and enables conversational data queries."),
        ("5. The Design Studio", "8 UI/UX Agents", "Applies brand colors, logos, and turns the app into an installable mobile phone app."),
        ("6. The Building Crew", "6 Coding Agents", "Writes rock-solid Python and database code with automatic bug self-healing."),
        ("7. The Quality Inspectors", "7 QA & Security Agents", "Simulates users, runs automated tests, blocks hackers, and enforces GDPR."),
        ("8. Customer Launch Crew", "10 Support Agents", "Captures UI screenshots, writes visual SOP manuals, and runs a 24/7 AI helpdesk.")
    ]
    for r_idx, (d_name, d_staff, d_resp) in enumerate(depts):
        row = dept_tbl.add_row()
        row.cells[0].paragraphs[0].text = d_name
        row.cells[1].paragraphs[0].text = d_staff
        row.cells[2].paragraphs[0].text = d_resp
        bg = "F0FDFA" if r_idx % 2 == 0 else "FFFFFF"
        format_row(row, bg, "333333")
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    doc.add_heading("4. The Technologies Used (And Why We Chose Them)", level=1)
    doc.add_paragraph(
        "We chose the world's most trusted, open-source technology stack to ensure total speed, reliability, and ownership:\n"
        "• Python: The world's #1 programming language. Powers the calculation engine and business rules.\n"
        "• JavaScript & Vue.js: Powers the interactive web interface so buttons react instantaneously.\n"
        "• MariaDB / PostgreSQL: Enterprise-grade database engines that act as secure, permanent digital vaults.\n"
        "• Redis: High-speed in-memory caching that allows executive dashboards to load in milliseconds.\n"
        "• Frappe Framework & ERPNext: Proven open-source enterprise engine trusted by over 50,000 businesses globally."
    )
    
    doc.add_heading("5. Financial Return on Investment (ROI)", level=1)
    
    roi_tbl = doc.add_table(rows=1, cols=4)
    roi_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_roi = roi_tbl.rows[0]
    h_roi.cells[0].paragraphs[0].text = "Financial Metric"
    h_roi.cells[1].paragraphs[0].text = "Custom Dev"
    h_roi.cells[2].paragraphs[0].text = "ServiceNow"
    h_roi.cells[3].paragraphs[0].text = "Frappe AES"
    format_row(h_roi, "0D9488", "FFFFFF", is_header=True)
    
    rois = [
        ("Upfront Build Cost", "$150,000 - $300,000", "$50,000 setup fee", "$0 (Included)"),
        ("Annual Seats (500 users)", "$0 (Maintenance costs)", "$1,200,000 / year", "$0 Per-Seat Fees"),
        ("Time to Deployment", "6 to 9 Months", "3 to 6 Months", "Under 5 Minutes"),
        ("Technical Skill Needed", "Senior Engineers", "Certified Admins", "Anyone (Non-Technical)"),
        ("Data Ownership", "Variable", "Locked in Proprietary Cloud", "100% Owned by You")
    ]
    for r_idx, (m_name, m_dev, m_sn, m_aes) in enumerate(rois):
        row = roi_tbl.add_row()
        row.cells[0].paragraphs[0].text = m_name
        row.cells[1].paragraphs[0].text = m_dev
        row.cells[2].paragraphs[0].text = m_sn
        row.cells[3].paragraphs[0].text = m_aes
        bg = "F0FDFA" if r_idx % 2 == 0 else "FFFFFF"
        format_row(row, bg, "333333")
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    add_callout(
        doc,
        "Bottom Line: A 500-person enterprise switching to Frappe AES saves over $1,170,000 in software fees every year "
        "while accelerating application delivery from months to minutes.",
        title="BOTTOM LINE IMPACT",
        alert_type="success"
    )
    
    output_docx = DOCS_DIR / "FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.docx"
    doc.save(str(output_docx))
    print(f"[SUCCESS] Built Simple English Report Word document: {output_docx}")
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
            print(f"[SUCCESS] Simple English Report PDF generated: {pdf_path}")
            return pdf_path
        else:
            print(f"[WARNING] Word COM conversion output: {res.stdout} / {res.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to run Word COM conversion: {e}")
        return None

def main():
    docx_path = build_executive_report_doc()
    pdf_path = convert_docx_to_pdf(docx_path)
    
    downloads_dir = Path(r"C:\Users\srikrishna.rg_quanti\Downloads")
    if downloads_dir.exists():
        import shutil
        if docx_path.exists():
            shutil.copy2(str(docx_path), str(downloads_dir / docx_path.name))
            print(f"[SUCCESS] Copied Simple English DOCX to Downloads: {downloads_dir / docx_path.name}")
        if pdf_path and pdf_path.exists():
            shutil.copy2(str(pdf_path), str(downloads_dir / pdf_path.name))
            print(f"[SUCCESS] Copied Simple English PDF to Downloads: {downloads_dir / pdf_path.name}")

if __name__ == "__main__":
    main()
