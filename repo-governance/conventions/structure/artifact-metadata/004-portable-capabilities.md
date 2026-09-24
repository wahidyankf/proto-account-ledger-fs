---
description: >-
  Restricts agent capabilities to a closed five-value vocabulary in canonical order, keeping tool and vendor names in
  adapters.
when_to_use: >-
  Use when declaring what an agent needs, or when a tool or permission name is proposed as a capability.
---

# Portable Capabilities

An agent's `capabilities` list draws only from this closed vocabulary, in this order:

1. `repository-read`
2. `repository-write`
3. `shell`
4. `network`
5. `subagent`

Nonempty, unique, canonical order. A value outside the list fails.

## What These Say

They describe what the agent needs to be able to do, in terms that survive changing harness. `repository-write` means
this agent modifies the repository — which matters to a reviewer, to a permission model, and to anyone deciding whether
to run it.

`shell` is separate from `repository-write` because the blast radius differs: one changes tracked files, the other can
do anything the user can.

## What Stays in the Adapter

Harness tool names, MCP server names, permission keys, colours, modes, and vendor options are not portable and do not
belong in canonical metadata.

They change per harness and per version. An agent declaring them describes one harness's configuration, which means the
canonical file has quietly become an adapter — and the actual adapters then have two sources.

The generator's job is exactly this translation: `shell` becomes whatever this harness calls a shell tool. That mapping
lives in one place and is updated once when a harness changes.

## Declare What Is Needed, Not What Is Available

An agent that reads and reports declares `repository-read`, not `repository-write` because writing might one day be
convenient.

The list is read as a claim about blast radius. Padding it makes every review of that agent more expensive and every
constraint on it less believable.

## Constraints Are Separate

`constraints` records what an agent must not do — `read-only` on a checker, for instance — even where its capability
list already implies it.

The redundancy is deliberate. A capability list says what was granted; a constraint says what was decided, and the
second survives someone adding a capability without reading why the first list was short.
