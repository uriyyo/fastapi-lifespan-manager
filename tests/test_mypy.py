import textwrap
from subprocess import run

import pytest


def _run_mypy(code: str) -> str:
    code = textwrap.dedent(code).strip()
    res = run(f"poetry run mypy -c '{code}'", capture_output=True, text=True, shell=True)

    return res.stdout


def _normalize_check(code: str = "", success: bool = True) -> str:
    code = textwrap.dedent(code).strip()
    if code:
        code += "\n"

    return code + "Success: no issues found in 1 source file\n" if success else ""


def test_manager_no_args():
    output = _run_mypy(
        """
    from fastapi_lifespan_manager import LifespanManager

    manager = LifespanManager()
    reveal_type(manager)
    """,
    )

    assert output == _normalize_check(
        """
    <string>:4:13: note: Revealed type is "fastapi_lifespan_manager.lifespan_manager.LifespanManager[fastapi.applications.FastAPI]"
    """,
    )


def test_manager_with_args():
    output = _run_mypy(
        """
    from starlette.applications import Starlette
    from fastapi_lifespan_manager import LifespanManager, NoState
    from typing import Iterator

    def _lifespan(app: Starlette) -> Iterator[NoState]:
        yield

    manager = LifespanManager[Starlette]([_lifespan])
    reveal_type(manager)
    """,
    )

    assert output == _normalize_check(
        """
    <string>:9:13: note: Revealed type is "fastapi_lifespan_manager.lifespan_manager.LifespanManager[starlette.applications.Starlette]"
    """,
    )


@pytest.mark.parametrize(
    "code",
    [
        """\
    def _lifespan(app: FastAPI) -> Iterator[NoState]:
        yield""",
        """\
    def _lifespan(app: FastAPI) -> Iterator[State]:
        yield {}""",
        """\
    @contextmanager
    def _lifespan(app: FastAPI) -> Iterator[NoState]:
        yield""",
        """\
    @contextmanager
    def _lifespan(app: FastAPI) -> Iterator[State]:
        yield {}""",
        """\
    async def _lifespan(app: FastAPI) -> AsyncIterator[NoState]:
        yield""",
        """\
    async def _lifespan(app: FastAPI) -> AsyncIterator[State]:
        yield {}""",
        """\
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[NoState]:
        yield""",
        """\
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[State]:
        yield {}""",
    ],
    ids=[
        "gen-no-state",
        "gen-with-state",
        "ctx-no-state",
        "ctx-with-state",
        "async-gen-no-state",
        "async-gen-with-state",
        "async-ctx-no-state",
        "async-ctx-with-state",
    ],
)
def test_different_kind_of_lifespans(code):
    output = _run_mypy(
        f"""
    from fastapi import FastAPI
    from fastapi_lifespan_manager import LifespanManager, NoState, State
    from typing import Iterator, AsyncIterator
    from contextlib import asynccontextmanager, contextmanager

{code}

    manager = LifespanManager([_lifespan])
    """,
    )

    assert output == _normalize_check()
