---
description: >-
  Owns the rules specific to README files: a navigation document of short summaries that link out, plain language, short
  paragraphs, and the sections each kind of README carries.
when_to_use: >-
  Use when writing, reviewing, or restructuring any README, or when a README has started explaining what another
  document already covers.
---

# README Quality

A README is a navigation document. Its job is to tell a reader what is here, why it matters, and where the details are —
not to be the details.

This convention owns the rules specific to READMEs. Rules every document follows — voice, headings, formatting,
accessible content, and emoji — stay with the conventions that own them, and the modules link to those rather than
restating them. A template, checklist, or repair procedure for READMEs supplies shape and links here; it does not
restate these rules, because a rule copied into a template is a rule with two versions.

## Modules

1. [Navigation and Scannability](readme-quality/001-navigation-and-scannability.md)
2. [Plain Language](readme-quality/002-plain-language.md)
3. [Required Sections](readme-quality/003-required-sections.md)

## Scope

Every `README.md`: a repository's root README, a component's README, and a directory index.

What each kind is for differs; how it reads does not. The first two modules apply to all of them, and the third says
what each kind contains.

A governed directory index also carries the frontmatter its schema requires — see
[Artifact Metadata](../structure/artifact-metadata.md). That schema decides the frontmatter; this convention decides how
the body reads.

## Why a Navigation Document

A README is the first document most readers open, and the one most often opened without a specific question. Detail
placed there is read by everyone and needed by few. It is also duplicated from wherever that detail properly lives, so
it becomes the copy that goes stale first, in the most visible place.

Summaries that link out keep a README short enough to be read to the end, and keep each detail in one place where it can
be corrected once — see [One Source Per Fact](../../principles/one-source-per-fact.md).

## Maintenance

A README changes in the same change as the thing it summarizes. A command, example, or link in it is verified when
written and re-verified when its target changes. An example that no longer runs is worse than none, because the reader
trusted it.

## Enforcement

An adopter checks README links and Markdown structure with its own link checker and linter in its own gate. Summary
balance, duplication, and plain language are review judgements, and review checks them against this convention.
