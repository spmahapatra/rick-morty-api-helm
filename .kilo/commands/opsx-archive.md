---
description: Archive a completed change and create durable capability specs
agent: general
---

# OpenSpec Archive Command

Archive a completed OpenSpec change and promote artifacts to durable capability specifications.

## What This Does

1. Review the completed change artifacts
2. Validate all implementation is finished
3. Move proposal artifacts to openspec/specs/
4. Archive change to openspec/changes/archive/
5. Update main project capabilities
6. Generate durable spec.md files
7. Clean up temporary planning artifacts

## How to Use

Type /opsx-archive with the change name:

/opsx-archive
/opsx-archive rick-morty-api-initial-spec
/opsx-archive add-authentication

The workflow will guide you through archival and validate completion.

## Expected Outcomes

- Change artifacts archived for historical reference
- Capability specs created in openspec/specs/
- Project capabilities inventory updated
- Implementation code validated
- Ready for next cycle of changes

Use this after implementation is complete and ready to formalize as project capabilities.
