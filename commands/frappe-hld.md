# /frappe:hld

**Purpose**: Generate a comprehensive High-Level Design (HLD) document with Mermaid C4 architecture diagrams, integration topologies, and scaling strategy.

## Usage
`/frappe:hld "<system or feature description>"`

## Execution Workflow
1. Invoke the **frappe-hld-architect** agent.
2. Activate the `frappe-hld-lld-design` skill.
3. Generate:
   - System Context & C4 Container Architecture Diagram (Mermaid).
   - Component boundaries and data flow (synchronous REST vs asynchronous RQ queues).
   - Non-functional requirements (SLA, caching with Redis, multi-tenant bench topology).
   - Infrastructure, reverse proxy (Nginx), and security architecture.
