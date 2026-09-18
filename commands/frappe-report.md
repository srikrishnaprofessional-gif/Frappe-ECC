# /frappe:report

**Purpose**: Scaffold a Frappe Script Report with paired Python query execution and JS filter definition.

## Usage
`/frappe:report "<Report Name>" --ref-doctype "<DocType>"`

## Execution Workflow
1. Invoke the **frappe-report-builder** agent.
2. Generate `<report_name>.json` setting `report_type: "Script Report"`.
3. Generate `<report_name>.py` with `execute(filters)` returning `columns, data, None, chart, report_summary`.
4. Generate `<report_name>.js` with interactive Desk filters.
