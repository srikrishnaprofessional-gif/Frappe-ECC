"""
Frappe Local Runtime Web Server & Desk Simulator
Serves the complete Frappe Desk UI, REST APIs, and autonomous real-time agent studio on localhost.
Zero external dependencies required (runs natively with Python 3.9+).
"""

import sys
import os
import json
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from .live_engine import db, event_bus, AutonomousAppBuilder, SimulatedDataFactory
from .registry import registry

# Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# INITIALIZE DEFAULT APPS & SEED REALISTIC SIMULATED DATA
# ---------------------------------------------------------------------------
def initialize_default_apps():
    """Seeds the local runtime with default enterprise applications and realistic data."""
    # 1. Equipment Loan Management
    loan_dt = {
        "doctype": "Equipment Loan",
        "module": "Loan Management",
        "fields": [
            {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
            {"fieldname": "applicant_name", "fieldtype": "Data", "label": "Applicant Name", "reqd": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nUnder Review\nApproved\nRejected\nCompleted"},
            {"fieldname": "requested_amount", "fieldtype": "Currency", "label": "Loan Amount"},
            {"fieldname": "submission_date", "fieldtype": "Date", "label": "Loan Date"},
            {"fieldname": "department", "fieldtype": "Data", "label": "Department"},
            {"fieldname": "notes", "fieldtype": "Text Editor", "label": "Loan Terms & Purpose"}
        ]
    }
    db.register_app("loan_management", "Equipment Loan Management", "Automated equipment leasing, credit review, and asset return tracking")
    db.register_doctype(loan_dt, "loan_management")

    # Seed 25 realistic loan records if empty
    if db.count("Equipment Loan") == 0:
        records = SimulatedDataFactory.generate_records(loan_dt, count=25)
        for r in records:
            db.insert("Equipment Loan", r)

    # 2. Procurement Requisition Flow
    proc_dt = {
        "doctype": "Purchase Requisition",
        "module": "Procurement Flow",
        "fields": [
            {"fieldname": "title", "fieldtype": "Data", "label": "Requisition Title", "reqd": 1},
            {"fieldname": "applicant_name", "fieldtype": "Data", "label": "Requesting Officer", "reqd": 1},
            {"fieldname": "supplier_name", "fieldtype": "Data", "label": "Preferred Vendor"},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nUnder Review\nApproved\nRejected\nOrdered"},
            {"fieldname": "requested_amount", "fieldtype": "Currency", "label": "Budget Estimated"},
            {"fieldname": "department", "fieldtype": "Data", "label": "Cost Center"},
            {"fieldname": "notes", "fieldtype": "Text Editor", "label": "Procurement Justification"}
        ]
    }
    db.register_app("procurement_flow", "Enterprise Procurement Flow", "Three-way invoice matching and purchase order approval system")
    db.register_doctype(proc_dt, "procurement_flow")

    if db.count("Purchase Requisition") == 0:
        records = SimulatedDataFactory.generate_records(proc_dt, count=20)
        for r in records:
            db.insert("Purchase Requisition", r)


# ---------------------------------------------------------------------------
# EMBEDDED FRAPPE DESK HTML/CSS/JS APPLICATION
# ---------------------------------------------------------------------------
def get_desk_html() -> str:
    """Returns the complete Frappe Desk UI with real-time Autonomous Studio and dynamic views."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frappe Autonomous Enterprise Desk (Local Runtime)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --primary-light: #eff6ff;
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --bg-sidebar: #0f172a;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --border-dark: #334155;
            --green: #10b981;
            --orange: #f59e0b;
            --red: #ef4444;
            --purple: #8b5cf6;
            --radius: 8px;
            --radius-lg: 12px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.08);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-page); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

        /* Top Navbar */
        .navbar {
            background: #ffffff;
            border-bottom: 1px solid var(--border);
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 50;
        }
        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 16px;
            color: var(--primary);
            text-decoration: none;
        }
        .navbar-brand svg { width: 24px; height: 24px; fill: var(--primary); }
        .live-tag {
            background: #ecfdf5;
            color: #059669;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .live-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

        .nav-actions { display: flex; align-items: center; gap: 12px; }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 500;
            border-radius: var(--radius);
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
            text-decoration: none;
        }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-outline { background: white; border-color: var(--border); color: var(--text-main); }
        .btn-outline:hover { background: var(--bg-page); }
        .btn-stimulate { background: #fdf2f8; color: #db2777; border-color: #fbcfe8; }
        .btn-stimulate:hover { background: #fce7f3; }
        .btn-studio { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; }
        .btn-studio:hover { opacity: 0.95; }

        /* Main Layout */
        .app-container { display: flex; flex: 1; height: calc(100vh - 56px); overflow: hidden; }

        /* Sidebar */
        .sidebar {
            width: 240px;
            background: var(--bg-sidebar);
            color: #f1f5f9;
            display: flex;
            flex-direction: column;
            border-right: 1px solid var(--border-dark);
            flex-shrink: 0;
        }
        .sidebar-section { padding: 16px 14px 8px; font-size: 11px; font-weight: 600; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; }
        .sidebar-menu { list-style: none; padding: 0 8px; }
        .sidebar-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 12px;
            border-radius: var(--radius);
            color: #cbd5e1;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
            margin-bottom: 2px;
        }
        .sidebar-item:hover { background: rgba(255,255,255,0.06); color: white; }
        .sidebar-item.active { background: var(--primary); color: white; }
        .sidebar-item .badge { margin-left: auto; font-size: 11px; background: rgba(255,255,255,0.15); padding: 2px 7px; border-radius: 10px; }

        /* Main Content View */
        .content-area { flex: 1; overflow-y: auto; background: var(--bg-page); padding: 24px 32px; display: flex; flex-direction: column; }

        /* Breadcrumbs & View Header */
        .view-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .view-title { font-size: 20px; font-weight: 700; color: var(--text-main); }
        .view-subtitle { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

        /* Cards & Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 16px 20px;
            box-shadow: var(--shadow-sm);
        }
        .metric-label { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.04em; }
        .metric-value { font-size: 26px; font-weight: 700; color: var(--text-main); margin: 6px 0 4px; }
        .metric-sub { font-size: 12px; color: var(--green); font-weight: 500; }

        /* Charts Section */
        .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px; }
        .chart-box {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px;
            box-shadow: var(--shadow-sm);
        }
        .chart-title { font-size: 14px; font-weight: 600; margin-bottom: 15px; color: var(--text-main); display: flex; justify-content: space-between; }

        /* List View */
        .list-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }
        .list-toolbar {
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }
        .filter-group { display: flex; gap: 6px; }
        .filter-btn {
            background: var(--bg-page);
            border: 1px solid var(--border);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
        }
        .filter-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
        .search-box {
            position: relative;
            flex: 1;
            max-width: 320px;
        }
        .search-input {
            width: 100%;
            padding: 7px 12px 7px 32px;
            font-size: 13px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            outline: none;
        }
        .search-input:focus { border-color: var(--primary); }
        .search-icon { position: absolute; left: 10px; top: 9px; width: 14px; height: 14px; color: var(--text-muted); }

        .table-records { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
        .table-records th { background: #f8fafc; padding: 10px 18px; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); font-size: 12px; }
        .table-records td { padding: 12px 18px; border-bottom: 1px solid var(--border); vertical-align: middle; }
        .table-records tr:hover td { background: #f8fafc; cursor: pointer; }

        .status-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }
        .status-Draft { background: #f1f5f9; color: #475569; }
        .status-Under-Review { background: #fef3c7; color: #b45309; }
        .status-Approved { background: #ecfdf5; color: #047857; }
        .status-Rejected { background: #fee2e2; color: #b91c1c; }
        .status-Completed { background: #eff6ff; color: #1d4ed8; }

        /* Form Modal / Drawer */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.5);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }
        .modal-overlay.active { display: flex; }
        .modal-card {
            background: white;
            border-radius: var(--radius-lg);
            width: 720px;
            max-width: 90vw;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            padding: 18px 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .modal-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-group.full { grid-column: span 2; }
        .form-label { font-size: 12px; font-weight: 600; color: var(--text-main); }
        .form-input, .form-select, .form-textarea {
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 13px;
            font-family: inherit;
            outline: none;
        }
        .form-input:focus, .form-select:focus, .form-textarea:focus { border-color: var(--primary); }
        .modal-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            background: #f8fafc;
        }

        /* Autonomous Flight Deck Studio Panel */
        .studio-panel {
            display: none;
            flex-direction: column;
            gap: 20px;
        }
        .studio-panel.active { display: flex; }
        .prompt-hero {
            background: linear-gradient(135deg, #1e1b4b, #312e81);
            color: white;
            border-radius: var(--radius-lg);
            padding: 24px 28px;
            box-shadow: var(--shadow-md);
        }
        .prompt-hero h2 { font-size: 20px; margin-bottom: 6px; font-weight: 700; }
        .prompt-hero p { font-size: 13px; color: #cbd5e1; margin-bottom: 16px; }
        .prompt-input-row { display: flex; gap: 10px; }
        .prompt-field {
            flex: 1;
            padding: 12px 16px;
            border-radius: var(--radius);
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.08);
            color: white;
            font-size: 14px;
            outline: none;
        }
        .prompt-field::placeholder { color: #94a3b8; }
        .prompt-field:focus { border-color: #818cf8; background: rgba(255,255,255,0.12); }

        .presets-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
        .preset-chip {
            background: rgba(255,255,255,0.1);
            color: #e2e8f0;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .preset-chip:hover { background: rgba(255,255,255,0.2); color: white; }

        .flight-deck {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .console-box {
            background: #0f172a;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
            border-radius: var(--radius-lg);
            padding: 16px;
            height: 380px;
            overflow-y: auto;
            font-size: 12px;
            border: 1px solid var(--border-dark);
            display: flex;
            flex-direction: column;
        }
        .console-header { color: #94a3b8; font-size: 11px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; }
        .console-log { margin-bottom: 4px; line-height: 1.4; }
        .console-log .time { color: #64748b; margin-right: 6px; }
        .console-log.success { color: #4ade80; }
        .console-log.agent { color: #fbbf24; font-weight: 500; }

        .agent-roster-box {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 16px;
            height: 380px;
            overflow-y: auto;
        }
        .roster-header { font-size: 13px; font-weight: 700; color: var(--text-main); margin-bottom: 12px; display: flex; justify-content: space-between; }
        .agent-chip-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .agent-chip {
            padding: 8px 10px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 8px;
            background: #f8fafc;
        }
        .agent-chip.active { border-color: var(--primary); background: #eff6ff; }
        .agent-chip.done { border-color: #10b981; background: #ecfdf5; }
        .chip-dot { width: 7px; height: 7px; border-radius: 50%; background: #94a3b8; }
        .agent-chip.active .chip-dot { background: var(--primary); animation: pulse 1s infinite; }
        .agent-chip.done .chip-dot { background: #10b981; }

        /* Notification Toast */
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #0f172a;
            color: white;
            padding: 12px 20px;
            border-radius: var(--radius);
            font-size: 13px;
            display: none;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-lg);
            z-index: 200;
        }
        .toast.show { display: flex; animation: slideIn 0.2s ease; }
        @keyframes slideIn { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <nav class="navbar">
        <div style="display:flex; align-items:center; gap: 20px;">
            <a href="#" class="navbar-brand" onclick="switchView('desk')">
                <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                <span>Frappe Autonomous ECC</span>
            </a>
            <span class="live-tag"><span class="live-dot"></span> Live Local Machine Runtime :8050</span>
        </div>

        <div class="nav-actions">
            <button class="btn btn-stimulate" onclick="stimulateData()">
                ⚡ Stimulate 25 Records
            </button>
            <button class="btn btn-studio" onclick="switchView('studio')">
                🤖 Autonomous AI Studio
            </button>
            <button class="btn btn-primary" onclick="openNewRecordModal()">
                + New Record
            </button>
        </div>
    </nav>

    <!-- Main Application Container -->
    <div class="app-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="sidebar-section">Active Applications</div>
            <ul class="sidebar-menu" id="appsList">
                <!-- Dynamically populated -->
            </ul>

            <div class="sidebar-section" style="margin-top: 15px;">Doctypes & Views</div>
            <ul class="sidebar-menu" id="doctypesList">
                <!-- Dynamically populated -->
            </ul>

            <div class="sidebar-section" style="margin-top: auto; padding-bottom: 16px;">
                <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 11px;">
                    <div style="color: #94a3b8;">53 AI Agents Active</div>
                    <div style="color: #4ade80; margin-top: 4px; font-weight: 600;">Autonomous Engine Ready</div>
                </div>
            </div>
        </aside>

        <!-- Dynamic Content Body -->
        <main class="content-area">

            <!-- 1. FRAPPE DESK VIEW -->
            <div id="deskView">
                <div class="view-header">
                    <div>
                        <h1 class="view-title" id="currentAppTitle">Equipment Loan Management</h1>
                        <div class="view-subtitle" id="currentDocTypeSub">Managing active records in local stimulated runtime</div>
                    </div>
                </div>

                <!-- KPI Metric Cards -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Total Stimulated Records</div>
                        <div class="metric-value" id="kpiTotal">0</div>
                        <div class="metric-sub">↑ Real-time in memory</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Sanctioned Volume ($)</div>
                        <div class="metric-value" id="kpiVolume">$0</div>
                        <div class="metric-sub" style="color: var(--primary);">Approved pipeline</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Under Review</div>
                        <div class="metric-value" id="kpiReview">0</div>
                        <div class="metric-sub" style="color: var(--orange);">Requires action</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Approval Velocity</div>
                        <div class="metric-value" id="kpiRate">84%</div>
                        <div class="metric-sub">SLA &lt; 24h</div>
                    </div>
                </div>

                <!-- Interactive Records List Table -->
                <div class="list-container">
                    <div class="list-toolbar">
                        <div class="filter-group">
                            <button class="filter-btn active" onclick="setFilter('ALL', this)">All</button>
                            <button class="filter-btn" onclick="setFilter('Draft', this)">Draft</button>
                            <button class="filter-btn" onclick="setFilter('Under Review', this)">Under Review</button>
                            <button class="filter-btn" onclick="setFilter('Approved', this)">Approved</button>
                            <button class="filter-btn" onclick="setFilter('Rejected', this)">Rejected</button>
                        </div>
                        <div class="search-box">
                            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                            <input type="text" class="search-input" placeholder="Search applicant, ID, or title..." oninput="handleSearch(this.value)">
                        </div>
                    </div>

                    <table class="table-records">
                        <thead>
                            <tr>
                                <th style="width: 130px;">ID</th>
                                <th>Title / Purpose</th>
                                <th>Applicant</th>
                                <th style="width: 140px;">Amount</th>
                                <th style="width: 120px;">Creation Date</th>
                                <th style="width: 120px; text-align: center;">Status</th>
                                <th style="width: 140px; text-align: right;">Action</th>
                            </tr>
                        </thead>
                        <tbody id="recordsTbody">
                            <!-- Dynamically loaded rows -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 2. AUTONOMOUS AI FLIGHT DECK STUDIO -->
            <div id="studioView" class="studio-panel">
                <div class="prompt-hero">
                    <h2>🚀 Autonomous AI App Builder</h2>
                    <p>Enter any business application requirement. The 53 Frappe AI agents will collaborate autonomously, synthesize DocTypes, schemas, controllers, workflows, and launch the application locally with simulated data in real time.</p>
                    <div class="prompt-input-row">
                        <input type="text" id="aiPromptInput" class="prompt-field" placeholder="e.g. Build a Healthcare Clinic & Patient EHR with appointment booking, diagnosis records, and billing...">
                        <button class="btn btn-primary" style="padding: 0 24px; font-weight: 600;" onclick="triggerAutonomousBuild()">
                            ⚡ Launch AI Agents
                        </button>
                    </div>
                    <div class="presets-row">
                        <span style="font-size: 11px; color: #94a3b8; align-self: center;">Quick Presets:</span>
                        <div class="preset-chip" onclick="usePreset('Build a Healthcare Clinic and Patient Prescription System with diagnosis records and billing')">🏥 Clinic EHR System</div>
                        <div class="preset-chip" onclick="usePreset('Build a Fleet Logistics & Vehicle Maintenance Tracker with trip logs, fuel consumption, and service alerts')">🚚 Fleet Management</div>
                        <div class="preset-chip" onclick="usePreset('Build a Real Estate Commercial Property Leasing and Tenant Rent Tracking portal')">🏢 Real Estate Leasing</div>
                        <div class="preset-chip" onclick="usePreset('Build a Construction Equipment and Heavy Machinery Loan Tracker with return inspections')">🏗️ Equipment Loans</div>
                        <div class="preset-chip" onclick="usePreset('Build a Corporate Travel Requisition and Expense Claim Reimbursement system')">✈️ Travel & Expenses</div>
                    </div>
                </div>

                <div class="flight-deck">
                    <div class="console-box" id="consoleBox">
                        <div class="console-header">
                            <span>AUTONOMOUS AGENT REAL-TIME EXECUTION STREAM</span>
                            <span id="agentStatusBadge">IDLE</span>
                        </div>
                        <div id="consoleLogs">
                            <div class="console-log"><span class="time">[INIT]</span> Autonomous Runtime daemon listening on Port 8050.</div>
                            <div class="console-log"><span class="time">[INIT]</span> Ready for natural language application prompts.</div>
                        </div>
                    </div>

                    <div class="agent-roster-box">
                        <div class="roster-header">
                            <span>ACTIVE AGENT COLLABORATION ROSTER</span>
                            <span style="font-size: 11px; color: var(--primary);">53 AI Specialists</span>
                        </div>
                        <div class="agent-chip-grid" id="agentRosterGrid">
                            <!-- Populated with key agents -->
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <!-- Record Detail / Edit Modal -->
    <div class="modal-overlay" id="recordModal">
        <div class="modal-card">
            <div class="modal-header">
                <div>
                    <h3 style="font-size: 16px; font-weight: 700;" id="modalTitle">Record Details</h3>
                    <span id="modalDocname" style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;"></span>
                </div>
                <button class="btn btn-outline" style="padding: 4px 8px;" onclick="closeModal()">✕</button>
            </div>
            <div class="modal-body" id="modalFormFields">
                <!-- Dynamically populated from DocType schema -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
                <button class="btn btn-outline" style="color: var(--red); border-color: #fca5a5;" id="btnReject" onclick="updateRecordStatus('Rejected')">Reject</button>
                <button class="btn btn-primary" style="background: var(--green);" id="btnApprove" onclick="updateRecordStatus('Approved')">Quick Approve</button>
                <button class="btn btn-primary" onclick="saveRecord()">Save Record</button>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div class="toast" id="toastMessage">Record updated successfully</div>

    <script>
        let currentApp = "loan_management";
        let currentDocType = "Equipment Loan";
        let allRecords = [];
        let activeFilter = "ALL";
        let activeDocname = null;

        const KEY_AGENTS = [
            "frappe-autonomous-orchestrator",
            "frappe-prompt-to-app-builder",
            "frappe-product-manager",
            "frappe-hld-architect",
            "frappe-lld-designer",
            "frappe-fullstack-developer",
            "frappe-desk-builder",
            "frappe-backend-builder",
            "frappe-bpmn-visual-workflow-builder",
            "frappe-notification-omnichannel-agent",
            "frappe-bi-dashboard-synthesizer",
            "frappe-data-synthesizer",
            "frappe-tdd-guide",
            "frappe-working-sop-author",
            "frappe-custom-app-git-builder",
            "frappe-security-reviewer"
        ];

        // Initialize application on load
        window.addEventListener("DOMContentLoaded", () => {
            renderAgentRoster();
            loadApps();
            loadDoctypes();
            loadRecords();
            startEventPolling();
        });

        function switchView(view) {
            document.getElementById("deskView").style.display = view === 'desk' ? 'block' : 'none';
            document.getElementById("studioView").className = view === 'studio' ? 'studio-panel active' : 'studio-panel';
        }

        function renderAgentRoster() {
            const grid = document.getElementById("agentRosterGrid");
            grid.innerHTML = KEY_AGENTS.map(name => `
                <div class="agent-chip" id="chip-${name}">
                    <span class="chip-dot"></span>
                    <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${name.replace('frappe-', '')}</span>
                </div>
            `).join("");
        }

        async function loadApps() {
            try {
                const res = await fetch("/api/apps");
                const apps = await res.json();
                const listEl = document.getElementById("appsList");
                listEl.innerHTML = apps.map(app => `
                    <li class="sidebar-item ${app.name === currentApp ? 'active' : ''}" onclick="selectApp('${app.name}', '${app.title}')">
                        <span>📦</span>
                        <span>${app.title}</span>
                    </li>
                `).join("");
            } catch (e) {
                console.error("Error loading apps", e);
            }
        }

        async function loadDoctypes() {
            try {
                const res = await fetch(`/api/doctypes?app=${currentApp}`);
                const dts = await res.json();
                const listEl = document.getElementById("doctypesList");
                listEl.innerHTML = dts.map(dt => `
                    <li class="sidebar-item ${dt.name === currentDocType ? 'active' : ''}" onclick="selectDocType('${dt.name}')">
                        <span>📄</span>
                        <span>${dt.name}</span>
                        <span class="badge" id="badge-${dt.name.replace(/\\s/g, '_')}">0</span>
                    </li>
                `).join("");
            } catch (e) {
                console.error("Error loading doctypes", e);
            }
        }

        function selectApp(appName, appTitle) {
            currentApp = appName;
            document.getElementById("currentAppTitle").innerText = appTitle;
            loadApps();
            loadDoctypes();
            switchView('desk');
        }

        function selectDocType(dtName) {
            currentDocType = dtName;
            document.getElementById("currentDocTypeSub").innerText = `Managing ${dtName} stimulated records`;
            loadDoctypes();
            loadRecords();
            switchView('desk');
        }

        async function loadRecords() {
            try {
                const res = await fetch(`/api/resource/${encodeURIComponent(currentDocType)}`);
                allRecords = await res.json();
                renderRecords();
                updateKPIs();
            } catch (e) {
                console.error("Error loading records", e);
            }
        }

        function renderRecords() {
            const tbody = document.getElementById("recordsTbody");
            let filtered = allRecords;

            if (activeFilter !== "ALL") {
                filtered = filtered.filter(r => (r.status || "Draft").toLowerCase() === activeFilter.toLowerCase());
            }

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 30px; color:#94a3b8;">No records found. Click "+ New Record" or "⚡ Stimulate 25 Records".</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => {
                const amt = r.requested_amount ? "$" + parseFloat(r.requested_amount).toLocaleString(undefined, {minimumFractionDigits: 2}) : "-";
                const statusCls = `status-${(r.status || 'Draft').replace(/\\s+/g, '-')}`;
                return `
                    <tr onclick="openRecordModal('${r.name}')">
                        <td style="font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--primary);">${r.name}</td>
                        <td style="font-weight:600;">${r.title || r.name}</td>
                        <td>${r.applicant_name || '-'}</td>
                        <td style="font-weight:600;">${amt}</td>
                        <td style="color:#64748b;">${r.creation_date || (r.creation ? r.creation.split(' ')[0] : '-')}</td>
                        <td style="text-align:center;"><span class="status-badge ${statusCls}">${r.status || 'Draft'}</span></td>
                        <td style="text-align:right;">
                            <button class="btn btn-outline" style="padding: 4px 8px; font-size:11px;" onclick="event.stopPropagation(); quickApprove('${r.name}')">Approve</button>
                        </td>
                    </tr>
                `;
            }).join("");

            // Update badge
            const b = document.getElementById(`badge-${currentDocType.replace(/\\s/g, '_')}`);
            if (b) b.innerText = allRecords.length;
        }

        function updateKPIs() {
            document.getElementById("kpiTotal").innerText = allRecords.length;
            const totalVol = allRecords.reduce((acc, r) => acc + (parseFloat(r.requested_amount) || 0), 0);
            document.getElementById("kpiVolume").innerText = "$" + totalVol.toLocaleString(undefined, {maximumFractionDigits: 0});
            const reviewCount = allRecords.filter(r => (r.status || '').toLowerCase() === 'under review').length;
            document.getElementById("kpiReview").innerText = reviewCount;
        }

        function setFilter(status, btn) {
            activeFilter = status;
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            renderRecords();
        }

        function handleSearch(term) {
            term = term.toLowerCase();
            const filtered = allRecords.filter(r => {
                return (r.name && r.name.toLowerCase().includes(term)) ||
                       (r.title && r.title.toLowerCase().includes(term)) ||
                       (r.applicant_name && r.applicant_name.toLowerCase().includes(term));
            });
            const tbody = document.getElementById("recordsTbody");
            tbody.innerHTML = filtered.map(r => {
                const amt = r.requested_amount ? "$" + parseFloat(r.requested_amount).toLocaleString(undefined, {minimumFractionDigits: 2}) : "-";
                const statusCls = `status-${(r.status || 'Draft').replace(/\\s+/g, '-')}`;
                return `
                    <tr onclick="openRecordModal('${r.name}')">
                        <td style="font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--primary);">${r.name}</td>
                        <td style="font-weight:600;">${r.title || r.name}</td>
                        <td>${r.applicant_name || '-'}</td>
                        <td style="font-weight:600;">${amt}</td>
                        <td style="color:#64748b;">${r.creation_date || (r.creation ? r.creation.split(' ')[0] : '-')}</td>
                        <td style="text-align:center;"><span class="status-badge ${statusCls}">${r.status || 'Draft'}</span></td>
                        <td style="text-align:right;">
                            <button class="btn btn-outline" style="padding: 4px 8px; font-size:11px;" onclick="event.stopPropagation(); quickApprove('${r.name}')">Approve</button>
                        </td>
                    </tr>
                `;
            }).join("");
        }

        async function stimulateData() {
            showToast("Synthesizing 25 realistic simulated records...");
            try {
                const res = await fetch("/api/data/synthesize", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({doctype: currentDocType, count: 25})
                });
                const data = await res.json();
                showToast(`Generated ${data.seeded_count} simulated records with realistic data!`);
                loadRecords();
            } catch (e) {
                console.error("Error stimulating data", e);
            }
        }

        async function quickApprove(name) {
            try {
                await fetch(`/api/resource/${encodeURIComponent(currentDocType)}/${encodeURIComponent(name)}`, {
                    method: "PUT",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({status: "Approved"})
                });
                showToast(`Record ${name} Approved!`);
                loadRecords();
            } catch (e) {
                console.error(e);
            }
        }

        function openRecordModal(name) {
            const rec = allRecords.find(r => r.name === name);
            if (!rec) return;
            activeDocname = name;
            document.getElementById("modalTitle").innerText = rec.title || "Record Details";
            document.getElementById("modalDocname").innerText = `${currentDocType}: ${name}`;

            const fieldsDiv = document.getElementById("modalFormFields");
            fieldsDiv.innerHTML = `
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Title / Requisition Name</label>
                        <input type="text" id="modal_f_title" class="form-input" value="${rec.title || ''}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Applicant / Requesting Party</label>
                        <input type="text" id="modal_f_applicant" class="form-input" value="${rec.applicant_name || ''}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Workflow Status</label>
                        <select id="modal_f_status" class="form-select">
                            <option value="Draft" ${rec.status === 'Draft' ? 'selected' : ''}>Draft</option>
                            <option value="Under Review" ${rec.status === 'Under Review' ? 'selected' : ''}>Under Review</option>
                            <option value="Approved" ${rec.status === 'Approved' ? 'selected' : ''}>Approved</option>
                            <option value="Rejected" ${rec.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                            <option value="Completed" ${rec.status === 'Completed' ? 'selected' : ''}>Completed</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Amount ($)</label>
                        <input type="number" id="modal_f_amount" class="form-input" value="${rec.requested_amount || 0}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Submission Date</label>
                        <input type="date" id="modal_f_date" class="form-input" value="${rec.creation_date || (rec.creation ? rec.creation.split(' ')[0] : '')}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Operational Notes & Justification</label>
                        <textarea id="modal_f_notes" class="form-textarea" rows="3">${rec.notes || ''}</textarea>
                    </div>
                </div>
            `;
            document.getElementById("recordModal").classList.add("active");
        }

        function openNewRecordModal() {
            activeDocname = null;
            document.getElementById("modalTitle").innerText = `New ${currentDocType} Record`;
            document.getElementById("modalDocname").innerText = "Will be assigned autoname upon creation";

            const fieldsDiv = document.getElementById("modalFormFields");
            fieldsDiv.innerHTML = `
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Title / Requisition Name</label>
                        <input type="text" id="modal_f_title" class="form-input" placeholder="e.g. Q4 Server Hardware Requisition">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Applicant / Requesting Party</label>
                        <input type="text" id="modal_f_applicant" class="form-input" placeholder="e.g. Jane Doe">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Workflow Status</label>
                        <select id="modal_f_status" class="form-select">
                            <option value="Draft" selected>Draft</option>
                            <option value="Under Review">Under Review</option>
                            <option value="Approved">Approved</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Amount ($)</label>
                        <input type="number" id="modal_f_amount" class="form-input" value="10000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Submission Date</label>
                        <input type="date" id="modal_f_date" class="form-input" value="${new Date().toISOString().split('T')[0]}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Operational Notes & Justification</label>
                        <textarea id="modal_f_notes" class="form-textarea" rows="3" placeholder="Enter business justification..."></textarea>
                    </div>
                </div>
            `;
            document.getElementById("recordModal").classList.add("active");
        }

        async function saveRecord() {
            const payload = {
                title: document.getElementById("modal_f_title").value,
                applicant_name: document.getElementById("modal_f_applicant").value,
                status: document.getElementById("modal_f_status").value,
                requested_amount: parseFloat(document.getElementById("modal_f_amount").value) || 0,
                creation_date: document.getElementById("modal_f_date").value,
                notes: document.getElementById("modal_f_notes").value
            };

            try {
                if (activeDocname) {
                    await fetch(`/api/resource/${encodeURIComponent(currentDocType)}/${encodeURIComponent(activeDocname)}`, {
                        method: "PUT",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(payload)
                    });
                    showToast(`Record ${activeDocname} updated!`);
                } else {
                    const res = await fetch(`/api/resource/${encodeURIComponent(currentDocType)}`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(payload)
                    });
                    const created = await res.json();
                    showToast(`Record ${created.name} created!`);
                }
                closeModal();
                loadRecords();
            } catch (e) {
                console.error(e);
            }
        }

        async function updateRecordStatus(newStatus) {
            if (!activeDocname) return;
            try {
                await fetch(`/api/resource/${encodeURIComponent(currentDocType)}/${encodeURIComponent(activeDocname)}`, {
                    method: "PUT",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({status: newStatus})
                });
                showToast(`Record marked as ${newStatus}!`);
                closeModal();
                loadRecords();
            } catch (e) {
                console.error(e);
            }
        }

        function closeModal() {
            document.getElementById("recordModal").classList.remove("active");
        }

        function showToast(msg) {
            const toast = document.getElementById("toastMessage");
            toast.innerText = msg;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 3500);
        }

        function usePreset(prompt) {
            document.getElementById("aiPromptInput").value = prompt;
        }

        async function triggerAutonomousBuild() {
            const promptText = document.getElementById("aiPromptInput").value.trim();
            if (!promptText) {
                alert("Please enter a business application description.");
                return;
            }

            document.getElementById("agentStatusBadge").innerText = "AUTONOMOUS AGENTS ACTIVE";
            document.getElementById("agentStatusBadge").style.color = "#4ade80";

            logToConsole("USER", `Autonomous Prompt Submitted: "${promptText}"`);
            logToConsole("ORCHESTRATOR", "Awakening Autonomous Multi-Agent DAG Pipeline...");

            // Reset agent chips
            document.querySelectorAll(".agent-chip").forEach(c => {
                c.classList.remove("active", "done");
            });

            try {
                const res = await fetch("/api/autonomous/build", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({prompt: promptText})
                });
                const data = await res.json();

                logToConsole("SUCCESS", `Application '${data.app_title}' (${data.app_slug}) synthesized in ${data.execution_time_sec}s!`);
                logToConsole("DATA", `Seeded ${data.simulated_records_seeded} realistic enterprise records.`);

                showToast(`Application '${data.app_title}' built and deployed locally!`);
                document.getElementById("agentStatusBadge").innerText = "IDLE";
                document.getElementById("agentStatusBadge").style.color = "#94a3b8";

                // Refresh sidebar & switch to the newly created application
                await loadApps();
                selectApp(data.app_slug, data.app_title);

            } catch (e) {
                logToConsole("ERROR", "Failed to build: " + e.message);
                document.getElementById("agentStatusBadge").innerText = "ERROR";
            }
        }

        function logToConsole(tag, msg, isSuccess = false) {
            const c = document.getElementById("consoleLogs");
            const time = new Date().toLocaleTimeString();
            const logEl = document.createElement("div");
            logEl.className = "console-log" + (isSuccess ? " success" : "");
            logEl.innerHTML = `<span class="time">[${time}]</span> <span style="font-weight:600;">[${tag}]</span> ${msg}`;
            c.appendChild(logEl);
            document.getElementById("consoleBox").scrollTop = document.getElementById("consoleBox").scrollHeight;
        }

        function startEventPolling() {
            setInterval(async () => {
                try {
                    const res = await fetch("/api/events");
                    const events = await res.json();
                    if (!events || events.length === 0) return;

                    events.forEach(ev => {
                        const d = ev.data;
                        if (ev.event_type === "AGENT_STARTING") {
                            logToConsole("AGENT", `[${d.step}/${d.total_steps}] ${d.agent} running...`);
                            const chip = document.getElementById(`chip-${d.agent}`);
                            if (chip) {
                                chip.classList.add("active");
                            }
                        } else if (ev.event_type === "AGENT_COMPLETED") {
                            const chip = document.getElementById(`chip-${d.agent}`);
                            if (chip) {
                                chip.classList.remove("active");
                                chip.classList.add("done");
                            }
                        } else if (ev.event_type === "SIMULATION_STARTING") {
                            logToConsole("SIMULATOR", d.message);
                        }
                    });
                } catch (e) {}
            }, 1000);
        }
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTTP REQUEST HANDLER
# ---------------------------------------------------------------------------
class FrappeLocalRuntimeHandler(BaseHTTPRequestHandler):
    """Handles REST APIs, Desk assets, and Autonomous Builder endpoints."""

    def log_message(self, format, *args):
        # Mute standard noisy HTTP log lines for clean console
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Root / Desk Web App
        if path in ["/", "/app", "/desk", "/index.html"]:
            html = get_desk_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        # 2. API: Get Apps
        if path == "/api/apps":
            apps = db.get_apps()
            self._send_json(apps)
            return

        # 3. API: Get DocTypes
        if path == "/api/doctypes":
            app_filter = query.get("app", [None])[0]
            dts = db.get_doctypes(app_filter)
            self._send_json(dts)
            return

        # 4. API: Query Resources / Records: GET /api/resource/{doctype}
        if path.startswith("/api/resource/"):
            parts = [urllib.parse.unquote(p) for p in path.split("/")[3:] if p]
            if len(parts) == 1:
                doctype = parts[0]
                status_filter = query.get("status", [None])[0]
                search = query.get("search", [None])[0]
                records = db.get_list(doctype, status_filter, search)
                self._send_json(records)
                return
            elif len(parts) >= 2:
                doctype, name = parts[0], parts[1]
                doc = db.get_doc(doctype, name)
                if doc:
                    self._send_json(doc)
                else:
                    self._send_error(404, f"Document '{name}' not found")
                return

        # 5. API: Event Stream Polling
        if path == "/api/events":
            events = event_bus.get_recent(limit=25)
            self._send_json(events)
            return

        self._send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Autonomous Builder API
        if path == "/api/autonomous/build":
            prompt = payload.get("prompt", "Enterprise Application")
            app_slug = payload.get("app_slug")
            app_title = payload.get("app_title")

            def run_async():
                AutonomousAppBuilder.build_from_prompt(prompt, app_slug, app_title)

            # Run in worker thread
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()

            # Execute synchronous first phase to immediately return details
            result = AutonomousAppBuilder.build_from_prompt(prompt, app_slug, app_title)
            self._send_json(result)
            return

        # 2. Stimulate Data API
        if path == "/api/data/synthesize":
            doctype_name = payload.get("doctype", "Equipment Loan")
            count = int(payload.get("count", 25))

            # Retrieve doctype schema
            dts = [d for d in db.get_doctypes() if d["name"] == doctype_name]
            schema = dts[0]["schema"] if dts else {"doctype": doctype_name, "fields": []}

            records = SimulatedDataFactory.generate_records(schema, count=count)
            for r in records:
                db.insert(doctype_name, r)

            self._send_json({"status": "success", "seeded_count": len(records), "doctype": doctype_name})
            return

        # 3. Create Record API: POST /api/resource/{doctype}
        if path.startswith("/api/resource/"):
            parts = [urllib.parse.unquote(p) for p in path.split("/")[3:] if p]
            if len(parts) == 1:
                doctype = parts[0]
                created = db.insert(doctype, payload)
                self._send_json(created, status_code=201)
                return

        self._send_error(404, "Endpoint not found")

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # Update Record API: PUT /api/resource/{doctype}/{name}
        if path.startswith("/api/resource/"):
            parts = [urllib.parse.unquote(p) for p in path.split("/")[3:] if p]
            if len(parts) >= 2:
                doctype, name = parts[0], parts[1]
                updated = db.update_doc(doctype, name, payload)
                if updated:
                    self._send_json(updated)
                else:
                    self._send_error(404, f"Document '{name}' not found")
                return

        self._send_error(404, "Endpoint not found")

    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code, message):
        body = json.dumps({"error": message, "code": code}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# LOCAL RUNTIME SERVER LIFECYCLE
# ---------------------------------------------------------------------------
def run_server(port: int = 8050, open_browser: bool = True):
    """Starts the Frappe Local Runtime Server on localhost."""
    initialize_default_apps()

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, FrappeLocalRuntimeHandler)

    print("\n" + "=" * 80)
    print("🚀 FRAPPE AUTONOMOUS LOCAL RUNTIME & DESK SIMULATOR ACTIVE")
    print(f"URL: http://localhost:{port}")
    print(f"Active Port: {port} | Database: In-Memory SQLite (Frappe Schema Compliant)")
    print("Pre-seeded Applications: Equipment Loan Management, Enterprise Procurement")
    print("Autonomous AI Studio: Integrated with all 53 Frappe AI Agents")
    print("=" * 80 + "\n")

    if open_browser:
        # Launch browser in a background thread
        def launch():
            time.sleep(1.0)
            url = f"http://localhost:{port}"
            # Prefer Chrome or Edge in application mode
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            if os.path.exists(edge_path):
                import subprocess
                subprocess.Popen([edge_path, f"--app={url}"])
            elif os.path.exists(chrome_path):
                import subprocess
                subprocess.Popen([chrome_path, f"--app={url}"])
            else:
                import webbrowser
                webbrowser.open(url)

        t = threading.Thread(target=launch, daemon=True)
        t.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping Frappe Local Runtime Server...")
        httpd.server_close()


if __name__ == "__main__":
    port_arg = 8050
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])
    run_server(port=port_arg, open_browser=False)
