---
description: >-
  Requires explicit authorization before staging, committing, or pushing, makes each grant single-use and scoped to what
  it names, and keeps it apart from every other permission.
when_to_use: >-
  Use before staging, committing, or pushing, or when deciding whether an instruction or an approved plan permits
  recording history.
---

# Commit Authorization

Deciding what to change and recording it in history are separate decisions. An agent may make, verify, and describe a
change freely. Staging it, committing it, and pushing it each wait for permission.

This standard implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md) and
[Immutability](../../principles/immutability.md): a recorded commit is a value other people may already hold, so it is
created only from a decision someone actually made.

## The Rule

Stage, commit, or push only when one of these holds:

- the user explicitly asked for that action; or
- a plan the user approved reaches a step naming that action.

With neither, prepare the change, verify it, report what remains uncommitted, and ask when the action is needed.

## A Grant Is Single-Use

An authorization covers the action it names, once, and is spent by it.

- Permission to commit one change set does not cover the next change, however small or soon.
- A change set authorized as a whole may be recorded as several [thematic commits](thematic-commits.md). Dividing it is
  how the authorized action is carried out, not a further decision to commit.
- Nothing carries over from a finished task into later work, or from an earlier session into this one.

The strict reading is deliberate. A standing permission turns every later change into one nobody approved, and the user
learns of it from the history.

## What Does Not Grant It

- A request to edit, fix, test, finish, or tidy. Completing work is not recording it.
- A plan the agent wrote that the user has not approved.
- Permission for another action. Committing does not authorize pushing, and pushing existing commits does not authorize
  a new commit.
- Permission in a different repository, including one this repository depends on or pins.

Keep to the stated scope, meaning the files, theme, branch, and target it names, and ask before widening it.

| Instruction                 | Authorizes                            |
| --------------------------- | ------------------------------------- |
| "commit these changes"      | one commit action, no push            |
| "push the existing commits" | that push, no new commit              |
| "commit and push"           | both, within the current task's scope |
| "finish this" or "fix it"   | neither                               |

## Separate Permissions

| Action                          | Governed by                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| choosing where a change goes    | [Integration Path](integration-path.md), which picks a route and grants none        |
| merging a pull request          | Pull Request Merge                                                                  |
| rewriting or discarding history | [No Destructive Git Operations](no-destructive-git-operations.md)                   |
| bypassing a hook                | [Hook Verification](hook-verification.md); a commit or push grant never includes it |

## Why the Cost Is Asymmetric

A commit not yet made costs one question. A pushed commit reaches other clones within minutes and cannot be withdrawn;
see [Public Outbound Safety](../../conventions/security/public-outbound-safety.md). The rule accepts the small cost on
every change to avoid the large one on any.
