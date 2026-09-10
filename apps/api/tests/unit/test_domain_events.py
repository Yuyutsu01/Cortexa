"""Unit Tests for Domain Events and Event Dispatcher."""

from uuid import uuid4

import pytest

from app.domain.enums import UserRole
from app.domain.events import (
    BaseDomainEvent,
    EventDispatcher,
    MembershipCreatedEvent,
    OrganizationCreatedEvent,
    UserCreatedEvent,
)


@pytest.mark.asyncio
async def test_domain_event_creation_and_attributes() -> None:
    """Verify base and specialized domain event attributes."""
    user_id = uuid4()
    org_id = uuid4()

    event = UserCreatedEvent(
        actor_id=user_id,
        user_id=user_id,
        email="test@cortexa.ai",
        full_name="Test User",
    )
    assert event.event_name == "UserCreatedEvent"
    assert event.user_id == user_id
    assert event.email == "test@cortexa.ai"
    assert event.occurred_at is not None

    org_event = OrganizationCreatedEvent(
        actor_id=user_id,
        organization_id=org_id,
        name="Acme Corp",
        slug="acme-corp",
        owner_user_id=user_id,
    )
    assert org_event.event_name == "OrganizationCreatedEvent"
    assert org_event.slug == "acme-corp"


@pytest.mark.asyncio
async def test_event_dispatcher_pub_sub() -> None:
    """Verify that subscribed handlers receive dispatched events."""
    dispatcher = EventDispatcher()
    received_events: list[BaseDomainEvent] = []

    async def sample_handler(event: UserCreatedEvent) -> None:
        received_events.append(event)

    dispatcher.subscribe(UserCreatedEvent, sample_handler)

    test_event = UserCreatedEvent(
        user_id=uuid4(),
        email="event@cortexa.ai",
    )
    await dispatcher.publish(test_event)

    assert len(received_events) == 1
    assert received_events[0] == test_event


@pytest.mark.asyncio
async def test_event_dispatcher_handles_failing_subscribers() -> None:
    """Verify that failing subscribers do not prevent other handlers or raise unhandled exceptions."""
    dispatcher = EventDispatcher()
    execution_order: list[str] = []

    async def broken_handler(event: MembershipCreatedEvent) -> None:
        execution_order.append("broken")
        raise RuntimeError("Simulated subscriber crash")

    async def good_handler(event: MembershipCreatedEvent) -> None:
        execution_order.append("good")

    dispatcher.subscribe(MembershipCreatedEvent, broken_handler)
    dispatcher.subscribe(MembershipCreatedEvent, good_handler)

    event = MembershipCreatedEvent(
        membership_id=uuid4(),
        user_id=uuid4(),
        role=UserRole.ADMIN,
    )
    # Publish should not raise
    await dispatcher.publish(event)

    assert "broken" in execution_order
    assert "good" in execution_order
