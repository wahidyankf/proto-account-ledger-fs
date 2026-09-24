---
description: >-
  Indexes the structure conventions, which govern how files, directories, and multi-document sets are shaped and named,
  how governance and plans are organized, and how repositories relate.
when_to_use: >-
  Use when naming a file, laying out a directory or repository, splitting a document, or shaping a plan.
---

# Structure Conventions

Structure conventions answer where something goes and what it is called. They exist because a reader — human or agent —
should be able to predict a path before opening it, and a validator should be able to check that prediction
mechanically.

| Convention                                                  | Governs                                                                                  |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [Artifact Metadata](artifact-metadata.md)                   | the frontmatter every governed artifact family carries                                   |
| [File Naming](file-naming.md)                               | how files and directories are named, and how a document splits                           |
| [Repository Configuration](repository-configuration.md)     | what a repository is, and what must pass before a change lands                           |
| [Plans](plans.md)                                           | the plan system: lifecycle, documents, delivery, and archival                            |
| [Plan Specification Changes](plan-specification-changes.md) | how a plan states its specification and architecture delta                               |
| [Plan Migrations](plan-migrations.md)                       | how a plan preserves data and structure through a transition                             |
| [Command-Line Interface](command-line-interface.md)         | the exit vocabulary, streams, and output a tool owes its callers                         |
| [Directory Indexes](directory-indexes.md)                   | the README index every indexed directory carries                                         |
| [Document Word Budget](document-word-budget.md)             | the word ceiling on instruction and governance documents, and repair                     |
| [Documentation Architecture](documentation-architecture.md) | where documentation lives and the one mode each page serves                              |
| [Governance Layers](governance-layers.md)                   | what each governance level answers and which level wins a conflict                       |
| [Monorepo Layout](monorepo-layout.md)                       | dependency direction and project boundaries inside a monorepo                            |
| [Project READMEs](project-readmes.md)                       | what a project's root README covers, and what it leaves to its specification             |
| [Related Repositories](related-repositories.md)             | parity, consumption, and knowledge-sharing relationships                                 |
| [Specification Tree](specification-tree.md)                 | one specification corpus per logical owner, fully specified for Gherkin, C4, and OpenAPI |
| [Temporary Files](temporary-files.md)                       | where scratch files and reports go, and how they are named and written                   |

## Directory Map

- [Artifact Metadata](artifact-metadata.md)
- [Artifact Metadata Modules](artifact-metadata/README.md) — schemas by path, shared value rules, and the portable tiers
  and capabilities
- [File Naming](file-naming.md)
- [File Naming Modules](file-naming/README.md) — portable characters, dated and numbered names, and source filenames
- [Repository Configuration](repository-configuration.md)
- [Repository Configuration Modules](repository-configuration/README.md) — the top-level schema, gate entries, surfaces
  and mutation, and governance categories
- [Plans Convention](plans.md)
- [Plans Convention Modules](plans/README.md) — eighteen modules, from lifecycle and required documents to learning
  triage and routing
- [Plan Validator Contract](plan-validator-contract.md) — the frozen inputs, rule identifiers, messages, and exit
  classes of plan-structure validation
- [Plan Validator Contract Modules](plan-validator-contract/README.md) — inputs and exits, rule identifiers, the fixture
  corpus, and exclusions
- [Plan Specification Changes](plan-specification-changes.md)
- [Plan Migrations](plan-migrations.md)
- [Plan Migrations Modules](plan-migrations/README.md) — the source inventory and contracts, then transition and
  recovery
- [Command-Line Interface](command-line-interface.md)
- [Command-Line Interface Modules](command-line-interface-details/README.md) — the seven interface modules
- [Directory Indexes](directory-indexes.md)
- [Document Word Budget](document-word-budget.md)
- [Documentation Architecture](documentation-architecture.md)
- [Governance Layers](governance-layers.md)
- [Monorepo Layout](monorepo-layout.md)
- [Project READMEs](project-readmes.md) — the sections of a project README and its boundary with the specification
- [Related Repositories](related-repositories.md)
- [Specification Tree](specification-tree.md) — corpus placement, required files, and as-built architecture
- [Temporary Files](temporary-files.md) — designated directories, collision-free names, and progressive reports
