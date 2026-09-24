---
description: >-
  Requires the technical shape to carry one annotated file-impact tree naming every planned path and its action, and
  fixes the action labels.
when_to_use: >-
  Use when writing or reviewing a plan's file-impact section, or when a plan cannot yet name a file it needs.
---

# File Impact

Every formal plan's technical shape carries a `## File Impact` section. In the directory shape, `tech-docs/README.md`
either holds it or lists the companion that does.

Its primary view is one annotated tree, rooted at the repository root, in a fenced `text` block. A reviewer reads the
scope from the tree without assembling it from prose.

```text
.
├── docs/importer.md          [M] from docs/import.md
├── generated/importer.json   [G] regenerated from schema.ts
├── specs/importer.feature    [E] header-row scenarios
└── src/importer/
    ├── legacy-reader.ts      [D] superseded by reader.ts
    ├── reader.ts             [E] accept a header row
    └── schema.ts             [N] exact input contract
```

## Action Labels

Each entry carries exactly one label:

| Label | Means                                                 |
| ----- | ----------------------------------------------------- |
| `[E]` | an existing file is edited                            |
| `[N]` | a new file is created                                 |
| `[M]` | a file moves; the entry shows both paths              |
| `[D]` | a file is deleted                                     |
| `[G]` | a generated file is regenerated, never edited by hand |

`[G]` exists because a hand edit to a generated file is overwritten by the next generation. A plan that labels such a
file `[E]` has scheduled a change that will silently disappear.

## Exact Paths

Every expected code, test, specification, documentation, configuration, and runtime path appears. A directory, an
ellipsis, a described area, or "related files" is not a path. A runtime-instance placeholder such as `<user-id>` is
allowed only where the plan states who generates the value and the fixed path shape around it.

Where a necessary file cannot be named because a decision has not been made, that decision becomes a prerequisite and
execution blocks on it. A vague entry hides the gap and hands the decision to whoever reaches it mid-execution.

## Patterns: an Adopter Decision

| Option                   | Requires                                                                                                                               | Trade-off                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| exact paths only         | every entry is one file; an unknown name is a blocking prerequisite                                                                    | fully reviewable before execution; costs discovery up front for sweeping changes |
| bounded pattern families | a `*` entry names a bounded family and the rule that discovers its members, and `delivery.md` records the members before any is edited | practical for mechanical sweeps; the exact scope is visible only after discovery |

An unbounded pattern — a whole directory, or every file of a type — is never an entry under either option.

## Readability

Group a large tree into short blocks by area, with aligned, concise annotations. Behaviour belongs in the design and
specification sections, not in annotations stretched across the screen.

Where the tree cannot carry non-obvious context — ordering, discovery criteria, cross-cutting mechanics — a
`### More Detail` subsection follows it. That subsection maps back to entries in the tree, never replaces or repeats it,
and holds no checklist items, because actions stay in `delivery.md`.

An adopter that wants the section and its label vocabulary checked mechanically enforces them in its own plan gate.
