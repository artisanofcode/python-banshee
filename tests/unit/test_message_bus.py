"""
Tests for :class:`banshee.bus.MessageBus`
"""

import typing

import conjecture
import pytest

import banshee
import banshee.bus
import banshee.message

import tests.fixture


class _Request:  # pylint: disable=too-few-public-methods
    pass


@pytest.mark.asyncio
async def test_handle_should_dispatch_request_to_middleware() -> None:
    """
    handle() should dispatch request to middleware
    """

    middleware = tests.fixture.mock_middleware()

    bus = banshee.bus.MessageBus([middleware])

    request = object()

    await bus.handle(request)

    middleware.assert_awaited_once_with(
        banshee.message_for(request),
        conjecture.instance_of(banshee.message.MiddlewareChain),
    )


@pytest.mark.asyncio
async def test_handle_should_dispatch_request_with_context() -> None:
    """
    handle() should dispatch request to middleware
    """

    middleware = tests.fixture.mock_middleware()

    bus = banshee.bus.MessageBus([middleware])

    request = object()
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy2()

    await bus.handle(request, contexts=[context1, context2])

    middleware.assert_awaited_once_with(
        banshee.message_for(request, contexts=[context1, context2]),
        conjecture.instance_of(banshee.message.MiddlewareChain),
    )


@pytest.mark.asyncio
async def test_handle_should_return_updated_message_from_middleware() -> None:
    """
    handle() should dispatch request to middleware
    """

    T = typing.TypeVar("T")

    context = tests.fixture.Dummy1()

    async def middleware(
        message: banshee.Message[T],
        handle: banshee.HandleMessage,  # pylint: disable=unused-argument
    ) -> banshee.Message[T]:
        return await handle(message.including(context))

    bus = banshee.bus.MessageBus([middleware])

    request = object()

    result = await bus.handle(request)

    assert result == banshee.message_for(request, contexts=[context])


@pytest.mark.asyncio
async def test_query_should_return_handler_result() -> None:
    """
    query() should return handler result
    """

    T = typing.TypeVar("T")

    expected = object()

    async def middleware(
        message: banshee.Message[T],
        handle: banshee.HandleMessage,  # pylint: disable=unused-argument
    ) -> banshee.Message[T]:
        message = message.including(banshee.Dispatch(name="test", result=expected))

        return await handle(message)

    bus = banshee.bus.MessageBus([middleware])

    result = await bus.query(_Request())

    assert result is expected


@pytest.mark.asyncio
async def test_query_should_raise_when_not_handled() -> None:
    """
    query() should raise when not handled
    """
    middleware = tests.fixture.mock_middleware()

    bus = banshee.bus.MessageBus([middleware])

    with pytest.raises(
        banshee.ConfigurationError,
        match="no handler for _Request found",
    ):
        await bus.query(_Request())


@pytest.mark.asyncio
async def test_query_should_raise_when_handled_more_than_once() -> None:
    """
    query() should raise when handled more than once
    """

    T = typing.TypeVar("T")

    async def middleware(
        message: banshee.Message[T],
        handle: banshee.HandleMessage,  # pylint: disable=unused-argument
    ) -> banshee.Message[T]:
        message = message.including(
            banshee.Dispatch(name="test1", result=None),
            banshee.Dispatch(name="test2", result=None),
        )

        return await handle(message)

    bus = banshee.bus.MessageBus([middleware])

    with pytest.raises(
        banshee.ConfigurationError,
        match="multiple handlers for _Request found",
    ):
        await bus.query(_Request())
