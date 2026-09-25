# Business Requirements

Why the restructure is worth doing before submission, for whom, and what would make it not worth it. The brief is
[challenge-raw.md](../../../challenge-raw.md); this document cites it rather than restating it.

## Business Goal

Make the code as easy to defend as the documents already are. The brief says candidates are evaluated "primarily on the
live defense: every number and design decision must be explained precisely and without AI assistance". Every figure is
already proven; what is hard to defend today is where a rule lives. The owner's example: `list_records` takes only an
account's history yet sits in `authorizations.py`, not with the history, so a reader must search to find what a type can
do. The owner asked for code that is type-safe, laid out in DDD terms, grouped so that nothing is scattered, called as
`DomainName.do_something()`, and immutable first, with nothing a user or an assessor can observe changing: "hasil akhir
gak boleh berubah. cuman struktur yang boleh."

## Roles Served

- **Candidate** — the repository's author, who defends it live without AI. Needs every rule about an account in one
  place, and one answer to "where does this live, and why".
- **Assessor** — whoever reads the repository and runs the defense. Needs the architecture to match the tree, and the
  same report, figures, and refusals as before.
- **Reader** — anyone who later reuses the design. Needs layers whose dependencies point one way, enforced by tools.

## Outcomes

1. **One place per concept.** Every rule about one account is a method of the Account aggregate, in one module; every
   rule across accounts is a method of the `Ledger`; every operation on a value is a method of that value.
2. **DDD and hexagonal layers.** The domain, the application with its ports, the adapters, and the shell, each with an
   import ban its tools enforce.
3. **Composition, not inheritance.** No class derives from another save a `Protocol`, `Generic`, `Enum`, or exception,
   and a lint gate enforces it.
4. **Type-safe to the end.** No `assert`, `Any`, `cast`, `# type: ignore`, or `# noqa` in the source; every proof is a
   type.
5. **Nothing observable changes.** The program's standard output, standard error, and exit code for every input; every
   test and its cases; every assessment doc's figure, verdict, and cited test name.
6. **Every document is as built.** The architecture, the READMEs, the trade-offs document, and the rules describe the
   code as it is after the plan, and the assessment docs stay in agreement with one another.

## Non-Goals

- Any change to a rule, a figure, a message, or an exit status a user can reach. One internal line is added that no
  input reaches ([005](tech-docs/005-specification-rule-and-doc-changes.md#public-contracts)).
- Performance. The design still recomputes every balance from the log; the timings are re-measured, not improved.
- The Part 2 PDF. It is written beside this plan, from the trade-offs document, and is not one of its phases.
- A new feature, such as a hold lifetime, which stays the known weakness (AMB-018).

## Business Risks

- **A behaviour changes unnoticed.** A moved rule computes one figure differently and the assessor sees it. The
  behaviour corpus is compared at every phase gate, and a difference stops the phase
  ([004](tech-docs/004-behaviour-preservation-and-tests.md)).
- **A cited test disappears.** The assessment docs cite 60 test names; a lost one is a broken claim. The cited-name
  check runs at every phase gate.
- **The candidate cannot explain the new structure.** A structure the candidate did not choose is harder to defend.
  Every structural choice was the owner's at the pre-write gate, and each has a decision record
  ([007](tech-docs/007-decision-records.md)).
- **The push runs out of time before submission.** A half-restructured tree is worse than either end. Each phase is one
  commit whose gate passed, so stopping after any phase leaves a coherent, pushed tree
  ([006](tech-docs/006-migration-inventory.md#recovery)).
