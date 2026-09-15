# AI Customization Architecture Blueprint

To create a scalable, maintainable setup for your AI assistant across multiple projects, you should adopt a **Two-Tiered Architecture**: 
1. **The Global Toolbelt** (Your machine-wide AI setup)
2. **The Project Sandbox** (Codebase-specific instructions shared with your team)

---

## 1. Global Setup (`~/.gemini/config/`)
Think of the global configuration as your **personal AI operating system**. It contains your preferred workflows, universal tools, and general coding philosophies. Anything here applies to *every* project you open on your machine.

### What goes here?
*   **Universal Workflows (Skills):**
    *   `openspec-propose` / `openspec-explore` (You want the ability to scaffold OpenSpec changes in *any* repo you work on).
    *   A `github-pr-reviewer` skill (A workflow you run on any repo to summarize PRs).
*   **Prompt Enhancers (Rules):**
    *   `rules/my-coding-style.md`: "Always use early returns, avoid deeply nested if-statements, prefer explicit variable names."
    *   `rules/openspec.md`: Instructions on how to interface with the OpenSpec CLI.
*   **Global Security/Validation (Hooks):**
    *   A `hooks.json` that prevents the AI from running `rm -rf /` or forces a confirmation prompt before running any `docker push` command.

---

## 2. Project Setup (`<project_root>/.agents/` & `GEMINI.md`)
*Note: While Kilo used `.github/`, Gemini looks for an `.agents/` folder or a `GEMINI.md` file at the root of your project.*

Think of this as the **Employee Onboarding Handbook** for a specific codebase. It contains rules that a new developer (or AI) *must* know to successfully contribute to this specific repository without breaking things. Because these are checked into Git, your whole team benefits from them.

### What goes here?
*   **Project-Specific Workflows (Skills):**
    *   `.agents/skills/deploy-to-staging/SKILL.md`: A complex 10-step process for deploying *this specific app* to your AWS environment.
    *   `.agents/skills/scaffold-new-route/SKILL.md`: A workflow that knows exactly where to put controllers, models, and views for this specific architecture.
*   **Project Guidelines (Rules):**
    *   `GEMINI.md` (at repo root): "This project uses FastAPI and SQLAlchemy 2.0. Do not use legacy SQLAlchemy 1.4 syntax. All database models must inherit from `Base` in `src/models/base.py`."
    *   `frontend/GEMINI.md`: "Use React Server Components. Do not use `useEffect` for data fetching."
*   **Project-Specific Validations (Hooks):**
    *   `.agents/hooks.json`: A hook that automatically runs `npm run lint` or `pytest` after the AI modifies a file, ensuring the AI fixes its own errors before continuing.

---

## 3. Reference Example: Structuring This Project

Let's look at how we would structure your current project (`setupAppCreDepHelmPkg`) as a starting point.

### The Global Tier (Already Done)
We already moved your OpenSpec skills and general agent rules to your global config.
```text
~/.gemini/config/
├── rules/
│   └── openspec.md           <- Tells AI how OpenSpec works generally
└── skills/
    ├── openspec-explore/     <- Universal workflow to explore ideas
    ├── openspec-propose/     <- Universal workflow to propose changes
    └── ...
```

### The Project Tier (To-Do)
Currently, your project has `.github/workflows/` (GitHub Actions, which is fine), but it lacks Gemini-specific project constraints. You should create:

```text
setupAppCreDepHelmPkg/
├── GEMINI.md                 <- The "Master Rulebook" for this repo
├── .agents/
│   ├── skills/
│   │   └── build-docker/     <- Skill specific to this repo's Docker/Helm setup
│   │       └── SKILL.md
│   └── hooks.json            <- E.g., Auto-run pytest after the AI edits tests
```

#### Example `GEMINI.md` for this project:
```markdown
# Project Guidelines
- **Architecture**: This is a Python backend with Docker and Helm deployments.
- **Dependencies**: All new Python packages must be added to `requirements.txt`.
- **Testing**: Use `pytest`. Test files must be placed in the `tests/` directory and match the name `test_*.py`.
- **Docker**: When modifying the `Dockerfile`, always ensure the base image remains lightweight (e.g., `python:3.9-slim`).
```
