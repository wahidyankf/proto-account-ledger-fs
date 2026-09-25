# Explanation

Background and reasoning behind the ledger's design and trade-offs, and how the code carries them out.

## Directory Map

- [Architecture Trade-Offs](architecture-trade-offs.md) — what the append-only log costs at scale, what value dates
  expose in production, every way an authorization ends, and what was cut. It is printed as the Part 2 PDF,
  `architecture-trade-offs.pdf` at the root, by [build-architecture-pdf.py](../../scripts/build-architecture-pdf.py);
  rebuild it after any change here.
- [Code Walkthrough](code-walkthrough.md) — one run at function level, with a sequence diagram for each case, the day
  and authorization state machines, and where a change would go.
- [Fees and Interest](fees-and-interest.md) — how the close decides each fee, refund, and interest event, day by day,
  behind 285.76 and 10.008.
- [How This Was Built](how-this-was-built.md) — who wrote the code, how decisions were made, and the time it took
  against the brief's budget.
- [Python Crash Course](python-crash-course.md) — each Python feature the code uses, where, and why it was chosen.
