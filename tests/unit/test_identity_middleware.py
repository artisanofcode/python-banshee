"""
Tests for :class:`banshee.IdentityMiddleware`
"""

import uuid

import pytest

import banshee

import tests.fixture


@pytest.mark.asyncio
async def test_it_should_add_identity_context_to_message_when_absent() -> None:
    """
    it should add identity context to message when absent.
    """
    unique_id = uuid.uuid4()

    message = banshee.message_for(object())

    fake_handle = tests.fixture.mock_handle_message()

    middleware = banshee.IdentityMiddleware()

    result = await middleware(message, fake_handle)

    unique_id = result[banshee.Identity].unique_id

    assert isinstance(unique_id, uuid.UUID)

    expected = message.including(banshee.Identity(unique_id=unique_id))

    fake_handle.assert_awaited_once_with(expected)

    assert result == expected


@pytest.mark.asyncio
async def test_it_should_not_add_identity_context_to_message_when_present() -> None:
    """
    it should not add identity context to message when already present.
    """
    message = banshee.message_for(object(), [banshee.Identity(uuid.uuid4())])

    fake_handle = tests.fixture.mock_handle_message()

    middleware = banshee.IdentityMiddleware()

    result = await middleware(message, fake_handle)

    fake_handle.assert_awaited_once_with(message)

    assert result == message


@pytest.mark.asyncio
async def test_it_should_add_a_unique_identity_context_to_messages() -> None:
    """
    it should add a unique identity context to messages.
    """
    unique_ids = set()

    middleware = banshee.IdentityMiddleware()

    for _ in range(10):
        result = await middleware(
            banshee.message_for(object()),
            tests.fixture.mock_handle_message(),
        )

        unique_ids.add(result[banshee.Identity].unique_id)

    assert len(unique_ids) == 10
