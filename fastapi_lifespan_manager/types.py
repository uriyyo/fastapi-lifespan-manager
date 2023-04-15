from typing import Any, AsyncContextManager, AsyncIterator, Callable, ContextManager, Iterator, Mapping, Union

from typing_extensions import TypeAlias, TypeVar

NoState: TypeAlias = None
State: TypeAlias = Mapping[str, Any]
AnyState: Any = Union[NoState, State]

TApp = TypeVar("TApp")

RawLifespan: TypeAlias = Union[
    Callable[[TApp], Iterator[NoState]],
    Callable[[TApp], Iterator[State]],
    Callable[[TApp], ContextManager[NoState]],
    Callable[[TApp], ContextManager[State]],
    Callable[[TApp], AsyncIterator[NoState]],
    Callable[[TApp], AsyncIterator[State]],
    Callable[[TApp], AsyncContextManager[NoState]],
    Callable[[TApp], AsyncContextManager[State]],
]
Lifespan: TypeAlias = Union[
    Callable[[TApp], AsyncContextManager[NoState]],
    Callable[[TApp], AsyncContextManager[State]],
]

__all__ = [
    "TApp",
    "State",
    "NoState",
    "AnyState",
    "Lifespan",
    "RawLifespan",
]
