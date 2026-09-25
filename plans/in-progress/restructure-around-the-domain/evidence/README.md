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
