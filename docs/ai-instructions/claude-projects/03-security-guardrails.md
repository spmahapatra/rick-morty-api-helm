# SECURITY HOOKS & SYSTEM GUARDRAILS

You MUST manually enforce these guardrails on yourself BEFORE taking any actions:

### 🛡️ Guardrail: artifact-redirector
- **Rule:** Scratch files MUST be written to `.ai_scratch/`.

### 🛡️ Guardrail: branch-architect
- **Rule:** FORBIDDEN from editing code if branch is `master` or `main`.

### 🛡️ Guardrail: auto-checkpoint
- **Rule:** Run `git add . && git commit -m 'chore: auto-checkpoint'` before major edits.

### 🛡️ Guardrail: secrets-redactor
- **Rule:** FORBIDDEN from hardcoding AWS Keys, GitHub Tokens, or Passwords.

### 🛡️ Guardrail: token-saver
- **Rule:** Do not read files larger than 1000 lines in full.

### 🛡️ Guardrail: auto-formatter
- **Rule:** After editing Python code, run `black .` or `ruff`.

### 🛡️ Guardrail: security-bouncer
- **Rule:** FORBIDDEN from running `rm -rf`, `sudo`, etc.

### 🛡️ Guardrail: commit-enforcer
- **Rule:** Git commit messages MUST follow Conventional Commits.

### 🛡️ Guardrail: context-injector
- **Rule:** Emulate behavior: {'PreInvocation': [{'hooks': [{'command': 'python3 ~/.gemini/config/scripts/context-injector.py'}]}]}

### 🛡️ Guardrail: test-enforcer
- **Rule:** MUST run unit tests before stopping. Fix if they fail.

### 🛡️ Guardrail: auto-doc-updater
- **Rule:** If source code is modified, update README.md before stopping.

### 🛡️ Guardrail: uv-enforcer
- **Rule:** Emulate behavior: {'PreToolUse': [{'matcher': 'run_command', 'hooks': [{'command': 'python3 ~/.gemini/config/scripts/uv-enforcer.py'}]}]}

### 🛡️ Guardrail: docker-enforcer
- **Rule:** Emulate behavior: {'PreToolUse': [{'matcher': 'write_to_file|replace_file_content', 'hooks': [{'command': 'python3 ~/.gemini/config/scripts/docker-enforcer.py'}]}]}

