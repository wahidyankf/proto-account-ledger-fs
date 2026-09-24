---
description: >-
  Requires a real-browser check of every changed browser-rendered interface and a direct request to every API operation
  a behaviour change exercises, with a trigger table, a browser checklist, and tool-selection rules.
when_to_use: >-
  Use after implementing a change that alters what a user sees or what an API caller receives, before the change is
  reported complete.
---

# Behaviour Change Verification

Automated tests confirm what they were written to confirm. After a behaviour change, someone also exercises the running
system the way its users will, because the defects that survive a green suite are the ones nobody thought to encode.

This module makes the check mandatory when a change alters behaviour. It narrows nothing in
[Verification Layers](002-verification-layers.md): a change with no interface or API surface still marks those layers
inapplicable and states why.

## When It Applies

| Change                                     | Real-browser check                | Direct API request                             |
| ------------------------------------------ | --------------------------------- | ---------------------------------------------- |
| new page, view, or component               | required                          | required for every operation it exercises      |
| interface defect fix                       | required                          | required for every operation the fix exercises |
| new API operation                          | required if an interface uses it  | required                                       |
| changed API behaviour                      | required if an interface shows it | required                                       |
| change spanning interface and API          | required                          | required                                       |
| styling-only change                        | required                          | not applicable, with the reason                |
| internal refactor with no behaviour change | not applicable, with the reason   | not applicable, with the reason                |
| documentation-only change                  | not applicable, with the reason   | not applicable, with the reason                |

## Interfaces Outside a Browser

The real-browser column, the checklist, and the tool rules below govern interfaces a browser renders. For a desktop,
native mobile, terminal, or other interface, the adopter records how the check drives the real built runtime its users
meet:

| Option                                       | Gains                                                | Costs                                                              |
| -------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------ |
| the installed build on a real device or host | observes exactly what users meet                     | needs a device or host for each supported platform                 |
| the real build in an emulator or simulator   | repeatable, and reaches platforms nobody has at hand | can differ from real hardware in rendering, input, and performance |

The same trigger rows decide when such an interface is checked, with the recorded option taking the place of the
real-browser check.

## Browser Checklist

For a browser-rendered interface, in a real browser at the exact served origin, confirm that:

- the page renders with its intended content and layout;
- every changed interaction works, including its error and empty states;
- the console reports no errors;
- every network request the page makes succeeds, or fails only as designed;
- the visual result matches the intended design;
- each supported locale renders correctly;
- each declared viewport class renders correctly; and
- text that is present is also legible, checked by computed size or bounding box, because an element can exist in the
  document while clipped, hidden, or zero-sized.

Captures kept as evidence carry text alternatives and follow
[Evidence Safety and Accessibility](005-evidence-safety.md).

## Choosing the Browser Tool

Before verifying, find a browser-driving integration and confirm it responds. Record the tool used, any fallback, and
any capability it lacks, such as viewport emulation or network inspection.

While a live browser can be driven, reading source, fetching HTML, or inspecting HTTP responses does not count as
browser verification: none of them runs scripts, applies styles, or lays out the page the way a user's browser does.
When no browser can be driven at all, record that the check could not run and why; never record it as passed.

## API Requests

Every affected API operation receives a direct request against the exact served origin, recorded as API Testing sets
out.

## What Does Not Substitute

Reading the code, inferring styles from source, passing tests, and design files are supporting evidence. None of them
replaces observing the running system.

## Supplements, Never Replaces

This check never replaces required automated proof and never excuses a failed gate. A behaviour that works by hand while
its test fails is a failing change, handled under [Quality Gate Results](001-quality-gate-results.md).
