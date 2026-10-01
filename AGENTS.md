# AGENTS.md: working on harness-duel

harness-duel compares two coding-agent harnesses by running both on the same tasks, deciding a
winner per task, and applying a sign test. Read README.md first.

## Rules that keep the results trustworthy
- Hidden tests are copied into a workspace only AFTER the agent has finished. Never earlier.
- Lint counts only issues the agent ADDED (after minus before), never pre-existing ones.
- A failed or timed-out run is scored as it is. Never drop it.
- The per-task decision order is: hidden tests, then new lint issues, then cost. If you change
  it, update decide.py's docstring, the README and the tests together.
- Keep it simple: stdlib + pytest + ruff only. No new dependencies without asking.

## Workflow
1. Explain which file you will change and why before editing. If I ask for a plan, only plan.
2. Plan approval is not permission to implement. After approval, write the test first, run it,
   and show me it fails.
3. Then implement, run `uv run pytest -q`, and paste the full output.
4. If you asked me a question, wait for my answer before acting.
