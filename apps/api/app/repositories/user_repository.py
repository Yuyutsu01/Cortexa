"""User Repository Module."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access repository for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str, include_deleted: bool = False) -> User | None:
        """Find a user by normalized lowercase email address."""
        query = select(User).where(User.email == email.lower().strip())
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        user = await self.get_by_email(email, include_deleted=True)
        return user is not None
