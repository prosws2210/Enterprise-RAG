"""
Enterprise RAG — Async PostgreSQL connection pool.

Uses psycopg3's async pool so all route handlers share a fixed set of
connections instead of opening a new connection per request.

Usage (FastAPI dependency):

    from app.db.pool import get_db_conn

    @router.get("/example")
    async def example(conn=Depends(get_db_conn)):
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import psycopg
from psycopg_pool import AsyncConnectionPool

from app.config import settings

_pool: AsyncConnectionPool | None = None


async def init_pool() -> None:
    """Create the shared async connection pool.  Call once at app startup."""
    global _pool
    _pool = AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=2,
        max_size=10,
        open=False,
    )
    await _pool.open()


async def close_pool() -> None:
    """Close the shared async connection pool.  Call once at app shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def _acquire() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """Internal context manager to borrow a connection from the pool."""
    if _pool is None:
        raise RuntimeError("DB pool not initialised — call init_pool() at startup.")
    async with _pool.connection() as conn:
        yield conn


async def get_db_conn() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """FastAPI dependency that yields a pooled async psycopg connection."""
    async with _acquire() as conn:
        yield conn
