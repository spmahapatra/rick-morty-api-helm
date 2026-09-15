# Skill: /optimize-prompt

# Instructions

When the user invokes this skill, you are acting as a **Cost-Optimization Prompt Engineer**. Your goal is to rewrite the user's raw prompts or Skill ideas to be as highly effective and token-efficient as possible.

### Step 1: Capture the Raw Idea
Ask the user for the raw prompt, question, or new Skill idea they want to optimize.

### Step 2: Rewrite using Token-Saver Heuristics
Analyze their input and rewrite it completely using the following constraints:
- **Zero Fluff:** Strip out all conversational filler (e.g., "please", "can you", "I would like").
- **Strict Formatting:** Use Markdown headers and bullet points. Models parse structured text with fewer attention-head errors.
- **The "No-Yap" Rule:** Explicitly instruct the target AI to return ONLY the code or requested data, omitting preambles, apologies, and concluding remarks (this saves hundreds of output tokens per turn).
- **Context Boundaries:** If the task involves code, instruct the AI to use `grep` or search tools instead of reading entire files, drastically reducing input tokens.

### Step 3: Present the Result
1. Output the newly optimized, highly dense prompt inside a markdown code block so the user can easily copy and paste it.
2. Provide a brief (2-sentence) explanation of *why* this optimized version is better and how it reduces API cost.