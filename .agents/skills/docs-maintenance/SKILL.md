---
name: docs-maintenance
description: Instructions for keeping project documentation, architecture specifications, progress logs, and viva Q&A in sync after every coding task.
---

# Documentation Maintenance Workflow

## When to Use This Skill
Activate this skill at the end of **every single coding task or feature modification** before marking work as complete.

---

## Mandatory Documentation Update Checklist

1. **`docs/09_PROGRESS_LOG.md`:**
   - Add a new dated session entry detailing:
     - Features completed.
     - Files modified or created.
     - Verification steps performed.
     - Current operational server status.
     - Next upcoming task.

2. **`docs/01_FEATURES.md`:**
   - Update the status column (`Done`, `In progress`, `Todo`) for any affected feature IDs.

3. **`docs/04_URLS_AND_VIEWS.md`:**
   - Update if any URL patterns, view names, or access requirements were added or changed.

4. **`docs/03_DATABASE_SCHEMA.md`:**
   - Update if any models, fields, constraints, or database indexes were introduced or altered.

5. **`docs/10_VIVA_QA.md`:**
   - Append any new technical or algorithmic questions that an examiner might ask about the newly implemented feature.
