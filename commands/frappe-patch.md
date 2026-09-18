# /frappe:patch

**Purpose**: Generate a safe, idempotent database migration patch and register it in `patches.txt`.

## Usage
`/frappe:patch "<patch description>" --version "<vX_Y>"`

## Execution Workflow
1. Invoke the **frappe-migration-patcher** agent.
2. Create the patch script in `<app>/patches/<version>/<patch_name>.py`.
3. Implement idempotent `execute()` function with `frappe.reload_doc()` and existence checks.
4. Add the entry to `<app>/patches.txt`.
5. Guide the developer on testing with `bench --site <site> migrate`.
