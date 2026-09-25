"""Result: a failure is a value the caller must handle, never an exception it might miss.

A fallible function returns ``Result[T, E]``: ``Ok`` with its value, or ``Err`` with a named fault. The caller takes it
apart with ``match`` or an ``isinstance`` early return, or chains it: ``map`` and ``map_err`` change one side,
``flat_map`` and ``flat_map_err`` continue with a step that may itself fail, and ``tap`` and ``tap_err`` look at one
side and pass the result on unchanged. Each method acts on its own side and hands the other back as it is.

Both are hand-written rather than dataclasses: each exposes its content only through a read-only property, so pyright
infers them covariant, and an ``Ok[bool]`` is an ``Ok[int]``; a frozen dataclass would be invariant. Each still refuses
every write and delete at runtime, its private slot included, with ``FrozenInstanceError`` as a frozen dataclass does;
typing the value ``Never`` keeps pyright refusing a write to any other name too.
"""

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Never, final


@final
class Ok[T]:
    """A success, holding its value."""

    __slots__ = ("_value",)
    __match_args__ = ("value",)
    _value: T

    def __init__(self, value: T) -> None:
        """Hold the success's value."""

        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> T:
        """The success's value."""

        return self._value

    @property
    def _content(self) -> object:
        """The held value, typed without ``T`` so another ``Ok`` can be compared with it."""

        return self._value

    def map[U](self, transform: Callable[[T], U]) -> Ok[U]:
        """The value, transformed."""

        return Ok(transform(self._value))

    def map_err(self, transform: Callable[[Never], object]) -> Ok[T]:
        """This success, unchanged: there is no fault to transform."""

        return self

    def flat_map[U, F](self, step: Callable[[T], Result[U, F]]) -> Result[U, F]:
        """What the next fallible step makes of the value."""

        return step(self._value)

    def flat_map_err(self, step: Callable[[Never], object]) -> Ok[T]:
        """This success, unchanged: there is no fault to recover from."""

        return self

    def tap(self, action: Callable[[T], object]) -> Ok[T]:
        """This success, unchanged, once ``action`` has seen its value."""

        action(self._value)

        return self

    def tap_err(self, action: Callable[[Never], object]) -> Ok[T]:
        """This success, unchanged: there is no fault to see."""

        return self

    def __setattr__(self, name: str, value: Never) -> Never:
        raise FrozenInstanceError(f"cannot assign to field {name!r}")

    def __delattr__(self, name: str) -> Never:
        raise FrozenInstanceError(f"cannot delete field {name!r}")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ok) and self._content == other._content

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"


@final
class Err[E]:
    """A failure, holding its fault."""

    __slots__ = ("_error",)
    __match_args__ = ("error",)
    _error: E

    def __init__(self, error: E) -> None:
        """Hold the failure's fault."""

        object.__setattr__(self, "_error", error)

    @property
    def error(self) -> E:
        """The failure's fault."""

        return self._error

    @property
    def _content(self) -> object:
        """The held fault, typed without ``E`` so another ``Err`` can be compared with it."""

        return self._error

    def map(self, transform: Callable[[Never], object]) -> Err[E]:
        """This failure, unchanged: there is no value to transform."""

        return self

    def map_err[F](self, transform: Callable[[E], F]) -> Err[F]:
        """The fault, transformed."""

        return Err(transform(self._error))

    def flat_map(self, step: Callable[[Never], object]) -> Err[E]:
        """This failure, unchanged: the next step does not run."""

        return self

    def flat_map_err[U, F](self, step: Callable[[E], Result[U, F]]) -> Result[U, F]:
        """What the recovering step makes of the fault."""

        return step(self._error)

    def tap(self, action: Callable[[Never], object]) -> Err[E]:
        """This failure, unchanged: there is no value to see."""

        return self

    def tap_err(self, action: Callable[[E], object]) -> Err[E]:
        """This failure, unchanged, once ``action`` has seen its fault."""

        action(self._error)

        return self

    def __setattr__(self, name: str, value: Never) -> Never:
        raise FrozenInstanceError(f"cannot assign to field {name!r}")

    def __delattr__(self, name: str) -> Never:
        raise FrozenInstanceError(f"cannot delete field {name!r}")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Err) and self._content == other._content

    def __repr__(self) -> str:
        return f"Err({self._error!r})"


type Result[T, E] = Ok[T] | Err[E]
