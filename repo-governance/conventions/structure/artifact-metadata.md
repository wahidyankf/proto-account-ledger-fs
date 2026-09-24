---
description: >-
  Defines the frontmatter schema each governed artifact family carries, selected by path, and the portable vocabularies
  agent metadata may use.
when_to_use: >-
  Use when adding frontmatter to a governance document, workflow, skill, or agent, or when validating existing metadata.
---

# Artifact Metadata

Metadata exists to help discovery, routing, validation, and adapter generation. Nothing else earns a field.

The path selects the schema. That is why no artifact declares its own type: repeating what the path already says costs
context on every read and creates a second place for the answer to be wrong.

## Modules

1. [Schemas by Path](artifact-metadata/001-schemas-by-path.md)
2. [Shared Value Rules](artifact-metadata/002-shared-value-rules.md)
3. [Portable Tiers](artifact-metadata/003-portable-tiers.md)
4. [Portable Capabilities](artifact-metadata/004-portable-capabilities.md)

## Scope

In scope: live governance Markdown, canonical agent definitions, canonical skills, and generated harness adapters. A
governance directory `README.md` is in scope, because it is a live entrypoint rather than decoration.

Out of scope: plans, product documentation, changelogs, release notes, archived history, and root or application
READMEs. Those are read by people for reasons metadata does not help with.
