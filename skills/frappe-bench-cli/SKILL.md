---
name: frappe-bench-cli
description: Complete Bench CLI command reference, site management, troubleshooting, multi-site configuration, and developer environment commands.
---

# Frappe Bench CLI Master Reference

## 1. Core Development Commands
```bash
# Start bench services (Procfile: web, worker, schedule, redis)
bench start

# Create a new custom app
bench new-app <app_name>

# Install app on site
bench --site <site_name> install-app <app_name>

# Uninstall app from site
bench --site <site_name> uninstall-app <app_name>

# Run database schema migrations
bench --site <site_name> migrate

# Clear Redis cache
bench --site <site_name> clear-cache

# Build JS/CSS assets
bench build --app <app_name>
```

## 2. Interactive Console & Script Execution
```bash
# Launch interactive IPython shell loaded with frappe site context
bench --site <site_name> console

# Execute a Python function directly from CLI
bench --site <site_name> execute your_app.tasks.sync_hardware_telemetry

# Run unit tests
bench --site <site_name> run-tests --app <app_name>
```

## 3. Database & Site Administration
```bash
# Open MariaDB/Postgres CLI with credentials pre-loaded
bench --site <site_name> mariadb

# Backup site database and private files
bench --site <site_name> backup --with-files

# Restore database from backup
bench --site <site_name> restore /path/to/database.sql.gz

# Drop site completely
bench drop-site <site_name> --root-password <root_pass>
```

## 4. Troubleshooting & Diagnostics
```bash
# Run system doctor
bench doctor

# Show worker queues
bench worker --queue short,default,long
```
