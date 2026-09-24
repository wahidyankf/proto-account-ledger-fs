---
name: applying-content-quality
description: >-
  Guides applying the content quality rules to one Markdown document: which pass to run first, which defects stop a
  reader, and how to repair common defects without changing what the text means.
when_to_use: >-
  Use while drafting, revising, or reviewing a Markdown document for voice, headings, formatting, and accessible
  content, or when choosing which quality repair to make first.
compatibility: Requires read access to the document and to the conventions it links.
---

# Applying Content Quality

[Content Quality](../../../repo-governance/conventions/writing/content-quality.md) owns the rules for voice, headings,
accessible content, formatting, and time estimates, and its Owned Elsewhere table routes colour, diagrams, links, emoji,
and facts to their own conventions. This skill covers the judgement of applying those rules to one document: what to
check first, what matters most, and how to repair a defect without creating another.

## Outline Before Sentences

Fix the outline before the prose. Read the headings alone, top to bottom: one title, no skipped level, each heading
naming what its section holds. A sentence polished inside a section that later moves or merges gets polished twice.

Then read each section for its form. Prose comparing items across the same attributes wants a table; a numbered list
whose order carries no meaning wants bullets. Changing the form usually removes more words than any wording pass.

## Mechanical First, Judgement Second

Some defects have one correct answer anyone can confirm: a code fence with no language, a skipped heading level, an
informative image with no alt text, a duration promised in a tutorial. Settle those first; they are quick and rarely
need the author.

Voice, concision, and tone are judgements. Repair them afterwards, and rate them as quality rather than correctness, as
[Assessing Criticality and Confidence](../assessing-criticality-confidence/SKILL.md) explains.

## Rank by Who Is Stopped

When only some repairs fit, order them by who fails without them:

| Defect                                                          | Who it stops                         |
| --------------------------------------------------------------- | ------------------------------------ |
| an informative image with missing or meaningless alt text       | a screen-reader user, completely     |
| meaning carried only by colour or by visual position            | a reader who cannot perceive the cue |
| link text such as "here", or a bare path                        | anyone scanning a list of links      |
| a skipped heading level, or bold text standing in for a heading | anyone navigating by outline         |
| an instruction in the passive voice that hides who acts         | the reader who has to act            |
| filler, wordiness, and paragraphs that bury their point         | every reader, a little at a time     |

Accessibility defects come first because they shut part of the audience out; style defects only cost attention.

## Repair Without Changing Meaning

- **Passive to active.** Name the actor the passive concealed, and check it is the right one. When the actor is unknown,
  or the action rather than the actor is the subject, the passive stays: the voice module permits it.
- **Alt text.** Decide first whether the image informs or decorates. An informative image gets a sentence on what it
  shows and why it is there; a decorative one gets empty alt text, since describing it adds noise.
- **Link text.** Rephrase the sentence so the destination's name becomes the linked words, rather than appending a "see
  this" link after it.
- **Filler.** Delete the word, then reread. "Just" and "simply" often cover a step the text never explained, and the
  real repair is writing that step.
- **Time estimates.** Replace the duration with the outcome, the prerequisites, or the depth. A duration describing a
  system, such as a timeout, is a fact and stays.
- **Heading levels.** Promote or demote a heading together with everything beneath it, so each subsection keeps its
  parent.

## Leave Out-of-Scope Text Alone

Quotations keep their original wording, generated output stays as generated, and archived material stays as it was
closed; the convention's Scope section gives the reasons. A repair made there is itself a defect.

## The Last Read

Read the finished document once as its intended reader would, start to end, with the source material closed. What
survives every earlier pass is usually context the author supplied from memory: an acronym never defined, a step
assumed, a term used before it was introduced.
