---
description: Train and deploy machine learning models on Frappe data for demand forecasting and risk scoring.
---

# /frappe:predict

Train and deploy machine learning models on Frappe data for demand forecasting and risk scoring.

## Usage
```
/frappe:predict [target_metric] [doctype_source]
```

## Examples
```
/frappe:predict 'return_delay_risk' 'Equipment Loan'
```

## Description
Invokes `frappe-predictive-ai-forecaster` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
