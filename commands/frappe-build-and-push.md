---
description: Build a customized application on the Frappe framework and push it directly to Git.
---

# /frappe:build-and-push

Build a complete, customized application on the Frappe framework and push the entire codebase to a remote Git repository.

## Usage
```
/frappe:build-and-push [app_name] --prompt "[requirements]" --repo "[git_repo_url]" [--token "[git_token]"]
```

## Examples
```
/frappe:build-and-push clinic_ops --prompt "Clinic appointment booking, patient medical records, vitals tracking, and prescription billing" --repo "https://github.com/myorg/clinic_ops.git"
/frappe:build-and-push fleet_manager --prompt "Vehicle dispatch, GPS odometer tracking, fuel expense logs, and maintenance alerts" --repo "git@github.com:myorg/fleet_manager.git"
```

## Description
Invokes `frappe-custom-app-git-builder` to:
1. Scaffold the complete modern Frappe custom application directory structure (`pyproject.toml`, `hooks.py`, `modules.txt`, `patches.txt`).
2. Synthesize complete DocType schemas, Python controllers with lifecycle methods, Desk client scripts, whitelisted REST APIs, and seed fixtures.
3. Author production GitHub Actions CI/CD workflows and Docker configurations.
4. Execute pre-commit security audits via Frappe Shield.
5. Initialize local Git version control, stage all assets, author semantic conventional commits, and push directly to the designated Git repository (`main` branch) with semantic version tags.
