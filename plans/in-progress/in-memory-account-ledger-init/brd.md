# Business Requirements

Why this work is worth doing, for whom, and what would make it not worth it. The brief it answers is
[challenge-raw.md](../../../challenge-raw.md); this document cites it rather than restating it.

## Business Goal

Pass the "Staff Software Engineer — In-Memory Account Ledger Core" assessment. The brief says the written artifacts are
"your entry ticket" and that "a 45-minute live defense with no AI present is the assessment", and that candidates are
evaluated "primarily on the live defense: every number and design decision must be explained precisely and without AI
assistance".

The goal is therefore not a ledger that looks finished. It is a ledger whose every figure, rule, and refusal can be
traced from the brief, through a recorded decision, to a test that proves it, by a person who then has to explain that
chain aloud without help.

## Roles Served

- **Candidate** — the repository's author, who defends it live without AI. Needs code small enough to explain line by
  line, and one proof per claim to point at.
- **Assessor** — whoever opens the public repository and runs the defense. Needs a runnable replay, printed per day, and
  a test for every figure, refusal, and rule the documents claim.
- **Reader** — anyone who later reads the history or reuses the design. Needs an intact, thematic commit history and an
  as-built architecture model.

## Outcomes

1. **The replay runs.** One command replays the brief's stream and prints, per day, the report the brief names: "closing
   ledger balance, fee assessments, authorization states, and errors", exactly as
   [OUTPUT_TARGET](../../../OUTPUT_TARGET.md) shows it.
2. **Every claim is proven.** Each rule resolved in [AMBIGUITIES](../../../AMBIGUITIES.md) that states what the ledger
   does, and each criterion verdict in [REJECTED](../../../REJECTED.md) and [MOVEMENT](../../../MOVEMENT.md), has a
   named test that fails if the behaviour breaks.
3. **One weakness is exposed on purpose.** The brief asks for "One failing test against your own design,
   inline-annotated with what it reveals"; the suite carries exactly one, as a strict expected failure (AMB-018,
   AMB-031).
4. **The deliverables are complete.** The brief's "README — how to run the suite and read the output", plus NUMBERS,
   AMBIGUITIES, REJECTED, and WORKLOG, agree with the code, and the architecture trade-offs document that feeds the Part
   2 PDF covers the four sections the brief requires.
5. **The machinery stays explainable.** Nothing in the repository needs explaining that does not bear on the ledger,
   which is why the test suite is plain pytest rather than Gherkin bound at three layers (decision D12 in the
   [decision records](tech-docs/005-decision-records.md)).

## Non-Goals

- The Part 2 PDF itself. This plan writes the Markdown document it is made from; converting and uploading it is not
  planned here.
- A web layer, persistence, UI, or database, which the brief excludes: "No web layer, no persistence, no UI, no
  database."
- Any rule the brief and the resolved ambiguities do not state. A hold lifetime, for example, is the known weakness, not
  a feature (AMB-018).
- A machine-readable or product-grade command-line surface. The command sits at the floor tier of the
  [command-line interface convention](../../../repo-governance/conventions/structure/command-line-interface.md) (D13).
- Performance at scale. Balances are recomputed from the log on every query (D7); what breaks first at 100× volume is
  answered in the trade-offs document instead of being built.

## Business Risks

- **A figure in MOVEMENT is wrong and the code copies it.** The defense would contradict the brief on a number. The code
  derives every figure from the rules; a mismatch with OUTPUT_TARGET stops work for a decision instead of being patched
  on either side.
- **A resolution is documented but never built.** "Show me" would have no answer. Every rule a resolution states gets a
  test (D3).
- **Time runs out before AMB-013's partial capture.** A claim would stand without proof. AMB-013 is built last, with a
  fallback the owner approved in D3.
- **Governance work crowds out the ledger.** The ledger would land late. Each rule change is one early phase.
- **History looks reconstructed.** "timestamped, real" and "intact commit history" would fail. WORKLOG entries are
  written as work happens, and every phase is pushed once its gate passes (D10).
