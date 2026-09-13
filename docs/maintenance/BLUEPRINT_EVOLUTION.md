# Master Project Blueprint - Version Control & Update Procedures

**Document Version:** 1.0.0  
**Last Updated:** 2026-09-13  
**Status:** Active Living Document

---

## Table of Contents

1. [Overview](#overview)
2. [Version Scheme](#version-scheme)
3. [Change Management Process](#change-management-process)
4. [Maintenance Schedule](#maintenance-schedule)
5. [Evolution Tracking](#evolution-tracking)
6. [Update Procedures](#update-procedures)
7. [Documentation Standards](#documentation-standards)
8. [Feedback Loop](#feedback-loop)
9. [Release Notes](#release-notes)

---

## Overview

The Master Project Blueprint v1.0 is a **living document** that evolves based on:
- ✅ Lessons learned from new projects
- ✅ Emerging best practices in software engineering
- ✅ Team feedback and recommendations
- ✅ Technology and framework updates
- ✅ Security and compliance changes

This document defines how the blueprint is versioned, updated, and communicated to the team.

### Blueprint Location
- **Main Document**: `docs/maintenance/MASTER_PROJECT_BLUEPRINT.md`
- **Changelog**: `docs/maintenance/BLUEPRINT_CHANGELOG.md`
- **This Document**: `docs/maintenance/BLUEPRINT_EVOLUTION.md`
- **Onboarding**: `docs/guides/ONBOARDING.md`

### Governance
- **Maintainer**: Development Lead / Architecture Team
- **Review Cycle**: Quarterly (Q1, Q2, Q3, Q4)
- **Breaking Changes**: Require team consensus
- **Minor Updates**: Single maintainer approval

---

## Version Scheme

### Semantic Versioning (SemVer)

The blueprint follows **Semantic Versioning: MAJOR.MINOR.PATCH**

#### Major Version (X.0.0)
- **Trigger**: Significant architectural changes, new principles, restructured standards
- **Impact**: **Breaking changes** - projects may need updates to conform
- **Example**: 1.0.0 → 2.0.0 (fundamental restructuring)
- **Notification**: Team-wide announcement required
- **Migration Path**: Document compatibility guide
- **Timeline**: Every 18-24 months (estimated)

#### Minor Version (1.X.0)
- **Trigger**: New features, new standards, new patterns, new tools
- **Impact**: **Additive** - existing projects still conform, new projects get improvements
- **Example**: 1.0.0 → 1.1.0 (add new logging pattern)
- **Notification**: Team notification, update existing projects optionally
- **Timeline**: Every 3-6 months (estimated)

#### Patch Version (1.0.X)
- **Trigger**: Bug fixes, clarifications, documentation improvements, typo fixes
- **Impact**: **Non-breaking** - no action required
- **Example**: 1.0.0 → 1.0.1 (fix documentation typo)
- **Notification**: Commit message only, no team announcement
- **Timeline**: As needed

### Version History

| Version | Release Date | Type | Summary |
|---------|-------------|------|---------|
| 1.0.0 | 2026-09-13 | Release | Initial Blueprint v1.0 with 8 core principles, standardized structure, automation scripts |
| 1.0.1 | TBD | Patch | (Reserved for future patches) |
| 1.1.0 | TBD | Minor | (Reserved for future minor updates) |
| 2.0.0 | TBD | Major | (Reserved for future major revisions) |

---

## Change Management Process

### Phase 1: Observation (Ongoing)

**Timeline**: Continuous

**Trigger Events**:
- ✅ Patterns emerge from multiple new projects
- ✅ Team identifies repeated pain points
- ✅ Best practices or standards become outdated
- ✅ New tools or frameworks offer better solutions
- ✅ Security or compliance requirements change

**Activities**:
```
→ Observe patterns in project execution
→ Document suggested improvements
→ Collect feedback from developers
→ Research industry best practices
→ Evaluate new tools/frameworks
```

**Output**: Improvement proposals in `docs/dev-notes/observations/`

**Example**:
```markdown
# Observation: API Versioning Pattern Needed

## Issue
Multiple projects implementing different API versioning strategies.

## Suggested Pattern
- URL-based versioning: /api/v1/users
- Header-based fallback for backwards compatibility
- Deprecation timeline in API responses

## Projects Affected
- rick-morty-api (current)
- user-service (planned)
- payment-service (planned)
```

### Phase 2: Proposal (Review)

**Timeline**: 1-2 weeks per proposal

**Trigger**: Observation reaches sufficient detail and consensus

**Activities**:
```
→ Document detailed specification
→ Create implementation examples
→ Review with architecture team
→ Identify breaking changes
→ Plan migration path if needed
```

**Output**: Proposal document in `docs/maintenance/proposals/`

**Approval Gate**:
- ✅ Architecture team consensus (for major changes)
- ✅ Single maintainer approval (for minor changes)
- ✅ No blocking concerns

**Example Document Structure**:
```markdown
# Proposal: Add Structured Request Logging Pattern

## Problem Statement
[Describe the problem this solves]

## Proposed Solution
[Detailed solution with examples]

## Implementation Example
[Code showing the new pattern]

## Migration Path
[How existing projects adopt this]

## Success Criteria
[Measurable indicators of success]

## Timeline
[When this will be adopted]
```

### Phase 3: Testing (Pilot)

**Timeline**: 1-3 months

**Trigger**: Proposal approved

**Activities**:
```
→ Implement in pilot project(s)
→ Gather feedback from developers
→ Measure effectiveness
→ Identify edge cases
→ Refine based on experience
```

**Pilot Projects**:
- New projects are ideal pilots (no legacy code)
- Choose 1-3 projects based on relevance
- Document challenges and solutions

**Output**: Pilot report with recommendations

**Example Report**:
```markdown
# Pilot Report: API Versioning Pattern

## Pilot Project
- rick-morty-api (User service endpoints)

## Duration
- Start: 2026-09-15
- End: 2026-10-15

## Results
- ✅ Pattern easy to implement
- ✅ Backwards compatibility works well
- ⚠️ Documentation needs enhancement
- ✅ Team feedback positive

## Recommendations
1. Adopt pattern in blueprint v1.1.0
2. Update documentation with examples
3. Create scaffold template for API versioning
```

### Phase 4: Formalization (Decision)

**Timeline**: 1 week

**Trigger**: Pilot successful, ready for adoption

**Activities**:
```
→ Update MASTER_PROJECT_BLUEPRINT.md
→ Update BLUEPRINT_CHANGELOG.md
→ Update scaffold-project.sh if needed
→ Update validate-project.sh if needed
→ Communicate to team
```

**Update Checklist**:
- [ ] Blueprint document updated
- [ ] Changelog entries created
- [ ] Scaffold script updated (if applicable)
- [ ] Validation script updated (if applicable)
- [ ] Documentation examples updated
- [ ] Onboarding guide updated (if applicable)
- [ ] Pilot project documented
- [ ] Team notified
- [ ] Version bumped

**Communication Template**:
```markdown
# Blueprint Update: v1.0.0 → v1.1.0

## New Features
- ✨ Structured API versioning pattern added
- ✨ Request tracing correlation IDs improved

## What Changed
- Section 4.1: API Endpoints
- Section 5.2: Error Handling

## For Existing Projects
- No required action
- Recommended: Adopt new pattern for new endpoints

## For New Projects
- Scaffold includes API versioning by default
- See docs/api/VERSIONING.md for details

## Questions?
- Review: docs/maintenance/BLUEPRINT_CHANGELOG.md
- Contact: architecture-team@company.com
```

### Phase 5: Evolution (Ongoing)

**Timeline**: Continuous

**Trigger**: Blueprint version released

**Activities**:
```
→ Monitor adoption in new projects
→ Collect feedback on effectiveness
→ Identify edge cases and refinements
→ Plan next iteration
→ Return to Phase 1: Observation
```

**Metrics**:
- Number of projects adopting new pattern
- Developer satisfaction feedback
- Issues/bugs found with new pattern
- Time to implement new pattern

---

## Maintenance Schedule

### Quarterly Review Cycle

**Schedule**: End of each quarter (Sep 13, Dec 31, Mar 31, Jun 30)

#### Q4 Review (Sep-Dec)
- **Date**: December 31
- **Activities**:
  - Review observation notes
  - Evaluate new projects' learnings
  - Assess technology changes
  - Plan Q1 updates
- **Deliverable**: Draft changelog for review

#### Q1 Review (Jan-Mar)
- **Date**: March 31
- **Activities**:
  - Implement approved changes
  - Test updates in new projects
  - Gather feedback
  - Document learnings
- **Deliverable**: Updated blueprint v1.X.0 or v2.0.0

#### Q2 Review (Apr-Jun)
- **Date**: June 30
- **Activities**:
  - Assess Q1 changes adoption
  - Monitor effectiveness metrics
  - Collect team feedback
  - Plan H2 improvements
- **Deliverable**: Recommendations document

#### Q3 Review (Jul-Sep)
- **Date**: September 30 (or current day)
- **Activities**:
  - Finalize H2 changes
  - Create comprehensive changelog
  - Update all documentation
  - Prepare team communication
- **Deliverable**: Blueprint v1.X.0 or v2.0.0 + changelog

### Ad-Hoc Updates

**Trigger**: Critical issues that can't wait for quarterly review
- Security vulnerabilities
- Breaking framework changes
- Critical bugs in patterns
- Compliance requirements

**Process**: Abbreviated version of Change Management Process
- Phase 1: Observation (1 day)
- Phase 2: Proposal (1 day)
- Phase 3: Testing (1-3 days, abbreviated)
- Phase 4: Formalization (1 day)
- Phase 5: Communication (immediate)

---

## Evolution Tracking

### Observation Log

**Location**: `docs/dev-notes/blueprint-evolution/observations.md`

**Format**:
```markdown
## Observation: [Title]

**Date**: YYYY-MM-DD
**Source**: [Project name, discussion, etc.]
**Status**: open, resolved, accepted, rejected

### Description
[What was observed]

### Related Projects
- project-1
- project-2

### Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

### Proposal Tracking

**Location**: `docs/maintenance/proposals/`

**Format**: `[DATE]-[TITLE]-[STATUS].md`

**Example**: `2026-09-15-api-versioning-proposal-draft.md`

**Statuses**:
- `draft` - In preparation
- `review` - Under team review
- `approved` - Ready for pilot
- `pilot` - In pilot phase
- `accepted` - Approved for blueprint
- `rejected` - Not approved
- `deprecated` - Previously accepted, now obsolete

### Change Log

**Location**: `docs/maintenance/BLUEPRINT_CHANGELOG.md`

**Format**: Keep-a-changelog standard

```markdown
## [1.1.0] - 2026-12-31

### Added
- Structured API versioning pattern (new)
- Request correlation ID propagation (enhanced)
- Service health check standards (new)

### Changed
- Logging structure simplified (breaking: v1.0.0 incompatible)
- Configuration inheritance improved (non-breaking)
- Documentation reorganized (non-breaking)

### Deprecated
- Legacy error handling pattern (will be removed in v2.0.0)

### Fixed
- Docker multi-stage build examples corrected
- .gitignore patterns clarified

### Security
- Added OWASP security scanning to CI/CD
- Hardened Dockerfile security defaults

[1.1.0]: https://github.com/...compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/...releases/tag/v1.0.0
```

---

## Update Procedures

### Step-by-Step: How to Update the Blueprint

#### Step 1: Prepare Update Environment
```bash
cd /path/to/rick-morty-api-helm/

# Create update branch
git checkout -b docs/update-blueprint-v1.1.0
git pull origin master
```

#### Step 2: Update Main Blueprint Document
```bash
# Edit main document
vi docs/maintenance/MASTER_PROJECT_BLUEPRINT.md

# Key sections to update:
# - Overview (update version)
# - Principles (add/modify if needed)
# - Directory Structure (if changed)
# - Development Standards (if changed)
# - Automation Scripts (if enhanced)
# - Implementation Checklist (if modified)
# - Appendix (update references)
```

**Checklist During Update**:
- [ ] Update version number at top
- [ ] Update "Last Updated" date
- [ ] Update status if changed (e.g., "Active Living Document")
- [ ] Add new sections with clear structure
- [ ] Update table of contents if sections changed
- [ ] Add cross-references to new sections
- [ ] Update quick reference at end
- [ ] Verify all code examples are current

#### Step 3: Update Changelog
```bash
vi docs/maintenance/BLUEPRINT_CHANGELOG.md

# Format:
# ## [1.1.0] - 2026-12-31
#
# ### Added
# - Feature 1
# - Feature 2
#
# ### Changed
# - Change 1
#
# ### Deprecated
# - Old pattern 1
#
# ### Fixed
# - Bug 1
```

#### Step 4: Update Scaffold Script (if needed)
```bash
# If adding new templates or structure
vi ~/.config/kilo/scripts/scaffold-project.sh

# Update:
# - Directory structure creation
# - Template generation
# - Configuration examples
# - Version number (SCRIPT_VERSION)
```

**Example**: Adding new docs category
```bash
# Add to REQUIRED_DIRS
docs/new-category/
docs/new-category/README.md

# Add generation function
generate_new_category() {
    mkdir -p "${base_path}/docs/new-category"
    cat > "${base_path}/docs/new-category/README.md" << 'EOF'
# New Category
...
EOF
}

# Call in create_directory_structure()
generate_new_category "$base_path" "$project_name"
```

#### Step 5: Update Validation Script (if needed)
```bash
vi ~/.config/kilo/scripts/validate-project.sh

# Update:
# - Required files list
# - Required directories list
# - Validation checks
# - Version number (SCRIPT_VERSION)
```

#### Step 6: Update Onboarding Guide
```bash
vi docs/guides/ONBOARDING.md

# Review and update:
# - Quick Start section
# - Project Structure section
# - Configuration section
# - Common Tasks section
# - Troubleshooting section
# - Any examples showing old patterns
```

#### Step 7: Update GitHub CI/CD Templates
```bash
# Review for currency
vi .github/workflows/ci.yml
vi .github/workflows/cd.yml

# Update:
# - Python versions
# - Dependency versions
# - Test commands
# - Deployment procedures
```

#### Step 8: Test Changes

**Test with Pilot Project**:
```bash
# Test scaffold script
~/.config/kilo/scripts/scaffold-project.sh \
  --name BlueprintV11Test \
  --type python \
  --path /tmp/kilo

# Test validation script
~/.config/kilo/scripts/validate-project.sh \
  --project /tmp/kilo/BlueprintV11Test

# Verify all checks pass
echo "Expected: All validation checks passed"
```

**Test with Existing Project**:
```bash
# Validate current project
~/.config/kilo/scripts/validate-project.sh \
  --project /home/localadmin/localwork/setupAppCreDepHelmPkg

# Should pass with same/higher validation level
```

#### Step 9: Create PR and Get Review

```bash
# Commit changes
git add docs/ .github/ ~/.config/kilo/scripts/

git commit -m "docs: update Master Project Blueprint to v1.1.0

- Add structured API versioning pattern
- Enhance request tracing with correlation IDs
- Add service health check standards
- Update scaffold and validation scripts
- Update onboarding documentation"

# Push to remote
git push origin docs/update-blueprint-v1.1.0

# Create PR on GitHub
# Add changelog summary to PR description
```

#### Step 10: Address Review Feedback

```bash
# Make requested changes
# Commit: git commit --amend (if minor)
# Or: new commit (if substantial)

# Push changes
git push origin docs/update-blueprint-v1.1.0

# Respond to reviewers
```

#### Step 11: Merge and Release

```bash
# After approval, merge via GitHub
# Delete feature branch
git branch -d docs/update-blueprint-v1.1.0

# Pull latest master
git pull origin master

# Tag version (if major/minor release)
git tag -a v1.1.0 -m "Master Project Blueprint v1.1.0"
git push origin v1.1.0
```

#### Step 12: Communicate Update

**Team Announcement Email**:
```markdown
Subject: Master Project Blueprint Updated to v1.1.0

Hi Team,

The Master Project Blueprint has been updated to v1.1.0.

**Key Changes:**
- Added API versioning pattern
- Enhanced request tracing
- Improved security scanning

**For You:**
- No action required for existing projects
- New projects will automatically use v1.1.0
- See BLUEPRINT_CHANGELOG.md for full details

**Learn More:**
- Full changelog: docs/maintenance/BLUEPRINT_CHANGELOG.md
- Updated blueprint: docs/maintenance/MASTER_PROJECT_BLUEPRINT.md
- Onboarding: docs/guides/ONBOARDING.md

Questions? Reach out to the architecture team.

Best regards,
[Your Name]
```

### Automating Updates

#### GitHub Actions Workflow (Future)

```yaml
name: Blueprint Update Check

on:
  schedule:
    - cron: '0 0 1 1,4,7,10 *'  # First day of each quarter
  workflow_dispatch:

jobs:
  check-observations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for blueprint updates
        run: |
          # Check observations file
          # Summarize changes
          # Create issue if updates needed
```

---

## Documentation Standards

### Blueprint Document Requirements

Every blueprint version must include:

- ✅ **Version number** at top and in all references
- ✅ **Last updated date** (YYYY-MM-DD format)
- ✅ **Table of contents** with working links
- ✅ **Clear structure** with consistent heading levels
- ✅ **Practical examples** for all principles
- ✅ **Code snippets** for implementation
- ✅ **Directory tree** showing structure
- ✅ **Tables** for quick reference
- ✅ **Links** to related documents
- ✅ **Cross-references** between related sections

### Changelog Requirements

Every changelog entry must include:

- ✅ **Version number** (semantic versioning)
- ✅ **Release date** (YYYY-MM-DD format)
- ✅ **Clear categories**:
  - Added (new features)
  - Changed (existing features modified)
  - Deprecated (will be removed)
  - Removed (deleted features)
  - Fixed (bug fixes)
  - Security (security improvements)
- ✅ **Clear descriptions** of each change
- ✅ **Migration notes** for breaking changes
- ✅ **Related issues/PRs** if applicable

### Proposal Document Requirements

Every proposal must include:

- ✅ **Title** and **Date**
- ✅ **Problem statement** (what's the issue?)
- ✅ **Proposed solution** (how to solve it?)
- ✅ **Implementation example** (show the code)
- ✅ **Impact analysis** (who does this affect?)
- ✅ **Migration path** (how to adopt?)
- ✅ **Success criteria** (how to measure success?)
- ✅ **Timeline** (when should this happen?)
- ✅ **Risks** (what could go wrong?)
- ✅ **Alternatives** (other options considered?)

---

## Feedback Loop

### Collecting Feedback

#### From Developers
- Post-project retrospectives
- Developer surveys (quarterly)
- Code review observations
- GitHub discussions/issues

#### From Architecture Team
- Quarterly review meetings
- Ad-hoc discussions
- Industry research findings
- Technology trend analysis

#### From Automated Tools
- Project validation results
- Linting/formatting statistics
- Test coverage trends
- Security scan findings

### Feedback Form (Template)

```markdown
## Blueprint Feedback

**Your Name**: 
**Project**: 
**Date**: 

**What part of the blueprint did you use?**
- [ ] Directory structure
- [ ] Configuration management
- [ ] Docker setup
- [ ] GitHub workflows
- [ ] Logging patterns
- [ ] Error handling
- [ ] Other: ___________

**How well did it work for your project?**
- [ ] Excellent - saved significant time
- [ ] Good - mostly helpful
- [ ] Okay - some useful parts
- [ ] Poor - not very helpful
- [ ] N/A - didn't use this part

**What could be improved?**
[Your suggestions]

**Did you encounter any issues?**
[Describe issues]

**Do you have ideas for new patterns?**
[New pattern suggestions]

**Any other feedback?**
[General comments]
```

### Feedback Analysis

**Quarterly Analysis**:
1. Collect all feedback
2. Categorize by theme
3. Identify repeated issues
4. Prioritize improvements
5. Create observation entries
6. Plan changes

**Reporting**:
- Create summary in `docs/dev-notes/feedback-analysis/`
- Share with architecture team
- Incorporate into next quarterly review

---

## Release Notes

### Major Release (v2.0.0 Example)

```markdown
# Master Project Blueprint v2.0.0

**Release Date**: 2027-03-31

## Overview

Master Project Blueprint v2.0.0 represents a significant evolution of the blueprint
with major architectural improvements and modernization.

## What's New

### Breaking Changes ⚠️
- **Directory Structure Reorganized** - New categorization for better scalability
- **Configuration System Enhanced** - New config.py class hierarchy
- **Docker Standards Updated** - Multi-stage builds now mandatory

### Major Features
- Microservices architecture pattern support
- Enhanced API versioning standards
- Improved multi-environment deployment

### Enhancements
- 25+ documentation improvements
- Better type hints throughout
- Enhanced error handling decorators

### Deprecations
- Legacy error handling (removed in v2.0.0)
- Old configuration style (migrate to new format)

## Migration Guide

See [MIGRATION_GUIDE_v1_to_v2.md](./MIGRATION_GUIDE_v1_to_v2.md)

## Timeline

- v2.0.0: March 31, 2027 (release)
- Existing projects: 6 months to migrate (by Sept 30, 2027)
- v1.X.0 support: Until June 30, 2027

## Downloads

- [Blueprint PDF](./releases/blueprint-v2.0.0.pdf)
- [Scaffold Script v2.0.0](./releases/scaffold-project-v2.0.0.sh)
- [Changelog](./BLUEPRINT_CHANGELOG.md#200---2027-03-31)
```

---

## Summary

**Key Principles for Blueprint Evolution**:
1. ✅ **Iterative**: Changes happen in planned phases
2. ✅ **Evidence-Based**: Based on real project experiences
3. ✅ **Collaborative**: Team feedback is essential
4. ✅ **Documented**: Every change is recorded
5. ✅ **Communicated**: Team stays informed
6. ✅ **Tested**: Changes validated before adoption
7. ✅ **Reversible**: Mistakes can be corrected
8. ✅ **Versioned**: Clear versioning for compatibility

**Next Review**:
- **Date**: 2026-12-31 (End of Q4)
- **Focus**: Lessons from new projects, technology updates, team feedback
- **Target**: v1.1.0 or v1.0.1 depending on findings

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-09-13 | Development Team | Initial creation |

**Approved By**

- [ ] Architecture Lead
- [ ] Development Team
- [ ] Project Manager

**Last Review**: 2026-09-13  
**Next Review**: 2026-12-31
