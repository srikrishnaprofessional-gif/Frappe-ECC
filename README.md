# Frappe ECC

This repository holds two versions of Frappe ECC.

| Folder | What it is | Status |
|---|---|---|
| [`Version 2/`](Version%202/) | The current product: a Claude Code plugin (skills, agents, commands, Shield hook) plus the `frappe-ecc` CLI that validates app specs, generates installable Frappe apps, verifies them on a real bench, and scans code for security mistakes. | **Current. Use this.** |
| [`Version 1/`](Version%201/) | The original release (v2.x, up to commit `817dac5`), kept unchanged for reference. | Archived. It does not generate or install a real Frappe app: its prompt builder asks Claude for one DocType as JSON and stores simulated records in SQLite, and the other agents return fixed template text. See `Version 2/CHANGELOG.md`. |

## Install (Version 2)

```bash
claude plugin marketplace add srikrishnaprofessional-gif/Frappe-ECC
claude plugin install frappe-ecc@frappe-ecc
```

Or from a clone: `cd "Version 2" && ./install.sh`.

Full documentation: [`Version 2/README.md`](Version%202/README.md).
