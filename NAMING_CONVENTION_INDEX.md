# CI/CD Workflow Naming Convention - Complete Package

A comprehensive standardized naming convention for GitHub Actions workflows that enables developers to immediately identify a pipeline's purpose, trigger conditions, and execution frequency directly from the filename.

---

## 📚 Documentation Guide

This package contains **4 complete documents** that work together to explain and implement the standardized naming convention:

### 1. **CI_CD_NAMING_CONVENTION.md** (Comprehensive Guide)
**Purpose:** The authoritative reference for the naming convention  
**Audience:** Anyone who wants to understand the full system  
**Contents:**
- Core pattern and components
- Category reference (ci, cd, security, analysis, maintenance, setup)
- Trigger types (push, pr, tag, manual, scheduled)
- Frequency reference (per-commit, nightly, weekly, on-demand)
- Real-world examples for each category
- Best practices (✅ DO & ❌ DON'T)
- FAQ section
- Advanced patterns for complex workflows
- **Format:** Markdown, ~7,000 words
- **Read Time:** 15-20 minutes

**When to read this:**
- Setting up the convention for the first time
- Understanding the rationale behind each component
- Learning advanced naming patterns
- Creating new workflows

---

### 2. **WORKFLOW_NAMING_QUICK_REFERENCE.md** (One-Page Cheat Sheet)
**Purpose:** Quick lookup reference for naming decisions  
**Audience:** Developers who need quick answers  
**Contents:**
- The pattern at a glance: `[CATEGORY]-[PURPOSE]-[TRIGGER]-[FREQUENCY].yml`
- Component reference tables
- Quick examples by category
- Common mistakes and corrections
- Decision tree flowchart
- Validation checklist
- Template for new workflows
- **Format:** Markdown, ~2,500 words
- **Read Time:** 5-10 minutes

**When to use this:**
- Creating new workflows
- Verifying naming decisions
- Training team members
- Quick reference during implementation

**Best for:** Printing or pinning to your desk/wiki

---

### 3. **NAMING_CONVENTION_VISUAL_GUIDE.txt** (Visual Examples)
**Purpose:** Text-based visual guide with ASCII art and boxes  
**Audience:** Visual learners  
**Contents:**
- Core pattern with visual breakdown
- Component breakdown with examples
- Before/after real examples (6 workflows from this project)
- Migration summary showing improvements
- Common mistakes with corrections
- Decision flowchart
- Quick validation checklist
- Reference tables
- **Format:** Plain text with formatting boxes (ASCII art)
- **Read Time:** 10-15 minutes

**When to use this:**
- Understanding the pattern visually
- Seeing before/after examples of your actual workflows
- Referencing the decision flowchart
- Sharing with team visually

**Best for:** Team presentations, documentation wikis

---

### 4. **WORKFLOW_RENAMING_GUIDE.md** (Step-by-Step Implementation)
**Purpose:** Detailed instructions for migrating to the new naming convention  
**Audience:** Implementers/project leads  
**Contents:**
- Current → New names mapping for your 6 workflows
- Detailed analysis of each workflow
- Why each rename makes sense
- 6-phase migration plan:
  - Phase 1: Preparation
  - Phase 2: Rename workflows
  - Phase 3: Update documentation
  - Phase 4: Create commit
  - Phase 5: Testing & validation
  - Phase 6: Merge & communication
- Rollback plan (if needed)
- Implementation checklist
- **Format:** Markdown, ~4,500 words
- **Read Time:** 15-20 minutes

**When to use this:**
- First time implementing the convention
- Planning the migration
- Executing the actual rename
- Training someone else to do the migration

---

### 5. **IMPLEMENTATION_CHECKLIST.md** (Tactical Checklist)
**Purpose:** Step-by-step checkbox checklist for implementation  
**Audience:** Person doing the actual implementation  
**Contents:**
- Pre-implementation review (7 items)
- Technical preparation (4 items)
- Phase 1: Create feature branch
- Phase 2: Rename workflows (detailed steps with verification)
- Phase 3: Create documentation
- Phase 4: Create commit
- Phase 5: Testing & validation
- Phase 6: Merge to main
- Phase 7: Communication
- Future workflow additions (template)
- Troubleshooting guide
- Sign-off checklist
- **Format:** Markdown with checkboxes
- **Use Like:** A printed or digital task list
- **Estimated Duration:** 30-45 minutes

**When to use this:**
- During actual implementation
- As reference while executing steps
- Tracking progress
- Training new team members

---

### 6. **NAMING_CONVENTION_VISUAL_GUIDE.txt** (Reference Card)
A text-based visual guide perfect for:
- Team presentations
- Documentation wikis
- Quick visual reference
- Understanding the pattern at a glance

---

## 🎯 Core Pattern (TL;DR)

```
[CATEGORY]-[PURPOSE]-[TRIGGER]-[FREQUENCY].yml
```

**Example:** `ci-test-push-per-commit.yml`

| Component | Meaning | Example |
|-----------|---------|---------|
| **CATEGORY** | Type of workflow | `ci` (testing), `cd` (deployment) |
| **PURPOSE** | What it does | `test`, `build`, `deploy`, `scan` |
| **TRIGGER** | When it runs | `push`, `pr`, `tag`, `manual`, `scheduled` |
| **FREQUENCY** | How often | `per-commit`, `nightly`, `on-demand` |

---

## 📊 Your Project's Workflows: Before & After

### Current (Before) → New Names (After)

| Old Name | New Name | Category | Purpose | Trigger | Frequency |
|----------|----------|----------|---------|---------|-----------|
| `ci.yml` | `ci-test-multi-per-commit.yml` | ci | test | multi | per-commit |
| `fast-track.yml` | `ci-validation-pr-per-pr.yml` | ci | validation | pr | per-pr |
| `cd.yml` | `cd-deploy-manual-on-demand.yml` | cd | deploy | manual | on-demand |
| `cd-with-dockerhub.yml` | `cd-build-push-tag-on-demand.yml` | cd | build-push | tag | on-demand |
| `fast-track-tag-release.yml` | `cd-release-validation-tag-on-demand.yml` | cd | release-validation | tag | on-demand |
| `copilot-setup-steps.yml` | `setup-copilot-multi-on-demand.yml` | setup | copilot | multi | on-demand |

---

## 🗂️ How to Use This Package

### Scenario 1: "I want to understand the naming convention"
1. Read **CI_CD_NAMING_CONVENTION.md** (comprehensive)
2. Reference **WORKFLOW_NAMING_QUICK_REFERENCE.md** (quick lookup)
3. Review **NAMING_CONVENTION_VISUAL_GUIDE.txt** (visual examples)

### Scenario 2: "I need to rename our workflows"
1. Read **WORKFLOW_RENAMING_GUIDE.md** (understand each workflow)
2. Use **IMPLEMENTATION_CHECKLIST.md** (step-by-step)
3. Follow the numbered steps and checkboxes

### Scenario 3: "I'm teaching someone about this"
1. Start with **NAMING_CONVENTION_VISUAL_GUIDE.txt** (visual intro)
2. Use **WORKFLOW_NAMING_QUICK_REFERENCE.md** (for reference)
3. Reference **WORKFLOW_RENAMING_GUIDE.md** (for context of your project)

### Scenario 4: "I'm adding a new workflow"
1. Check **WORKFLOW_NAMING_QUICK_REFERENCE.md** (decision tree)
2. Review examples in **NAMING_CONVENTION_VISUAL_GUIDE.txt**
3. Verify with validation checklist in **CI_CD_NAMING_CONVENTION.md**

### Scenario 5: "I need to print something"
1. Print **WORKFLOW_NAMING_QUICK_REFERENCE.md** (1-2 pages)
2. Print **NAMING_CONVENTION_VISUAL_GUIDE.txt** (3-5 pages)
3. Post on wall or add to team wiki

---

## 📖 Categories at a Glance

### CI (Continuous Integration)
Tests, linting, type-checking, validation
```
ci-test-push-per-commit.yml          # Run tests
ci-lint-pr-per-pr.yml                # Lint code
ci-type-check-push-per-commit.yml    # TypeScript validation
```

### CD (Continuous Deployment)
Building, pushing images, deployments
```
cd-build-push-tag-on-demand.yml      # Build Docker image
cd-deploy-manual-on-demand.yml       # Manual deployment
cd-release-validation-tag-on-demand.yml  # Release validation
```

### Security
Scanning, audits, compliance
```
security-sast-push-nightly.yml
security-deps-scan-scheduled-weekly.yml
```

### Analysis
Metrics, benchmarks, coverage reports
```
analysis-coverage-report-pr-per-pr.yml
analysis-benchmarks-scheduled-weekly.yml
```

### Maintenance
Cleanup, cache management, updates
```
maintenance-cache-cleanup-scheduled-weekly.yml
maintenance-deps-update-scheduled-weekly.yml
```

### Setup
Configuration, environment initialization
```
setup-copilot-multi-on-demand.yml
setup-env-manual-on-demand.yml
```

---

## ✅ Quick Checklist for Naming

Before finalizing a workflow name, verify:

- [ ] **Category is clear** (ci, cd, security, analysis, maintenance, setup)
- [ ] **Purpose is specific** (test, lint, deploy, scan, etc.)
- [ ] **Trigger is explicit** (push, pr, tag, manual, scheduled, multi)
- [ ] **Frequency is accurate** (per-commit, per-pr, nightly, on-demand, etc.)
- [ ] **Name is ≤50 characters**
- [ ] **Uses hyphens** (not underscores or camelCase)
- [ ] **No ambiguity** (same name = same meaning to anyone)
- [ ] **Alphabetical grouping works** (ci-*, cd-* all group together)

---

## 🔄 Implementation Timeline

**Estimated Total Time: 1-2 hours**

| Phase | Time | Activity |
|-------|------|----------|
| **Preparation** | 10-15 min | Read docs, understand patterns |
| **Rename Workflows** | 10-15 min | Execute git mv commands |
| **Documentation** | 10-15 min | Create/update reference files |
| **Testing** | 15-30 min | Push branch, test workflows, review |
| **Merge & Deploy** | 10-15 min | Merge PR, communicate changes |
| **Followup** | 10 min | Update team docs, answer questions |

**Difficulty Level:** Low (mostly file renames, easy rollback)  
**Risk Level:** Low (git preserves history)  
**Impact:** High (improves clarity for entire team)

---

## 📋 Document Inventory

| Document | Size | Focus | Audience | Format |
|----------|------|-------|----------|--------|
| CI_CD_NAMING_CONVENTION.md | 22 KB | Comprehensive guide | Everyone | Markdown |
| WORKFLOW_NAMING_QUICK_REFERENCE.md | 8.2 KB | Quick reference | Developers | Markdown |
| NAMING_CONVENTION_VISUAL_GUIDE.txt | 40 KB | Visual examples | Visual learners | Text |
| WORKFLOW_RENAMING_GUIDE.md | 16 KB | Step-by-step implementation | Project leads | Markdown |
| IMPLEMENTATION_CHECKLIST.md | 21 KB | Tactical checklist | Implementer | Markdown |
| NAMING_CONVENTION_INDEX.md | This file | Navigation & summary | Everyone | Markdown |

**Total Documentation:** ~150 KB of comprehensive guidance

---

## 🎓 Learning Paths

### Path 1: "Quick Start" (30 minutes)
1. Skim **NAMING_CONVENTION_INDEX.md** (this file) - 5 min
2. Read **WORKFLOW_NAMING_QUICK_REFERENCE.md** - 10 min
3. Review examples in **NAMING_CONVENTION_VISUAL_GUIDE.txt** - 10 min
4. Understand your specific workflows - 5 min

**Outcome:** You can name new workflows correctly

### Path 2: "Deep Dive" (60 minutes)
1. Read **CI_CD_NAMING_CONVENTION.md** - 20 min
2. Study **NAMING_CONVENTION_VISUAL_GUIDE.txt** - 15 min
3. Review **WORKFLOW_RENAMING_GUIDE.md** - 15 min
4. Practice with examples - 10 min

**Outcome:** You understand rationale and can teach others

### Path 3: "Implementation" (90 minutes)
1. Read **WORKFLOW_RENAMING_GUIDE.md** - 20 min
2. Follow **IMPLEMENTATION_CHECKLIST.md** step-by-step - 60 min
3. Test and verify - 10 min

**Outcome:** Workflows successfully renamed in your repository

---

## 🚀 Getting Started

### Step 1: Read One of These First
- **If visual:** NAMING_CONVENTION_VISUAL_GUIDE.txt
- **If quick:** WORKFLOW_NAMING_QUICK_REFERENCE.md
- **If thorough:** CI_CD_NAMING_CONVENTION.md

### Step 2: Understand Your Workflows
- Review: WORKFLOW_RENAMING_GUIDE.md → "Workflow Details & Recommendations"
- See how your 6 current workflows map to new names

### Step 3: Ready to Implement?
- Use: IMPLEMENTATION_CHECKLIST.md
- Follow step-by-step checkboxes
- Takes 30-45 minutes

### Step 4: Questions?
- Check: CI_CD_NAMING_CONVENTION.md → "FAQ"
- Reference: WORKFLOW_NAMING_QUICK_REFERENCE.md → "Troubleshooting"

---

## 💡 Key Benefits

✅ **Instant Clarity** - Purpose clear from filename  
✅ **Better Discovery** - Related workflows group together when sorted  
✅ **Visible Triggers** - Know when workflow runs without opening file  
✅ **Frequency Transparency** - Execution cadence obvious at a glance  
✅ **Scalability** - Works with 6 workflows or 60+  
✅ **Self-Documenting** - Filenames serve as documentation  
✅ **Easier Onboarding** - New team members understand quickly  
✅ **Consistent** - Standard applies across entire organization  

---

## 🎯 Success Criteria

After implementing the naming convention, you'll know it's successful when:

- ✅ All workflows have descriptive, standardized names
- ✅ New team members understand what workflows do without asking
- ✅ Workflow files naturally group by category when sorted
- ✅ You can quickly find workflows by their purpose or trigger
- ✅ New workflows are named consistently without discussion
- ✅ Documentation maintenance is easier (names are self-explanatory)
- ✅ Code reviews mention naming consistency without prompting
- ✅ Team members cite the naming convention naturally

---

## 📞 Support & Resources

**For comprehensive details:**
- CI_CD_NAMING_CONVENTION.md - Complete reference guide
- WORKFLOW_NAMING_QUICK_REFERENCE.md - Quick lookup
- NAMING_CONVENTION_VISUAL_GUIDE.txt - Visual reference

**For implementation:**
- WORKFLOW_RENAMING_GUIDE.md - Understand your workflows
- IMPLEMENTATION_CHECKLIST.md - Step-by-step execution

**For teams:**
- Print: WORKFLOW_NAMING_QUICK_REFERENCE.md
- Share: NAMING_CONVENTION_VISUAL_GUIDE.txt
- Wiki: CI_CD_NAMING_CONVENTION.md

---

## 📝 Document Information

- **Package Created:** 2026-09-14
- **Repository:** setupAppCreDepHelmPkg
- **Status:** Complete & Ready for Adoption
- **Version:** 1.0
- **Audience:** Developers, DevOps, Team Leads
- **Maintenance:** Refer to CI_CD_NAMING_CONVENTION.md for updates

---

## 🔗 Quick Navigation

| Want to... | Read this... | Time |
|-----------|---|------|
| Understand the pattern | NAMING_CONVENTION_VISUAL_GUIDE.txt | 10 min |
| Name a new workflow | WORKFLOW_NAMING_QUICK_REFERENCE.md | 5 min |
| Learn everything | CI_CD_NAMING_CONVENTION.md | 20 min |
| Implement in my repo | WORKFLOW_RENAMING_GUIDE.md + IMPLEMENTATION_CHECKLIST.md | 45 min |
| Present to team | NAMING_CONVENTION_VISUAL_GUIDE.txt | 10 min |
| Train a colleague | Start with WORKFLOW_NAMING_QUICK_REFERENCE.md | 15 min |
| Find reference tables | WORKFLOW_NAMING_QUICK_REFERENCE.md or NAMING_CONVENTION_VISUAL_GUIDE.txt | 5 min |

---

**This is your starting point. Pick a document above and dive in!**
