---
description: >-
  Indexes this repository's governance artifacts by the level of authority each one carries, from vision down to
  workflows.
when_to_use: >-
  Use when locating a governance artifact or deciding which authority level a new one belongs to.
---

# Repository Governance

This repository's governance artifacts, organized by the level of authority each one carries. Most are adopted copies
from the `ose-rules` catalog (`github.com/wahidyankf/ose-rules`); each adoption commit names its sources and the catalog
commit in `OSE-Rules-Source` and `OSE-Rules-Commit` trailers. After adoption this repository owns its copy.

Levels are compared in order — `vision > principles > conventions > development > workflows` — and a lower level never
contradicts a higher one. Placing an artifact is therefore a decision about what kind of statement it is, not about
where it happens to fit.

| Level          | Holds                                                            |
| -------------- | ---------------------------------------------------------------- |
| `principles/`  | durable constraints that outlive any particular repository       |
| `conventions/` | repository choices — the decisions a repository makes for itself |
| `development/` | engineering standards and practices                              |
| `workflows/`   | procedures: the ordered steps for doing a thing                  |

## Directory Map

- [Principles](principles/README.md)
- [Conventions](conventions/README.md)
- [Development](development/README.md)
- [Workflows](workflows/README.md)

`vision/` is named in the ordering above and is not published here. A repository has no directory for a level it holds
nothing at: an empty governed directory is a promise about future content, and a reader who opens one learns only that
somebody intended to write something.
