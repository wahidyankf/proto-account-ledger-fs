---
description: >-
  Fixes the exact frontmatter keys and key order for governance documents, workflows, skills, and agents.
when_to_use: >-
  Use when writing frontmatter, or when deciding whether a proposed field belongs in metadata at all.
---

# Schemas by Path

| Family     | Path                                | Keys, in order                                                                                          |
| ---------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------- |
| governance | `repo-governance/**/*.md`           | `description`, `when_to_use`                                                                            |
| workflow   | `repo-governance/workflows/**/*.md` | `name`, `description`, `when_to_use`                                                                    |
| skill      | `.agents/skills/<name>/SKILL.md`    | `name`, `description`, `when_to_use`, optional `compatibility`                                          |
| agent      | `.agents/agents/<name>.md`          | `name`, `description`, `when_to_use`, `tier`, `capabilities`, optional `skills`, optional `constraints` |

Workflows are governance documents whose path selects the more specific schema.

## Why Governance Documents Have No `name`

The path is the identity. A `name` field would be a second copy of it, and the first time the two disagree there is no
rule for which one wins.

Workflows, skills, and agents carry `name` because they are invoked by it. A reader or a harness needs to know what to
say, and that is a fact about the artifact rather than about where it lives — though it still has to match the path.

## Key Order Is Enforced

The order above is exact, and an out-of-order file fails. This looks pedantic and is not: a fixed order makes the
frontmatter diffable, makes a missing key visible by position, and removes an argument that would otherwise be had in
every review.

## Unknown Fields Fail

Unknown, deprecated, irrelevant, null, and empty fields all fail, as do duplicate keys — checked before a YAML parser
can silently discard one of them.

The list of things deliberately excluded is longer than the list of fields: no type, category, subcategory, location,
title, author, date, version, revision history, status, or tags. Every one of those is either derivable from the path,
recorded better by version control, or a field nobody updates after the first week.

## Naming

Names are lowercase alphanumeric words separated by single hyphens, and must match the path identity: the basename for a
workflow or agent, the directory name for a skill or a group index.
