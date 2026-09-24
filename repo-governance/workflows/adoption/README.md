---
name: adoption
description: >-
  Indexes the two adoption workflows: comparing a repository against the catalog, and copying named artifacts into it on
  explicit request.
when_to_use: >-
  Use when comparing a repository with this catalog, or when adopting a named artifact from it.
---

# Adoption Workflows

Two workflows, and the boundary between them is the point of the design: one reads and one writes, and nothing crosses
from the first into the second without a person asking.

| Workflow                                | Writes                                                  |
| --------------------------------------- | ------------------------------------------------------- |
| [Assess Alignment](assess-alignment.md) | nothing                                                 |
| [Adopt Artifact](adopt-artifact.md)     | only the artifacts a user named, plus their integration |

An assessment that could adopt would make every comparison a negotiation about whether to change something. Keeping the
read strictly read-only is what makes it safe to run on any repository at any time.

## Directory Map

- [Assess Alignment](assess-alignment.md)
- [Adopt Artifact](adopt-artifact.md)
