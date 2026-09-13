---
description: Apply a change by implementing tasks and verifying completion
agent: general
---

# OpenSpec Apply Command

Track and implement an OpenSpec change by working through its tasks in order.

## What This Does

1. Check the current change status and task list
2. Load tasks.md for implementation work
3. Execute each task group in dependency order
4. Verify completion criteria for each task
5. Run tests and validation steps
6. Update task status as items are completed
7. Report progress and identify any blockers

## How to Use

Type /opsx-apply with an optional change name:

/opsx-apply
/opsx-apply rick-morty-api-initial-spec
/opsx-apply add-authentication

The workflow will locate your change and guide you through implementation.

## Expected Outcomes

- All planning artifacts reviewed and validated
- Each task group executed and verified
- Tests passing
- Integration verified
- Ready for archival and production deployment

Use this after proposal artifacts are finalized and ready for implementation.
