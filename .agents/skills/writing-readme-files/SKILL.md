---
name: writing-readme-files
description: >-
  Supplies a root README section template and repairs for the most common README mistakes, applying the README
  conventions without restating their rules.
when_to_use: >-
  Use when starting a README from nothing, or when repairing one that buries its purpose, repeats other documents, or
  loses readers in jargon.
compatibility: Requires read access to the project the README describes and the documents it links.
---

# Writing README Files

[README Quality](../../../repo-governance/conventions/writing/readme-quality.md) and its modules own every README rule:
navigation, plain language, paragraph length, and the sections each kind carries. Project READMEs owns what a project
README covers, [Directory Indexes](../../../repo-governance/conventions/structure/directory-indexes.md) owns index
READMEs, and Docs Propagation owns keeping a README true as its project changes. This skill supplies shape and repairs;
where it and a convention seem to differ, the convention wins.

## Decide the Kind First

| The README introduces     | Its shape comes from                                                                                                        |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| a whole repository        | the root order in [Required Sections](../../../repo-governance/conventions/writing/readme-quality/003-required-sections.md) |
| an application or library | Project READMEs                                                                                                             |
| a directory of documents  | Directory Indexes                                                                                                           |

A README that tries to be two kinds, such as a root README summarizing every component, holds copies that belong to the
component READMEs.

## Root README Template

Every placeholder is replaced with real content or its section is removed; no heading ships with nothing beneath it.

```markdown
# <Name>

<One sentence: what this is, named plainly.>

## Motivation

<The situation a reader is in, then what this does about it, in two or three short paragraphs.>

## Quick Start

<Prerequisites, stated explicitly.>

<Copy-paste installation.>

<A command whose output confirms setup worked.>

## Features

- <A benefit to the reader, then how it is delivered.>
- [Complete feature list](link)

## Usage

<The most common use, as a real, runnable example.>

## Documentation

- [<Guide or reference title>](link) — <what a reader finds there>

## Contributing

<A short invitation.> See [Contributing](CONTRIBUTING.md).

## License

<License name>. See [License](LICENSE).
```

## Repairs for Common Mistakes

| The README                                                       | Repair                                                                          |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| opens with a feature list                                        | move the situation it serves to the top, then say what it does about it         |
| leaves an acronym bare                                           | expand it at first use and add what the thing is or does                        |
| uses a term only insiders know                                   | use the everyday word, or define the term once where it first appears           |
| has a paragraph that runs on                                     | split it into paragraphs that each make one point, or into a list               |
| reproduces its reference documentation                           | cut each section to a short summary and link the document that holds the detail |
| carries a paragraph copied from another document                 | keep a summary written for this README and link the original                    |
| lists endpoints, routes, or payload shapes                       | name each interface and link its specification                                  |
| praises itself with adjectives                                   | replace each with a checkable claim about the reader's situation, or delete it  |
| starts setup without a quick start, or ends without verification | add the minimal path and finish it with a command that proves success           |
| shows a command that calls a tool directly                       | show the repository's declared task entry point, run from the root              |
| holds a command nobody has run lately                            | run it now; fix it or remove it                                                 |

To find a copy, ask whether this README would need the same edit if the linked document changed. If it would, it holds a
copy, not a summary.

## Before Publishing

Run every command exactly as written, follow every link, then give the final newcomer read to
[applying-content-quality](../applying-content-quality/SKILL.md), which covers it for every document.
