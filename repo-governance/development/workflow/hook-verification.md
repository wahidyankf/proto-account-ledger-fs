---
description: >-
  Requires explicit per-operation authorization before skipping a commit or push hook, and requires a failing hook to be
  reproduced and fixed at its cause, never muted, weakened, or routed around.
when_to_use: >-
  Use when a hook fails, when skipping a hook is proposed for any reason, or when a fixture commit must be built so a
  gate can be shown refusing it.
---

# Hook Verification

A hook that fails has found something. The response is to fix what it found, never to route around the hook.

This standard implements [Root Cause Orientation](../../principles/root-cause-orientation.md),
[Fail Closed](../../principles/fail-closed.md), and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md).

## Bypass Is a Separate Permission

Skipping the hooks on a commit or a push needs explicit authorization that names the bypass, or clearly includes it, for
that one operation.

- A request to commit or push never authorizes a bypass; see [Commit Authorization](commit-authorization.md).
- The authorization is spent by the operation it names. It never carries into a later operation or a wider scope.
- Nothing stands in for it: not convenience, time pressure, a slow hook, a failure that looks unrelated, repeated
  failure, a cause that is hard to find, an urgent fix, or an investigation of the blocker already under way.

The rule has no emergency or investigation exception. Those are exactly the situations in which a skipped check is most
likely to matter and least likely to be run again.

## When a Hook Fails

1. Keep its output and identify the failing check.
2. Reproduce the failure without skipping verification.
3. Trace it to the earliest responsible code, test, configuration, dependency, or environment, and fix that within the
   authorized scope.
4. Rerun the failed check and the relevant verification, then repeat the operation with hooks running.

Never disable, remove, mute, weaken, or superficially satisfy a hook or any check it runs to get an operation through. A
check that fails because a file it names was renamed is reporting an unfinished rename, not a wrong check.

If the cause cannot be fixed within the authorized scope, report the evidence and the open blocker, and ask for
direction only once inspection leaves a genuine choice; see
[Deliberate Problem-Solving](../../principles/deliberate-problem-solving.md).

A hook held back because a local compute guard reported a busy host has not failed. Retry that same invocation once the
stated condition clears, as Resource-Aware Development requires.

## When the Hook Is Wrong

A hook that fires on something it should not is a defect in the hook. Change the hook in a reviewed change that states
the reason. Routing around it quietly leaves it misfiring for everyone else.

## When a Bypass Is Authorized

- Before proceeding, disclose which safeguards will be skipped and any failure still unresolved.
- Record the approval and its reason in the commit record, so the skipped validation stays visible and is rerun
  promptly.
- An authorized hook bypass never licenses publishing anything the outbound safety screen has not passed. That screen
  has no bypass; see [Public Outbound Safety](../../conventions/security/public-outbound-safety.md).

## After Every Push

Whether a push bypasses a hosted branch rule depends on server rules and the pusher's privileges, so no bypass of that
kind can be approved in advance. Read the output of every push. A reported rule bypass is a discovered violation: report
which rule was bypassed, record in the plan or task log why its check did not run or pass, and never count the push's
success as evidence that the bypassed check would pass.

## Deliberately Failing Fixtures

A commit built to fail, so a test can show a gate refusing it, still needs the bypass permission. It lives on a
throwaway branch that never merges, and its bypass is disclosed like any other.

## Why It Is Shaped This Way

A hook usually mirrors a hosted check. Skipping it does not skip the check; it moves the failure later, where it costs
more and blocks the merge anyway. The two permissions stay apart because granting one to reach the other hides the
decision that actually needed making.

An adopter repeats its hook contracts in its hosted checks, where a skipped local hook cannot skip them.
