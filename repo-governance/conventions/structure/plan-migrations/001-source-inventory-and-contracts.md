---
description: >-
  Requires a migration plan to list every affected source before its steps, to diagram a changed persistent data model,
  and to explain each resulting field in plain language.
when_to_use: >-
  Use while a migration plan's source list is being drafted, or whenever a plan adds, alters, or drops a persistent
  schema.
---

# Source Inventory and Contracts

## Inventory Every Source

The inventory is written before the first migration step, with one entry per affected source:

| Field               | Records                                                               |
| ------------------- | --------------------------------------------------------------------- |
| location or key     | the precise path, key, or table                                       |
| readers and writers | each command, job, service, hook, or document that reads or writes it |
| accepted shape      | its present format, version marker, and limits                        |
| owner               | the component or rule responsible for it                              |
| destination         | where it ends up, exactly, or a stated retirement                     |
| compatibility       | what a consumer still on the old shape sees during the change         |
| disposition proof   | which `delivery.md` item demonstrates the entry was handled           |

Every later step is checked against this list, which is why it comes first. Steps planned from recollection of who uses
a source leave out the consumer nobody recalled, and that consumer is the last to fail.

List the sources that actually exist, found by looking, not the ones expected to exist. Link to evidence in the
repository where doing so is safe. A credential, token, personal value, or private runtime value never goes into the
plan, a fixture, or version control.

## Data-Model Changes

When a plan adds, alters, or drops a persistent schema, a diagram of the data model sits next to the exact contract,
drawn in the form the repository's [Diagrams](../../writing/diagrams.md) rule sets.

| Model                                | The diagram shows                                                                      |
| ------------------------------------ | -------------------------------------------------------------------------------------- |
| relational                           | the entities involved, their primary, foreign, and unique keys, links, and cardinality |
| document, key-value, event, or graph | the records involved, their keys and references, and where ownership changes hands     |

Even a change to one entity draws that entity, together with the keys and neighbouring ownership a reader needs to make
sense of it.

The diagram helps a reader understand; it is not the contract. Old and new field definitions, with each type,
constraint, and default, are still written out exactly, as are compatibility, validation, the migration itself,
rollback, and tests. Anything critical is stated in prose a search can find, not only in the picture.

## Field Guide

Each schema contract includes a plain-language entry for every column, property, or key of each resulting table or
record, stating:

- what it is for;
- what produces it, or who owns it;
- the shape of its values, with a unit or timezone where relevant;
- whether it is required, how it treats null, and its default;
- whether it is a primary, foreign, or unique key, or a reference;
- how sensitive it is; and
- when it is created, updated, and cleared, and how long it is kept.

The schema remains the authority on types and constraints. The guide is there because names mislead: a field called
`balance` does not say in which currency, whether pending entries are included, or who may change it, and two
implementers left to guess will not guess alike.
