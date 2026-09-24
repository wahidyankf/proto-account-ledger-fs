---
description: >-
  Indexes the development layer, which holds engineering standards and practices that apply while work is being done,
  and maps each stage of delivering a change to the artifacts that govern it.
when_to_use: >-
  Use when locating an engineering standard, when deciding whether new guidance is a standard rather than a procedure,
  or when finding which artifact governs a stage of delivering a change.
---

# Development

Engineering standards. A convention decides how the repository is arranged; a standard here decides how work inside it
is done well.

| Area        | Holds                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| `agents/`   | standards for the coding-agent capabilities a repository publishes                                          |
| `quality/`  | what proves a change works, what a proof has to look like, and how code is designed, tested, and contracted |
| `workflow/` | the shape of work itself, rather than its subject, from setup through commit and integration                |

## Lifecycle Map

Where each stage of delivering a change is governed. The map adds no rule; each linked artifact owns its own.

| Stage         | Governed by                                                                                                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| idea and plan | [Plans](../conventions/structure/plans.md), [Ideas Grooming](../workflows/plan/plan-ideas-grooming.md), [Planning](../workflows/plan/plan-planning.md), [Plan Quality Gate](../workflows/plan/plan-quality-gate.md) |

## Directory Map

- [Agents](agents/README.md)
- [Quality](quality/README.md)
- [Workflow](workflow/README.md)
