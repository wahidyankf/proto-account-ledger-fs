---
description: >-
  Structures a module as a pure functional core that holds every decision and a thin imperative shell that holds every
  effect, with dependencies pointing only from shell to core.
when_to_use: >-
  Use when structuring or reviewing a module that mixes logic with input, output, rendering, or framework wiring, or
  when deciding whether code belongs in the core or the shell.
---

# Functional Core, Imperative Shell

[Pure Functions](../../../principles/pure-functions.md) states the principle: decide without effects, and carry out the
decision at a thin edge. This standard turns it into module structure, with two zones, one dependency direction, and a
check that tells them apart.

It also implements [Immutability](../../../principles/immutability.md),
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md), and
[Simplicity Over Complexity](../../../principles/simplicity-over-complexity.md).

## Two Zones

Each feature module splits into at most two zones, and its directory layout makes the zone of every file visible.

| Zone  | Holds                                                                                                                                                                    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| core  | validation, transformation, derivation, calculation, and formatting; value and data types; data schemas; constant tables; interfaces the shell implements                |
| shell | interface components, input and output, network and storage access, framework entry points and wiring, and anything that reads the clock, randomness, or the environment |

The shell gathers inputs, calls the core for decisions, and carries out the results. It stays thin enough that there is
little in it to get wrong.

Create only the zones a feature needs. A feature with no logic has only a shell, and a feature with no effects has only
a core. An empty placeholder zone promises structure nobody asked for.

## One Direction

```text
shell  --imports-->  core    allowed
core   --imports-->  shell   forbidden
```

The core imports only other core modules and effect-free libraries. It never imports an interface framework, a server
framework, a filesystem or network module, a database or HTTP client, or ambient platform globals, not even for a type.
A core file that needs one of those belongs in the shell.

Where the core depends on something the shell supplies, such as a repository, the interface lives in the core and the
shell implements it. The dependency still points from shell to core.

## Inside the Core

- **Data is immutable.** A function returns a new value and never changes an argument.
- **Every input is a parameter.** The current time, a random value, and configuration are passed in, never read.
- **Functions are small and composed.** Behaviour is built from small named functions with one job each, not from one
  large function that validates, transforms, filters, and aggregates at once.
- **Business logic is functions.** A class is acceptable as a plain data container, where a framework demands one, or at
  an interface boundary. Business rules, transformations, calculations, and validation are functions.

## Why It Holds

The core is tested with an input and an expected output: no runtime, no interface, no filesystem, no network, and no
mock. The shell is tested at its real boundary, and because it holds no decisions, little is left to test there.

An effect buried in a calculation, such as a log write, a notification, or a database call, makes the calculation
untestable without rebuilding everything it reaches. Moving the effect to the shell costs a few lines and removes the
problem.

## Introducing It Incrementally

1. Write new features this way from the start.
2. Convert an existing function to pure when a change touches it.
3. Convert business logic before infrastructure.
4. Put tests around code before restructuring it.
5. Record why any code deliberately stays imperative.

## Choosing Between This and Hexagonal Layering

Both keep decisions free of effects. This pattern uses two zones and no ports; Hexagonal Architecture adds ports,
adapters, and composition roots where infrastructure must be replaceable. The adopter's choice for web applications, and
its trade-offs, are in Application Shapes.

## Enforcement

An adopter enforces the dependency direction mechanically, in its own gate: an import-boundary lint rule, or a search
for effectful imports under every core zone that must find nothing.
