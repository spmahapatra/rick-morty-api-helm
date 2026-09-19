# Skill: /list-hooks

# Instructions

When the user asks you to list the hooks or run this skill, you MUST execute the following steps:

1. **Read Global Hooks:** Run `cat ~/.gemini/config/hooks.json` using the `run_command` tool.
2. **Read Project Hooks:** Run `cat .agents/hooks.json` (or check if it exists in the current project root).
3. **Format and Present:** Parse the JSON output and generate a beautifully formatted markdown response for the user. 
   - Clearly separate Global Hooks from Project-Level Hooks.
   - For each hook, list its name and provide a brief 1-sentence description of what it does (infer this from the `"description"` field in the JSON if it exists, otherwise infer it intelligently from the hook's name and script).
   - List the event that triggers it (e.g., `PreToolUse`), the tool it intercepts (the `matcher`), and the script it executes.
   - Use bolding, bullet points, and code blocks to make it highly readable for a DevOps engineer.