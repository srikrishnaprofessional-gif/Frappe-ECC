---
description: Execute complete autonomous prompt-to-production pipeline for Frappe Framework from a single natural language description.
---

# /frappe:auto

Autonomous prompt-to-production pipeline execution for the Frappe Framework.

## Usage
```
/frappe:auto "<prompt>"
```

## Examples
```
/frappe:auto "Build an automated Clinic Management System with doctor scheduling, patient intake, prescription printouts, WhatsApp notifications, and billing with Stripe integration"
/frappe:auto "Build a Gym Membership & Access Control System with QR code badges, automated renewals, and trainer booking"
```

## Autonomous Workflow Stages
1. Ingests prompt and dispatches to `frappe-product-manager` to generate PRD.
2. Architects HLD container diagrams and LLD entity relationships (`frappe-hld-architect`, `frappe-lld-designer`).
3. Formulates realistic synthetic fixtures and access control rules (`frappe-data-synthesizer`, `frappe-rbac-compliance-guardian`).
4. Generates visual wireframes and a clickable browser prototype (`frappe-wireframe-builder`, `frappe-interactive-prototyper`).
5. Writes failing unit tests and turnkey full-stack code (`frappe-tdd-guide`, `frappe-fullstack-developer`).
6. Implements third-party integrations and print formats (`frappe-integrations-broker`, `frappe-print-format-designer`).
7. Executes unit tests, Playwright browser tests, and Frappe Shield security audit (`frappe-automated-tester`, `frappe-security-reviewer`).
8. If any failure occurs, auto-patches code via `frappe-self-healing-debugger`.
9. Packages CI/CD workflows and Docker configurations (`frappe-release-devops`).
