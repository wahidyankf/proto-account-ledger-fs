---
name: adopt-artifact
description: >-
  Copies explicitly named catalog artifacts into a target repository, resolving the source commit first and recording
  provenance in the adopting commit.
when_to_use: >-
  Use only after a user names an artifact or bounded family to adopt into a specific repository.
---

# Adopt Artifact

## Entry

A user has **explicitly asked** to adopt, and has named the artifact or a bounded family of artifacts.

Nothing else opens this workflow. An agent that notices a useful catalog artifact while doing something else may report
the option and its trade-off, and must stop there.

## Sequence

1. **Resolve the source before reading or editing anything.** A version, tag, or moving branch name is not a source. If
   the request names a commit, require a full SHA reachable from the canonical remote's published `main`. Otherwise:

   1. resolve the canonical remote's default branch and require it to be `main`;
   2. resolve its published head to a full 40-character commit SHA;
   3. verify that the commit and every named artifact can be read;
   4. show the resolved source; and
   5. stop if any identity, reachability, or content check is ambiguous or unverifiable.

2. **Read the target repository's instructions.** Adoption is intent-first: the artifact is mapped into local ownership,
   not pasted into place.
3. **Preserve stronger local requirements.** Where the local rule is stricter, it wins. Adoption never loosens a
   repository.
4. **Refuse contradictions rather than resolving them silently.** An artifact that conflicts with a local rule stops and
   reports; it does not overwrite the rule and it does not quietly weaken itself to fit.
5. **Change only the requested scope**, plus the binding and index edits those artifacts genuinely need to work.
   Unrelated cleanup encountered along the way is reported, not performed.
6. **Record provenance in the adopting commit:**

   ```text
   OSE-Rules-Source: <artifact-path>
   OSE-Rules-Source: <second-artifact-path>
   OSE-Rules-Commit: <full-commit-sha>
   ```

   `OSE-Rules-Source` repeats once per artifact. `OSE-Rules-Commit` appears exactly once. No catalog version trailer is
   recorded.

## Exit

The named artifacts exist in local form, only the requested scope and its integration changed, and the commit carries
its trailers.

## Adoption Is a Copy, Not a Subscription

After adoption the target owns its copy outright. It may adapt, extend, or diverge, and nothing checks it afterwards: no
synchronization, no pin check, no byte-identity comparison, no drift ledger.

The trailers explain where something came from. They create no future obligation, and a later local edit needs no
trailer unless it is another explicit adoption.

This is a deliberate trade. Guaranteed consistency would require the adopting repository to accept an ongoing obligation
it never agreed to, and a catalog that can change your repository is not a catalog.
