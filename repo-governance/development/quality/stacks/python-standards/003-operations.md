---
description: >-
  Puts each operation on the type it is about, as a method, names the few cases that stay functions, and gives kinds of
  one concept a shared base when they share behaviour or the fields the code reads through their union.
when_to_use: >-
  Use when deciding whether an operation is a method or a function, or when several frozen dataclasses of one concept
  repeat the same fields or the same code.
---

# Operations

A reader looking for what a type can do opens the type. An operation spread across modules as loose functions has to be
searched for, and two modules can grow two versions of it.

## On Their Type

An operation whose subject is one type must be a method of that type: a query of its own data, an operation on its
value, or a rule its aggregate answers, called as `history.list_instalments(credit)` or `money.format_digits()`. A
frozen type stays frozen, so a method returns a new value and never changes its subject. It stays a function in these
cases only:

1. **Layer:** as a method, it would make a lower layer know a higher one, such as rendering, CSV parsing, the shell, or
   a model type that would have to know an aggregate's type.
2. **Two subjects:** it dispatches on two closed sets at once, one `match` over both as the table.
3. **No class to hold it:** its subject is a type alias such as a tuple or a mapping, it builds one of a union's kinds
   from text, or it narrows a type with `TypeIs`, which cannot narrow `self`.
4. **A service:** it runs across aggregates, such as processing an event or closing a day.
5. **Private internals:** it is a rule module's private step, which a public method reaches.
6. **Keeps a type variable:** it is a generic rule that must return `Result[M, …]` for the caller's currency. Pyright
   gives a method called on a value typed by a constrained variable the union of every constraint's result, which is not
   `Result[M, …]`, so such a rule stays a generic function, such as `sum_money`.

Inside an aggregate's package, a rule several of its modules share stays a public function, since the aggregate imports
the rules and they cannot import it back. A rule only its own module uses is private, and a rule a caller outside the
package uses is a method of the aggregate. It is followed when every such caller reaches the rule through a method, and
violated when a function outside these cases takes one type as its subject.

## Shared Bases

Kinds of one concept must share a base class when they share behaviour, or share fields that every kind repeats and the
code reads through their union, such as the event every domain event holds. The base is a frozen slots dataclass whose
name starts with `_`, holding the shared fields first, in the kinds' order, so positional construction and `match`
patterns are unchanged. Data that differs by kind is a `ClassVar`, and an operator or constructor on the base takes and
returns `Self`, so one kind never mixes with another. Order, which compares values, is defined on each kind, not on the
base, so two kinds never compare.

Kinds do not share a base when their likeness is chance, such as two different concepts that each hold a number; when
they share no field; or when no code reads the shared fields through their union. It is followed when no two kinds of
one concept repeat a field set the code reads through their union, and violated when they do.
