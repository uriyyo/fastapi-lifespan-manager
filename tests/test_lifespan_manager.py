from contextlib import asynccontextmanager, contextmanager

import pytest
from asgi_lifespan import LifespanManager as ASGILifespanManager
from fastapi import FastAPI

from fastapi_lifespan_manager.lifespan_manager import LifespanManager

STATE = {"foo": "bar"}
NO_STATE = None


async def _async_gen_no_state(_):
    yield


async def _async_gen_with_state(_):
    yield STATE


@asynccontextmanager
async def _async_ctx_no_state(_):
    yield


@asynccontextmanager
async def _async_ctx_with_state(_):
    yield STATE


def _gen_no_state(_):
    yield


def _gen_with_state(_):
    yield STATE


@contextmanager
def _ctx_no_state(_):
    yield


@contextmanager
def _ctx_with_state(_):
    yield STATE


async def _async_gen_no_state_no_app():
    yield


async def _async_gen_with_state_no_app():
    yield STATE


@asynccontextmanager
async def _async_ctx_no_state_no_app():
    yield


@asynccontextmanager
async def _async_ctx_with_state_no_app():
    yield STATE


def _gen_no_state_no_app():
    yield


def _gen_with_state_no_app():
    yield STATE


@contextmanager
def _ctx_no_state_no_app():
    yield


@contextmanager
def _ctx_with_state_no_app():
    yield STATE


async def get_state(manager: LifespanManager):
    app = FastAPI(lifespan=manager)

    async with ASGILifespanManager(app) as asgi_manager:
        return {**asgi_manager._state}


@pytest.mark.parametrize(
    ("raw_lifespan", "has_state"),
    [
        (_async_gen_no_state, False),
        (_async_gen_with_state, True),
        (_async_ctx_no_state, False),
        (_async_ctx_with_state, True),
        (_gen_no_state, False),
        (_gen_with_state, True),
        (_ctx_no_state, False),
        (_ctx_with_state, True),
        (_async_gen_no_state_no_app, False),
        (_async_gen_with_state_no_app, True),
        (_async_ctx_no_state_no_app, False),
        (_async_ctx_with_state_no_app, True),
        (_gen_no_state_no_app, False),
        (_gen_with_state_no_app, True),
        (_ctx_no_state_no_app, False),
        (_ctx_with_state_no_app, True),
    ],
)
@pytest.mark.asyncio()
async def test_lifespan_manager(raw_lifespan, has_state):
    manager = LifespanManager([raw_lifespan])

    state = await get_state(manager)
    assert state == (STATE if has_state else {})


@pytest.mark.asyncio()
async def test_add():
    manager = LifespanManager()

    called = False

    @manager.add
    async def _lifespan(_):
        nonlocal called
        called = True
        yield

    assert not called

    await get_state(manager)

    assert called


@pytest.mark.asyncio()
async def test_state_inside_lifespan():
    manager = LifespanManager()

    @manager.add
    async def _lifespan_1(app, state):
        assert state == {}
        yield {"foo": "bar"}

    @manager.add
    async def _lifespan_2(app, state):
        assert state == {"foo": "bar"}
        yield

    await get_state(manager)


@pytest.mark.asyncio()
async def test_remove():
    manager = LifespanManager()

    called = False

    @manager.add
    async def _lifespan(_):
        nonlocal called
        called = True
        yield

    assert not called

    manager.remove(_lifespan)

    await get_state(manager)

    assert not called


@pytest.mark.asyncio()
async def test_include():
    calls = 0

    def _lifespan():
        nonlocal calls
        calls += 1
        yield

    parent = LifespanManager([_lifespan])
    child = LifespanManager([_lifespan])

    await get_state(parent)
    assert calls == 1

    parent.include(child)

    await get_state(parent)
    assert calls == 3
