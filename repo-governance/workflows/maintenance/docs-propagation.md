---
name: docs-propagation
description: >-
  Carries one change into every human-facing document it affects in one bounded pass: stale facts corrected, obsolete
  documents removed, each fact kept in its one home, and the result readable by a newcomer.
when_to_use: >-
  Use automatically before committing a change that alters what a document describes, when adding, moving, or deleting a
  document, or when the Docs Quality Gate hands over findings.
---

# Docs Propagation

## Entry

A change about to be committed alters what a document's reader relies on, a document is added, moved, or deleted, or the
[Docs Quality Gate](../quality/docs-quality-gate.md) hands over findings. Entry is automatic: whoever makes the change
starts here as part of the work, without a separate request. Edits made inside one run start no second one.

- `change` (`string`, required): the revision range or working-tree change.
- `findings` (`file`, optional): a handed-over ledger.

The document set is every human-facing document: every README, the documentation and specification trees, documents
inside projects, the standard files per the ose-rules Repository Documentation Files convention (not adopted here), and
a plan's documents where they describe the repository. Governance and agent instructions stay with
[Rules Propagation](rules-propagation.md). Formatting, links, indexes, and word budgets stay with the checks the
repository already runs; this workflow runs them and adds none.

## Sequence

1. **Freeze the inputs:** the change, any ledger, the revision, and uncommitted paths. A material change ends the run as
   input changed, never restarting it.
2. **Find what went stale.** Search the whole document set for every name, path, command, flag, version, and interface
   the change removed, renamed, or redefined. Each ledger row is an item too.
3. **Remove what is obsolete.** A document describing something the repository no longer has is deleted, with every link
   and index entry pointing at it. Unique meaning that is still true moves to its canonical home first.
4. **Keep each fact in its one home.** The root README orients; a project README follows
   [Project READMEs](../../conventions/structure/project-readmes.md); an index follows
   [Directory Indexes](../../conventions/structure/directory-indexes.md); a page serves one mode per
   [Documentation Architecture](../../conventions/structure/documentation-architecture.md). A summary links one level
   down to its detail, per [Progressive Disclosure](../../principles/progressive-disclosure.md), and a fact with a
   canonical home is linked, never copied.
5. **Write for a newcomer.** Each affected document tells a reader new to the repository what it is and why it matters
   from the opening, shows the next step without assuming the layout, and leaves no undefined term or skipped
   prerequisite, per [README Quality](../../conventions/writing/readme-quality.md) and
   [Content Quality](../../conventions/writing/content-quality.md), never a readability score. A sparing marker per
   [Emoji Usage](../../conventions/writing/emoji-usage.md) may aid scanning; decoration never does.
6. **Run what is safe to run.** Execute every command and example an affected document shows through the repository's
   declared entry point, per
   [Only What Was Run](../../conventions/structure/documentation-architecture.md#only-what-was-run). Never run one that
   touches a production or shared system, publishes, spends, needs a secret, or cannot be undone; the document says
   plainly that it was not exercised.
7. **Treat specifications as canonical.** Refresh their readability, navigation, and links; when one disagrees with the
   implementation, the partial outcome applies.
8. **Change only what is stale, missing, or obsolete.** Never rewrite accurate prose, invent behaviour, or fold in
   unrelated work.
9. **Verify once.** Run the repository's existing checks. Repair only failures this run caused, and only while their
   count strictly decreases, per [Bounded Convergence](../../development/workflow/bounded-convergence.md).
10. **Commit with the change it explains,** per [Thematic Commits](../../development/workflow/thematic-commits.md). A
    handed-over ledger's repairs land as their own commit.

## Exit

Outputs: `status` (`enum`: `no-change`, `landed`, `partial`, `input-changed`), `updated-docs` (`file-list`), `removed`
(`file-list`), and `not-run` (`record`, each command left unexecuted and why).

Partial outcome: when the code, a specification, or the audience is ambiguous or they disagree, that document stays
unchanged and the owner is asked through [Grill Me](../../../.agents/skills/grill-me/SKILL.md); the rest lands. A rerun
on unchanged inputs changes nothing.

## Example Usage

```text
Run docs-propagation for the change on the current branch.
```

## Related Workflows

- [Docs Quality Gate](../quality/docs-quality-gate.md) audits documents and hands its findings here.
- [Planning](../plan/plan-planning.md) adds this workflow to each delivery unit that changes what a document describes.

## One Writer

The gate finds; only propagation writes, so every document edit is made in one bounded place. This workflow implements
[One Source Per Fact](../../principles/one-source-per-fact.md) and
[Evidence Over Assertion](../../principles/evidence-over-assertion.md).
