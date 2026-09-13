---
description: Synchronize changes with upstream specs and validate consistency
agent: general
---

# OpenSpec Sync Command

Synchronize OpenSpec changes with upstream or central capability specifications and validate consistency.

## What This Does

1. Compare local changes with upstream specs
2. Identify conflicts or inconsistencies
3. Validate all capabilities are accounted for
4. Merge upstream changes if applicable
5. Resolve conflicts
6. Generate sync report

## How to Use

Type /opsx-sync with optional parameters:

/opsx-sync
/opsx-sync rick-morty-api-initial-spec
/opsx-sync --validate

The workflow will check synchronization status and resolve issues.

## Expected Outcomes

- Changes synchronized with upstream
- Conflicts resolved
- Consistency validated
- Sync report generated
- Ready for next phase

Use this when working with shared or upstream capability repositories.
