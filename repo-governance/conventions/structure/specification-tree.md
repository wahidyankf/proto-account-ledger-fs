---
description: >-
  Fixes one specification corpus per logical owner, each holding an index, an as-built architecture document, and a tree
  of behaviour specifications, executable features in the fully specified case.
when_to_use: >-
  Use when placing or reviewing a specification corpus in any declared form, most fully when behaviour is Gherkin,
  architecture is C4, and HTTP contracts are OpenAPI.
---

# Specification Tree

This convention applies to any specification corpus a repository declares. Its fully specified case is a repository that
writes behaviour as Gherkin features, describes architecture with the C4 model's zoom levels, and publishes HTTP
contracts as OpenAPI documents; Other Specification Forms, below, covers the rest. It fixes where each of those lives,
so a reader finds the specification for a deployable without searching and a structure check can confirm it is complete.

## One Corpus Per Logical Owner

| Owner                           | Corpus                          |
| ------------------------------- | ------------------------------- |
| a deployed surface of a product | `specs/apps/<product>/<owner>/` |
| a library                       | `specs/libs/<library>/`         |

A logical owner is something that deploys and runs on its own: a web front end, a backend service, a command-line tool.
Two perspectives on one deployable, such as an administrator console served by the same service as its public pages, are
one owner with one corpus.

A corpus per product would mix scenarios that different deployables must satisfy, so no single test run proves it and a
change to one surface forces a review of the rest. A corpus per perspective would split an architecture that is in fact
one system.

## Inside a Corpus

```text
specs/apps/<product>/
├── overview.md           optional: what spans the product's owners
└── <owner>/
    ├── README.md         required: the index, linking back to the project
    ├── architecture.md   required: the as-built C4 description
    ├── behaviours/       required: .feature files at any depth, with a README.md
    │   └── <domain>/     optional: a business-area grouping
    └── contracts/        optional: OpenAPI documents, in the owner that serves them
```

- **`behaviours/` is never empty.** At least one `.feature` file sits somewhere below it. A corpus with no scenario
  states nothing a test can check.
- **Domain directories only group.** They sort features by business area, are optional, and carry no meaning a tool
  relies on.
- **A contract lives with its server.** `contracts/` belongs to the owner that serves the interface. A consumer links to
  that contract; a copy in the consumer is a second contract that drifts.
- **`overview.md` spans owners.** It sits at product level, says how the owners fit together, and holds no scenario and
  no architecture.

A library corpus has the same shape without the product level.

## Architecture Is As-Built

`architecture.md` describes the system as it runs, not as someone proposed it. Each zoom level the owner needs — system
context, containers, components — is a section of that one document rather than a file of its own, so the levels move
together.

It changes in the same delivery unit that changes what it describes. A proposed change stays in its plan until then, as
[Plan Specification Changes](plan-specification-changes.md) requires.

## Indexed Throughout

A repository adopting this convention indexes its specification tree, with every file type counted, per
[Directory Indexes](directory-indexes.md). A feature file absent from its index is a scenario nobody browsing the tree
will find. The project side of each corpus follows [Project READMEs](project-readmes.md), whose README links here and is
linked back.

An adopter enforces the required files, non-empty behaviours, and index completeness with its own structure check in
pre-commit or CI.

## Other Specification Forms

A repository that uses only part of this stack, or other forms, still applies one corpus per logical owner, the index,
and the as-built rule, since none of them depends on a format. Its `architecture.md` uses the repository's declared
notation, `contracts/` holds whatever contract format the owner serves, and `behaviours/` holds the owner's behaviour
specifications in the declared form. Only the requirement that they be `.feature` files belongs to the format.

## Principles

This convention implements [One Source Per Fact](../../principles/one-source-per-fact.md), because each contract and
each architecture has exactly one corpus that owns it, and
[Evidence Over Assertion](../../principles/evidence-over-assertion.md), because a corpus states behaviour as
specifications, executable where its form allows, rather than prose claims about behaviour.
