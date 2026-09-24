---
description: >-
  Places a plan's evidence files in a plan-owned folder that moves with the plan, fixes what is inline versus filed, and
  sets naming and coverage for captures and API responses.
when_to_use: >-
  Use when capturing, naming, storing, or referencing verification evidence while executing a plan.
---

# Evidence Files

[Evidence and Quality](007-evidence-and-quality.md) makes evidence a file with a command, commit, time, result, and
sanitized findings, and
[Evidence Safety and Accessibility](../../../development/quality/manual-verification/005-evidence-safety.md) fixes what
it may contain. This module fixes where a plan's evidence lives and how a checklist item points at it.

## The Plan Owns Its Evidence

File-based evidence lives in an `evidence/` folder inside the plan root, `plans/<stage>/<slug>/evidence/`. It is
committed, and it moves with the plan through every lifecycle move, including archival into `done/`.

`evidence/` holds artifacts, not plan documents. It is not one of the [Required Documents](002-required-documents.md),
which permits it beside them, and it is not a technical-shape companion.

File-based evidence anywhere else is misplaced. Immutable hosted results, where the safety rule above permits them,
remain valid evidence. A repository-root evidence folder outlives the work that produced it, and nothing links to it;
evidence left in scratch space disappears. An adopter that wants a backstop rejects a root-level evidence folder in its
own hook, gate, or CI. A root-anchored ignore rule is a weaker substitute, because it hides misplaced files instead of
reporting them.

## Inline or Filed

| Evidence                                              | Goes                                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------------------ |
| a short command output, status code, or response body | inline, under the checklist item it proves                               |
| a console or network summary                          | inline                                                                   |
| a capture, an exported report, or a coverage report   | `evidence/`, referenced from the item                                    |
| a response or log longer than about twenty lines      | `evidence/`, with the item quoting the command, the status, and the head |

The checklist item always carries the reference. A file in `evidence/` that no item cites proves nothing to a reviewer,
and an item saying "verified manually" with neither an inline record nor a reference is not evidenced at all.

Orientation captures nobody cites, scratch scripts used to produce captures, and draft findings are not evidence and are
not committed.

```markdown
- [x] [AI] Verify the export page at every declared viewport — acceptance: AC-4
  > Evidence (YYYY-MM-DD, `<commit>`): mobile capture `evidence/phase-3-export-page-mobile.png` — the download button
  > stays above the fold; tablet and desktop captures alongside.
```

## Naming

```text
phase-<N>-<subject>[-<variant>][-<viewport>].<ext>
```

The phase ties a file to the part of the checklist that produced it. The subject says what was checked. The variant
names a state, locale, or input where one check covers several, and the viewport names the declared device class or
width. A name carrying all of that lets a reviewer spot a coverage gap from the directory listing alone.

## Capture Coverage

A capture-based check covers every viewport class the change declares, in the normal state and in every error, empty, or
loading state the check exercises. Where a product declares further variants — locales, themes, roles — its own
verification rule sets that coverage; this module does not.

Every capture carries the text alternative its safety rule requires.

## API Response Evidence

For each endpoint verified, record:

1. the exact command, so it can be re-run;
2. the status code;
3. the response body, or its opening lines with the truncation stated and the full body filed; and
4. at least one error path beside the success path — the invalid input, and the error status and body it produced.

A success path alone proves that an endpoint answers, not that it rejects. Any credential in the command or the response
is replaced with a placeholder such as `<api-token>` before it is recorded.
