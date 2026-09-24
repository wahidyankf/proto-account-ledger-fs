# Plans

Plans are this repository's working record of change: why work exists, what it depends on, and what evidence proves it
finished. They are not documentation. `docs/` explains the repository to a reader and `repo-governance/` holds its
rules; a plan describes one piece of work and retires when that work lands.

Plan documents are created only when the owner explicitly requests a plan. The
[plans convention](../repo-governance/conventions/structure/plans.md) owns structure, naming, checklist rules, and
archival.

## Directory Map

- [`ideas/`](ideas/README.md) — two-page briefs for problems not yet worth a plan.
- [`backlog/`](backlog/README.md) — full plans prepared but not started.
- [`in-progress/`](in-progress/README.md) — plans under active execution.
- [`done/`](done/README.md) — completed plans, kept as history.

## How a Plan Runs

1. [plan-planning](../repo-governance/workflows/plan/plan-planning.md) explores, grills every open decision with
   options, and writes the six-document plan into `backlog/`.
2. [plan-quality-gate](../repo-governance/workflows/plan/plan-quality-gate.md) reviews it when the owner asks and must
   return `PASS` before execution starts.
3. [plan-execution](../repo-governance/workflows/plan/plan-execution.md) moves it to `in-progress/` and executes it
   phase by phase.
4. [plan-execution-check](../repo-governance/workflows/plan/plan-execution-check.md) must pass before the plan moves to
   `done/`.

Delivery goes directly to `main`: a phase ends, its gate passes, the work is committed and pushed. There are no task
branches and no pull requests, per the [integration path](../repo-governance/development/workflow/integration-path.md).
