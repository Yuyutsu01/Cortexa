"""Domain Events & Event Dispatcher.

Provides a lightweight, decoupled event-driven foundation for domain state transitions.
"""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import UUID, uuid4

from app.domain.enums import UserRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BaseDomainEvent:
    """Base class for all domain events in Cortexa."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    actor_id: UUID | None = None
    organization_id: UUID | None = None

    @property
    def event_name(self) -> str:
        """Name identifier of the event."""
        return self.__class__.__name__


@dataclass(frozen=True)
class UserCreatedEvent(BaseDomainEvent):
    """Fired when a new user account is registered."""

    user_id: UUID = field(default_factory=uuid4)
    email: str = ""
    full_name: str | None = None


@dataclass(frozen=True)
class OrganizationCreatedEvent(BaseDomainEvent):
    """Fired when a new organization tenant is established."""

    organization_id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""
    owner_user_id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class MembershipCreatedEvent(BaseDomainEvent):
    """Fired when a user is granted membership in an organization."""

    membership_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    role: UserRole = UserRole.MEMBER


@dataclass(frozen=True)
class MembershipRoleUpdatedEvent(BaseDomainEvent):
    """Fired when a member's role within an organization is changed."""

    membership_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    old_role: UserRole = UserRole.MEMBER
    new_role: UserRole = UserRole.MEMBER


@dataclass(frozen=True)
class MembershipRemovedEvent(BaseDomainEvent):
    """Fired when a user membership is revoked from an organization."""

    membership_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)


# Event Handler Type
E = TypeVar("E", bound=BaseDomainEvent)
EventHandler = Callable[[Any], Awaitable[None]]


class EventDispatcher:
    """Asynchronous in-memory event dispatcher for domain events."""

    def __init__(self) -> None:
        self._handlers: dict[type[BaseDomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[BaseDomainEvent], handler: EventHandler) -> None:
        """Register an async handler callback for a specific domain event."""
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler %s to event %s", handler.__name__, event_type.__name__)

    async def publish(self, event: BaseDomainEvent) -> None:
        """Dispatch a domain event to all registered handlers concurrently."""
        handlers = self._handlers.get(type(event), [])
        if not handlers:
            logger.debug("No handlers registered for event %s", event.event_name)
            return

        logger.info("Publishing domain event: %s (id: %s)", event.event_name, event.event_id)
        # Execute handlers concurrently and safely capture errors without breaking callers
        tasks = [self._safe_execute(handler, event) for handler in handlers]
        await asyncio.gather(*tasks)

    async def _safe_execute(self, handler: EventHandler, event: BaseDomainEvent) -> None:
        try:
            await handler(event)
        except Exception as exc:
            logger.error(
                "Error executing event handler %s for event %s: %s",
                handler.__name__,
                event.event_name,
                exc,
                exc_info=True,
            )


# Global event dispatcher singleton
event_dispatcher = EventDispatcher()
