# Specifications

The shared description of what this repository's software is expected to do. Specifications describe intent and
observable behaviour, separate from the code, so a change can be discussed from one source of truth. Gherkin scenarios
under `behaviours/` are executed by both the unit and the integration test projects of the owner they describe.

A specification owner lives at `specs/apps/<product>/<owner>/` and holds a `README.md`, an `architecture.md`, and a
`behaviours/` tree.

## Directory Map

- [Applications](apps/README.md) — specifications for deployable applications.
