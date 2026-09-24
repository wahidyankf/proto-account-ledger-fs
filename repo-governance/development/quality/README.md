---
description: >-
  Indexes the quality standards: how work is verified and what counts as evidence that it holds; how code is designed,
  tested, contracted, checked, delivered, and kept accessible; and the rules a language or framework stack adds.
when_to_use: >-
  Use when deciding how a change will be verified, or what a piece of evidence has to contain, or which design, code,
  testing, contract, delivery, accessibility, stack, or repository-check standard applies.
---

# Quality Standards

Verification standards. They answer what proves a change works, and what a proof has to look like to be worth anything
to someone who was not there when it was produced. Design, code, testing, contract, delivery, interface, stack, and
repository-check standards sit alongside them.

## Directory Map

- [Architecture and Contracts](architecture/README.md) — architecture models, application structure, and published
  interfaces
- [Checks and Gates](checks/README.md) — rule enforcement, which gate runs each check, strictness, validators, and what
  a new check needs
- [Deletion With Proof](deletion-with-proof.md) — what must be demonstrated before something is removed
- [Evidence](evidence/README.md) — finding ratings, grounded plan claims, measurement, specifications, failing gates,
  and preserved content
- [Manual Verification](manual-verification.md) — the layers automation cannot reach, behaviour-change checks, coverage,
  and the evidence they produce
- [Manual Verification Modules](manual-verification/README.md) — eight modules, from gate results to usability probes
- [Stacks](stacks/README.md) — per-language and per-framework gates, defaults, and design rules, adopted only with that
  stack
- [Testing](testing/README.md) — test layers and gates, test-first work, and API, behaviour, and end-to-end tests with
  isolated data
