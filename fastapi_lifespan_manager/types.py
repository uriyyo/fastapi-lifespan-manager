from typing import Any, AsyncContextManager, AsyncIterator, Callable, ContextManager, Iterator, Mapping, TypeVar, Union

from typing_extensions import TypeAlias

TApp = TypeVar("TApp")


NoState: TypeAlias = None
State: TypeAlias = Mapping[str, Any]
AnyState: Any = Union[NoState, State]

AnyContextManager: TypeAlias = Union[ContextManager[AnyState], AsyncContextManager[AnyState]]
AnyIterator: TypeAlias = Union[Iterator[AnyState], AsyncIterator[AnyState]]

RawLifespan: TypeAlias = Union[
    # (app, state) -> ...
    Callable[[TApp, State], Union[AnyContextManager, AnyIterator]],
    # (app) -> ...
    Callable[[TApp], Union[AnyContextManager, AnyIterator]],
    # () -> ...
    Callable[[], Union[AnyContextManager, AnyIterator]],
]
Lifespan: TypeAlias = Union[
    Callable[[TApp], AsyncContextManager[NoState]],
    Callable[[TApp], AsyncContextManager[State]],
]

__all__ = [
    "AnyContextManager",
    "AnyIterator",
    "AnyState",
    "Lifespan",
    "NoState",
    "RawLifespan",
    "State",
    "TApp",
]
