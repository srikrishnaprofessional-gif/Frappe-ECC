# /frappe:manual-qa

**Purpose**: Generate a comprehensive manual test plan, exploratory test charter, edge-case test matrix, and QA sign-off checklist.

## Usage
`/frappe:manual-qa "<DocType or Feature Name>"`

## Execution Workflow
1. Invoke the **frappe-manual-qa** agent.
2. Activate the `frappe-qa-testing-automation` skill.
3. Generate:
   - Structured test case matrix (Test ID, Title, Pre-conditions, Steps, Input Data, Expected Results).
   - Boundary & edge-case scenarios (empty inputs, zero values, date limits, unicode characters).
   - Role-permission verification scenarios (access checks across all configured roles).
   - Release audit QA sign-off template.
