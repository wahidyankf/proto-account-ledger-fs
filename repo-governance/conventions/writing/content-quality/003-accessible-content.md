---
description: >-
  Requires descriptive alt text on informative images, empty alt text on decorative ones, descriptive link text,
  semantic elements, and meaning that never depends on colour or layout alone.
when_to_use: >-
  Use when adding an image, a link, or raw HTML, or when reviewing whether a document works for a screen-reader user.
---

# Accessible Content

Accessibility is a baseline, not a feature. A document that a screen-reader user, a keyboard user, or a reader who
cannot distinguish colours cannot use has failed for part of its audience.

## Alt Text

Every informative image carries alt text saying what it shows and why it is there, in a sentence or two. Include any
text in the image that the reader needs.

Do not open with "image of" or "picture of": the screen reader has already announced an image. Do not use the filename
or the word "screenshot" as alt text: neither says what the reader is missing.

A purely decorative image carries empty alt text, so assistive technology skips it instead of announcing noise.

## Link Text

Link text names the destination. Write `see the artifact metadata schema` as the linked phrase — never `click here`,
`this page`, `link`, or a bare path or filename.

Screen readers offer a list of every link on a page, read out of context. A list of "here", "this", and "link" tells the
reader nothing, and a list of filenames tells them little more.

## Colour Is Never the Only Cue

Meaning carried by colour is also carried by text, shape, position, or pattern. Wherever colour is used, the palette,
contrast, and testing rules in Colour Accessibility apply.

## Semantic Elements

Use the element that means the thing: a heading for a section, list syntax for a list, a header row for a table's
columns, a blockquote for a callout. Assistive technology exposes structure only through those elements; formatting that
merely looks right carries none of it.

Where raw HTML is needed, prefer native elements. Add ARIA attributes only when native semantics cannot express the role
or the label, because an incorrect attribute is worse than none: it announces something false.

## Reading Order

Content reads correctly from top to bottom. An instruction that depends on visual layout — "see the box on the right" —
has no right-hand side for a reader who cannot see the page.
