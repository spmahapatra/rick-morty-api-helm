# Skill: /bootstrap-enterprise-project

# Instructions

When the user invokes this skill, you are acting as an Enterprise Platform Architect. 

### Step 1: Interactive Component Selection
Before you write any code, you MUST use the `ask_question` tool to ask the user which components they want to scaffold for this new project. 

Provide a multi-select question with the following options:
1. Python Microservice (FastAPI + uv)
2. Secure Dockerfile & docker-compose
3. Helm Chart (Kubernetes Manifests)
4. GitHub Actions CI/CD Pipeline
5. Local Git Hooks (pre-commit, pre-push)

### Step 2: Component Scaffolding
Once the user responds, scaffold ONLY the selected components. You MUST strictly follow the standards defined in your `enterprise-devops.md` global rule. 

**Execution Guidelines:**
- **Python:** Use `run_command` to initialize a `uv` project (`uv init` or manual structure). 
- **Docker:** Ensure the Dockerfile has a non-root `appuser`, multi-stage builds, and no `latest` tags (to satisfy your `docker-enforcer` hook).
- **Helm:** Create a `helm/` directory with standardized `values.yaml` and resource limits.
- **Git Hooks:** If selected, generate standard bash hooks in `.githooks/` and set `core.hooksPath`.

### Step 3: Summary
When finished, output a summary of the generated components and explain how they meet the enterprise standards.