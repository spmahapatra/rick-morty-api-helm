---
description: Propose a new OpenSpec change with complete planning artifacts
agent: general
---

# OpenSpec Propose Command

Create a new OpenSpec change with proposal, specs, design, and tasks artifacts ready for implementation.

## What This Does

1. Understand what you want to build or change
2. Load project context and existing specs
3. Create a new OpenSpec change directory
4. Generate proposal.md (Why, What Changes, Capabilities, Impact)
5. Generate specs files (Requirements with scenarios)
6. Generate design.md (Technical decisions and trade-offs)
7. Generate tasks.md (Implementation checklist with verification)

## How to Use

Type /opsx-propose followed by a description:

/opsx-propose
/opsx-propose add user authentication
/opsx-propose refactor database layer

Describe what you want to build. The workflow will ask clarifying questions and generate all planning artifacts.

## Expected Outcomes

- Complete proposal document with business justification
- Detailed specifications with testable requirements
- Technical design with architectural decisions
- 31 implementation tasks with verification criteria
- Ready for review or implementation

Use this to formalize and plan a new feature or change before implementation begins.
