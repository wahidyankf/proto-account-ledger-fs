---
description: >-
  Defines the grouped top-level configuration keys, requires each declared policy to have a visible owner, and rejects
  unknown keys rather than inheriting policy.
when_to_use: >-
  Use when creating a repository configuration file or adding a top-level key to one.
---

# Top-Level Schema

## Grouped Core

| Key           | Holds                                                 |
| ------------- | ----------------------------------------------------- |
| `schema`      | the grouped schema identifier and version             |
| `repository`  | repository-owned identity and structural policy       |
| `scan`        | explicit walk exclusions                              |
| `harness`     | canonical meaning, requirements, and adapter profiles |
| `policies`    | opt-in Markdown, governance, and convention policy    |
| `environment` | declared environment safety contract                  |
| `toolchains`  | direct probe and provision policy                     |
| `gates`       | typed lifecycle entries and PR composition            |
| `extensions`  | opaque, named data owned outside the shared schema    |

Only `schema` is universal. Every other group is omitted when the repository has no policy to declare; an empty group is
not a substitute for a decision. A command whose group is absent refuses rather than applying a hidden default.

`gates.entries` is ordered. A runner executes the selected entries in that order and stops at the first nonzero result.
A repository with no lifecycle gate omits `gates`; it never invents an unregistered gate at a caller.

## Policy Groups Have Owners

| Group         | Owns                                                    |
| ------------- | ------------------------------------------------------- |
| `harness`     | canonical field mapping, required meaning, and profiles |
| `policies`    | opt-in validator settings the repository selected       |
| `environment` | named safe examples, detectors, and staged paths        |
| `toolchains`  | declared probes and explicit provision vectors          |
| `extensions`  | payload an independently named owner validates          |

An extension is not an exemption: it may not conceal a credential, host, or an untyped command. It is visible so a
reviewer can identify its owner and select the validator that understands it.

## Unknown Keys Fail

A top-level key outside the grouped contract fails. Guessing an unknown key makes policy look enforced while no command
can prove what it meant. A repository needs a reviewed extension or a shared schema change, never a tolerated typo.
