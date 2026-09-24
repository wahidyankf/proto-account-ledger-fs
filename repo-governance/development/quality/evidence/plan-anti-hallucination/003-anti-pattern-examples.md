---
description: >-
  Illustrates the recurring ways plans invent facts, each paired with the check that would have caught it, as supporting
  examples for the grounding and evidence rules.
when_to_use: >-
  Use when reviewing a plan for invented references, or when a claim resembles a known failure and needs the matching
  check.
---

# Anti-Pattern Examples

These examples support the rules in [Grounding and Labels](001-grounding-and-labels.md) and
[Absence and Completeness](002-absence-and-completeness.md). They add no rule; each shows what an invented claim looks
like and the check that exposes it.

## Invented References

| Anti-pattern                         | Looks like                                                         | Check that catches it                                   |
| ------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------- |
| a version stated from memory         | "upgrade from version 4", when the manifest pins 5                 | read the manifest or lock file                          |
| a path that ought to exist           | "update `<config-directory>/settings.json`", which was never there | list the directory at the current commit                |
| a command target that is assumed     | "run the `lint:strict` target"                                     | read the target definitions or the tool's listing       |
| a function or method name that fits  | "call `validateAll()`" where the real function has another name    | find the definition in the source                       |
| a numeric target with no baseline    | "cut build time by 40 percent"                                     | measure a baseline first, or label it `[Judgment call]` |
| a test name that sounds right        | "extend the `handles-empty-input` test"                            | find the test in the test files                         |
| an agent or skill nobody defined     | "delegate to the release checker agent"                            | confirm the definition file exists                      |
| a flag taken on trust                | "pass `--fix-all`"                                                 | read the installed tool's help output                   |
| a behaviour claim with no source     | "the library retries three times by default"                       | cite the documentation with URL, date, and excerpt      |
| a link to a file that does not exist | a relative link to a guide that was renamed                        | resolve every link before writing                       |

## Invented Evidence

| Anti-pattern                                   | Looks like                                                        | Check that catches it                                          |
| ---------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------- |
| a zero result treated as proof                 | "no references remain", from a search whose errors were discarded | record the command, inspect the status, run a positive control |
| completeness from a text search                | "every service is listed", because a search found each listed one | diff against the set from its owning authority                 |
| a sweep that validates itself                  | a rule change confirmed by re-running the pattern used to edit it | sweep by inbound link with a different instrument              |
| a validator result without its real invocation | "the checker passes", from a target that runs nothing             | confirm the invocation, then run it                            |

## What the Examples Share

Every example reads as fluent and plausible, and none would fail a reading review. Each was caught only by a check
against something outside the author's memory: the repository, the tool, or an authoritative source.
