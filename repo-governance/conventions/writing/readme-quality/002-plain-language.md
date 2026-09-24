---
description: >-
  Requires plain language in READMEs: everyday words over jargon, acronyms given context beyond their expansion,
  sentences addressed to the reader, and benefits stated for the reader.
when_to_use: >-
  Use when README wording leans on jargon, leaves an acronym unexplained, or takes the reader's knowledge of the project
  for granted.
---

# Plain Language

A README is read by people who do not yet share the project's vocabulary: new contributors, evaluators, and readers
working in a second language. Pitch the text at an expert in the subject who is meeting this project for the first time.

## The Why Before the What

The opening of a README, and of any motivation section, states the problem before the solution — the situation this
exists for — so a reader can decide within two sentences whether they are in that situation.

## Everyday Words Over Jargon

| Instead of                  | Write                                       |
| --------------------------- | ------------------------------------------- |
| utilize, leverage           | use                                         |
| solution                    | tool, library, or service — whichever it is |
| best-in-class, cutting-edge | a specific, checkable claim, or nothing     |
| paradigm shift              | new approach                                |

Where a technical term is exact and no plain word is, use the term and define it once, on first use.

## Acronyms Get Context, Not Just Expansion

[Voice and Clarity](../content-quality/001-voice-and-clarity.md) requires an acronym to be defined at its first use. A
README goes further: give what the acronym stands for **and** what the thing is or does:

```markdown
- Trunk-based development (TBD) — everyone integrates small changes into one main branch, often
```

An expansion alone tells the reader the words, not the idea. For a term from another language, lead with its meaning in
the README's language and give the original name after it.

## Addressed to the Reader

Active voice follows [Voice and Clarity](../content-quality/001-voice-and-clarity.md). A README also addresses its
reader directly: "Run `npm test` to check your setup", not "The setup can be verified by running the tests". Prefer the
verb to its noun — "validate", not "perform validation". Do not hedge deterministic behaviour: a command that always
does something "does" it, not "may do" it.

Keep sentences short.

## Benefits, Not Just Features

Say what the reader gains, then how. "Your data stays in plain files you can open anywhere" tells a reader why to care;
"file-based storage backend" leaves them to work it out. Highlight the three to five benefits that matter most, and link
to the complete feature list.

This is not marketing. A benefit is a checkable claim about the reader's situation. An adjective such as "powerful" is
not a claim at all, and belongs in neither form.

## Invite, Do Not Command

A README welcomes its reader — "Here is how to get started", rather than "You must follow these steps exactly". The
instructions stay precise: invitation changes the tone, never the accuracy.
