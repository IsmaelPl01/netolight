"""This module provides helper functions for managing postgres."""

import functools
from collections.abc import AsyncGenerator
from typing import Any

import sqlalchemy as sa
import sqlalchemy.ext.asyncio
import sqlalchemy.orm
import sqlalchemy.types

import api.config


class Base(sqlalchemy.orm.DeclarativeBase):  # type: ignore[name-defined]
    """Base class for models."""

    type_annotation_map = {dict[str, Any]: sqlalchemy.types.JSON}  # noqa: RUF012


Db = sqlalchemy.ext.asyncio.AsyncSession


@functools.lru_cache
def get_engine() -> sqlalchemy.ext.asyncio.AsyncEngine:
    """Get the async engine instance."""
    settings = api.config.get_settings()
    return sqlalchemy.ext.asyncio.create_async_engine(
        settings.NL_API_POSTGRES_URI, pool_pre_ping=True, echo=False
    )


def get_session() -> (
    sa.ext.asyncio.async_sessionmaker[sa.ext.asyncio.AsyncSession]
):
    """Get an SqlAlchemy async session."""
    return sqlalchemy.ext.asyncio.async_sessionmaker(  # type: ignore[attr-defined]
        get_engine(), expire_on_commit=False
    )


async def get_db() -> AsyncGenerator:
    """Get a DB instance."""
    async with get_session().begin() as db:
        yield db
