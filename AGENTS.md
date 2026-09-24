# Repository Guidelines

## Purpose and Working Style

This repository holds an in-memory account ledger core written in Python, built as an Nx monorepo. Use the smallest
responsible change; see [minimal sufficiency](repo-governance/principles/minimal-sufficiency.md). Resolve every material
open decision by grilling with options, one decision per question and one recommendation, using the
[grill-me skill](.agents/skills/grill-me/SKILL.md); never settle it silently in prose.

Keep a live task list for every task as a Markdown checklist in the gitignored `local-tmp/` directory, per
[task tracking](repo-governance/development/agents/task-tracking.md). Write scratch output only to `local-tmp/` and
reports only to `generated-reports/`; see [temporary files](repo-governance/conventions/structure/temporary-files.md).

## Governance

[repo-governance/](repo-governance/README.md) holds principles, conventions, development standards, and workflows,
mostly adopted from `ose-rules`. Levels are ordered — principles, then conventions, then development, then workflows —
and a lower level never contradicts a higher one. `README.md` and `docs/` serve people, this file and `.agents/` serve
agents, and `repo-governance/` serves both. `CLAUDE.md` only imports this file.

Change a rule through [rules-propagation](repo-governance/workflows/maintenance/rules-propagation.md), and carry every
change into the documents it makes stale through
[docs-propagation](repo-governance/workflows/maintenance/docs-propagation.md) before committing it. Run
[rules-quality-gate](repo-governance/workflows/maintenance/rules-quality-gate.md),
[docs-quality-gate](repo-governance/workflows/quality/docs-quality-gate.md), and
[plan-quality-gate](repo-governance/workflows/plan/plan-quality-gate.md) only when the owner explicitly asks. Adopt more
catalog artifacts only through [adopt-artifact](repo-governance/workflows/adoption/adopt-artifact.md), recording
`OSE-Rules-Source` and `OSE-Rules-Commit` trailers.

## Project Structure

- `apps/` runnable applications; `libs/` reusable libraries (none yet).
- `specs/` the as-built architecture; behaviour is specified by the plain pytest tests that prove it.
- `plans/` delivery plans; `docs/` Diátaxis documentation for people.
- Root assessment docs, such as `AMBIGUITIES.md` and `NUMBERS.md`, answer the challenge brief and must agree with one
  another; see [assessment docs](repo-governance/conventions/structure/assessment-docs.md).
- `.agents/` canonical agents and skills; `.claude/`, `.codex/`, and `.opencode/` are generated adapters.

## Commands

```bash
npm install                               # bootstrap; Nx targets run uv sync first
npx nx run account-ledger-cli:run         # run the CLI
npx nx run account-ledger-cli:test:quick  # typecheck, lint, unit tests with coverage gate
npx nx run account-ledger-cli:test:integration
npx nx run account-ledger-cli:test:e2e
npm run generate:bindings                 # regenerate harness adapters after editing .agents/
npm run check:hygiene                     # every declared main-surface gate
```

Nx is a raw task runner: `command` targets and ordered `nx:run-commands` aggregates, no `@nx/*` plugins; see the
[Nx workspace policy](repo-governance/development/workflow/nx-workspace-policy.md). Rhino (`./rhino`, pinned by
`rhino.lock`) runs the gates declared in `repo-config.yml`.

## Planning

Create plan documents only when the owner explicitly requests a plan. A plan moves through `plans/ideas/`, `backlog/`,
`in-progress/`, and `done/` with six documents; see the
[plans convention](repo-governance/conventions/structure/plans.md). Author with
[plan-planning](repo-governance/workflows/plan/plan-planning.md), execute with
[plan-execution](repo-governance/workflows/plan/plan-execution.md), and archive only after
[plan-execution-check](repo-governance/workflows/plan/plan-execution-check.md) passes. Plan structure is checked by
reading, not by a validator; see
[structural validation](repo-governance/conventions/structure/plans/006-structural-validation.md).

## Coding Conventions

Follow the [Python standards](repo-governance/development/quality/stacks/python-standards.md): a functional core with an
imperative shell, frozen dataclasses and enums for the domain, `Decimal` for money, strict pyright, and ruff for lint
and format. Prettier is the source of truth for Markdown, JSON, and YAML; prose wraps at 120 columns, and outside
`repo-governance/` and the harness directories every Markdown line, tables included, stays within 120; see
[Markdown prose wrap](repo-governance/conventions/writing/markdown-prose-wrap.md). Diagrams are plain-text ASCII only,
never Mermaid; see [diagrams](repo-governance/conventions/writing/diagrams.md).

## Testing

Implement behaviour test-first as plain pytest tests, one behaviour per red-green-refactor cycle; see
[test-driven development](repo-governance/development/quality/testing/test-driven-development.md). No Gherkin is written
or bound: [behaviour-driven development](repo-governance/development/quality/testing/behaviour-driven-development.md)
binds only its layers here. `test:unit` runs in-process with every OS-facing dependency injected and enforces 80% line
coverage; `test:integration` uses real, isolated local resources and never the network; `test:e2e` runs the CLI through
its public process boundary. Never skip a test.

## Commits and Integration

Commit on local `main` and push directly to `origin/main`; no task branches and no pull requests. See the
[integration path](repo-governance/development/workflow/integration-path.md). Use
[Conventional Commits](repo-governance/development/workflow/commit-messages.md) with one purpose per commit under
[thematic commits](repo-governance/development/workflow/thematic-commits.md). Commit and push are separate permissions
the owner grants; see [commit authorization](repo-governance/development/workflow/commit-authorization.md).

Never add AI or harness attribution to a commit or pull request: no `Co-Authored-By` trailer naming a model or harness
and no "Generated with" line. Never amend, rebase, or force-push existing commits without the owner's explicit
instruction for that instance; see
[no destructive git operations](repo-governance/development/workflow/no-destructive-git-operations.md). The hooks run
public-safety screening and commitlint on commit, and `test:quick`, `test:integration`, and `test:e2e` for affected
projects on push. Fix a failing hook at its cause; never bypass it.
