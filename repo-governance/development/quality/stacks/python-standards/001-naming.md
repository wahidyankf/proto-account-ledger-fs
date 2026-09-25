---
description: >-
  Names every function and method by a verb and its object, and every variable, parameter, and field by a noun, with the
  exemptions Python fixes and the gate that holds the function names.
when_to_use: >-
  Use when naming or reviewing a function, method, variable, parameter, or field in Python, or when a new leading verb
  is needed.
---

# Naming

A name says what its code does or holds, so a reader follows a call without opening it.

- **Functions:** every function and method name must start with a verb followed by that verb's object, such as
  `parse_stream`, `_format_amount`, or `compute_closing`, never a bare noun like `_amount` or a bare verb like
  `process`. A method may leave its object to its class, as `Day.parse` and `Amount.make` do. A name adds where its
  value comes from or goes to, such as `from_csv` or `to_text`, only where its signature and module leave that
  ambiguous; a constructor with more than one source takes `from_` and the source. Magic methods, a method overriding a
  library's (`write` on an `io` subclass), a `@property`, which reads as an attribute, and the entry point `main` are
  exempt.
- **Variables:** every variable, parameter, and field must be named with a noun or a noun phrase, such as
  `closing_balances`, `state_after`, or `undoing_id`, never a bare verb, participle, adjective, or single letter. A
  boolean may instead be named as a yes-or-no question, such as `is_force_post`. A magic method's parameters keep
  Python's own names, such as `other`.

pylint's `invalid-name`, with `function-rgx` and `method-rgx` naming the allowed leading verbs, gates the function rule;
a new verb joins that list in the change that first needs it. No tool can tell a noun from a verb, so review applies the
variable rule.
