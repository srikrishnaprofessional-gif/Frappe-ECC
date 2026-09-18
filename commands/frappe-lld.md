# /frappe:lld

**Purpose**: Generate a Low-Level Design (LLD) technical document with Mermaid ER diagrams, controller class hierarchies, state machines, and API payload schemas.

## Usage
`/frappe:lld "<feature or DocType name>"`

## Execution Workflow
1. Invoke the **frappe-lld-designer** agent.
2. Activate the `frappe-hld-lld-design` skill.
3. Generate:
   - Entity-Relationship Diagram (Mermaid `erDiagram`) with exact field types, primary keys, and foreign keys.
   - Class hierarchy (Mermaid `classDiagram`) with method signatures and argument types.
   - State transition tables with conditions and side-effects.
   - Exact API schemas (Request headers, parameters, body JSON, and response formats).
