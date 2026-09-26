# /frappe:plan

**Purpose**: Design the complete architecture and implementation blueprint for a Frappe feature, module, or application before writing code.

## Usage
`/frappe:plan "<feature description>"`

## Execution Workflow
1. Invoke the **frappe-planner** agent.
2. Analyze the business requirements and map out:
   - DocType taxonomy (Standard, Single, Child Table, Submittable).
   - Field definitions, data types, options, mandatory flags, and search indexes.
   - Autonaming rules and series expressions.
   - Module file manifest (`.json`, `.py`, `.js`, `test_*.py`).
   - Hooks requirements (`hooks.py`).
   - Role Permission matrix.
3. Generate a structured Markdown blueprint.
