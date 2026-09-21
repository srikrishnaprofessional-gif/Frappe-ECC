---
description: Configure automated OCR and vision extraction pipelines for scanned paper forms, receipts, and invoices.
---

# /frappe:ocr

Configure automated OCR and vision extraction pipelines for scanned paper forms, receipts, and invoices.

## Usage
```
/frappe:ocr [doctype_target] [document_path]
```

## Examples
```
/frappe:ocr 'Equipment Loan' uploads/signed_handover_slip.pdf
```

## Description
Invokes `frappe-ocr-document-ingestor` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
