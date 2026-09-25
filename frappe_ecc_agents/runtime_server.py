"""
Frappe Local Runtime Web Server & Desk Simulator
Starts in pure Prompt Studio mode with zero pre-seeded apps.
When prompt is provided, 53 autonomous agents build the full application from scratch in real time
with domain-tailored stimulated data.
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


def get_desk_html() -> str:
    """Returns the pure prompt interface and real-time Frappe Desk application."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frappe Autonomous Enterprise Studio</title>
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
            height: 58px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
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
            cursor: pointer;
        }
        .navbar-brand svg { width: 24px; height: 24px; fill: var(--primary); }
        .live-tag {
            background: #ecfdf5;
            color: #059669;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .live-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
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

        /* Main Container */
        .app-container { display: flex; flex: 1; height: calc(100vh - 58px); overflow: hidden; position: relative; }

        /* Sidebar (shown once app is built) */
        .sidebar {
            width: 240px;
            background: var(--bg-sidebar);
            color: #f1f5f9;
            display: flex;
            flex-direction: column;
            border-right: 1px solid var(--border-dark);
            flex-shrink: 0;
            transition: transform 0.2s ease;
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

        /* Main Area */
        .content-area { flex: 1; overflow-y: auto; background: var(--bg-page); padding: 28px 36px; display: flex; flex-direction: column; }

        /* -------------------------------------------------------------
           PURE PROMPT STUDIO VIEW (Default Starting State)
           ------------------------------------------------------------- */
        .prompt-view-container {
            max-width: 920px;
            margin: 20px auto 40px;
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        .hero-banner {
            text-align: center;
            padding: 24px 10px 10px;
        }
        .hero-title {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #0f172a;
            margin-bottom: 10px;
        }
        .hero-subtitle {
            font-size: 15px;
            color: #64748b;
            max-width: 680px;
            margin: 0 auto;
            line-height: 1.6;
        }
        .prompt-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            padding: 24px 28px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .prompt-textarea {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px 18px;
            font-family: inherit;
            font-size: 15px;
            color: var(--text-main);
            outline: none;
            resize: vertical;
            min-height: 110px;
            line-height: 1.5;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .prompt-textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }
        .prompt-controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-muted);
        }
        .select-sim {
            padding: 6px 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 12px;
            font-weight: 500;
            background: white;
            outline: none;
        }
        .btn-build-main {
            padding: 12px 28px;
            font-size: 14px;
            font-weight: 600;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25);
        }
        .btn-build-main:hover {
            box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.35);
            transform: translateY(-1px);
        }

        .presets-title { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px; }
        .preset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 10px; }
        .preset-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .preset-card:hover {
            border-color: var(--primary);
            background: var(--primary-light);
            transform: translateY(-1px);
        }
        .preset-header { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 13px; color: var(--text-main); }
        .preset-desc { font-size: 11.5px; color: var(--text-muted); line-height: 1.4; }

        /* Real-Time Flight Deck Animation (When building) */
        .flight-deck-modal {
            display: none;
            background: #0f172a;
            color: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: var(--shadow-lg);
            flex-direction: column;
            gap: 16px;
            margin-top: 10px;
        }
        .flight-deck-modal.active { display: flex; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: #1e293b;
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            transition: width 0.3s ease;
        }
        .console-stream {
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 14px;
            height: 180px;
            overflow-y: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            color: #38bdf8;
            line-height: 1.5;
        }
        .agent-pills { display: flex; flex-wrap: wrap; gap: 6px; }
        .agent-pill {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 10.5px;
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
        }
        .agent-pill.active { background: #2563eb; color: white; border-color: #60a5fa; }
        .agent-pill.done { background: #064e3b; color: #34d399; border-color: #059669; }

        /* -------------------------------------------------------------
           DESK VIEW (Active after app is built)
           ------------------------------------------------------------- */
        .desk-view { display: none; flex-direction: column; }
        .desk-view.active { display: flex; }

        .view-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }
        .view-title { font-size: 22px; font-weight: 700; color: var(--text-main); }
        .view-subtitle { font-size: 13px; color: var(--text-muted); margin-top: 3px; }

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
            padding: 18px 20px;
            box-shadow: var(--shadow-sm);
        }
        .metric-label { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.04em; }
        .metric-value { font-size: 26px; font-weight: 700; color: var(--text-main); margin: 6px 0 4px; }
        .metric-sub { font-size: 12px; color: var(--green); font-weight: 500; }

        /* Table & Lists */
        .list-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }
        .list-toolbar {
            padding: 14px 20px;
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
        .table-records th { background: #f8fafc; padding: 12px 20px; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); font-size: 12px; }
        .table-records td { padding: 12px 20px; border-bottom: 1px solid var(--border); vertical-align: middle; }
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

        /* Modal */
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

        /* SOP Markdown Viewer */
        .sop-viewer { font-size: 13px; line-height: 1.6; color: #334155; }
        .sop-viewer h1, .sop-viewer h2, .sop-viewer h3 { color: #0f172a; margin: 16px 0 8px; }
        .sop-viewer p { margin-bottom: 10px; }
        .sop-viewer ul, .sop-viewer ol { padding-left: 20px; margin-bottom: 10px; }

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
        <div style="display:flex; align-items:center; gap: 16px;">
            <a class="navbar-brand" onclick="openPromptStudio()">
                <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                <span>Frappe Autonomous ECC</span>
            </a>
            <span class="live-tag"><span class="live-dot"></span> Port 8050 Active</span>
        </div>

        <div class="nav-actions" id="topNavActions">
            <button class="btn btn-studio" onclick="openPromptStudio()">
                ⚡ Build Another App
            </button>
            <button class="btn btn-outline" id="btnViewSop" style="display:none;" onclick="openSopModal()">
                📘 Working SOP
            </button>
            <button class="btn btn-stimulate" id="btnStimulate" style="display:none;" onclick="stimulateData()">
                ⚡ Stimulate 25 Records
            </button>
            <button class="btn btn-primary" id="btnNewRecord" style="display:none;" onclick="openNewRecordModal()">
                + New Record
            </button>
        </div>
    </nav>

    <!-- Main Workspace Area -->
    <div class="app-container">

        <!-- Sidebar (Visible only when an app exists and in desk mode) -->
        <aside class="sidebar" id="appSidebar" style="display:none;">
            <div class="sidebar-section">Active Applications</div>
            <ul class="sidebar-menu" id="appsList">
                <!-- Dynamically loaded -->
            </ul>

            <div class="sidebar-section" style="margin-top: 15px;">DocTypes & Modules</div>
            <ul class="sidebar-menu" id="doctypesList">
                <!-- Dynamically loaded -->
            </ul>

            <div class="sidebar-section" style="margin-top: auto; padding-bottom: 16px;">
                <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 11px;">
                    <div style="color: #94a3b8;">53 Autonomous AI Agents</div>
                    <div style="color: #4ade80; margin-top: 3px; font-weight: 600;">Dual Engine Ready</div>
                </div>
            </div>
        </aside>

        <main class="content-area">

            <!-- 1. PURE PROMPT STUDIO VIEW (Default Starting State) -->
            <div id="promptView" class="prompt-view-container">
                <div class="hero-banner">
                    <h1 class="hero-title">Autonomous Frappe Enterprise Builder</h1>
                    <p class="hero-subtitle">Enter any enterprise business application requirement. 53 autonomous AI agents will design the architecture, generate DocTypes, write Python controllers, create workflows, synthesize realistic stimulated data, and launch your application locally from scratch.</p>
                </div>

                <div class="prompt-card">
                    <label style="font-size: 13px; font-weight: 700; color: #1e293b;">Application Requirement Prompt</label>
                    <textarea id="mainPromptText" class="prompt-textarea" placeholder="e.g. Build an autonomous Healthcare Clinic & Patient EHR system with appointment bookings, physician diagnoses, prescription notes, and billing..."></textarea>
                    
                    <div class="prompt-controls">
                        <div class="control-group">
                            <span>Stimulate Data:</span>
                            <select id="simCountSelect" class="select-sim">
                                <option value="25" selected>25 Realistic Records</option>
                                <option value="50">50 Realistic Records</option>
                                <option value="100">100 Realistic Records</option>
                            </select>
                        </div>
                        <button class="btn btn-build-main" onclick="startAutonomousBuildFromScratch()">
                            ⚡ Build Application From Scratch
                        </button>
                    </div>

                    <!-- Real-Time Flight Deck Animation Card (Illuminates when building) -->
                    <div id="flightDeckBox" class="flight-deck-modal">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight:700; font-size:13px; color:#38bdf8;">AUTONOMOUS AGENT PIPELINE RUNNING</div>
                            <div id="pipelineStatusText" style="font-size:11px; color:#94a3b8;">Synthesizing full application...</div>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="progressFill"></div>
                        </div>
                        <div class="console-stream" id="consoleLogs">
                            <div>[INIT] Awakening 53 Autonomous Frappe AI Agents...</div>
                        </div>
                        <div class="agent-pills" id="activeAgentPills">
                            <!-- Populated with key agents -->
                        </div>
                    </div>
                </div>

                <!-- Quick Presets -->
                <div>
                    <div class="presets-title">Or Choose an Enterprise Domain to Build From Scratch:</div>
                    <div class="preset-grid">
                        <div class="preset-card" onclick="usePreset('Build an autonomous Healthcare Clinic and Patient Prescription EHR with appointment scheduling, physician notes, and consultation billing')">
                            <div class="preset-header"><span>🏥</span> Healthcare Clinic & Patient EHR</div>
                            <div class="preset-desc">Appointments, patient medical history, physician diagnosis, prescriptions, and invoice billing.</div>
                        </div>
                        <div class="preset-card" onclick="usePreset('Build an autonomous Fleet Logistics & Vehicle Telematics Tracker with trip logs, fuel consumption, driver records, and maintenance scheduling')">
                            <div class="preset-header"><span>🚚</span> Fleet Logistics & Telematics</div>
                            <div class="preset-desc">Vehicle assets, route trip logs, cargo weight, driver assignments, fuel costs, and service alerts.</div>
                        </div>
                        <div class="preset-card" onclick="usePreset('Build an autonomous Real Estate Property Leasing & Tenant Rent Management portal with lease agreements and payments')">
                            <div class="preset-header"><span>🏢</span> Real Estate Leasing & Tenants</div>
                            <div class="preset-desc">Commercial property units, tenant profiles, lease covenants, monthly rent schedules, and deposits.</div>
                        </div>
                        <div class="preset-card" onclick="usePreset('Build an autonomous Equipment Loan & Heavy Machinery Requisition system with return inspections and asset values')">
                            <div class="preset-header"><span>🏗️</span> Heavy Machinery Loan Tracker</div>
                            <div class="preset-desc">Asset requisitions, department loan approvals, return dates, inspection notes, and valuation.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. DESK VIEW (Activated after app is built) -->
            <div id="deskView" class="desk-view">
                <div class="view-header">
                    <div>
                        <h1 class="view-title" id="currentAppTitle">Application Dashboard</h1>
                        <div class="view-subtitle" id="currentDocTypeSub">Managing active records in local stimulated runtime</div>
                    </div>
                </div>

                <!-- Metric Number Cards -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Stimulated Records</div>
                        <div class="metric-value" id="kpiTotal">0</div>
                        <div class="metric-sub">↑ Real-time in memory</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Volume ($)</div>
                        <div class="metric-value" id="kpiVolume">$0</div>
                        <div class="metric-sub" style="color: var(--primary);">Aggregated pipeline</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Under Review</div>
                        <div class="metric-value" id="kpiReview">0</div>
                        <div class="metric-sub" style="color: var(--orange);">Requires action</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Approval Velocity</div>
                        <div class="metric-value" id="kpiRate">88%</div>
                        <div class="metric-sub">SLA &lt; 24h</div>
                    </div>
                </div>

                <!-- Interactive Records Table -->
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
                            <input type="text" class="search-input" placeholder="Search records, titles, applicants..." oninput="handleSearch(this.value)">
                        </div>
                    </div>

                    <table class="table-records">
                        <thead>
                            <tr>
                                <th style="width: 140px;">Record ID</th>
                                <th>Primary Title / Purpose</th>
                                <th>Responsible Party</th>
                                <th style="width: 140px;">Amount ($)</th>
                                <th style="width: 120px;">Creation Date</th>
                                <th style="width: 120px; text-align: center;">Status</th>
                                <th style="width: 140px; text-align: right;">Action</th>
                            </tr>
                        </thead>
                        <tbody id="recordsTbody">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

        </main>
    </div>

    <!-- Record Detail / Form Modal -->
    <div class="modal-overlay" id="recordModal">
        <div class="modal-card">
            <div class="modal-header">
                <div>
                    <h3 style="font-size: 16px; font-weight: 700;" id="modalTitle">Record Details</h3>
                    <span id="modalDocname" style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;"></span>
                </div>
                <button class="btn btn-outline" style="padding: 4px 8px;" onclick="closeModal('recordModal')">✕</button>
            </div>
            <div class="modal-body" id="modalFormFields">
                <!-- Dynamically populated from schema -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('recordModal')">Cancel</button>
                <button class="btn btn-outline" style="color: var(--red); border-color: #fca5a5;" onclick="updateRecordStatus('Rejected')">Reject</button>
                <button class="btn btn-primary" style="background: var(--green);" onclick="updateRecordStatus('Approved')">Quick Approve</button>
                <button class="btn btn-primary" onclick="saveRecord()">Save Record</button>
            </div>
        </div>
    </div>

    <!-- SOP Document Modal -->
    <div class="modal-overlay" id="sopModal">
        <div class="modal-card" style="width: 800px;">
            <div class="modal-header">
                <div>
                    <h3 style="font-size: 16px; font-weight: 700;">Standard Operating Procedure (SOP)</h3>
                    <span style="font-size: 12px; color: var(--text-muted);">Generated automatically by Frappe Working SOP Author</span>
                </div>
                <button class="btn btn-outline" style="padding: 4px 8px;" onclick="closeModal('sopModal')">✕</button>
            </div>
            <div class="modal-body sop-viewer" id="sopContent">
                <!-- Populated dynamically -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="closeModal('sopModal')">Done</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toastMessage">Application initialized</div>

    <script>
        let currentApp = null;
        let currentDocType = null;
        let allRecords = [];
        let activeFilter = "ALL";
        let activeDocname = null;
        let currentSchema = null;

        const KEY_PIPELINE_AGENTS = [
            "frappe-autonomous-orchestrator",
            "frappe-prompt-to-app-builder",
            "frappe-product-manager",
            "frappe-hld-architect",
            "frappe-lld-designer",
            "frappe-fullstack-developer",
            "frappe-desk-builder",
            "frappe-bpmn-visual-workflow-builder",
            "frappe-bi-dashboard-synthesizer",
            "frappe-data-synthesizer",
            "frappe-working-sop-author"
        ];

        window.addEventListener("DOMContentLoaded", () => {
            renderAgentPills();
            checkInitialAppState();
        });

        function renderAgentPills() {
            const container = document.getElementById("activeAgentPills");
            container.innerHTML = KEY_PIPELINE_AGENTS.map(name => `
                <span class="agent-pill" id="pill-${name}">${name.replace('frappe-', '')}</span>
            `).join("");
        }

        async function checkInitialAppState() {
            try {
                const res = await fetch("/api/apps");
                const apps = await res.json();
                if (apps && apps.length > 0) {
                    // Apps exist, load the latest app into Desk
                    selectApp(apps[0].name, apps[0].title);
                } else {
                    // Zero apps exist, display pure Prompt Studio!
                    openPromptStudio();
                }
            } catch (e) {
                openPromptStudio();
            }
        }

        function openPromptStudio() {
            document.getElementById("promptView").style.display = "flex";
            document.getElementById("deskView").className = "desk-view";
            document.getElementById("appSidebar").style.display = "none";
            document.getElementById("btnViewSop").style.display = "none";
            document.getElementById("btnStimulate").style.display = "none";
            document.getElementById("btnNewRecord").style.display = "none";
        }

        function usePreset(prompt) {
            document.getElementById("mainPromptText").value = prompt;
            window.scrollTo({top: 0, behavior: 'smooth'});
        }

        async function startAutonomousBuildFromScratch() {
            const promptText = document.getElementById("mainPromptText").value.trim();
            if (!promptText) {
                alert("Please enter a business application description prompt.");
                return;
            }

            const simCount = parseInt(document.getElementById("simCountSelect").value) || 25;

            // Show Flight Deck
            const deck = document.getElementById("flightDeckBox");
            deck.classList.add("active");
            document.getElementById("progressFill").style.width = "10%";
            document.getElementById("pipelineStatusText").innerText = "Awakening 53 AI Specialists...";

            logConsole("ORCHESTRATOR", `Received requirement prompt: "${promptText}"`);
            logConsole("DECOMPOSITION", "Analyzing business entities, workflow states, and data models...");

            // Simulate animated stage progression
            const stages = [
                {pct: "25%", text: "Stage 1: Deducing DocType Schemas & PRD..."},
                {pct: "50%", text: "Stage 2: Synthesizing Controllers, APIs & Workflows..."},
                {pct: "75%", text: "Stage 3: Stimulating Realistic Enterprise Data..."},
                {pct: "95%", text: "Stage 4: Compiling Working SOP & Hot-Reloading..."}
            ];

            let stageIdx = 0;
            const progressTimer = setInterval(() => {
                if (stageIdx < stages.length) {
                    document.getElementById("progressFill").style.width = stages[stageIdx].pct;
                    document.getElementById("pipelineStatusText").innerText = stages[stageIdx].text;
                    stageIdx++;
                }
            }, 300);

            try {
                const res = await fetch("/api/autonomous/build", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({prompt: promptText, simulated_count: simCount})
                });
                const data = await res.json();
                clearInterval(progressTimer);

                document.getElementById("progressFill").style.width = "100%";
                document.getElementById("pipelineStatusText").innerText = "Application Built & Deployed Successfully!";
                logConsole("SUCCESS", `Built '${data.app_title}' with ${data.deliverables} deliverables and ${data.simulated_records_seeded} simulated records!`);

                showToast(`Application '${data.app_title}' built and deployed from scratch!`);

                // Mark all pills done
                document.querySelectorAll(".agent-pill").forEach(p => p.classList.add("done"));

                // Switch to Desk after short delay
                setTimeout(async () => {
                    deck.classList.remove("active");
                    await selectApp(data.app_slug, data.app_title);
                }, 1000);

            } catch (e) {
                clearInterval(progressTimer);
                logConsole("ERROR", "Build failed: " + e.message);
                document.getElementById("pipelineStatusText").innerText = "Build failed";
            }
        }

        function logConsole(tag, msg) {
            const c = document.getElementById("consoleLogs");
            const time = new Date().toLocaleTimeString();
            const logEl = document.createElement("div");
            logEl.innerHTML = `<span style="color:#64748b;">[${time}]</span> <span style="font-weight:600; color:#fbbf24;">[${tag}]</span> ${msg}`;
            c.appendChild(logEl);
            c.scrollTop = c.scrollHeight;
        }

        async function selectApp(appSlug, appTitle) {
            currentApp = appSlug;
            document.getElementById("promptView").style.display = "none";
            document.getElementById("deskView").className = "desk-view active";
            document.getElementById("appSidebar").style.display = "flex";
            document.getElementById("btnViewSop").style.display = "inline-flex";
            document.getElementById("btnStimulate").style.display = "inline-flex";
            document.getElementById("btnNewRecord").style.display = "inline-flex";

            document.getElementById("currentAppTitle").innerText = appTitle;

            await loadSidebarApps();
            await loadDoctypes();
            await loadRecords();
        }

        async function loadSidebarApps() {
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
                console.error(e);
            }
        }

        async function loadDoctypes() {
            try {
                const res = await fetch(`/api/doctypes?app=${currentApp}`);
                const dts = await res.json();
                if (dts && dts.length > 0) {
                    currentDocType = dts[0].name;
                    currentSchema = dts[0].schema;
                    document.getElementById("currentDocTypeSub").innerText = `Managing ${currentDocType} records in stimulated runtime`;
                }
                const listEl = document.getElementById("doctypesList");
                listEl.innerHTML = dts.map(dt => `
                    <li class="sidebar-item ${dt.name === currentDocType ? 'active' : ''}" onclick="selectDocType('${dt.name}')">
                        <span>📄</span>
                        <span>${dt.name}</span>
                        <span class="badge" id="badge-${dt.name.replace(/\\s/g, '_')}">0</span>
                    </li>
                `).join("");
            } catch (e) {
                console.error(e);
            }
        }

        function selectDocType(dtName) {
            currentDocType = dtName;
            document.getElementById("currentDocTypeSub").innerText = `Managing ${dtName} records in stimulated runtime`;
            loadDoctypes();
            loadRecords();
        }

        async function loadRecords() {
            if (!currentDocType) return;
            try {
                const res = await fetch(`/api/resource/${encodeURIComponent(currentDocType)}`);
                allRecords = await res.json();
                renderRecords();
                updateKPIs();
            } catch (e) {
                console.error(e);
            }
        }

        function renderRecords() {
            const tbody = document.getElementById("recordsTbody");
            let filtered = allRecords;

            if (activeFilter !== "ALL") {
                filtered = filtered.filter(r => (r.status || "Draft").toLowerCase() === activeFilter.toLowerCase());
            }

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 40px; color:#94a3b8;">No records found. Click "+ New Record" or "⚡ Stimulate 25 Records".</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => {
                const amt = r.requested_amount ? "$" + parseFloat(r.requested_amount).toLocaleString(undefined, {minimumFractionDigits: 2}) : "-";
                const statusCls = `status-${(r.status || 'Draft').replace(/\\s+/g, '-')}`;
                const titleVal = r.title || r.case_title || r.name;
                const partyVal = r.patient_name || r.applicant_name || r.tenant_name || r.driver_name || '-';
                const dateVal = r.submission_date || r.creation_date || (r.creation ? r.creation.split(' ')[0] : '-');

                return `
                    <tr onclick="openRecordModal('${r.name}')">
                        <td style="font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--primary);">${r.name}</td>
                        <td style="font-weight:600;">${titleVal}</td>
                        <td>${partyVal}</td>
                        <td style="font-weight:600;">${amt}</td>
                        <td style="color:#64748b;">${dateVal}</td>
                        <td style="text-align:center;"><span class="status-badge ${statusCls}">${r.status || 'Draft'}</span></td>
                        <td style="text-align:right;">
                            <button class="btn btn-outline" style="padding: 4px 8px; font-size:11px;" onclick="event.stopPropagation(); quickApprove('${r.name}')">Approve</button>
                        </td>
                    </tr>
                `;
            }).join("");

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
                const combined = JSON.stringify(r).toLowerCase();
                return combined.includes(term);
            });
            const tbody = document.getElementById("recordsTbody");
            tbody.innerHTML = filtered.map(r => {
                const amt = r.requested_amount ? "$" + parseFloat(r.requested_amount).toLocaleString(undefined, {minimumFractionDigits: 2}) : "-";
                const statusCls = `status-${(r.status || 'Draft').replace(/\\s+/g, '-')}`;
                const titleVal = r.title || r.name;
                const partyVal = r.patient_name || r.applicant_name || r.tenant_name || '-';
                return `
                    <tr onclick="openRecordModal('${r.name}')">
                        <td style="font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--primary);">${r.name}</td>
                        <td style="font-weight:600;">${titleVal}</td>
                        <td>${partyVal}</td>
                        <td style="font-weight:600;">${amt}</td>
                        <td style="color:#64748b;">${r.creation_date || '-'}</td>
                        <td style="text-align:center;"><span class="status-badge ${statusCls}">${r.status || 'Draft'}</span></td>
                        <td style="text-align:right;">
                            <button class="btn btn-outline" style="padding: 4px 8px; font-size:11px;" onclick="event.stopPropagation(); quickApprove('${r.name}')">Approve</button>
                        </td>
                    </tr>
                `;
            }).join("");
        }

        async function stimulateData() {
            showToast("Synthesizing 25 more simulated records...");
            try {
                const res = await fetch("/api/data/synthesize", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({doctype: currentDocType, count: 25})
                });
                const data = await res.json();
                showToast(`Generated ${data.seeded_count} simulated records!`);
                loadRecords();
            } catch (e) {
                console.error(e);
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
                        <label class="form-label">Title / Subject</label>
                        <input type="text" id="modal_f_title" class="form-input" value="${rec.title || ''}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Responsible / Requesting Party</label>
                        <input type="text" id="modal_f_applicant" class="form-input" value="${rec.patient_name || rec.applicant_name || rec.tenant_name || rec.driver_name || ''}">
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
                        <label class="form-label">Monetary Amount ($)</label>
                        <input type="number" id="modal_f_amount" class="form-input" value="${rec.requested_amount || 0}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Date</label>
                        <input type="date" id="modal_f_date" class="form-input" value="${rec.submission_date || rec.creation_date || (rec.creation ? rec.creation.split(' ')[0] : '')}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Operational Notes & Justification</label>
                        <textarea id="modal_f_notes" class="form-textarea" rows="3">${rec.notes || rec.prescription_notes || ''}</textarea>
                    </div>
                </div>
            `;
            document.getElementById("recordModal").classList.add("active");
        }

        function openNewRecordModal() {
            activeDocname = null;
            document.getElementById("modalTitle").innerText = `New ${currentDocType} Record`;
            document.getElementById("modalDocname").innerText = "Will be assigned autoname upon insertion";

            const fieldsDiv = document.getElementById("modalFormFields");
            fieldsDiv.innerHTML = `
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Title / Subject</label>
                        <input type="text" id="modal_f_title" class="form-input" placeholder="e.g. Enterprise Requisition Order">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Responsible / Requesting Party</label>
                        <input type="text" id="modal_f_applicant" class="form-input" placeholder="e.g. John Doe">
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
                        <label class="form-label">Monetary Amount ($)</label>
                        <input type="number" id="modal_f_amount" class="form-input" value="15000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Date</label>
                        <input type="date" id="modal_f_date" class="form-input" value="${new Date().toISOString().split('T')[0]}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group full">
                        <label class="form-label">Operational Notes & Justification</label>
                        <textarea id="modal_f_notes" class="form-textarea" rows="3" placeholder="Enter notes..."></textarea>
                    </div>
                </div>
            `;
            document.getElementById("recordModal").classList.add("active");
        }

        async function saveRecord() {
            const payload = {
                title: document.getElementById("modal_f_title").value,
                applicant_name: document.getElementById("modal_f_applicant").value,
                patient_name: document.getElementById("modal_f_applicant").value,
                status: document.getElementById("modal_f_status").value,
                requested_amount: parseFloat(document.getElementById("modal_f_amount").value) || 0,
                submission_date: document.getElementById("modal_f_date").value,
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
                closeModal('recordModal');
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
                closeModal('recordModal');
                loadRecords();
            } catch (e) {
                console.error(e);
            }
        }

        async function openSopModal() {
            if (!currentApp) return;
            try {
                const res = await fetch(`/api/app/sop?name=${currentApp}`);
                const data = await res.json();
                document.getElementById("sopContent").innerHTML = `
                    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0; white-space:pre-wrap; font-family:'JetBrains Mono',monospace; font-size:12px;">
${data.sop || "No SOP generated for this application."}
                    </div>
                `;
                document.getElementById("sopModal").classList.add("active");
            } catch (e) {
                console.error(e);
            }
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove("active");
        }

        function showToast(msg) {
            const toast = document.getElementById("toastMessage");
            toast.innerText = msg;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 3500);
        }
    </script>
</body>
</html>
"""


class FrappeLocalRuntimeHandler(BaseHTTPRequestHandler):
    """Handles REST APIs, Desk assets, and Autonomous Builder endpoints."""

    def log_message(self, format, *args):
        # Mute standard noisy HTTP log lines
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

        # 3. API: Get App SOP
        if path == "/api/app/sop":
            app_name = query.get("name", [None])[0]
            app_data = db.get_app(app_name) if app_name else None
            sop_text = app_data.get("sop_markdown", "") if app_data else ""
            self._send_json({"sop": sop_text})
            return

        # 4. API: Get DocTypes
        if path == "/api/doctypes":
            app_filter = query.get("app", [None])[0]
            dts = db.get_doctypes(app_filter)
            self._send_json(dts)
            return

        # 5. API: Query Resources / Records: GET /api/resource/{doctype}
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

        # 6. API: Event Stream Polling
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
            prompt = payload.get("prompt", "Custom Application")
            app_slug = payload.get("app_slug")
            app_title = payload.get("app_title")
            simulated_count = int(payload.get("simulated_count", 25))

            # Execute autonomous build from scratch
            result = AutonomousAppBuilder.build_from_prompt(
                prompt, app_slug, app_title, simulated_count=simulated_count
            )
            self._send_json(result)
            return

        # 2. Stimulate Data API
        if path == "/api/data/synthesize":
            doctype_name = payload.get("doctype")
            count = int(payload.get("count", 25))

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


def run_server(port: int = 8050, open_browser: bool = True):
    """Starts the Frappe Local Runtime Server on localhost with zero pre-seeded apps."""
    # Ensure database is clean of example apps
    db.clear_all()

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, FrappeLocalRuntimeHandler)

    print("\n" + "=" * 80)
    print("🚀 FRAPPE AUTONOMOUS LOCAL RUNTIME ACTIVE (PURE PROMPT MODE)")
    print(f"URL: http://localhost:{port}")
    print(f"Active Port: {port} | Database: Clean In-Memory (Zero Example Apps)")
    print("Awaiting User Natural Language Prompt to Build Application From Scratch...")
    print("=" * 80 + "\n")

    if open_browser:
        def launch():
            time.sleep(1.0)
            url = f"http://localhost:{port}"
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
