---
description: Add one or more DocTypes to an existing Frappe app from a description, then migrate and test
argument-hint: "<description of the DocType(s)> [app path]"
---
Add DocTypes to an existing Frappe app: $ARGUMENTS

1. Find the app (argument, current directory, or ask). Read its `hooks.py`, `modules.txt` and existing
   DocTypes so new ones fit: reuse existing masters through Link fields and match naming style.
2. Following ${CLAUDE_PLUGIN_ROOT}/skills/frappe-app-spec/SKILL.md and ${CLAUDE_PLUGIN_ROOT}/skills/frappe-doctypes/SKILL.md, write a spec with
   the app's `app` block (name, title, publisher, email from hooks.py) and only the new DocTypes,
   in an existing or new module.
3. `frappe-ecc validate <spec>`, fix errors, show the user the DocTypes and fields, and confirm.
4. `frappe-ecc add-doctypes <spec> <app_path>`.
5. `bench --site <site> migrate` on a development site, then run the new DocTypes' tests
   (`bench --site <site> run-tests --app <app> --doctype "<name>"`). Report the results.
