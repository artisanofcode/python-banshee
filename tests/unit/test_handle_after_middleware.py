"""
Tests for :class:`banshee.HandleAfterMiddleware`
"""

import asyncio
import typing
import unittest.mock
import uuid

import pytest

import banshee

import tests.fixture

T = typing.TypeVar("T")


@pytest.mark.asyncio
async def test_it_should_do_nothing_when_context_is_not_present() -> None:
    """
    it should do nothing when context is not present
    """
    messages = [banshee.message_for(uuid.uuid4()) for _ in range(5)]

    iterator = iter(messages)

    async def _side_effect(message: banshee.Message[T]) -> banshee.Message[T]:
        for next_message in iterator:
            await middleware(next_message, fake_handle)

            # the message was processed inline
            fake_handle.assert_any_await(next_message)

        return message

    fake_handle = tests.fixture.mock_handle_message()
    fake_handle.side_effect = _side_effect

    middleware = banshee.HandleAfterMiddleware()

    result = await middleware(next(iterator), fake_handle)

    assert result == messages[0]

    # check all messages were processed in order
    fake_handle.assert_has_awaits(unittest.mock.call(v) for v in messages)


@pytest.mark.asyncio
async def test_it_should_postpone_handling_when_context_is_present() -> None:
    """
    it should postpone handling when context is present
    """
    messages = [
        banshee.message_for(uuid.uuid4(), contexts=[banshee.HandleAfter()])
        for _ in range(5)
    ]

    iterator = iter(messages)

    async def _side_effect(message: banshee.Message[T]) -> banshee.Message[T]:
        for next_message in iterator:
            await middleware(next_message, fake_handle)

            # we only have the original call...
            fake_handle.assert_awaited_once_with(
                messages[0].excluding(banshee.HandleAfter)
            )

        return message

    fake_handle = tests.fixture.mock_handle_message()
    fake_handle.side_effect = _side_effect

    middleware = banshee.HandleAfterMiddleware()

    result = await middleware(next(iterator), fake_handle)

    # check all messages were processed in order
    fake_handle.assert_has_awaits(
        [unittest.mock.call(v.excluding(banshee.HandleAfter)) for v in messages]
    )

    assert result == messages[0].excluding(banshee.HandleAfter)


@pytest.mark.asyncio
async def test_it_should_postpone_handling_recursively() -> None:
    """
    it should postpone handling recursively
    """
    messages = [
        banshee.message_for(uuid.uuid4(), contexts=[banshee.HandleAfter()])
        for _ in range(5)
    ]

    iterator = iter(messages)

    middleware = banshee.HandleAfterMiddleware()

    fake_handle = tests.fixture.mock_recursive_handle_message(iterator, middleware)

    result = await middleware(next(iterator), fake_handle)

    # check all messages were processed in order
    fake_handle.assert_has_awaits(
        [unittest.mock.call(v.excluding(banshee.HandleAfter)) for v in messages]
    )

    assert result == messages[0].excluding(banshee.HandleAfter)


@pytest.mark.asyncio
async def test_it_should_drop_postponed_messages_on_error() -> None:
    """
    it should drop postponed messages on error
    """
    messages = [
        banshee.message_for(uuid.uuid4(), contexts=[banshee.HandleAfter()])
        for _ in range(5)
    ]

    iterator = iter(messages)

    async def _side_effect(_: banshee.Message[T]) -> banshee.Message[T]:
        for next_message in iterator:
            await middleware(next_message, fake_handle)

        raise RuntimeError("foobar")

    fake_handle = tests.fixture.mock_handle_message()
    fake_handle.side_effect = _side_effect

    middleware = banshee.HandleAfterMiddleware()

    with pytest.raises(RuntimeError, match="foobar"):
        await middleware(next(iterator), fake_handle)

    # only called with the breaking event
    fake_handle.assert_awaited_once_with(messages[0].excluding(banshee.HandleAfter))


@pytest.mark.asyncio
async def test_it_should_drop_nested_postponed_messages_on_error() -> None:
    """
    it should postpone handling recursively
    """
    messages = [
        banshee.message_for(uuid.uuid4(), contexts=[banshee.HandleAfter()])
        for _ in range(5)
    ]

    iterator = iter(messages)

    async def _side_effect(message: banshee.Message[T]) -> banshee.Message[T]:
        if next_message := next(iterator, None):
            await middleware(next_message, fake_handle)

        if next_message == messages[3]:
            raise RuntimeError("boom!")

        return message

    fake_handle = tests.fixture.mock_handle_message()
    fake_handle.side_effect = _side_effect

    middleware = banshee.HandleAfterMiddleware()

    with pytest.raises(
        banshee.MultipleErrors, match="errors while handling postponed messages."
    ) as error:
        await middleware(next(iterator), fake_handle)

    assert len(error.value.exceptions) == 1
    assert isinstance(error.value.exceptions[0], RuntimeError)
    assert error.value.exceptions[0].args[0] == "boom!"

    # check all messages were processed in order
    fake_handle.assert_has_awaits(
        [unittest.mock.call(v.excluding(banshee.HandleAfter)) for v in messages[:3]]
    )


@pytest.mark.asyncio
async def test_it_should_only_consider_current_asyncio_task() -> None:
    """
    it should only consider current asyncio task.
    """
    messages = [
        banshee.message_for(uuid.uuid4(), contexts=[banshee.HandleAfter()])
        for _ in range(5)
    ]

    middleware = banshee.HandleAfterMiddleware()

    async def _side_effect(message: banshee.Message[T]) -> banshee.Message[T]:
        # release the event loop
        await asyncio.sleep(0)
        # add a context so we can differentiate the messages that were postponed from
        # the ones that were processed and returned
        return message.including(tests.fixture.Dummy1())

    # run all the messages at once, when not properly isolated this will fail as the
    # middleware will mistakenly postpone some of the parallel messages.
    results = await asyncio.gather(
        *(
            asyncio.create_task(middleware(message, _side_effect))
            for message in messages
        )
    )

    expected = {
        message.excluding(banshee.HandleAfter).including(tests.fixture.Dummy1())
        for message in messages
    }

    assert set(results) == expected
