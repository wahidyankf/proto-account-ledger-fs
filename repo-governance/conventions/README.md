---
description: >-
  Indexes the conventions layer, which holds the choices a repository makes for itself rather than durable constraints.
when_to_use: >-
  Use when locating an existing convention or deciding whether a new rule belongs in this layer.
---

# Conventions

A convention records a choice. Two repositories could reasonably decide differently and both be right; what matters is
that one of them decided, wrote it down, and now applies it consistently.

That is what separates this layer from the one above it. A principle explains why something is true regardless of
repository. A convention says which of several defensible options this repository picked.

| Area         | Holds                                                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `security/`  | what enters history, who reads real values, what leaves                                                                         |
| `structure/` | how files, directories, and documents are shaped and named, how governance and plans are organized, and how repositories relate |
| `writing/`   | how a repository's documents are expressed, formatted, and illustrated                                                          |

## Directory Map

- [Security](security/README.md)
- [Structure](structure/README.md)
- [Writing](writing/README.md)
