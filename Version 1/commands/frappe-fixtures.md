---
description: Synthesize realistic, domain-accurate seed fixtures, master catalog records, and relational test data for immediate application testing.
---

# /frappe:fixtures

Autonomous seed data and fixture synthesis for Frappe Framework DocTypes.

## Usage
```
/frappe:fixtures "<DocType Name>" [--count 10]
```

## Description
Invokes `frappe-data-synthesizer` to generate realistic, domain-specific seed fixtures (`fixtures/<doctype>.json`) and QA mock records (`qa/test_data.json`) with relational integrity and edge-case values.
