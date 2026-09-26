---
description: Write a data migration patch for a schema or data change
argument-hint: "<what changed and what data must move>"
---
Write a patch for: $ARGUMENTS

Follow ${CLAUDE_PLUGIN_ROOT}/skills/frappe-patches/SKILL.md: choose pre_model_sync or post_model_sync, make it
idempotent, register it in patches.txt, and test it by running `bench --site <dev-site> migrate`
on a site that has data in the old shape. Report what the patch does and the before/after check.
