# Scripts

This directory is reserved for small, repository-local automation scripts that do not belong to an Nx project or a Git
hook.

Keep scripts focused, portable, and well commented. Prefer adding repeatable development tasks as Nx `command` targets;
place hook orchestration in `.husky/`.

## Directory Map

- [validate-commit-message](validate-commit-message) — adapts Rhino's sealed message text to commitlint's file input for
  the Conventional Commits gate.
- [format-staged](format-staged) — formats the staged paths Rhino selects on `pre-commit`: Prettier for its file types,
  and for Python, ruff's safe fixes then `ruff format` with the settings of the nearest `pyproject.toml`, skipping
  generated harness adapters.
- [public-safety/](public-safety/README.md) — the publication screen that runs first on every gate surface.
