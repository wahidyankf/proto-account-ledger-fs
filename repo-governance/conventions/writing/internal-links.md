---
description: >-
  Requires every internal Markdown link to be relative, to resolve to an existing document, and to be repaired in the
  same change that moves, renames, or deletes its target.
when_to_use: >-
  Use when adding an internal link, or before moving, renaming, or deleting a document that other files may link to.
---

# Internal Links

An internal link that does not resolve is a defect, found either by a gate before merge or by a reader after it. This
convention exists so that it is always the gate.

## Form

- **A relative path from the linking file.** An absolute path, or a URL pointing at the repository's own hosting, breaks
  when the tree moves, when it is read from a fork, and when it is read offline.
- **Standard Markdown link syntax, with the file extension**, unless a repository has decided otherwise for a tool-bound
  tree, as below. An extensionless path resolves in some renderers and not others.
- **A document, never a directory.** Link the directory's `README.md` index. This is the stricter portable rule:
  renderers and validators resolve a directory target differently, so a link naming the document resolves the same
  everywhere, even where a repository's own tools would resolve the directory to its index.
- **Descriptive link text**, per [Accessible Content](content-quality/003-accessible-content.md).

## What the Check Covers

A link's target resolves from the file that contains it, stays inside the repository, and exists. A fragment or a query
string does not change which file is checked.

Links with a scheme — external URLs and mail addresses — are outside this check. An external link can rot without
failing anything here, which is also why an external link is never proof that a local fact is true.

## Repair in the Same Change

A change that moves, renames, or deletes a document also edits each file that points at it. Before making it, search the
repository for the target's filename, and repair every inbound link in the same change.

Deferring the repair to a later documentation pass leaves a window in which every gate fails and every reader who
follows the link lands nowhere. The repair also extends to trees few people open, such as draft notes, where a broken
link sits unnoticed longest; archived trees follow the decision below.

For a deletion, removing or re-pointing the link — a table row, a list item, a sentence — is mechanical repair and
belongs to the deletion. Explaining what replaced the deleted document is substantive writing and may follow in its own
change. Keeping the two apart keeps the deletion green without shortchanging the explanation. The same rule appears in
[Deletion With Proof](../../development/quality/deletion-with-proof.md): every reference is updated in the same change.

## Wiki-Style Links Are an Adopter Decision

Whether a tree may use wiki-style links is a decision each repository makes and records.

| Option                                      | Gains                                                                   | Costs                                                                         |
| ------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| standard relative links everywhere          | every link passes a general link checker and resolves in every renderer | a notes tool's backlinks and rename tracking may not follow them              |
| wiki-style links in a tool-bound notes tree | the notes tool's backlinks and rename tracking work on every link       | the links resolve only inside that tool, and no general validator checks them |

A tree using wiki-style links sits outside the standard check, so its links are only as sound as the tool resolving
them.

## Archived Trees Are an Adopter Decision

Whether archived material is validated as a link **source** is a decision each repository makes and records in its link
validator's configuration. Archived material stays a valid link **target** either way.

| Option                                   | Gains                                                                | Costs                                                                                |
| ---------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| validate every source, archives included | every link in the repository resolves, with no exception to remember | a move or deletion forces edits inside archived documents, rewriting a closed record |
| exclude archived trees as sources        | archives stay exactly as they were closed                            | links inside an archive rot, so an archived document stops being a reliable map      |

A repository with no archived tree declares an empty exclusion list, so the absence reads as a decision rather than an
oversight.

## Enforcement

An adopter enforces this with its own internal-link gate on every change, with any excluded sources declared in its
repository configuration rather than inside the gate.
