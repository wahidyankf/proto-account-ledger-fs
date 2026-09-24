---
description: >-
  Completes the enumerated coverage of a verification pass with usability probes, a recheck of earlier defect classes
  and changed areas, and a closing completeness critic.
when_to_use: >-
  Use when running the usability part of a verification pass, carrying findings from an earlier pass forward, or
  deciding whether a pass is finished.
---

# Usability Probes and Completeness

These are the last two of the six forcing functions begun in [Enumerated Coverage](007-enumerated-coverage.md). The
first probes what a newcomer meets; the second makes each pass learn from the last and admit what it skipped.

## 5. Usability Probes

Apply every probe on every surface where it could apply, not only where a problem is suspected:

- **Discoverability.** Each hidden, collapsed, or conditionally shown control can be found, and its purpose understood,
  by someone using the interface for the first time.
- **Jargon.** Every visible label, heading, tooltip, placeholder, and button text makes sense to someone new to the
  domain, from context alone.
- **Redundancy.** No element repeats identical information on several views.
- **Units.** Every numeric input that takes a unit states that unit beside the input or its label, and any unit or
  currency the user can choose is shown as chosen, not as a fixed default. Clear labels and instructions for input are
  also [WCAG 2.2 Success Criterion 3.3.2](https://www.w3.org/TR/WCAG22/#labels-or-instructions).

## 6. Recurrence, Change Adjacency, and Completeness

- **Recurrence.** At the start of a pass, list the defect classes that earlier passes found, not only the individual
  findings, and recheck each class on every surface. A class fixed in one place but present in an equivalent place is a
  partial fix.
- **Change adjacency.** Note what changed since the last pass, and recheck the surfaces next to or dependent on those
  changes, not only the changed parts themselves.
- **Completeness critic.** End the pass by listing every category of surface, such as views, viewport classes, locales,
  and control types, and confirming each was covered. A category never enumerated is an open gap, never an implied pass.

## Why Enumeration Is Worth Its Cost

Enumeration is slower than sampling, and that slowness is the point. The defects these functions target, a control inert
on one surface or an invariant broken for one input, are invisible to any sample that happens to miss them. A pass that
names what it did not cover gives the next pass somewhere to start; a pass that stays silent hands on an unknown gap.

Where a forcing function can run as a script, such as collecting computed styles or replaying address round-trips,
automating it in the adopter's own tooling is preferred, keeping human judgement for the probes that need it.
