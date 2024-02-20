from __future__ import annotations

import inspect
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager, suppress
from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    ContextManager,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
    cast,
    overload,
)

from fastapi import FastAPI
from fastapi.concurrency import contextmanager_in_threadpool
from typing_extensions import Self

from .types import AnyContextManager, AnyState, RawLifespan, State, TApp


def _maybe_call(call: Callable[..., AnyContextManager], app: Optional[TApp], state: State) -> AnyContextManager:
    with suppress(TypeError):
        return call(app, state)

    with suppress(TypeError):
        return call(app)

    return call()


def _convert_raw_lifespan_to_ctx(
    app: TApp,
    state: State,
    raw_lifespan: RawLifespan[TApp],
) -> Union[ContextManager[AnyState], AsyncContextManager[AnyState]]:
    if inspect.isasyncgenfunction(raw_lifespan):
        return _maybe_call(asynccontextmanager(raw_lifespan), app, state)
    if inspect.isgeneratorfunction(raw_lifespan):
        return _maybe_call(contextmanager(raw_lifespan), app, state)

    return _maybe_call(cast(Callable[..., AnyContextManager], raw_lifespan), app, state)


@asynccontextmanager
async def _run_raw_lifespan(
    raw_lifespan: RawLifespan[TApp],
    app: TApp,
    state: State,
) -> AsyncIterator[AnyState]:
    ctx = _convert_raw_lifespan_to_ctx(app, state, raw_lifespan)

    actx: AsyncContextManager[AnyState]
    actx = contextmanager_in_threadpool(ctx) if isinstance(ctx, ContextManager) else ctx

    async with actx as res:
        yield res


class LifespanManager(Generic[TApp]):
    lifespans: List[RawLifespan[TApp]]

    if TYPE_CHECKING:

        @overload
        def __new__(cls, __lifespans: Iterable[RawLifespan[TApp]], /) -> LifespanManager[TApp]:
            pass

        @overload
        def __new__(cls, __lifespans: Literal[None] = None, /) -> LifespanManager[FastAPI]:
            pass

        def __new__(cls, __lifespans: Optional[Iterable[RawLifespan[TApp]]] = ..., /) -> LifespanManager[Any]:
            pass

    else:

        def __init__(self, lifespans: Optional[Iterable[RawLifespan[TApp]]] = None, /) -> None:
            self.lifespans = [*(lifespans or [])]

    def add(self, lifespan: RawLifespan[TApp]) -> RawLifespan[TApp]:
        self.lifespans.append(lifespan)
        return lifespan

    def remove(self, lifespan: RawLifespan[TApp]) -> None:
        self.lifespans.remove(lifespan)

    def include(self, other: Self) -> None:
        self.lifespans.extend(other.lifespans)

    @asynccontextmanager
    async def __call__(self, app: TApp) -> AsyncIterator[AnyState]:
        async with AsyncExitStack() as astack:
            state: Dict[str, Any] = {}
            state_proxy: State = MappingProxyType(state)

            for raw_lifespan in self.lifespans:
                sub_state = await astack.enter_async_context(_run_raw_lifespan(raw_lifespan, app, state_proxy))

                if sub_state:
                    state.update(sub_state)

            yield state


if not TYPE_CHECKING:
    # mypy complains about using a dataclass directly with LifeSpanManager
    LifeSpanManager = dataclass(init=False)(LifespanManager)

__all__ = [
    "LifespanManager",
]
