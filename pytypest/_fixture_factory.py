from __future__ import annotations

from typing import (
    Callable, Iterator, Literal, ParamSpec, Protocol, TypeVar, overload,
)

from ._fixture import Fixture
from ._scope import Scope


R = TypeVar('R')
P = ParamSpec('P')


class FixtureMaker(Protocol):
    @overload
    def __call__(self, callback: Callable[P, Iterator[R]]) -> Fixture[P, R]:
        ...

    @overload
    def __call__(self, callback: Callable[P, R]) -> Fixture[P, R]:
        ...

    def __call__(self, callback):
        ...


class FixtureMakerWithScope(Protocol):
    @overload
    def __call__(self, callback: Callable[[], Iterator[R]]) -> Fixture[[], R]:
        ...

    @overload
    def __call__(self, callback: Callable[[], R]) -> Fixture[[], R]:
        ...

    def __call__(self, callback):
        ...


@overload
def fixture(
    callback: None = None,
    *,
    scope: Literal[Scope.FUNCTION] = Scope.FUNCTION,
) -> FixtureMaker:
    pass


@overload
def fixture(
    callback: None = None,
    *,
    scope: Scope,
) -> FixtureMakerWithScope:
    pass


@overload
def fixture(callback: Callable[P, Iterator[R]]) -> Fixture[P, R]:
    pass


@overload
def fixture(callback: Callable[P, R]) -> Fixture[P, R]:
    pass


def fixture(callback: Callable | None = None, **kwargs) -> Fixture[P, R] | Callable:
    def wrapper(callback):
        return Fixture(callback, **kwargs)
    if callback is not None:
        return Fixture(callback, **kwargs)
    return wrapper
