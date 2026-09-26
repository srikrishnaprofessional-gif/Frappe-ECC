# /frappe:test

**Purpose**: Scaffold test cases and execute Frappe tests using `FrappeTestCase` and `bench run-tests`.

## Usage
`/frappe:test "<DocType Name>" [--run]`

## Execution Workflow
1. Invoke the **frappe-tdd-guide** agent.
2. Generate comprehensive unit tests in `test_<doctype>.py`:
   - Basic creation and autoname assertion.
   - Required fields and validation edge cases.
   - Submission and cancellation lifecycles.
   - Permission denials.
3. If `--run` is supplied, execute `bench --site <site> run-tests --app <app> --doctype "<DocType>"`.
