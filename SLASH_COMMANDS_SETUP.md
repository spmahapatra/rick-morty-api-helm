# Why Slash Commands Like `/opsx-apply` Aren't Functioning: Setup and Activation Guide

## Summary

Slash commands (also called **workflows** in Kilo) are not automatically available in your chat interface. They require explicit configuration and activation through Kilo's workflow system. The commands you have in `.github/prompts/` (like `opsx-apply.prompt.md`) are documentation files, not active slash commands. This document explains what's needed to enable them.

---

## What Are Slash Commands?

Slash commands (e.g., `/opsx-apply`, `/opsx-propose`, `/opsx-explore`) are **workflow shortcuts** that invoke pre-defined step-by-step instructions in the chat interface. They:

- Start with a forward slash `/` followed by a command name
- Execute a sequence of operations (reading files, running tools, asking questions)
- Are stored as Markdown files in a specific directory
- Must be registered in Kilo's configuration to appear in the command picker

**Current Status**: Your project has the documentation/prompt files but they are NOT registered as active slash commands in the Kilo system.

---

## Why Your Commands Aren't Working

### Issue 1: No `.kilo/commands/` Directory
Your project structure is missing the required **commands directory** where Kilo looks for slash command definitions:

```
Your current structure:
/home/localadmin/localwork/setupAppCreDepHelmPkg/
├── .github/
│   ├── agents/        ✅ Has OpenSpec agent
│   ├── prompts/       📄 Has prompt documentation (not active commands)
│   ├── skills/        ✅ Has OpenSpec skills
│   └── workflows/     (empty or unused)
├── openspec/
└── app.py

Missing critical structure:
├── .kilo/             ❌ NOT PRESENT
│   ├── commands/      ❌ NOT PRESENT - Where slash commands live
│   └── agents/        (optional - for custom agents)
```

**Kilo looks for commands in these locations** (in order of precedence):
1. **Project-level commands**: `.kilo/commands/` ← **You need this**
2. **Global commands**: `~/.config/kilo/commands/` (optional, for all projects)

### Issue 2: Prompt Files ≠ Slash Commands
The files in `.github/prompts/` (like `opsx-apply.prompt.md`) are documentation or prompt templates, not active slash command definitions. They describe what the commands should do but don't register them with Kilo.

```
.github/prompts/opsx-apply.prompt.md     ← Documentation/reference
.kilo/commands/opsx-apply.md              ← Actual slash command (missing)
```

### Issue 3: No Kilo Project Configuration
Your project lacks a `.kilo/` directory structure. Kilo uses this to store:
- Command definitions (`.kilo/commands/`)
- Custom agents (`.kilo/agents/`)
- Project-level configuration (`kilo.jsonc`)

---

## How to Enable Slash Commands

### Step 1: Create the `.kilo/commands/` Directory

```bash
mkdir -p /home/localadmin/localwork/setupAppCreDepHelmPkg/.kilo/commands
```

### Step 2: Create Slash Command Files

Create Markdown files in `.kilo/commands/` for each command you want to activate. Example:

**File: `.kilo/commands/opsx-explore.md`**
```markdown
---
description: Explore project structure and requirements using OpenSpec
agent: general
---

# OpenSpec Explore Command

Activate explore mode to investigate the project structure, existing specs, and codebase.

Run these steps:
1. Read the project README and key source files
2. Check openspec/config.yaml for project context
3. List existing specs and changes: `openspec list --specs`
4. Investigate relevant code and architecture
5. Generate insights about capabilities and gaps
6. Suggest improvements or areas for formalization

Follow the conversation naturally - ask clarifying questions and explore
interdependencies before committing to a specific plan.
```

**File: `.kilo/commands/opsx-propose.md`**
```markdown
---
description: Propose a new OpenSpec change with complete planning artifacts
agent: general
---

# OpenSpec Propose Command

Create a new OpenSpec change with proposal, specs, design, and tasks artifacts.

1. Understand what the user wants to build or change
2. Load project context from openspec/config.yaml
3. Create a new OpenSpec change
4. Generate proposal.md (Why, What, Capabilities, Impact)
5. Generate specs/*.md (Requirements with scenarios)
6. Generate design.md (Technical decisions, trade-offs)
7. Generate tasks.md (31 implementation checkboxes)

After artifacts are complete, ask if the user wants to proceed with
implementation or review the proposal.
```

**File: `.kilo/commands/opsx-apply.md`**
```markdown
---
description: Apply a change by implementing tasks and verifying completion
agent: general
---

# OpenSpec Apply Command

Track and implement an OpenSpec change by working through its tasks.

1. Check the current change status
2. Review tasks.md for implementation work
3. Execute each task group in dependency order
4. Verify completion criteria for each task
5. Run tests and validation
6. Update task status as you complete items
7. Report progress and any blockers

Use this after proposal artifacts are ready for implementation.
```

### Step 3: Test Command Availability

After creating the `.kilo/commands/` directory with `.md` files:

1. **In VS Code extension**: 
   - Press `Ctrl+P` (or `Cmd+P` on Mac)
   - Type `/` to see the command picker
   - You should see your new commands listed

2. **In CLI**:
   ```bash
   cd /home/localadmin/localwork/setupAppCreDepHelmPkg
   # Commands are auto-discovered from .kilo/commands/
   ```

3. **In chat**: Type `/opsx-explore` or `/opsx-propose` to invoke

---

## Alternative: Use Existing Prompt Files

If you don't want to set up `.kilo/commands/`, you can still use the prompts manually:

```bash
# Instead of /opsx-explore, you can ask directly:
"Please help me explore the project structure using OpenSpec framework"

# Or reference the file:
"Please follow the instructions in .github/prompts/opsx-explore.prompt.md"
```

However, this **does not** provide the slash command shortcut (`/opsx-explore`).

---

## Comprehensive Setup: Full `.kilo/` Structure

For complete Kilo integration, create this structure:

```
.kilo/
├── commands/
│   ├── opsx-explore.md
│   ├── opsx-propose.md
│   ├── opsx-apply.md
│   ├── opsx-archive.md
│   ├── opsx-update.md
│   └── opsx-sync.md
├── agents/
│   └── openspec.md           (optional - custom agent for OpenSpec work)
└── .gitignore                (to version control .kilo/commands but not temporary files)
```

### Optional: Project-Level Kilo Configuration

Create `.kilo/kilo.jsonc` for project-specific settings:

```json
{
  "$schema": "https://app.kilo.ai/config.json",
  "agent": {
    "openspec": {
      "description": "OpenSpec framework specialist",
      "mode": "subagent",
      "prompt": "You are an OpenSpec framework expert..."
    }
  },
  "command": {
    "opsx-explore": {
      "description": "Explore project using OpenSpec"
    },
    "opsx-propose": {
      "description": "Propose OpenSpec change"
    }
  },
  "permission": {
    "bash": {
      "openspec *": "allow"
    }
  }
}
```

---

## Permissions and Security

Your global Kilo configuration already allows OpenSpec commands:

```jsonc
// ~/.config/kilo/kilo.jsonc
{
  "permission": {
    "bash": {
      "openspec *": "allow"
    }
  }
}
```

This permits bash commands starting with `openspec`. For slash commands to work with file operations:

```jsonc
{
  "permission": {
    "read": "allow",
    "edit": "allow",
    "bash": {
      "openspec *": "allow"
    }
  }
}
```

---

## Converting Existing Prompts to Slash Commands

Your `.github/prompts/` files can be adapted as slash commands. Here's the conversion:

**From**: `.github/prompts/opsx-explore.prompt.md` (16 KB documentation)
**To**: `.kilo/commands/opsx-explore.md` (concise workflow)

**Conversion steps**:
1. Extract the core instruction section
2. Simplify to step-by-step workflow
3. Add YAML frontmatter with description and agent
4. Save in `.kilo/commands/`

Example extraction:
```markdown
---
description: Enter explore mode to investigate the project
agent: general
---

# Explore Mode

Follow these steps:

1. Check existing context with `openspec list --specs` and `openspec list`
2. Read relevant project files to understand structure
3. Map current architecture and dependencies
4. Identify gaps or areas needing formalization
5. Surface risks and recommendations
6. Ask clarifying questions to understand intent

Think deeply. Visualize freely. Follow the conversation.
```

---

## Verification Checklist

After setup, verify your slash commands are working:

- [ ] `.kilo/commands/` directory exists
- [ ] `.kilo/commands/opsx-explore.md` exists and is readable
- [ ] `.kilo/commands/opsx-propose.md` exists and is readable
- [ ] `.kilo/commands/opsx-apply.md` exists and is readable
- [ ] Kilo configuration allows bash commands with `openspec *`
- [ ] In VS Code, press `Ctrl+P` and type `/` to see command list
- [ ] Type `/opsx-explore` in chat and confirm it executes
- [ ] Monitor the command output for errors or permissions blocks

---

## Troubleshooting

### Problem: Commands don't appear in picker
**Solution**: 
- Verify `.kilo/commands/` exists: `ls -la .kilo/commands/`
- Check files end with `.md`: `ls .kilo/commands/*.md`
- Reload Kilo (VS Code: F1 → Developer: Reload Window)

### Problem: "Permission denied" when running command
**Solution**:
- Check `~/.config/kilo/kilo.jsonc` permissions
- Ensure `"openspec *": "allow"` is in `permission.bash`
- Verify `read`, `edit` are allowed in permissions

### Problem: Commands execute but give wrong output
**Solution**:
- Verify working directory is correct project root
- Check that command `.md` file has proper YAML frontmatter
- Review frontmatter syntax (must start/end with `---`)
- Test manually: `openspec status --change "rick-morty-api-initial-spec"`

### Problem: "No such command" error
**Solution**:
- Filename must match command name (e.g., `opsx-explore.md` → `/opsx-explore`)
- Remove `.md` extension when typing the command
- Commands are case-sensitive; use lowercase

---

## Using Slash Commands Effectively

Once enabled, use them as shortcuts:

```
# Existing workflow (works now):
Manual typing: "Please use OpenSpec to explore the project"

# Future workflow (after slash commands are enabled):
/opsx-explore          # Automatically invokes the workflow
```

Common usage patterns:

```bash
# Explore phase
/opsx-explore

# Planning phase
/opsx-propose rick-morty-api-enhancements

# Implementation phase
/opsx-apply

# Updates during implementation
/opsx-update

# Finalization
/opsx-archive

# Sync with upstream
/opsx-sync
```

---

## Next Steps

1. **Immediate**: Create `.kilo/commands/` directory and copy slash command files
2. **Verify**: Test command availability in VS Code or CLI
3. **Integrate**: Use `/opsx-*` commands in your workflow
4. **Optional**: Create custom agents for specialized OpenSpec work
5. **Documentation**: Update project README to document available commands

---

## Summary

| Item | Status | Action |
|------|--------|--------|
| Slash command system | ✅ Available in Kilo | No action needed |
| `.kilo/commands/` directory | ❌ Missing | Create it |
| Command `.md` files | ⚠️ In `.github/prompts/` | Move/adapt to `.kilo/commands/` |
| Permissions | ✅ Configured | No action needed |
| Global config | ✅ Allows openspec | No action needed |
| Project config | ⚠️ Optional | Create for advanced setup |

**Action Required**: Create `.kilo/commands/` and populate with command Markdown files. After that, slash commands will be available in your chat interface.

