from asyncio import new_event_loop

import pytest


@pytest.fixture(scope="session")
def event_loop():
    loop = new_event_loop()
    yield loop
    loop.close()
