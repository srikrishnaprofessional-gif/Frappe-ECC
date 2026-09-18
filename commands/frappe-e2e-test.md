# /frappe:e2e-test

**Purpose**: Generate Playwright automated browser test scripts and API regression tests for Frappe Desk workflows.

## Usage
`/frappe:e2e-test "<DocType or Workflow Name>" [--runner playwright|cypress]`

## Execution Workflow
1. Invoke the **frappe-automated-tester** agent.
2. Activate the `frappe-qa-testing-automation` skill.
3. Generate:
   - Playwright test script simulating user login, navigation, form data entry, and button clicks.
   - Status badge and alert message assertions.
   - GitHub Actions CI workflow to run headless tests on every push.
