---
description: >-
  Puts each operation on the type it is about, as a method, names the few cases that stay functions, and allows no class
  inheritance.
when_to_use: >-
  Use when deciding whether an operation is a method or a function, or when a class would derive from another.
---

# Operations

A reader looking for what a type can do opens the type. An operation spread across modules as loose functions has to be
searched for, and two modules can grow two versions of it.

## On Their Type

An operation whose subject is one type must be a method of that type: a query of its own data, an operation on its
value, or a rule its aggregate answers, called as `account.list_instalments(credit)` or `money.format_digits()`. A
frozen type stays frozen, so a method returns a new value and never changes its subject. It stays a function in these
cases only:

1. **Layer:** as a method, it would make a lower layer know a higher one, such as rendering, CSV parsing, the shell, or
   a model type that would have to know an aggregate's type.
2. **Two subjects:** it dispatches on two closed sets at once, one `match` over both as the table.
3. **No class to hold it:** it builds one of a union's kinds from text, or it narrows a type with `TypeIs`, which cannot
   narrow `self`.
4. **Private internals:** it is a rule module's private step, which a public method reaches.

An aggregate is one class in one module, and a rule about it is its method, private where only it calls the rule. It is
followed when every such caller reaches the rule through a method, and violated when a function outside these cases
takes one type as its subject.

## No Inheritance

A class must derive from nothing but `Protocol`, `Generic`, `Enum`, or an exception class. Kinds of one concept each
declare their own fields; behaviour they share is one private function each kind's method calls; a contract a signature
consumes is a `Protocol`, any data member of it a read-only property, so a frozen type satisfies it by its shape. A
change to a base reaches every kind, wanted or not, so composition is preferred, as
[Simplicity Over Complexity](../../../../principles/simplicity-over-complexity.md) holds. pylint's `too-many-ancestors`,
with no parent allowed but these, enforces it: it is followed when that check passes on `src` and `tests`, and violated
when a class derives from any other.
