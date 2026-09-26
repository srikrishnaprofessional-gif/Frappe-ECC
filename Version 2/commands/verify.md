---
description: Install, migrate and test a Frappe app on a real bench site and report actual results
argument-hint: "[app path] [--site <site>] [--bench <bench>]"
---
Verify a Frappe app on a real site: $ARGUMENTS

1. Work out the app path (default: the app in the current directory), the bench (current directory
   upwards) and the site. The site must be a throwaway or development site because tests write
   data. Ask if unclear, and never use a production site.
2. Run `frappe-ecc verify <app_path> --bench <bench> --site <site> --report verify-report.json`.
3. If preflight fails (site missing, redis down), show the user the exact fix from the output.
4. If a step fails, show the failing step's output, then diagnose with the **frappe-debugger**
   agent if the user wants it fixed.
5. Report the step table and the test counts exactly as printed. `VERIFIED` means every step
   passed and tests ran; anything else is not verified.
