---
name: adopt-artifact
description: >-
  Guides mapping a named catalog artifact into a target repository's own ownership, preserving stronger local rules and
  refusing contradictions.
when_to_use: >-
  Use only after a user has explicitly named an artifact or bounded family to adopt into a specific repository.
compatibility: Requires write access to the target repository and read access to the catalog.
---

# Adopting an Artifact

The [Adopt Artifact](../../../repo-governance/workflows/adoption/adopt-artifact.md) workflow owns the sequence,
including source resolution and provenance. This is about the adaptation itself.

## Adoption Is Intent-First

The artifact was written for no particular repository. The target has paths, names, tooling, and constraints the
artifact knows nothing about.

Mapping it means asking what the artifact is for and how this repository would express that — which layer it belongs to,
what it should be called here, what it must reference locally. Copying the file verbatim produces something that reads
as foreign and is followed as optional.

## Never Loosen the Target

Where the local rule is stricter, the local rule survives. Adoption adds capability; it does not trade a repository's
existing guarantees for consistency with a catalog.

This is easy to violate by accident, because a catalog artifact usually looks more complete than the local rule it
touches. More complete is not stronger.

## Refuse Contradictions

An artifact that genuinely conflicts with a local rule stops and reports. Do not overwrite the local rule; do not
silently weaken the artifact until it fits.

Both of those produce a repository whose rules no longer say what its maintainers decided, and the difference will be
discovered by someone following one of them.

## Stay Inside the Scope

Change the named artifacts and the binding, index, or configuration edits they genuinely need to function. Nothing else.

Adoption passes through code that could be improved. Note it; leave it. A change nobody requested, mixed into a change
they did, makes the whole thing harder to review and harder to revert.

## The Copy Belongs to the Target

Once adopted, the artifact is the target repository's. It may be edited, extended, or eventually contradicted, and
nothing checks it against the catalog afterwards.

The provenance trailers say where it came from. They are a fact about history, not a commitment about the future.
