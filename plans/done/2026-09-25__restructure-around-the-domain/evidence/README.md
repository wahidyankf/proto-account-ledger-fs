# Evidence

What each phase gate recorded, one file per record, headed by the command, the commit, and the time. Each file is cited
by the `delivery.md` item that produced it.

## Directory Map

- [phase-0-baseline.txt](phase-0-baseline.txt) — the baseline gates, counts, manifest, timings, sweep, and audit.
- [phase-0-corpus.txt](phase-0-corpus.txt) — the behaviour corpus on the baseline copy, 56 inputs.
- [phase-0-literals.txt](phase-0-literals.txt) — each test function's literal constants on the baseline.
- [phase-0-tests.txt](phase-0-tests.txt) — each test function's name and case count on the baseline.
- [phase-5-no-inheritance.txt](phase-5-no-inheritance.txt) — the inheritance gate, failing on the baseline and a probe,
  then passing on the tree.
- [phase-8-corpus.txt](phase-8-corpus.txt) — the behaviour corpus on the result, equal to Phase 0's.
- [phase-8-literals.txt](phase-8-literals.txt) — each test function's literal constants on the result.
- [phase-8-mutations.txt](phase-8-mutations.txt) — the six mutation spot-checks, each naming the tests that failed.
- [phase-8-tests.txt](phase-8-tests.txt) — each test function's name and case count on the result.
- [phase-8-timings.txt](phase-8-timings.txt) — Phase 0's timings beside the result's.
