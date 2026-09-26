---
description: Set up CI, Docker or production deployment for a Frappe app
argument-hint: "<ci | docker | production | upgrade> [details]"
---
Deployment task: $ARGUMENTS

Use the **frappe-devops** agent. Confirm with the user before anything that touches production,
deletes data or restarts shared services. Report the files created and commands run with results.
