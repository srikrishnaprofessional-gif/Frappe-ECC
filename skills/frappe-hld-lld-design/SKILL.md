---
name: frappe-hld-lld-design
description: Architect and author complete High-Level Design (HLD) and Low-Level Design (LLD) specifications with Mermaid diagrams, database schemas, and state machines.
---

# Frappe HLD & LLD System Design Mastery

## 1. High-Level Design (HLD) Workflow
HLD articulates the macro architecture, component boundaries, and non-functional requirements.

### C4 Container Architecture Template
```mermaid
graph TD
    Client["Web Browser / Mobile App"]
    Nginx["Nginx Reverse Proxy"]
    Gunicorn["Frappe Gunicorn (Web Worker)"]
    RQ["Redis RQ Workers (Short, Default, Long)"]
    RedisCache["Redis Cache (Port 11000)"]
    RedisQueue["Redis Queue (Port 12000)"]
    MariaDB[("MariaDB 10.6+ / PostgreSQL")]

    Client -->|HTTPS :443| Nginx
    Nginx -->|Proxy Pass :8000| Gunicorn
    Gunicorn -->|Session / Doc Cache| RedisCache
    Gunicorn -->|Enqueue Background Task| RedisQueue
    RQ -->|Pop Job| RedisQueue
    Gunicorn -->|SQL Queries| MariaDB
    RQ -->|Execute Task & Update DB| MariaDB
```

---

## 2. Low-Level Design (LLD) Workflow
LLD provides precise technical specifications: entity relationships, class hierarchies, method signatures, and state machines.

### Entity-Relationship (ER) Modeling Template
```mermaid
erDiagram
    ASSET_ITEM ||--o{ ASSET_COMPONENT : contains
    ASSET_ITEM }|--|| ASSET_CATEGORY : categorized_by
    ASSET_ITEM ||--o{ ASSET_MAINTENANCE_LOG : undergoes

    ASSET_ITEM {
        varchar(140) name PK "Autoname AST-.YYYY.-.#####"
        varchar(140) asset_name "Indexed"
        varchar(140) asset_category FK
        varchar(50) status "Draft | In Use | Under Maintenance | Decommissioned"
        varchar(140) serial_no UK "Unique Index"
        date purchase_date
        decimal total_component_cost
        int docstatus "0=Draft, 1=Submitted, 2=Cancelled"
    }

    ASSET_COMPONENT {
        varchar(140) name PK
        varchar(140) parent FK "References ASSET_ITEM"
        varchar(140) component_name
        varchar(140) serial_no
        decimal cost
        int idx "Row Order"
    }
```

### State Machine Lifecycle
| Current State | Trigger / Action | Conditions | Next State | Side Effects |
|---|---|---|---|---|
| `Draft` (`docstatus=0`) | Click `Submit` | All required fields present; components > 0 | `Submitted` (`docstatus=1`) | Status set to `In Use`; post asset ledger entry |
| `In Use` (`docstatus=1`) | Click `Schedule Maintenance` | No active maintenance tickets | `Under Maintenance` | Send notification to IT technician |
| `Under Maintenance` | Click `Resolve Maintenance` | Resolution notes present | `In Use` | Update maintenance history log |
| `Submitted` (`docstatus=1`) | Click `Cancel` | Reason provided; no active dependencies | `Cancelled` (`docstatus=2`) | Reverse asset allocations |
