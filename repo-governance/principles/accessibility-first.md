---
description: >-
  States that content is usable from its first version by readers who cannot see it, cannot tell colours apart, or
  navigate by structure, against a stated external contrast floor.
when_to_use: >-
  Use when producing or reviewing a document, diagram, capture, or interface, or when accessibility is proposed as a
  pass to run later.
---

# Accessibility First

Content is usable by every reader it is meant for from its first version. Accessibility is a property of the draft, not
a pass applied to a finished one.

## Retrofitting Costs More Than It Looks

An inaccessible artifact is not a nearly finished accessible one. The choice that excluded someone — meaning carried by
colour, a diagram with no description, a layout whose structure exists only visually — is usually load-bearing by the
time anyone notices, and undoing it means redoing the work built on top of it.

That is why the requirement attaches to the first draft. Applied at the end, it competes with a deadline and loses.
Applied at the start, it is one more constraint shaping the design, and it costs almost nothing.

## What It Requires

| Requirement                                                                                                         | Because                                                                 |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| meaning never depends on colour alone                                                                               | a reader who cannot tell two colours apart receives two identical items |
| every image, diagram, and capture carries a text alternative                                                        | a reader who cannot see it otherwise receives nothing                   |
| structure is real, not styled: heading levels follow the real hierarchy with none skipped, and lists are real lists | assistive technology navigates by structure, and bold text is not one   |
| every interactive element is reachable and operable without a pointer                                               | some readers use a keyboard, a switch, or a voice, and never a mouse    |
| text and essential interface elements meet the contrast floor                                                       | low contrast is illegible to some readers and tiring for all of them    |

The floor is a named, external, measurable conformance standard, never below
[WCAG 2](https://www.w3.org/WAI/standards-guidelines/wcag/) Level AA in whichever 2.x version the adopter's legal or
stated baseline names, nor below that baseline. Level AA's contrast requirements from version 2.1 on are at least 4.5:1
for normal text, 3:1 for large text, and 3:1 for interface components and meaningful graphics. A repository may raise
the floor; a result below it is not accessible.

## The Alternative Is the Content

A text alternative that names the kind of thing — "diagram", "screenshot" — satisfies a linter and informs nobody. It
says what a sighted reader would have learned by looking, in the respect that matters to the document.

A redundant cue works the same way. Colour may reinforce a label, a shape, or a position; it may not replace one.

## Where It Is Already Load-Bearing

| Applied in                                                                                             | As                                                                         |
| ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| [Diagrams](../conventions/writing/diagrams.md)                                                         | a diagram in either form is described for a reader who will never see it   |
| [Evidence Safety and Accessibility](../development/quality/manual-verification/005-evidence-safety.md) | every capture carries a text alternative stating the finding               |
| [Interface Alternatives](../development/quality/manual-verification/004-interface-alternatives.md)     | accessibility is a named selection criterion, not a check after selection  |
| [Verification Layers](../development/quality/manual-verification/002-verification-layers.md)           | accessibility rules belong to the programmatic layer, captures stay usable |
| [Verification Routing](../development/agents/planning-capabilities/006-verification-routing.md)        | evidence is itself accessible                                              |
| [Top-Level Schema](../conventions/structure/repository-configuration/001-top-level-schema.md)          | heading hierarchy has its own validator section                            |

## The Benefit Is Wider Than the Obligation

The same properties serve readers with no disability at all. A text alternative is what a search indexes and what an
agent reads. Real structure is what a table of contents is generated from. A described diagram survives the renderer
that failed to draw it.

That argument persuades people the first one does not, but it is not the reason. An artifact that some of its intended
readers cannot use is defective even if nobody else would benefit from the fix.

## What Stays Out of the Principle

A specific palette, a diagram tool, a simulator, a testing service, or a single-top-heading rule is a choice, and it
belongs to a convention a repository writes for itself. This principle fixes what must be true, not how a repository
gets there.

The mechanical parts — heading levels, missing alternatives, the contrast of declared colours — are enforced by an
adopter in its own gate, where a reviewer's tired eye cannot skip them.
