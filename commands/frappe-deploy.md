---
description: Generate production-ready GitHub Actions CI/CD workflows, multi-stage Dockerfile, and compose.yaml for automated testing and deployment.
---

# /frappe:deploy

Autonomous CI/CD and containerized deployment generator for Frappe Framework apps.

## Usage
```
/frappe:deploy "<app_name>" [--target github-actions|docker|frappe-cloud]
```

## Description
Invokes `frappe-release-devops` to deliver automated `.github/workflows/ci.yml` (running MariaDB, Redis, bench tests, and Frappe Shield security gate), Dockerfiles, and compose configurations.
