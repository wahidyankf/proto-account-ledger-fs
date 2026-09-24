---
description: >-
  Shapes each test as arrange, act, and assert, named for its behaviour, asserting one logical outcome, free of shared
  mutable state and order dependence, and guarding completeness with derived sets.
when_to_use: >-
  Use when writing, naming, or reviewing a test, deciding how much one test should assert, or proving that a check
  inspected everything it should.
---

# Test Design

A test is read far more often than it is written, usually by someone trying to learn why it just failed. Its shape
decides how long that takes.

## Arrange, Act, Assert

Every test has three parts, in this order: arrange the inputs and state, act by invoking the behaviour once, and assert
on what that action produced. A test that acts, asserts, and then acts again is two tests sharing one name.

## Properties Every Test Has

| Property        | Means                                                                  |
| --------------- | ---------------------------------------------------------------------- |
| fast            | a unit test finishes quickly enough to run on every change             |
| independent     | no test relies on another test's state or on the order tests run in    |
| repeatable      | the same code yields the same result on every run and every machine    |
| self-validating | the test decides pass or fail by itself; nobody has to read its output |
| timely          | the test exists before the production code that satisfies it           |

Each property protects the signal. A slow test gets skipped, a dependent or unrepeatable one produces results nobody
trusts, and a test that needs a person to judge its output is a manual check wearing a test's name.

## Names Describe Behaviour

A test's name states the expected behaviour and the condition under which it holds, in plain language, for example
`rejects an expired session on refresh`. A name such as `test1`, or one that only repeats a function name, tells the
reader of a failure nothing about what broke.

## One Logical Assertion

Each test verifies one logical outcome. Several checks on a single result that together express one outcome are one
logical assertion. Unrelated checks bundled together are not: the first failure hides the rest, and no name can describe
them all.

## No Shared Mutable State

Tests never share mutable state and never depend on execution order. Each test builds what it needs or receives its own
fresh copy. When one test changes data another reads, the second test's result depends on which ran first, and a
parallel run will eventually expose it. Rules for the data and fixtures a test owns are in Test Data Isolation.

## Guard Completeness With a Derived Set

A test asserting that nothing escaped a check compares against a set derived from the source the production code reads,
never against a hard-coded count. A count fails open where it matters, since a new member outside the inspected set can
leave the number unchanged. It also fails closed where it should not, since a legitimate restructure changes the number
with nothing wrong.

Whenever a test asserts how many, ask which set it is really about, and derive that set.
