---
description: >-
  Names every function and method by a verb and its object, every variable, parameter, and field by a noun, and every
  type generic over the currency with `In`, with the exemptions Python fixes and the gates that hold the names.
when_to_use: >-
  Use when naming or reviewing a function, method, variable, parameter, field, class, or type alias in Python, or when a
  new leading verb is needed.
---

# Naming

A name says what its code does or holds, so a reader follows a call without opening it.

- **Functions:** every function and method name must start with a verb followed by that verb's object, such as
  `parse_event_id`, `_format_amount`, or `compute_closing`, never a bare noun like `_amount` or a bare verb like
  `process`. A method may leave its object to its class, as `Day.parse` and `AmountIn.make` do. A name adds where its
  value comes from or goes to, such as `from_csv` or `to_text`, only where its signature and module leave that
  ambiguous; a constructor with more than one source takes `from_` and the source. Magic methods, a `@property`, which
  reads as an attribute, the entry point `main`, and the Result combinators `flat_map` and `flat_map_err`, which keep
  the names the idiom gives them, are exempt.
- **Variables:** every variable, parameter, and field must be named with a noun or a noun phrase, such as
  `closing_balances`, `state_after`, or `undoing_id`, never a bare verb, participle, adjective, or single letter. A
  boolean may instead be named as a yes-or-no question, such as `is_force_post`. A magic method's parameters keep
  Python's own names, such as `other`.
- **Types:** a class generic over the currency must be named by its noun followed by `In`, such as `AccountIn[M]`, read
  as an account in `M`, and the union over its currencies must take the plain noun, as `Money` is `Aed | Bhd` and
  `Account` is `AccountIn[Aed] | AccountIn[Bhd]`. No class or type alias may start with `Any`, which reads as
  `typing.Any`, a type these standards restrict.

pylint's `invalid-name`, with `function-rgx` and `method-rgx` naming the allowed leading verbs, gates the function rule;
a new verb joins that list in the change that first needs it. Its `class-rgx` and `typealias-rgx` refuse a name starting
with `Any`. No tool can tell a noun from a verb, or see which types are generic over the currency, so review applies the
variable rule and the `In` pairing.
