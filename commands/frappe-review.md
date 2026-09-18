# /frappe:review

**Purpose**: Run fresh-context code review on Frappe code to detect anti-patterns, performance bottlenecks, and transaction bugs.

## Usage
`/frappe:review [path/to/file or git diff]`

## Execution Workflow
1. Invoke the **frappe-code-reviewer** agent.
2. Check for:
   - `frappe.db.commit()` inside controller events.
   - N+1 queries (`frappe.get_doc` in loops).
   - Direct DOM modifications in client scripts.
   - Unindexed fields used in heavy filters.
   - Untranslated strings missing `_("...")`.
3. Provide line-numbered findings with specific remediation diffs.
