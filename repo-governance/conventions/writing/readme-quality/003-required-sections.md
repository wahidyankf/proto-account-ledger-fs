---
description: >-
  Fixes what a repository's root README contains and in what order, and how a component README and a directory index
  README are shaped.
when_to_use: >-
  Use when creating a README, or when checking that a root, component, or directory index README has what it needs.
---

# Required Sections

Every README opens with its title and one sentence saying what this is. That sentence is the most-read line in the
directory it introduces, and it names the thing plainly.

## Root README

A repository's root README carries these sections, in this order:

| #   | Section               | Contains                                                                                 |
| --- | --------------------- | ---------------------------------------------------------------------------------------- |
| 1   | Title and description | the name, one or two sentences on what it does, and status badges where a status exists  |
| 2   | Motivation            | the problem it addresses, who it is for, and why it exists                               |
| 3   | Quick start           | prerequisites stated explicitly, copy-paste installation, and a command that verifies it |
| 4   | Features              | the key capabilities as reader benefits, linking to the complete list                    |
| 5   | Usage                 | a real, runnable example of the most common use, linking to fuller documentation         |
| 6   | Documentation         | links to the tutorials, guides, and reference that hold the detail                       |
| 7   | Contributing          | a short invitation and a link to the contributing guide                                  |
| 8   | License               | the license name and a link to the license file                                          |

The order follows the reader's questions: what is it, is it for me, can I run it, what does it do, how do I use it,
where is the rest, how do I help, and may I use it.

Quick start sits near the top because trying the thing is the most common reason to open a root README. It is short
enough to finish in a few minutes — anything longer is a guide, linked from here — and it ends with verification: a
command whose output confirms success. A reader who cannot tell whether setup worked cannot tell whether the next
failure is theirs.

The contributing guide and the license file are defined in Repository Documentation Files.

## Component README

A README for an application, package, or library inside a larger repository carries its title and description, what the
component is for and where it fits, how to run or use it, and links to its detailed documentation.

The root README links to each component README rather than summarizing all of them itself, so each component's summary
has one owner.

## Directory Index README

A README whose job is to index a directory carries:

- the title and a short statement of what the directory holds;
- every child document and child index, each as a link titled with the target's title, followed by a one-line
  description of what a reader finds there; and
- nothing that belongs in the children themselves.

An index that omits a child hides it, and an index that explains a child in full duplicates it. The one line is the
whole budget.
