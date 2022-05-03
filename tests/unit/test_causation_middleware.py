"""
Tests for :class:`banshee.CausationMiddleware`
"""

import asyncio
import logging
import typing
import unittest.mock
import uuid

import pytest

import banshee

import tests.fixture

T = typing.TypeVar("T")


@pytest.mark.asyncio
async def test_it_should_skip_when_identity_context_is_absent(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    it should skip when identity context is absent.
    """
    message = banshee.Message(object())

    fake_handle = tests.fixture.mock_handle_message()

    middleware = banshee.CausationMiddleware()

    with caplog.at_level(logging.DEBUG, logger="banshee.middleware.causation"):
        result = await middleware(message, fake_handle)

    assert caplog.record_tuples == [
        (
            "banshee.middleware.causation",
            logging.INFO,
            "no identity for %(request_class)s found.",
        )
    ]

    assert typing.cast(typing.Any, caplog.records[0]).request_class == "object"

    fake_handle.assert_awaited_once_with(message)

    assert result == message


@pytest.mark.asyncio
async def test_it_should_add_causation_context_when_identity_context_exists() -> None:
    """
    it should add causation context when identity context exists.
    """
    unique_id = uuid.uuid4()

    message = banshee.message_for(object(), [banshee.Identity(unique_id)])

    fake_handle = tests.fixture.mock_handle_message()

    middleware = banshee.CausationMiddleware()

    result = await middleware(message, fake_handle)

    expected = message.including(banshee.Causation(unique_id, unique_id))

    fake_handle.assert_awaited_once_with(expected)

    assert result == expected


@pytest.mark.asyncio
async def test_it_should_add_causation_context_for_each_message() -> None:
    """
    it should add causation context for each message.
    """
    unique_ids = [uuid.uuid4() for _ in range(10)]

    messages = [
        banshee.message_for(object(), [banshee.Identity(v)]) for v in unique_ids
    ]

    fake_handle = tests.fixture.mock_handle_message()

    middleware = banshee.CausationMiddleware()

    for message in messages:
        await middleware(message, fake_handle)

    # sequential messages get causation context based on passed messages identity
    # context
    expected = (
        v.including(banshee.Causation(unique_ids[i], unique_ids[i]))
        for i, v in enumerate(messages)
    )

    fake_handle.assert_has_awaits(unittest.mock.call(v) for v in expected)


@pytest.mark.asyncio
async def test_it_should_add_causation_context_based_on_previous_messages() -> None:
    """
    it should add causation context based on previous message when nested.
    """
    unique_ids = [uuid.uuid4() for _ in range(10)]

    messages = [
        banshee.message_for(object(), [banshee.Identity(v)]) for v in unique_ids
    ]

    iterator = iter(messages)

    middleware = banshee.CausationMiddleware()

    fake_handle = tests.fixture.mock_recursive_handle_message(iterator, middleware)

    await middleware(next(iterator), fake_handle)

    # nested messages get causation_id context based on previous messages
    # identity and correlation_id of initial message
    expected = (
        v.including(banshee.Causation(unique_ids[max(0, i - 1)], unique_ids[0]))
        for i, v in enumerate(messages)
    )

    fake_handle.assert_has_awaits(unittest.mock.call(v) for v in expected)


@pytest.mark.asyncio
async def test_it_should_only_consider_current_asyncio_task() -> None:
    """
    it should only consider current asyncio task.
    """
    unique_ids = [uuid.uuid4() for _ in range(10)]

    messages = [
        banshee.message_for(object(), [banshee.Identity(unique_id)])
        for unique_id in unique_ids
    ]

    middleware = banshee.CausationMiddleware()

    # run all the messages at once, when not properly isolated this will fail as the
    # middleware will mistake messages from other tasks as being nested.
    results = await asyncio.gather(
        *(
            asyncio.create_task(
                middleware(message, tests.fixture.mock_handle_message())
            )
            for message in messages
        )
    )

    expected = {
        message.including(banshee.Causation(unique_id, unique_id))
        for unique_id, message in zip(unique_ids, messages)
    }

    assert set(results) == expected
