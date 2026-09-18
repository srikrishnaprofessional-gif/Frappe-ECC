# /frappe:bench

**Purpose**: Execute and troubleshoot bench operations, site creation, migrations, and developer server issues.

## Usage
`/frappe:bench [command or error description]`

## Execution Workflow
1. Invoke the **frappe-bench-devops** agent.
2. If given an error (e.g., Redis down, migration conflict, port in use), diagnose root cause and output exact remediation commands.
3. If given a task (e.g., setup multi-tenancy, install app, export fixtures), produce verified bench command sequence.
