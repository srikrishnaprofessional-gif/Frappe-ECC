---
name: frappe-wireframing-prototyping
description: Rapid wireframing and clickable interactive HTML prototyping for Frappe Desk forms, workspace dashboards, and custom portal workflows.
---

# Frappe Wireframing & Interactive Prototyping

## 1. Visual ASCII Wireframing Rules
ASCII wireframes provide instant structural alignment during feature planning.

### Desk Form View Wireframe Template
```
=================================================================================
 [<- Assets]  AST-2026-00108  [Submitted (Green)]            [Actions v]  [Menu]
=================================================================================
 SECTION 1: ASSET IDENTIFICATION
  Asset Name:      [ MacBook Pro M3 Max               ]
  Serial No:       [ MBP-M3-99201           ] (Unique)
  Category:        [ IT Laptops & Workstations      v ]
  Status:          (o) In Use   ( ) Under Maintenance   ( ) Decommissioned
---------------------------------------------------------------------------------
 SECTION 2: HARDWARE ALLOCATION
  Assigned To:     [ EMP-0042 - Sarah Jenkins       v ]
  Department:      [ Cloud Engineering                ]
  Handover Date:   [ 2026-06-01 ]   Warranty Expiry: [ 2029-06-01 ]
---------------------------------------------------------------------------------
 SECTION 3: PERIPHERALS & ACCESSORIES (Child Table)
  +---+---------------------------+---------------+--------------+------------+
  | # | Item Description          | Serial Number | Cost (USD)   | Action     |
  +---+---------------------------+---------------+--------------+------------+
  | 1 | Studio Display 27in 5K    | SD-5K-8812    | $ 1,599.00   | [Remove]   |
  | 2 | Magic Trackpad 3 Black    | TP-3B-1192    | $   149.00   | [Remove]   |
  +---+---------------------------+---------------+--------------+------------+
  [ + Add Row ]                                    Total Value:  $ 1,748.00
=================================================================================
```

---

## 2. Interactive Clickable HTML Prototype Pattern
Generate single-file prototypes using Tailwind CSS and Vue 3 (CDN) that simulate Frappe Desk behavior:
- Document save and status updates.
- Real-time child table calculations.
- Native-like modal dialog popups (`frappe.ui.Dialog` simulation).

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Frappe Desk Prototype</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body class="bg-gray-50 text-gray-800">
  <div id="app" class="max-w-5xl mx-auto p-8">
    <div class="bg-white border rounded-lg shadow-sm p-6">
      <div class="flex justify-between items-center border-b pb-4 mb-6">
        <div>
          <span class="text-xs text-gray-500 uppercase font-semibold">Asset Item</span>
          <h1 class="text-2xl font-bold text-gray-900">{{ doc.name }}</h1>
        </div>
        <div class="flex items-center space-x-3">
          <span :class="statusBadgeClass" class="px-3 py-1 rounded-full text-xs font-semibold">
            {{ doc.status }}
          </span>
          <button @click="openDialog" class="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded">
            Actions
          </button>
        </div>
      </div>
      <!-- Interactive Form Body -->
    </div>
  </div>
</body>
</html>
```
