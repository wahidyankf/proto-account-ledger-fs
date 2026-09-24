---
description: >-
  Requires a governance category outside the shared registry to be declared in configuration, and forbids creating an
  empty directory for one.
when_to_use: >-
  Use when a repository needs a governance category the shared set does not provide.
---

# Governance Categories

The governance tree has a shared set of layers, and most repositories need nothing beyond it. A repository that does
declares the addition rather than simply creating a directory.

## Declared, Not Inferred

A category outside the shared registry is accepted only when the consuming repository declares it in its governance
layer policy under `policies.governance.layers.categories`. An undeclared category fails.

Inferring categories from directories sounds friendlier and removes the only moment anyone considers whether the
category should exist. A typo becomes a category. A directory left behind by an abandoned experiment becomes a category.
Nothing ever fails, and after a year the tree has fourteen layers, four of which hold one file each.

Declaring one is deliberately a small piece of friction, applied exactly once, at the moment the decision is being made.

## No Empty Directories

Declaring a category does not create a directory, and an empty governed directory fails.

A directory exists because it holds something. An empty one is a promise about future content, and a reader who opens it
learns only that someone intended to write something. Where the intention is real, an idea brief records it; where it is
not, the directory is the only evidence the thought ever occurred.

The same applies to the shared layers: a repository with no workflows has no `workflows/` directory, and that is a true
statement about the repository rather than a gap in it.

## Local Categories Are Local

A declared local category is the declaring repository's. It does not propagate, and another repository that wants the
same category declares it too.

That looks like duplication and is the correct amount of it. Two repositories with a category of the same name may mean
different things by it, and a shared registry entry would assert an agreement neither made.

## Promotion Is Explicit

A local category several repositories independently declared may be worth promoting into the shared set. That is a
deliberate change to the shared contract, argued on its merits.

It does not happen automatically on a count. Three repositories choosing the same word is evidence, not a decision.
