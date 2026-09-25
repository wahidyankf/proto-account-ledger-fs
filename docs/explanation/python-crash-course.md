# Python Crash Course

This page is for a reader who has programmed before but is new to, or out of practice with, the typed Python this ledger
is written in. Each section shows one feature in a small example of its own, then where the ledger uses it, then why the
ledger uses it rather than something simpler. It covers every feature the code in [`apps/account-ledger-cli/src`][src]
relies on; the [code walkthrough](code-walkthrough.md) shows them working together, and the
[Python standards](../../repo-governance/development/quality/stacks/python-standards.md) are the rules the code follows.

The project runs Python 3.14, pinned in [`.python-version`][python-version] and `pyproject.toml`. Two things about 3.14
matter for reading the code: generics are written in square brackets on the class or function itself, and an annotation
may name a class before that class is defined, so `def open(config) -> Ledger` works inside `Ledger`.

## The Tools Around the Code

The code never runs unchecked. Each tool below runs through an Nx target, and the push hook runs them all; the
[application README](../../apps/account-ledger-cli/README.md#commands) lists the commands.

| Tool    | What it checks                                                                                 |
| ------- | ---------------------------------------------------------------------------------------------- |
| uv      | installs the pinned Python and the locked tools from `uv.lock`, into `.venv`                   |
| pyright | every type, in strict mode: an unannotated or unknown type is an error, not a guess            |
| ruff    | style, import order, complexity (at most 10 per function), nesting (at most 3), and formatting |
| pylint  | a docstring on every function, a verb at the start of every function name, and no inheritance  |
| vulture | dead code: a function or name nothing uses fails the build                                     |
| pytest  | the tests, with at least 80% of lines covered by the unit tests                                |

Two of these shape what the code looks like. pylint's `function-rgx` in [`pyproject.toml`][pyproject] makes every
function name start with a verb from a fixed list, such as `compute_closing` or `list_records`, so a name says what it
does. pyright's strict mode is why every function is annotated and why the code never uses `Any`.

## Running a Package as a Program

```python
# account_ledger/__main__.py
from account_ledger.cli import main

raise SystemExit(main())
```

`python -m account_ledger` runs the package's `__main__.py`. `SystemExit(main())` makes the process exit with the number
`main` returns. `PYTHONPATH=src` in the commands tells Python to look for `account_ledger` under `src/`, and every
import is absolute, such as `from account_ledger.domain.model.money import Aed`.

Where: [`__main__.py`][main-module] and [`cli.py`][cli]. Why: `main` returns the exit status as a value, so the tests
call `run_cli` and assert the number without starting a process; only the end-to-end tests run the real program.

## Type Hints

```python
def find_account(self, account_id: AccountId) -> AccountOpening | None: ...

entries: tuple[LogEntry, ...]          # a tuple of any length, every item a LogEntry
read_text: Callable[[str], Result[str, OSError | UnicodeDecodeError]]
```

An annotation states what a name holds or a function returns. `X | None` is "an X or nothing", `tuple[T, ...]` is a
tuple of any length, and `Callable[[A], B]` is a function from A to B. Python does not check annotations at run time;
pyright checks them before the code runs.

Why: in a ledger, most bugs are a value of the wrong kind in the right place, such as a BHD amount added to an AED
balance. Types let pyright refuse those before a test runs.

## Frozen Dataclasses

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True, slots=True, order=True)
class Day:
    number: int

day = Day(2)
day.number = 3                          # raises FrozenInstanceError
later = replace(day, number=3)          # a new Day; day is unchanged
Day(2) < Day(5)                         # True: order=True compares the fields
```

`@dataclass` writes the constructor, equality, and printing from the fields. `frozen=True` refuses any assignment after
construction. `slots=True` fixes the set of fields, so a misspelt attribute is an error. `order=True` adds `<`, `<=`,
`>`, and `>=`, comparing fields in order. `dataclasses.replace` copies an object with some fields changed.

Where: almost every class. `Day` in [`ids.py`][ids] and `Aed` and `Bhd` in [`money.py`][money] use `order=True`, which
is how `closing < zero` and `day <= last_day` work. `_ProcessingState.process_event` in [`stream.py`][stream] uses
`replace(self, ledger=ledger)`.

Why: the ledger is append-only (AMB-024), and immutability is how the code keeps that promise everywhere, not only in
the log. An object that cannot change can be shared, kept in the log as it stood at each day's close, and compared
safely.

## Constructors That Refuse

```python
@dataclass(frozen=True, slots=True, order=True)
class Day:
    number: int

    def __post_init__(self) -> None:            # runs after the generated __init__
        if self.number < 0:
            raise ValueError(f"a day is at least 0, not {self.number}")

    @classmethod
    def parse(cls, text: str) -> Result[Self, IdFault]:
        return cls.make(int(text)) if re.fullmatch(r"[0-9]+", text) else Err(IdFault("day", text))
```

There are two ways to build a value, and they fail differently:

- **`__post_init__`** runs inside the constructor and raises. Only a bug can reach it, because code builds values from
  values already checked.
- **`parse` and `make`** are class methods that return a `Result`: `Ok` with the value, or `Err` with a fault naming
  what was wrong. They are for input, which may be wrong for reasons that are not bugs.

`@classmethod` receives the class as `cls`, so `Aed.parse` builds an `Aed` and `Bhd.parse` a `Bhd` from one body. `Self`
is the type of that class. `ClassVar` marks a constant of the class rather than a field of each object, such as
`Aed.PLACES = 2`. `@staticmethod` is a function kept in a class's namespace with no `self` or `cls`, such as
`Ledger.open`. `@property` reads a method as an attribute, such as `AccountId.number`.

Where: `Day`, `InstalmentCount`, and the ID classes in [`ids.py`][ids]; `Aed`, `Bhd`, and `AmountIn` in
[`money.py`][money]; `LedgerConfig` in [`config.py`][config].

Why: no object may hold an illegal value, so code that receives a `Day` never checks it again. The
[failures standard](../../repo-governance/development/quality/stacks/python-standards/002-failures.md) records the
split: exceptions for bugs, returned results for input.

## Unions, Type Aliases, and Enums

```python
type Money = Aed | Bhd                                   # a type alias: one name for the union

@dataclass(frozen=True, slots=True)
class Approved:
    hold: Amount

@dataclass(frozen=True, slots=True)
class Declined:
    requested_amount: Amount

type AuthorizationState = Approved | PartiallySettled | Declined | Settled

class SettlementKind(Enum):
    FINAL = "final"
    PARTIAL = "partial"
```

A union says a value is one of several types. The `type` statement names a union, so a signature can say `Money` rather
than `Aed | Bhd`. An `Enum` is a closed set of named constants with no data of their own. A `Literal` type, such as
`Literal["CREDIT", "DEBIT"]`, is a closed set of exact strings.

Where: the event kinds (`IncomingEvent`, `GeneratedEvent`) in [`events.py`][events]; the log's entries (`LogEntry`) in
[`domain_events.py`][domain-events]; the reasons to refuse (`Rejection`) in [`rejections.py`][rejections]; the
authorization states in [`authorizations.py`][authorizations]; `SettlementKind` and `Direction` as enums; `RowKind` in
[`csv_file.py`][csv] as a `Literal`.

Why: a state that carries data is its own class, holding only its own data. `Approved` has a hold and `Declined` has
none, so no code can read the hold of a declined authorization, as it could if one class had an optional `hold` field.
An enum is used where the choices carry no data.

## Pattern Matching

```python
match state:
    case Approved(hold=hold) | PartiallySettled(hold=hold):      # a class pattern, or-joined, capturing hold
        holds.append(hold.money)
    case Declined() | Settled():
        pass
    case _:
        assert_never(state)                                      # pyright: every case is handled
```

`match` compares a value against patterns in order and runs the first that fits. `Approved(hold=hold)` fits an
`Approved` and binds its `hold` field to a name. `A() | B()` fits either. A guard, `case Ok(day) if day <= last:`, adds
a condition. `as` names what a nested pattern matched: `Reversal(target=RefundId() as reversed_refund)`. A tuple pattern
matches several values at once: `case Approved(), SettlementKind.FINAL, _:`. `Ok(value)` without `value=` works because
`Ok` sets `__match_args__ = ("value",)`.

The last case, `case _: assert_never(value)`, is how the code stays complete. pyright works out that the value can have
no type left by then; if someone adds a new state and forgets a case, the value can still be the new state,
`assert_never` no longer type-checks, and pyright fails the build.

Where: everywhere a union is taken apart. `AccountIn.decide_event` in [`account.py`][account] dispatches on the event
kind; `apply_settlement` in [`authorizations.py`][authorizations] is the whole state machine as one `match` over a
tuple; `_format_reason` in [`text_report.py`][text-report] has one case per `Rejection`.

Why: the brief's rules are tables, so many functions are "for each kind, do this". A `match` reads as that table, and
`assert_never` makes the compiler, not a reviewer, check that no kind is missing.

## Generics

```python
class Box[T]:                                   # generic over any T
    def __init__(self, item: T) -> None: ...
    def map[U](self, change: Callable[[T], U]) -> Box[U]: ...

class AccountIn[M: (Aed, Bhd)]:                 # constrained: M is exactly Aed or exactly Bhd
    opening: M
    def compute_closing(self, day: Day) -> Result[M, CurrencyMismatch]: ...
```

A generic class or function takes a type as a parameter, written in square brackets. `class Ok[T]` holds a value of any
type `T`, and `def map[U]` introduces a type for one method. `[M: (Aed, Bhd)]` is a constrained type parameter: `M` must
be `Aed` or `Bhd` exactly, never the union `Aed | Bhd`. An `AccountIn[Aed]`'s `compute_closing` returns `Aed`, never
`Bhd`. `add_all` still accepts any `Money`, and returns `Err(CurrencyMismatch)` at run time if one is in the other
currency.

The union of both is named with the plain noun, `type Account = AccountIn[Aed] | AccountIn[Bhd]`, and the generic type
ends in `In`, per the
[naming standard](../../repo-governance/development/quality/stacks/python-standards/001-naming.md). A method called on
the union works: `account.compute_closing(day)` on an `Account` returns `Aed | Bhd`, so a caller never needs to know the
currency.

Where: `Ok`, `Err`, and their methods in [`result.py`][result]; `AmountIn` in [`money.py`][money]; `AccountIn` in
[`account.py`][account]; `AccountOpeningIn` in [`config.py`][config]; private helpers such as `_round_money[M]`.

Why: one currency per type is the brief's precision rule made structural. AED has two places and BHD three, and the two
must never be summed. With a constrained parameter, pyright refuses `Aed + Bhd`, since `__add__` takes `Self`, and keeps
each account's return types in one currency; a sum over mixed money, which only a bug could build, is caught at run time
by `add_all` and `require_same` as a `Result`. The first design reached each generic function through a dispatcher that
matched the currency first, because pyright cannot call a generic free function on the union; moving the operations onto
the types as methods removed the dispatchers
([REJECTED](../../REJECTED.md#functions-reached-through-currency-dispatchers)).

## Result Instead of Exceptions

```python
def run(self, source: EventSource, sink: ReportSink) -> Result[None, RunFault]:
    if isinstance(stream := source.read_events(self.config), Err):
        return stream                                   # hand the failure up, unchanged

    if isinstance(processed := stream.value.process(self.config), Err):
        return processed

    sink.publish(processed.value.reports)

    return Ok(None)
```

A function that can fail returns `Result[T, E]`, which is `Ok[T] | Err[E]`. `Ok(value).value` is the success and
`Err(error).error` the fault. The caller must unwrap it, so it cannot forget the failure the way it can forget to catch
an exception. The code does this in two ways:

- **An early return.** `x := f()` is the walrus operator: it assigns and yields the value in one expression.
  `if isinstance(x := f(), Err): return x` hands the failure up; after the `if`, pyright knows `x` is an `Ok`.
- **A chain.** `map` changes the value inside an `Ok` and passes an `Err` through; `map_err` does the opposite;
  `flat_map` continues with a step that can itself fail. `Aed.parse(text)` is `_read_decimal(text).flat_map(cls.make)`:
  read the number, then make the money, stopping at the first fault.

Where: [`result.py`][result] defines them by hand, not as dataclasses, so that pyright treats them as covariant: an
`Ok[Aed]` can be returned where a `Result[Money, CurrencyMismatch]` is expected, as an `Ok[bool]` is an `Ok[int]`. A
frozen dataclass would be invariant and refuse that. Each is marked `@final`, so nothing subclasses it; declares
`__slots__`, so it has no `__dict__`; and refuses every write in `__setattr__` and `__delattr__`, raising
`FrozenInstanceError` as a frozen dataclass does, while its constructor sets its one slot with `object.__setattr__`.
Typing the value `Never` in `__setattr__` makes pyright refuse a write too. The module's docstring explains it. They are
used in every layer.

Why: every expected failure is then visible in a signature, and pyright makes each caller handle it
([REJECTED](../../REJECTED.md#faults-as-bare-unions-and-exceptions)). The ledger refusing an event is not a failure:
`Ledger.process_event` returns `Ok` with an `EventRejected` entry, because the refusal is a fact the log records
(AMB-014). `Err` there means only a fault a bug brings.

## Protocols and Passing Effects In

```python
class ReportSink(Protocol):
    def publish(self, reports: tuple[DayReport, ...]) -> None: ...

@dataclass(frozen=True, slots=True)
class TextReportSink:                 # no base class, yet it is a ReportSink: it has publish
    out: TextOutput
    def publish(self, reports: tuple[DayReport, ...]) -> None: ...
```

A `Protocol` is an interface checked by shape: any class with the right methods satisfies it, without inheriting from
it. `run_cli(argv, read_text, out, err, run_ledger)` takes every effect as an argument: the file reader, the two output
streams, and the use case. Only `main` passes the real ones.

Where: the ports `EventSource`, `ReportSink`, and `RunLedger` in [`ports.py`][ports]; `TextOutput` in
[`text_report.py`][text-report]. The unit tests in [`tests/unit/test_cli.py`][test-cli] pass stand-ins such as
`FailingRun`, which returns a fault, and `ClosedPipe`, which raises `BrokenPipeError`.

Why: the domain and the application stay pure: they read no file and print nothing, so every rule is tested in memory
with no setup. The architecture calls this a functional core with an imperative shell. No class inherits from another
except a `Protocol`, `Generic`, `Enum`, or exception ([REJECTED](../../REJECTED.md#shared-base-classes)), and pylint's
`too-many-ancestors` check enforces it.

## Narrowing a Type With TypeIs

```python
def is_aed(account: AccountOpening) -> TypeIs[AccountOpeningIn[Aed]]:
    return isinstance(account.balance, Aed)

if is_aed(opening):
    return AccountIn(opening.id, opening.balance, entries)    # here: an AED opening
return AccountIn(opening.id, opening.balance, entries)        # here: pyright knows it is BHD
```

A function returning `TypeIs[X]` tells pyright that when it returns `True` its argument is an `X`, and when it returns
`False` it is whatever else the union allowed.

Where: `is_aed` in [`config.py`][config], used by `Ledger.find_account` in [`ledger.py`][ledger]. The two branches of
`find_account` read the same, and they are not a mistake: `AccountIn[M]` needs `M` to be exactly one currency, so each
branch builds the account from an opening whose currency pyright already knows. `_parse_amount` in [`csv_file.py`][csv]
does the same with `match sample: case Aed(): … case Bhd(): …`.

## Decimal, Never Float

```python
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_DOWN

0.1 + 0.2                                             # 0.30000000000000004, binary floating point
Decimal("0.1") + Decimal("0.2")                       # Decimal('0.3'), exact
Decimal("0.114").quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)   # Decimal('0.11')
Decimal("3.3333").quantize(Decimal("0.001"), rounding=ROUND_DOWN)      # Decimal('3.333')
```

`Decimal` is exact decimal arithmetic. It is built from a string, because `Decimal(0.1)` would copy the float's binary
error. `quantize` rounds to a given number of places with a named rounding mode: `ROUND_HALF_EVEN` sends an exact half
to the even digit, and `ROUND_DOWN` drops the extra digits. `value.as_tuple().exponent` gives a value's places as a
negative number, and `Decimal(1).scaleb(-2)` is 0.01. Python's default context keeps 28 significant digits.

Where: only [`money.py`][money]; no `Decimal` leaves it. `DAILY_RATE = Decimal("0.0004")`; `_round_money` rounds
half-even to the currency's places; `AmountIn.split` rounds down and puts the remainder on the last part;
`_make_scaled_value` refuses an amount with more places than its currency.

Why: money must be exact, so a float never touches it. Each constant and its reason, the rate literal, the 28 digits,
the amount limit, and the rounding mode, is in [NUMBERS](../../NUMBERS.md); the rounding mode is AMB-006 and the split
is AMB-020.

## Operators on Your Own Types

```python
def __add__(self, other: Self) -> Self:
    if type(other) is not type(self):
        return NotImplemented             # Python then raises TypeError
    return type(self)(self.value + other.value)
```

A method named `__add__`, `__sub__`, or `__neg__` defines `+`, `-`, or unary minus for a class. Returning
`NotImplemented` tells Python the operation is not defined for that pair, so `Aed + Bhd` fails.

Where: `Aed` and `Bhd` in [`money.py`][money]. Why: `closing - holds` reads as the rule it is, and the check refuses
mixed currencies at run time as well as in pyright. Code that sums many values uses `add_all`, which returns a
`CurrencyMismatch` as a `Result` rather than raising.

## Loops, Generators, and Unpacking

```python
def span_to(self, last_day: Day) -> Iterator[Day]:
    day = self
    while day <= last_day:
        yield day                              # hand out one day, then continue from here
        day = day.advance()

first = next((entry for entry in entries if entry.event.id == event_id), None)   # the first match, or None
log = EventLog((*self.entries, *entries))    # a new tuple: the old entries, then the new ones
```

A function with `yield` is a generator: it hands out values one at a time. `(x for x in xs if …)` is a generator
expression, and `next(generator, None)` takes its first value or `None`. `*` unpacks a tuple into another tuple or into
a call's arguments; `def _append(self, *entries)` takes any number of arguments as a tuple. `zip(a, b, strict=True)`
pairs two sequences and raises if their lengths differ. `enumerate(parts, start=1)` numbers the items from 1.

Where: `Day.span_to` in [`ids.py`][ids], which the fee and interest steps walk; `EventLog.find_first_entry` and
`EventLog.append` in [`event_log.py`][event-log]; `AccountIn._list_counted_events` in [`account.py`][account], a
generator; `Credit.make_instalments` in [`events.py`][events], with `enumerate`.

## Collections That Cannot Change

`tuple` is an immutable list, `frozenset` an immutable set, and `types.MappingProxyType` a read-only view of a dict. The
log is a tuple of entries; `capitalization_days` is a frozenset; each report's balances are a `MappingProxyType`. What
crosses an object or module boundary, the log, the configuration, and the reports, is one of these, so nothing that
receives it can change it; a private helper may still build and return a plain list or dict for its caller alone.

## Functions as Values

```python
steps: list[_Step] = [
    lambda account: account.assess_fees(today, self.config.first_day),
    lambda account: account.accrue_interest(today, self.config.first_day),
]
```

A `lambda` is a one-expression function. `Ledger.close_day` in [`ledger.py`][ledger] keeps the day's steps in a list and
runs each on every account, so the order of the steps (AMB-023) is the order of the list; `type _Step` names the
function type they share.

## Where Exceptions Remain

Exceptions are left for three things: a constructor guard that only a bug reaches (`__post_init__`); a library that
refuses by raising, caught at once and turned into an `Err`, as `_read_decimal` does with `InvalidOperation`,
`read_file` with `OSError` and `UnicodeDecodeError`, and `_read_rows` with `csv.Error`; and the shell's signals.
`run_cli` in [`cli.py`][cli] catches `BrokenPipeError` (exit 141), `KeyboardInterrupt` (exit 130), and, as a last
resort, any other exception, which prints one line and exits 2 rather than a traceback.

## Tests With pytest

```python
@pytest.mark.parametrize(("stream", "account", "reason", "_text"), REFUSALS.values(), ids=REFUSALS.keys())
def test_amb_014_a_rejected_event_is_that_days_error(
    stream: tuple[IncomingEvent, ...], account: AccountId, reason: Rejection, _text: str
) -> None:
    ...                                   # process the stream, then assert its refusal is the day's error
```

pytest runs every function named `test_*` in a file named `test_*.py`, and a plain `assert` is the check.
`@pytest.mark.parametrize` runs one test once per row of data. `@pytest.mark.xfail(strict=True, reason=…)` marks a test
expected to fail: the run stays green while it fails, and turns red if it starts to pass. `pyproject.toml` sets
`pythonpath = ["src", "tests"]` and `--import-mode=importlib`, so tests import `account_ledger` and the helpers in
`tests/support/` directly, with no `conftest.py` or `__init__.py`.

Where: `tests/unit/` mirrors the source folders and injects every effect; `tests/integration/` reads the real stream
file and runs `main` against real file descriptors; `tests/e2e/` runs `python -m account_ledger` as a subprocess and
compares its output with OUTPUT_TARGET. `tests/support/` holds the brief's stream as objects and as CSV, event builders
such as `make_debit`, readers that turn a log into plain values, and `REFUSALS`, one example stream per refusal, which
drives the parametrized tests. The one expected failure is `test_known_weakness_an_unsettled_hold_never_expires` in
[`test_stream.py`][test-stream], the brief's failing test (AMB-018, AMB-031).

Why: each criterion and resolved ambiguity names its test, so a reader goes from a rule to the test that proves it, and
the tests were written before the code they test, as the
[test-driven development](../../repo-governance/development/quality/testing/test-driven-development.md) rule requires.

[src]: ../../apps/account-ledger-cli/src/account_ledger/__init__.py
[python-version]: ../../apps/account-ledger-cli/.python-version
[pyproject]: ../../apps/account-ledger-cli/pyproject.toml
[main-module]: ../../apps/account-ledger-cli/src/account_ledger/__main__.py
[cli]: ../../apps/account-ledger-cli/src/account_ledger/cli.py
[ids]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/ids.py
[money]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/money.py
[config]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/config.py
[events]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/events.py
[stream]: ../../apps/account-ledger-cli/src/account_ledger/application/stream.py
[ports]: ../../apps/account-ledger-cli/src/account_ledger/application/ports.py
[result]: ../../apps/account-ledger-cli/src/account_ledger/common/result.py
[account]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/account.py
[authorizations]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/authorizations.py
[domain-events]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/domain_events.py
[rejections]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/rejections.py
[event-log]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/event_log.py
[ledger]: ../../apps/account-ledger-cli/src/account_ledger/domain/ledger/ledger.py
[csv]: ../../apps/account-ledger-cli/src/account_ledger/adapters/csv_file.py
[text-report]: ../../apps/account-ledger-cli/src/account_ledger/adapters/text_report.py
[test-cli]: ../../apps/account-ledger-cli/tests/unit/test_cli.py
[test-stream]: ../../apps/account-ledger-cli/tests/unit/application/test_stream.py
