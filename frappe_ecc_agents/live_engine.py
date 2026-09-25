"""
Frappe ECC Autonomous Live Engine & Data Simulator
Enables AI Agents to autonomously construct full-stack Frappe applications in real time
and simulate realistic enterprise data for immediate execution on local machines.
"""

import os
import sys
import json
import time
import uuid
import random
import datetime
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Callable

from .base import AgentContext, AgentStatus
from .registry import registry

# Windows UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class AutonomousEventStream:
    """Manages real-time log and state event streaming for autonomous agents."""

    def __init__(self):
        self.subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self.history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self.subscribers.append(callback)

    def emit(self, event_type: str, data: Dict[str, Any]):
        event = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": time.strftime("%H:%M:%S"),
            "event_type": event_type,
            "data": data
        }
        with self._lock:
            self.history.append(event)
            # Keep history capped at 500 events
            if len(self.history) > 500:
                self.history.pop(0)
            for sub in list(self.subscribers):
                try:
                    sub(event)
                except Exception:
                    pass
        return event

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.history[-limit:])


# Global event bus
event_bus = AutonomousEventStream()


class LocalFrappeDatabase:
    """
    Lightweight SQLite-backed local database implementing Frappe's table structure.
    Mimics MariaDB's `tab{DocType}` conventions, autonaming series, and document lifecycle.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_metadata_tables()

    def _init_metadata_tables(self):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS __series (
                    prefix TEXT PRIMARY KEY,
                    current_val INTEGER DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS __doctypes (
                    name TEXT PRIMARY KEY,
                    module TEXT,
                    app_name TEXT,
                    schema_json TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS __apps (
                    name TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    creation_time TEXT
                )
            """)
            self.conn.commit()

    def register_app(self, name: str, title: str, description: str):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO __apps (name, title, description, creation_time) VALUES (?, ?, ?, ?)",
                (name, title, description, time.strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.conn.commit()

    def register_doctype(self, doctype_dict: Dict[str, Any], app_name: str):
        name = doctype_dict.get("doctype") or doctype_dict.get("name")
        module = doctype_dict.get("module", app_name)
        schema_json = json.dumps(doctype_dict)

        table_name = f"tab{name.replace(' ', '_')}"
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO __doctypes (name, module, app_name, schema_json) VALUES (?, ?, ?, ?)",
                (name, module, app_name, schema_json)
            )

            # Create data table
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS [{table_name}] (
                    name TEXT PRIMARY KEY,
                    creation TEXT,
                    modified TEXT,
                    modified_by TEXT,
                    owner TEXT,
                    docstatus INTEGER DEFAULT 0,
                    status TEXT,
                    data_json TEXT
                )
            """)
            self.conn.commit()

    def get_apps(self) -> List[Dict[str, Any]]:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM __apps ORDER BY creation_time DESC")
            return [dict(r) for r in cur.fetchall()]

    def get_doctypes(self, app_name: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            cur = self.conn.cursor()
            if app_name:
                cur.execute("SELECT * FROM __doctypes WHERE app_name = ?", (app_name,))
            else:
                cur.execute("SELECT * FROM __doctypes")
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["schema"] = json.loads(d["schema_json"])
                out.append(d)
            return out

    def get_next_series(self, prefix: str = "REC-") -> str:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("SELECT current_val FROM __series WHERE prefix = ?", (prefix,))
            row = cur.fetchone()
            if row:
                val = row["current_val"] + 1
                cur.execute("UPDATE __series SET current_val = ? WHERE prefix = ?", (val, prefix))
            else:
                val = 1
                cur.execute("INSERT INTO __series (prefix, current_val) VALUES (?, ?)", (prefix, val))
            self.conn.commit()
            year = time.strftime("%Y")
            return f"{prefix}{year}-{val:05d}"

    def insert(self, doctype: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        table_name = f"tab{doctype.replace(' ', '_')}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        prefix = "REC-"
        # Deducing prefix from doctype initials
        words = doctype.split()
        if len(words) >= 2:
            prefix = f"{words[0][:2].upper()}{words[1][:2].upper()}-"
        elif len(words) == 1:
            prefix = f"{words[0][:3].upper()}-"

        doc_name = doc.get("name") or self.get_next_series(prefix)
        status = doc.get("status") or doc.get("workflow_state") or "Draft"

        record_data = dict(doc)
        record_data["name"] = doc_name
        record_data["doctype"] = doctype
        record_data["status"] = status
        record_data["creation"] = now
        record_data["modified"] = now
        record_data["owner"] = doc.get("owner") or "Administrator"

        with self._lock:
            cur = self.conn.cursor()
            cur.execute(f"""
                INSERT OR REPLACE INTO [{table_name}] 
                (name, creation, modified, modified_by, owner, docstatus, status, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_name,
                now,
                now,
                "Administrator",
                record_data["owner"],
                doc.get("docstatus", 0),
                status,
                json.dumps(record_data)
            ))
            self.conn.commit()

        event_bus.emit("RECORD_CREATED", {
            "doctype": doctype,
            "name": doc_name,
            "status": status,
            "title": doc.get("title") or doc.get("applicant_name") or doc_name
        })
        return record_data

    def get_list(self, doctype: str, status_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        table_name = f"tab{doctype.replace(' ', '_')}"
        with self._lock:
            cur = self.conn.cursor()
            # Verify table exists
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cur.fetchone():
                return []

            query = f"SELECT * FROM [{table_name}] WHERE 1=1"
            params = []
            if status_filter and status_filter.upper() != "ALL":
                query += " AND status = ?"
                params.append(status_filter)

            query += " ORDER BY creation DESC"
            cur.execute(query, params)
            rows = cur.fetchall()

            out = []
            for r in rows:
                data = json.loads(r["data_json"])
                if search:
                    term = search.lower()
                    haystack = f"{data.get('name', '')} {data.get('title', '')} {data.get('applicant_name', '')}".lower()
                    if term not in haystack:
                        continue
                out.append(data)
            return out

    def get_doc(self, doctype: str, name: str) -> Optional[Dict[str, Any]]:
        table_name = f"tab{doctype.replace(' ', '_')}"
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(f"SELECT data_json FROM [{table_name}] WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                return json.loads(row["data_json"])
            return None

    def update_doc(self, doctype: str, name: str, patch_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        table_name = f"tab{doctype.replace(' ', '_')}"
        doc = self.get_doc(doctype, name)
        if not doc:
            return None

        doc.update(patch_data)
        doc["modified"] = time.strftime("%Y-%m-%d %H:%M:%S")
        status = doc.get("status") or doc.get("workflow_state") or "Draft"

        with self._lock:
            cur = self.conn.cursor()
            cur.execute(f"""
                UPDATE [{table_name}] 
                SET modified = ?, status = ?, data_json = ? 
                WHERE name = ?
            """, (doc["modified"], status, json.dumps(doc), name))
            self.conn.commit()

        event_bus.emit("RECORD_UPDATED", {
            "doctype": doctype,
            "name": name,
            "status": status,
            "patch": patch_data
        })
        return doc

    def count(self, doctype: str) -> int:
        table_name = f"tab{doctype.replace(' ', '_')}"
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cur.fetchone():
                return 0
            cur.execute(f"SELECT COUNT(*) as cnt FROM [{table_name}]")
            return cur.fetchone()["cnt"]


# Global database instance
db = LocalFrappeDatabase()


# ---------------------------------------------------------------------------
# SYNTHETIC REALISTIC DATA STIMULATOR
# ---------------------------------------------------------------------------
class SimulatedDataFactory:
    """Synthesizes rich, realistic enterprise datasets across multiple business domains."""

    FIRST_NAMES = ["Liam", "Olivia", "Noah", "Emma", "Oliver", "Charlotte", "Elijah", "Amelia", "James", "Sophia", "William", "Isabella", "Benjamin", "Mia", "Lucas", "Evelyn", "Henry", "Harper", "Alexander", "Camila"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    COMPANIES = ["Apex Innovations", "Starlight Global", "Quantum Logistics", "Horizon Infrastructure", "Pinnacle Capital", "Vanguard Health", "NextGen Robotics", "OmniCorp International", "Atlas Dynamics", "Summit Technologies"]
    DEPARTMENTS = ["Operations", "Procurement", "Engineering", "Finance", "Logistics", "Information Technology", "Executive Office", "Quality Assurance"]
    STATUSES = ["Draft", "Under Review", "Approved", "Rejected", "Completed"]

    @classmethod
    def generate_records(cls, doctype_dict: Dict[str, Any], count: int = 20) -> List[Dict[str, Any]]:
        """Generates realistic records aligned with the fields defined in the DocType schema."""
        doctype_name = doctype_dict.get("doctype") or doctype_dict.get("name")
        fields = doctype_dict.get("fields", [])
        records = []

        now = datetime.datetime.now()

        for i in range(count):
            name_sample = f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}"
            company_sample = random.choice(cls.COMPANIES)
            created_days_ago = random.randint(0, 90)
            created_date = (now - datetime.timedelta(days=created_days_ago)).strftime("%Y-%m-%d")

            status = random.choices(cls.STATUSES, weights=[20, 35, 30, 10, 5], k=1)[0]
            amount = round(random.uniform(5000, 250000), 2)

            rec = {
                "doctype": doctype_name,
                "status": status,
                "creation_date": created_date,
            }

            # Map fields dynamically
            for f in fields:
                fname = f.get("fieldname")
                ftype = f.get("fieldtype")
                flabel = f.get("label", "").lower()

                if "title" in fname:
                    rec[fname] = f"{company_sample} - Project #{random.randint(100, 999)}"
                elif "applicant" in fname or "customer" in fname or "user" in fname:
                    rec[fname] = name_sample
                elif "company" in fname or "vendor" in fname or "supplier" in fname:
                    rec[fname] = company_sample
                elif "department" in fname:
                    rec[fname] = random.choice(cls.DEPARTMENTS)
                elif ftype == "Currency" or "amount" in fname or "rate" in fname or "total" in fname:
                    rec[fname] = amount
                elif ftype == "Date" or "date" in fname:
                    rec[fname] = created_date
                elif ftype == "Select" and f.get("options"):
                    opts = [opt.strip() for opt in f["options"].split("\n") if opt.strip()]
                    rec[fname] = random.choice(opts) if opts else status
                elif ftype == "Check":
                    rec[fname] = random.choice([0, 1])
                elif ftype == "Text Editor" or ftype == "Text" or "notes" in fname or "description" in fname:
                    rec[fname] = f"Application evaluated by {random.choice(cls.FIRST_NAMES)} in accordance with ISO enterprise policies. Verified by internal compliance."
                elif ftype == "Data":
                    if "code" in fname or "number" in fname:
                        rec[fname] = f"REF-{random.randint(10000, 99999)}"
                    elif "email" in fname:
                        rec[fname] = f"{name_sample.lower().replace(' ', '.')}@{company_sample.lower().replace(' ', '')}.com"
                    elif "phone" in fname:
                        rec[fname] = f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    else:
                        rec[fname] = f"{company_sample} {flabel.title()}"

            records.append(rec)
        return records


# ---------------------------------------------------------------------------
# REAL-TIME AUTONOMOUS APPLICATION BUILDER
# ---------------------------------------------------------------------------
class AutonomousAppBuilder:
    """
    Coordinates AI agents in real time to build a customized Frappe application
    from a high-level natural language prompt and deploy it directly into the local runtime.
    """

    @classmethod
    def build_from_prompt(cls, prompt_text: str, app_slug: Optional[str] = None, app_title: Optional[str] = None) -> Dict[str, Any]:
        """Executes full autonomous multi-agent pipeline and seeds stimulated data."""
        start_ts = time.time()

        # Deduce title & slug if not provided
        if not app_title or not app_slug:
            clean_prompt = prompt_text.strip().replace("Build", "").replace("Create", "").replace("a ", "").replace("an ", "")
            words = [w.capitalize() for w in clean_prompt.split()[:4]]
            app_title = " ".join(words) if words else "Enterprise Solution"
            app_slug = "_".join([w.lower() for w in words]) if words else "enterprise_app"

        event_bus.emit("PIPELINE_STARTED", {
            "app_title": app_title,
            "app_slug": app_slug,
            "prompt": prompt_text
        })

        # Register application in local database
        db.register_app(app_slug, app_title, prompt_text)

        # Context shared across agents
        context = AgentContext(
            project_name=app_slug,
            app_title=app_title,
            app_description=prompt_text,
            prompt=prompt_text
        )

        agent_pipeline = [
            # Ingestion
            "frappe-autonomous-orchestrator",
            "frappe-prompt-to-app-builder",
            "frappe-product-manager",
            # Architecture
            "frappe-hld-architect",
            "frappe-lld-designer",
            # Development
            "frappe-fullstack-developer",
            "frappe-desk-builder",
            "frappe-backend-builder",
            # Workflows
            "frappe-bpmn-visual-workflow-builder",
            "frappe-notification-omnichannel-agent",
            # Analytics
            "frappe-bi-dashboard-synthesizer",
            # Data Synthesis
            "frappe-data-synthesizer",
            # QA & SOP
            "frappe-tdd-guide",
            "frappe-working-sop-author",
            "frappe-custom-app-git-builder"
        ]

        generated_deliverables = []
        app_doctypes = []

        for idx, agent_name in enumerate(agent_pipeline, 1):
            agent = registry.get(agent_name)
            if not agent:
                continue

            event_bus.emit("AGENT_STARTING", {
                "step": idx,
                "total_steps": len(agent_pipeline),
                "agent": agent.name,
                "pillar": agent.pillar.value,
                "message": f"Executing {agent.name}..."
            })

            res = agent.run(context)
            generated_deliverables.extend(res.deliverables)

            event_bus.emit("AGENT_COMPLETED", {
                "step": idx,
                "agent": agent.name,
                "status": res.status.value,
                "latency_sec": res.execution_time_sec,
                "summary": res.summary,
                "deliverables_count": len(res.deliverables)
            })

        # Register DocTypes in Local Database
        for dt in context.doctypes:
            db.register_doctype(dt, app_slug)
            app_doctypes.append(dt)

        # If no DocType created, register default domain record
        if not app_doctypes:
            default_dt = {
                "doctype": f"{app_title} Record",
                "module": app_title,
                "fields": [
                    {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
                    {"fieldname": "applicant_name", "fieldtype": "Data", "label": "Applicant Name", "reqd": 1},
                    {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nUnder Review\nApproved\nRejected\nCompleted"},
                    {"fieldname": "requested_amount", "fieldtype": "Currency", "label": "Amount"},
                    {"fieldname": "submission_date", "fieldtype": "Date", "label": "Submission Date"},
                    {"fieldname": "department", "fieldtype": "Data", "label": "Department"},
                    {"fieldname": "notes", "fieldtype": "Text Editor", "label": "Notes"}
                ]
            }
            db.register_doctype(default_dt, app_slug)
            app_doctypes.append(default_dt)

        # -------------------------------------------------------------------
        # DATA STIMULATOR: Seed 25 realistic domain-specific records
        # -------------------------------------------------------------------
        event_bus.emit("SIMULATION_STARTING", {
            "message": "Generating 25 rich simulated records with realistic enterprise data..."
        })

        seeded_count = 0
        for dt in app_doctypes:
            simulated_records = SimulatedDataFactory.generate_records(dt, count=25)
            for rec in simulated_records:
                db.insert(dt.get("doctype") or dt.get("name"), rec)
                seeded_count += 1

        total_time = round(time.time() - start_ts, 3)

        event_bus.emit("PIPELINE_FINISHED", {
            "app_title": app_title,
            "app_slug": app_slug,
            "total_deliverables": len(generated_deliverables),
            "simulated_records_seeded": seeded_count,
            "execution_time_sec": total_time
        })

        return {
            "app_title": app_title,
            "app_slug": app_slug,
            "doctypes": app_doctypes,
            "deliverables": len(generated_deliverables),
            "simulated_records_seeded": seeded_count,
            "execution_time_sec": total_time
        }
