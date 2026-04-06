# Repo working rules

This repository currently focuses on one vertical only: Chinese civil-service essay tasks (申论).

When editing this repo:
- Keep the user-facing slash command stable as `/shenlun`.
- Prefer supporting files under `.claude/skills/shenlun/` instead of bloating `SKILL.md`.
- Treat any scoring rubric as an operational framework unless an explicit profile file says otherwise.
- When the prompt materials are incomplete, continue with a best-effort structure and state the uncertainty.
- Label synthetic essays and synthetic examples clearly.
- Save generated reports under `outputs/`.

Before expanding the repo beyond 申论, update `docs/shenlun-branch-scope.md` first.
