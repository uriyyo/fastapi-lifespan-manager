`fastapi-lifespan-manager` is a Python library that provides a lifespan manager for FastAPI applications.
`FastAPI` is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard
Python type hints. The lifespan manager in `fastapi-lifespan-manager` allows you to have multiple lifespan in one
application.

This library is particularly useful for managing background tasks, such as starting and stopping a database
connection or managing a cache, as well as for performing cleanup tasks, such as closing open file
handles or shutting down running processes.

To use `fastapi-lifespan-manager`, simply install it via pip:

```bash
pip install fastapi-lifespan-manager
```

Usage Example:

```python
from typing import AsyncIterator

from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_lifespan_manager import LifespanManager, State

manager = LifespanManager()


@manager.add
async def setup_db(app: FastAPI) -> AsyncIterator[State]:
    engine = await create_async_engine("postgresql+asyncpg://user:password@localhost/db")

    yield {"db": engine}

    await engine.dispose()


@manager.add
async def setup_cache(app: FastAPI) -> AsyncIterator[State]:
    redis = await Redis.from_url("redis://localhost:6379/0")

    yield {"cache": redis}

    await redis.close()
    await redis.wait_closed()


app = FastAPI(lifespan=manager)
```
