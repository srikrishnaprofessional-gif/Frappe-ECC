---
name: frappe-bench
description: Use the bench CLI to develop and operate Frappe - sites, apps, migrate, build, run, backups, config, logs, and fixing common errors (redis not running, missing module, migrate failures, assets not updating). Use when running or troubleshooting any bench command.
---

# bench

Run bench from the bench directory (the one with `apps/`, `sites/`, `env/`).

## Everyday commands

| Task | Command |
|---|---|
| Start dev servers (web, workers, redis, watch) | `bench start` |
| New site | `bench new-site <site> --admin-password <pw> [--db-root-password <pw>]` |
| Get an app from git or a local path | `bench get-app <url-or-path> [--branch main]` |
| Link a local app without copying | `bench get-app --soft-link <path>` |
| Install / uninstall on a site | `bench --site <site> install-app <app>` / `uninstall-app <app>` |
| Apply schema, patches, fixtures | `bench --site <site> migrate` |
| Rebuild JS/CSS | `bench build --app <app>` |
| Clear caches | `bench --site <site> clear-cache` |
| Python shell with site loaded | `bench --site <site> console` |
| Run a function | `bench --site <site> execute <dotted.path> --kwargs "{'a': 1}"` |
| Run tests | `bench --site <site> run-tests --app <app>` (needs `allow_tests`) |
| Developer mode (DocType edits write JSON) | `bench --site <site> set-config developer_mode 1` |
| Backup with files | `bench --site <site> backup --with-files` |
| Restore | `bench --site <site> restore <sql.gz> --with-public-files <tar> --with-private-files <tar>` |
| Default site | `bench use <site>` |
| Scheduler | `bench --site <site> enable-scheduler` / `scheduler status` |
| Logs | `logs/web.log`, `logs/worker.error.log`, `sites/<site>/logs/` |

Use `bench --site <site> ...` explicitly in scripts; don't rely on `bench use`.

## Development loop for an app

```bash
bench get-app --soft-link ~/code/clinic_management     # or frappe-ecc verify does this for you
bench --site dev.localhost install-app clinic_management
bench --site dev.localhost set-config developer_mode 1
bench start                                            # in another terminal
# edit code; Python reloads on the next request in dev; JSON changes need:
bench --site dev.localhost migrate
```

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `redis.exceptions.ConnectionError` / `Connection refused ...:13000` | Redis for this bench isn't running. `bench start`, or `redis-server config/redis_cache.conf` and `redis_queue.conf` |
| `ModuleNotFoundError: No module named '<app>'` | App not installed in the bench env. `./env/bin/pip install -e apps/<app>` or `bench setup requirements` |
| `App <app> not in apps.txt` / not found on install | App missing from `sites/apps.txt`. Re-run `bench get-app`, or add the line |
| Migrate: `DocType X not found` for a Link/Table | The target DocType is in an app not installed on the site, or it's defined later. Install the app, or check `required_apps` |
| Migrate: `Fieldname ... conflicting with meta object` | A fieldname equals a Document method. Rename the field |
| Changes to JS not visible | `bench build --app <app>` and hard-refresh; check `bench watch` is running |
| Changes to hooks.py not applied | `bench --site <site> clear-cache`; `bench restart` in production |
| `Access denied for user` on new-site | Wrong MariaDB root password; pass `--db-root-password` |
| Tests say "Testing is disabled" | `bench --site <site> set-config allow_tests true` |
| Scheduled jobs never run | `bench --site <site> scheduler status`; enable it and make sure workers run |

## Production notes

- `bench setup production <user>` configures supervisor and nginx; `bench restart` restarts workers.
- Update: `bench update --pull --patch --build` (or per app: `git pull`, `bench --site all migrate`, `bench build`, `bench restart`).
- Always take a backup before migrate in production.
- Frappe Cloud and the official `frappe_docker` images are the supported hosted and container setups.
