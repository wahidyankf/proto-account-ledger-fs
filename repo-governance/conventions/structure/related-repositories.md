---
description: >-
  Classifies relationships between repositories as parity, upstream consumption, knowledge sharing, or none, and fixes
  what each obliges, where awareness is recorded, and how a relationship changes.
when_to_use: >-
  Use when naming another repository in instructions, consuming or sharing with one, or changing how two repositories
  relate.
---

# Related Repositories

Naming another repository helps contributors route work. It must not quietly turn that repository into something to keep
in sync. This convention separates relationships that carry obligations from those that carry only navigation.

## Four Classes

| Relationship         | Means                                                  | Obliges                                                                    |
| -------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------- |
| parity               | two repositories keep a declared boundary in agreement | explicit propagation, recorded divergences, and proof by direct comparison |
| upstream consumption | one repository uses another's released output          | a pinned release, local consumer configuration, and no copy of upstream    |
| knowledge sharing    | learnings from one may inform the other                | nothing propagates automatically                                           |
| none                 | a one-off compatibility test or shared tool invocation | no catalogue entry                                                         |

## Parity

A parity relationship names its boundary exactly and names which side is the source of portable changes. The other side
receives them through an explicit sibling obligation, in its own delivery, never by assumption. Each side's local
constraints — access, licensing, delivery, CI — stay local and are recorded as divergences.

Each repository's own check proves only its own side. Agreement is proven by comparing the two sides directly; a clean
local check never proves the sibling matches.

## Upstream Consumption

A consumer uses a pinned, verified release and keeps consumer-specific configuration, mappings, and tests locally.
Upstream source, behaviour specifications, generic tests, and release automation stay upstream and are never copied,
vendored, or forked in.

A copy is a fork nobody decided to maintain. It drifts from the release it claims to match, and the drift is found by
whoever trusts it next.

A repository read only for examples is knowledge sharing: read-only, with local rules governing. Adopting artifacts by
an explicit one-off copy is knowledge sharing too, distinct from consumption: the copied artifacts become locally owned.

## Naming Is Navigation

Naming a repository creates navigation, not parity. No parity check, propagation workflow, or identity manifest widens
to include a repository because it is named.

A collective label for a set of repositories is a routing aid only. It is not an organization, a parent or container
repository, a parity group, or a shared release; members version, gate, and release independently. Membership obliges a
member to name the others so contributors can find them, and nothing more, and every surface using the label says so.

## Awareness Surfaces

| Surface                | Carries                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------- |
| root instruction file  | the related repositories a contributor must know before routing work, with each class |
| `README.md`            | a short relationship summary and a link to the catalogue                              |
| descriptive catalogue  | for each repository: visibility, license, role, ownership boundary, where to start    |
| the adopted convention | the normative rules, which the other surfaces link to rather than restate             |

The catalogue records only relationships contributors need for durable routing.

## Changing a Relationship

1. Classify the relationship first, as one of the four classes.
2. Update the normative convention before the instruction file and the catalogue.
3. Record a sibling obligation only for a portable change crossing a parity boundary.
4. Keep each side's local constraints as explicit divergences.
5. Run the instruction-budget, index, and link checks, and compare both sides of any parity boundary directly.

Placement and parity can be checked mechanically, and an adopter wires those checks into its own gates. Deciding which
repository owns a novel piece of work cannot be, and stays a human judgement recorded where the work is routed — see
Coordination Repository.

## Principles

This convention implements [One Source Per Fact](../../principles/one-source-per-fact.md), because upstream content is
consumed from its release rather than copied, and [Explicit Over Implicit](../../principles/explicit-over-implicit.md),
because every obligation between repositories is declared rather than implied by naming.
