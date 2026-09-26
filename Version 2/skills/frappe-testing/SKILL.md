---
name: frappe-testing
description: Write and run tests for Frappe apps - IntegrationTestCase (v16+) / FrappeTestCase (v15), test data with factories, bench run-tests options, what rolls back and what doesn't, permission and API tests, and CI. Use when adding tests, fixing failing tests, or proving a Frappe feature works.
---

# Testing Frappe apps

Tests run inside a real site against its database. Use a throwaway site, because tests
write data:

```bash
bench new-site test.localhost --admin-password admin   # once
bench --site test.localhost install-app <app>
bench --site test.localhost set-config allow_tests true
bench --site test.localhost run-tests --app <app>
```

Narrow the run while developing:

```bash
bench --site test.localhost run-tests --app <app> --doctype "Clinic Appointment"
bench --site test.localhost run-tests --module clinic_management.clinic.doctype.clinic_appointment.test_clinic_appointment
bench --site test.localhost run-tests --module <module> --test test_cancel_releases_slot
bench --site test.localhost run-tests --app <app> --failfast
```

`frappe-ecc verify <app_path> --site <site>` runs install, migrate and the full suite in one go
and reports real exit codes. Only call something tested after a run you watched pass.

## Base class (works on v15 and v16+)

```python
import frappe

try:
	from frappe.tests import IntegrationTestCase           # v16+
except ImportError:
	from frappe.tests.utils import FrappeTestCase as IntegrationTestCase  # v15
```

What rolls back: the database transaction is rolled back **once, after the whole test class**
(`addClassCleanup(_rollback_db)`), not after each test. Records created in one test are visible
to later tests in the same class. So:
- give unique values (e.g. `frappe.generate_hash(length=8)`) to fields that must be unique;
- create shared prerequisites in `setUpClass`, and per-test data inside each test;
- don't rely on test order.

Code that calls `frappe.db.commit()` makes its writes permanent, even in tests. That is one more
reason not to commit in controllers.

## Test data

Generated apps include `<app>/factories.py`:

```python
from clinic_management.factories import make_doc

patient = make_doc("Clinic Patient", patient_name="Asha")          # fills other mandatory fields
appt = make_doc("Clinic Appointment", patient=patient.name, submit=True)
settings = make_doc("Clinic Settings", clinic_name="Test Clinic")   # singles are saved, not inserted
```

`make_doc` fills mandatory fields with valid values and creates linked records from the same app.
For links to other apps' DocTypes, it reuses an existing record, or tells you to create one in `setUp`.

## What to test

For each DocType with logic, test the rule, not the framework:

```python
class TestClinicAppointment(IntegrationTestCase):
	def test_past_date_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			make_doc("Clinic Appointment", appointment_date="2000-01-01")

	def test_submit_updates_last_visit(self):
		appt = make_doc("Clinic Appointment", submit=True)
		self.assertEqual(
			frappe.db.get_value("Clinic Patient", appt.patient, "last_visit"), appt.appointment_date
		)

	def test_cancel_reverts(self):
		appt = make_doc("Clinic Appointment", submit=True)
		appt.cancel()
		self.assertEqual(appt.docstatus, 2)
```

Also cover:
- **Permissions**: `frappe.set_user(user)` then assert `frappe.PermissionError`; reset to
  "Administrator" in `finally`.
- **Whitelisted APIs**: call the Python function directly with the test user set; check
  permission denial and bad input.
- **Scheduled jobs and hooks**: call the function directly and assert its effect.
- **Background jobs**: `frappe.enqueue(..., now=True)` or call the job function directly.
- **Reports**: call `execute(filters)` and assert on columns and rows.

Useful assertions and helpers:
- `self.assertRaises(frappe.ValidationError | frappe.PermissionError | frappe.DuplicateEntryError, ...)`
- `self.assertDocumentEqual(expected_dict, doc)` compares only the keys you give.
- `frappe.flags.in_test` is True while tests run.

## Browser (UI) tests

Frappe's own UI tests use Cypress (`bench --site <site> run-ui-tests <app>`). For app-level
end-to-end checks, Playwright against `bench start` works well: log in via `/login`, open
`/app/<doctype-route>/new`, fill fields by `[data-fieldname="..."] input`, press Ctrl+S, and
assert on the saved document through the REST API. Keep UI tests few and focused on critical flows.

## CI

`frappe-ecc new --ci` adds `.github/workflows/ci.yml`, which starts MariaDB and Redis, runs
`bench init` for the Frappe branch in the matrix, installs the app on a new site and runs
`bench run-tests --app <app>` on Frappe v15 (Python 3.11, Node 18) and v16 (Python 3.14, Node 24).
Drop a matrix row if you don't support that version.
