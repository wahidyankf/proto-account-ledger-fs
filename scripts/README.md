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
- [build-architecture-pdf.py](build-architecture-pdf.py) — builds the Part 2 PDF, `architecture-trade-offs.pdf` at the
  root, from `docs/explanation/architecture-trade-offs.md`: it checks each Mermaid diagram against the limits the
  [diagrams rule](../repo-governance/conventions/writing/diagrams.md) declares, renders it with the Mermaid CLI, prints
  the page with headless Chrome, and fails unless the PDF has two to four pages. Run it with
  `uv run scripts/build-architecture-pdf.py` after any change to the Markdown.
