# How This Was Built

This page states how the repository was made, so that no reviewer has to guess. It claims nothing beyond what the owner
has stated, or what the git history and [WORKLOG](../../WORKLOG.md) show.

## Who Wrote What

The owner paired extensively with an AI coding harness, and well over 95% of the code was written by it. The brief
allows this: "AI tools are permitted and expected", and the assessment is "a 45-minute live defense with no AI present"
([brief](../../challenge-raw.md)).

The owner set the direction and made every material decision. Each open question was put to the owner as one question
with one recommended option, under the [grill-me skill](../../.agents/skills/grill-me/SKILL.md), and the owner chose.
The decisions are recorded where a reviewer can check them:

- [AMBIGUITIES](../../AMBIGUITIES.md): 38 readings of the brief, each with its options, the one first recommended, and
  the resolution. Nine were resolved against the recommendation; the
  [defense index](../reference/defense-index.md#decisions-against-the-first-recommendation) lists them.
- The decision records of the two delivered plans: 30 in the [first build][first-plan], and 22 in the [restructure
  around the domain][restructure-plan].
- [REJECTED](../../REJECTED.md): the brief's acceptance criteria the design refuses, and the approaches abandoned.

## Why Python

In the owner's words, Python is a middle ground: one of the most widely used programming languages. The git history
shows the repository began with an F# command-line skeleton (`e7fcde0`, 11:59 on 2026-09-24), rewritten in Python
(`8980cf4`, 13:17) before any ledger code was written. The
[Python standards](../../repo-governance/development/quality/stacks/python-standards.md) then set how the Python is
written, and the [Python crash course](python-crash-course.md) explains each feature the code uses and why.

## Time Against the Brief's Budget

The brief gives 48 hours and budgets "roughly 1–2 hours of design thinking, 2 hours of building, and the rest for
documentation". Design and building ran far past the three to four hours budgeted for them, inside the 48 hours:

- The repository's scaffolding, its governance, hooks, and tooling, was committed from 10:00 to 13:50 on 2026-09-24,
  before any ledger work; WORKLOG claims none of it.
- Before this documentation was written, WORKLOG's 58 entries ran from 13:56 on 2026-09-24 to 23:11 on 2026-09-25. With
  overlapping entries counted once, they span about 23 hours 51 minutes.
- Those hours cover design, building, documentation, and a restructuring around the domain, planned and executed as its
  own plan; WORKLOG names each section.

## What This Documentation Is For

The pages in this folder exist so the owner, whose last role was in engineering leadership rather than hands-on coding,
can learn the work rather than recite it, and can answer from the repository alone in a defense where no AI is present.
They add no rule and no figure: each points to the document that owns it, and every command and output they show was
run.

## Where to Start

- [Python crash course](python-crash-course.md): the language features, where they are used, and why.
- [Code walkthrough](code-walkthrough.md): one run, from the command line to the report, with a sequence diagram per
  case.
- [Fees and interest](fees-and-interest.md): the end-of-day logic behind 285.76 and 10.008.
- [Change the stream and watch](../tutorials/change-the-stream-and-watch.md): eight experiments on the real program.
- [Fix the known weakness](../how-to/fix-the-known-weakness.md): the deliberately failing test, and its fix.
- [Defense index](../reference/defense-index.md): likely questions and where each is answered.

[first-plan]: ../../plans/done/2026-09-25__in-memory-account-ledger-init/tech-docs/005-decision-records.md
[restructure-plan]: ../../plans/done/2026-09-25__restructure-around-the-domain/tech-docs/007-decision-records.md
