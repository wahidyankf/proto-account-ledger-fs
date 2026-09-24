---
description: >-
  States that a clean checkout, following only what the repository records, reaches the same environment and the same
  result on any machine that meets its documented prerequisites.
when_to_use: >-
  Use when adding a runtime, tool, dependency, environment variable, or setup step, or when two machines on the same
  commit disagree.
---

# Reproducibility

A clean checkout on a machine that meets the documented prerequisites reaches the same working environment, and the same
result, by following what the repository records. Nothing required lives only on one machine or in one person's memory.

## What It Requires

| Concern             | Recorded as                                                                         | Never                                                     |
| ------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------- |
| runtimes and tools  | exact versions in a committed file a version manager reads                          | whatever happens to be installed                          |
| dependencies        | a committed lockfile that automation installs from, failing if the manifest differs | a floating selector such as `latest`, resolved at install |
| system dependencies | documented, with the versions known to work                                         | discovered by a newcomer's first failure                  |
| configuration       | a committed example naming every variable, with placeholders such as `<api-token>`  | a real secret in the example, or an unlisted variable     |
| setup               | a script, run the same way by a person and by automation                            | steps passed on in conversation                           |

Which version manager, lockfile format, or setup tool is the adopter's choice. That the choice is recorded and committed
is not.

A version range in a manifest is acceptable only while a committed lock resolves it. The lock is what turns the range
from a question asked again at every install into a record.

## Where It Is Already Load-Bearing

| Applied in                                                                                          | As                                                                  |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [The Shared Fixture Corpus](../conventions/structure/plan-validator-contract/003-fixture-corpus.md) | two implementations agree only on bytes pinned by a digest          |
| [Adopt Artifact](../workflows/adoption/adopt-artifact.md)                                           | a source resolves from published `main` to a full commit before use |
| [Evidence and Quality](../conventions/structure/plans/007-evidence-and-quality.md)                  | evidence records the exact command and the commit it ran against    |
| [Quality Gate Results](../development/quality/manual-verification/001-quality-gate-results.md)      | a result is about a recorded commit, never a changing draft         |
| [Top-Level Schema](../conventions/structure/repository-configuration/001-top-level-schema.md)       | a configuration names the schema version it conforms to             |

## An Unrecorded Difference Is a Defect Nobody Can Find

A build that works on one machine and not another is a true report about a difference nobody wrote down. The time goes
into discovering the difference rather than fixing anything, and every person who meets it discovers it again.

An unpinned version is a decision made by the calendar: whatever was newest when the install ran. Two people on the same
commit then run different code, and neither can tell.

The cost is paid twice more. A newcomer spends a first day reconstructing someone else's machine. And anyone rebuilding
an older commit to find where a behaviour changed is searching with an instrument that only works if that commit still
builds the way it did.

## Acceptable Variance

Operating system, editor, and local preferences such as a port or a directory may differ. Where one of them changes
behaviour, the difference is documented. Where a preference is purely local, it lives in an uncommitted file that the
committed example describes.

## Enforced Where Automation Runs

An adopter enforces this in its own automated gate, continuous integration where it has one: a frozen install from the
lockfile on the pinned runtime, failing when the lock, the manifest, or any pinned runtime disagree. A check that runs
only on a developer's machine inherits that machine's differences, which are the thing being checked for.
