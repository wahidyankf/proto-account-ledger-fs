---
description: >-
  Requires internal references in a plan to be checked against the current commit, defines four confidence labels for
  claims, and fixes the order of refusal when a claim cannot be verified.
when_to_use: >-
  Use when a plan cites a path, command, flag, test, agent, skill, number, or external behaviour, or when a claim cannot
  be verified before it is written.
---

# Grounding and Labels

A reference in a plan is a promise that the thing exists. Grounding keeps that promise checkable, labels show how each
claim was established, and refusal covers the claims that cannot be established at all.

## Ground Every Internal Reference

Before a plan names anything inside the repository, whether a file, directory, command target, flag, function, test,
agent, or skill, verify that it exists at the current commit. When verification fails, take one of three paths:

1. find the correct reference and use it;
2. mark the reference as new, with a delivery item that creates it; or
3. refuse the claim, as described below.

A reference that ought to exist is not a reference.

## Four Labels

| Label             | Means                                                | Requires                                                               |
| ----------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| `[Repo-grounded]` | checked against the repository at the current commit | the check was actually performed, not assumed                          |
| `[Web-cited]`     | taken from an external source                        | the URL, the access date, and a short excerpt                          |
| `[Judgment call]` | the author's reasoned decision                       | the reasoning; every numeric target without a measured baseline has it |
| `[Unverified]`    | not checked, and stated as such                      | the consequence the adopter records under the decision below           |

## What an Unverified Claim Does

How a plan gate treats an `[Unverified]` claim, and a factual claim carrying no label, is an adopter decision:

| Option               | `[Unverified]` claim                          | Unlabelled factual claim                | Gains                                         | Costs                                                |
| -------------------- | --------------------------------------------- | --------------------------------------- | --------------------------------------------- | ---------------------------------------------------- |
| block the gate       | blocks the gate until verified and relabelled | treated as unverified, so it blocks too | no plan proceeds on an unchecked fact         | slow verification holds up the whole plan            |
| non-blocking finding | a `MEDIUM` finding that carries a disposition | a `HIGH` finding                        | work continues while the claim is followed up | an unchecked fact can still surprise execution later |

## Refuse When Uncertain

When a claim cannot be verified, take the first option that works:

1. omit it;
2. keep it, labelled `[Unverified]`;
3. restate it as a `[Judgment call]` with its reasoning; or
4. replace it with a placeholder and a delivery item that establishes the fact.

An unverified claim written without a label is never an option. A plan that says less and is right is worth more than
one that says more and is partly invented.

## Verify by Claim Category

| Claim                    | Verification                                                        |
| ------------------------ | ------------------------------------------------------------------- |
| file or directory path   | list or read it at the current commit                               |
| command target or script | read the file that defines it, or the tool's own listing of targets |
| command-line flag        | read the help output of the installed version                       |
| function, method, or API | find its definition in the source                                   |
| test name                | find it in the test files                                           |
| agent or skill           | confirm its definition file exists                                  |
| dependency version       | read the manifest or lock file                                      |
| numeric target           | cite a measured baseline, or label it `[Judgment call]`             |
| external behaviour       | cite an authoritative source with URL, access date, and excerpt     |
| cross-link               | resolve it to an existing file                                      |
