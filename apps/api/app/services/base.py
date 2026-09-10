"""Base Service Module.

Provides transaction lifecycle management, savepoint handling, and session coordination for business logic.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseService:
    """Base application service managing database sessions and transaction boundaries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """Execute a block of operations within an atomic transaction or savepoint."""
        if self.session.in_transaction():
            async with self.session.begin_nested():
                try:
                    yield self.session
                except Exception as exc:
                    logger.debug("Nested savepoint rollback triggered: %s", exc)
                    raise
        else:
            async with self.session.begin():
                try:
                    yield self.session
                except Exception as exc:
                    logger.warning("Transaction rollback triggered: %s", exc)
                    await self.session.rollback()
                    raise

    async def commit(self) -> None:
        """Explicitly commit pending session changes."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Roll back pending session changes."""
        await self.session.rollback()
