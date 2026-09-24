---
description: >-
  Replaces sampling with enumeration in a verification pass through forcing functions for shared controls, state
  round-trips, declared invariants, and styling consistency, with equivalents for API operations.
when_to_use: >-
  Use when planning or running an exploratory, usability, or design verification pass over an interface or an API, or
  when judging whether such a pass covered enough.
---

# Enumerated Coverage

A pass that checks a representative sample finds the defects in that sample. Cross-surface inconsistencies and partly
violated invariants live in the elements nobody picked, so a sampled pass can report clean while whole classes of defect
remain.

Six forcing functions replace sampling with enumeration. They run inside the single bounded pass that
[Exploratory and Usability Review](003-exploratory-and-usability.md) defines; they add no passes, they fix what the pass
covers. Fix each enumeration before the pass starts, so the list of what to check is not shaped by what turns up. This
module holds the first four; [Usability Probes and Completeness](008-usability-probes-and-completeness.md) holds the
rest. Functions 2 and 4 apply as written to browser-rendered interfaces, the scope
[Behaviour Change Verification](006-behaviour-change-verification.md) declares; for any other interface the pass applies
the equivalent the adopter records, or records them not applicable with the reason.

## 1. Shared Controls Across Surfaces

List each control present on two or more views, tabs, or surfaces, and build a matrix of control against surface.
Exercise every cell and confirm the behaviour is identical. A control that acts on one surface and does nothing on
another is a consistency defect, and an unfilled cell is an open gap. Identical functions identified consistently is
also [WCAG 2.2 Success Criterion 3.2.4](https://www.w3.org/TR/WCAG22/#consistent-identification).

## 2. State Round-Trip for Every Addressable Control

For every interactive control in scope, whether filter, input, toggle, selector, or tab: note the address, change the
value, confirm the address now reflects it, reload, and confirm the control shows the changed value. A value in scope
that a reload discards is a defect, recorded with the control, the expected address parameter, and what was observed.

Which controls are in scope is an adopter decision:

| Option                                               | Gains                                                           | Costs                                                                                   |
| ---------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| every stateful control is addressable (default)      | every view can be shared, bookmarked, and reloaded without loss | transient input reaches the address, history, and logs                                  |
| only controls the specification declares addressable | transient input stays out of the address                        | each specification has to declare its addressable controls, and an omission goes unseen |

A control outside the chosen scope is recorded with that disposition, never as a defect. Under either option, a control
that holds a credential, a secret, or personal data never enters the address, for the reason
[Evidence Safety and Accessibility](005-evidence-safety.md) gives; the pass records it out of scope with that reason,
not as a defect.

## 3. Declared Invariants Hold Everywhere

Before the pass, list every invariant declared by the change's specifications, acceptance criteria, repository
instructions, and source comments. For each, enumerate every element it applies to and check every one.

One failing element violates the invariant, however many others pass. The violation is at least a `HIGH` finding, and a
`CRITICAL` one where the invariant is a MUST or otherwise meets a `CRITICAL` condition under Criticality Levels.

## 4. Consistent Styling

Enumerate every interactive element on every surface, including buttons, inputs, selects, checkboxes, toggles, and
links, and record its computed background color, text color, border, corner radius, and font size. Two properties must
hold:

- no element renders as an unstyled native control while its counterpart on another surface is styled; and
- elements of the same semantic type and declared variant share the same recorded values on every surface.

## API Equivalents

A pass over an API applies the same discipline to operations:

- a matrix of every operation against each cross-cutting property, such as authorization, pagination, validation, and
  error shape;
- a round-trip of each cross-cutting convention through every operation that should honour it; and
- a check of every declared invariant against every operation it governs.

The recurrence and completeness functions in module 008 apply to API passes unchanged. Record each matrix and its result
as evidence under [Evidence Safety and Accessibility](005-evidence-safety.md).
