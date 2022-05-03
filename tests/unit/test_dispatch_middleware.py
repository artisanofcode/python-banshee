"""
Tests for :class:`banshee.DispatchMiddleware`
"""
import logging
import typing

import pytest

import banshee

import tests.fixture


class _Foo:  # pylint: disable=too-few-public-methods
    pass


class _Request:  # pylint: disable=too-few-public-methods
    pass


@pytest.mark.asyncio
async def test_it_should_log_when_no_handlers_found(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    it should log when no handlers founds
    """
    locator = tests.fixture.mock_locator()

    message = banshee.message_for(_Request())

    fake_handle = tests.fixture.mock_handle_message()
    middleware = banshee.DispatchMiddleware(locator, tests.fixture.mock_factory())

    with caplog.at_level(logging.DEBUG, logger="banshee.middleware.dispatch"):
        result = await middleware(message, fake_handle)

    assert caplog.record_tuples == [
        (
            "banshee.middleware.dispatch",
            logging.INFO,
            "no handlers for %(request_class)s found.",
        )
    ]

    assert typing.cast(typing.Any, caplog.records[0]).request_class == "_Request"

    fake_handle.assert_awaited_once_with(message)

    assert result == message


@pytest.mark.asyncio
async def test_it_should_call_handler_with_request(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    it should call handler with request
    """
    reference = banshee.HandlerReference[_Request]("test", _Foo)

    handler_result = object()

    locator = tests.fixture.mock_locator([reference])
    factory = tests.fixture.mock_factory()
    handler = tests.fixture.mock_handler(handler_result)

    factory.side_effect = [handler]

    request = _Request()
    message = banshee.message_for(request)

    fake_handle = tests.fixture.mock_handle_message()
    middleware = banshee.DispatchMiddleware(locator, factory)

    with caplog.at_level(logging.DEBUG, logger="banshee.middleware.dispatch"):
        result = await middleware(message, fake_handle)

    assert caplog.record_tuples == []

    locator.subscribers_for.assert_called_once_with(message)
    factory.assert_called_once_with(reference)
    handler.assert_awaited_once_with(request)

    assert result[banshee.Dispatch].name == "test"
    assert result[banshee.Dispatch].result == handler_result


@pytest.mark.asyncio
async def test_it_should_call_each_handler_with_request(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    it should call each handler with request
    """

    handler_result1 = object()
    handler_result2 = object()

    handler1 = tests.fixture.mock_handler(handler_result1)
    handler2 = tests.fixture.mock_handler(handler_result2)

    reference1 = banshee.HandlerReference[_Request]("test-one", handler1)
    reference2 = banshee.HandlerReference[_Request]("test-two", handler2)

    locator = tests.fixture.mock_locator([reference1, reference2])

    request = _Request()
    message = banshee.message_for(request)

    fake_handle = tests.fixture.mock_handle_message()
    middleware = banshee.DispatchMiddleware(locator, tests.fixture.mock_factory())

    with caplog.at_level(logging.DEBUG, logger="banshee.middleware.dispatch"):
        result = await middleware(message, fake_handle)

    assert caplog.record_tuples == []

    locator.subscribers_for.assert_called_once_with(message)
    handler1.assert_awaited_once_with(request)
    handler2.assert_awaited_once_with(request)

    contexts = tuple(result.all(banshee.Dispatch))

    assert contexts[0].name == "test-one"
    assert contexts[0].result is handler_result1
    assert contexts[1].name == "test-two"
    assert contexts[1].result is handler_result2


@pytest.mark.asyncio
async def test_it_should_not_call_handlers_that_are_already_dispatched() -> None:
    """
    it should call each handlers that are already dispatched
    """

    handler1 = tests.fixture.mock_handler()
    handler2 = tests.fixture.mock_handler()

    reference1 = banshee.HandlerReference[_Request]("test-one", handler1)
    reference2 = banshee.HandlerReference[_Request]("test-two", handler2)

    locator = tests.fixture.mock_locator([reference1, reference2])

    message = banshee.message_for(
        _Request(),
        contexts=[banshee.Dispatch(name="test-one", result=None)],
    )

    fake_handle = tests.fixture.mock_handle_message()
    middleware = banshee.DispatchMiddleware(locator, tests.fixture.mock_factory())

    await middleware(message, fake_handle)

    handler1.assert_not_awaited()
    handler2.assert_awaited_once()


@pytest.mark.asyncio
async def test_it_should_raise_after_all_handlers_on_error() -> None:
    """
    it should call each handlers that are already dispatched
    """

    handler1 = tests.fixture.mock_handler()
    handler2 = tests.fixture.mock_handler()

    reference1 = banshee.HandlerReference[_Request]("test-one", handler1)
    reference2 = banshee.HandlerReference[_Request]("test-two", handler2)

    handler1.side_effect = [RuntimeError("somme handler error")]

    locator = tests.fixture.mock_locator([reference1, reference2])

    message = banshee.message_for(_Request())

    fake_handle = tests.fixture.mock_handle_message()
    middleware = banshee.DispatchMiddleware(locator, tests.fixture.mock_factory())

    with pytest.raises(
        banshee.DispatchError,
        match="handling _Request failed.",
    ) as error:
        await middleware(message, fake_handle)

    handler1.assert_awaited_once()
    handler2.assert_awaited_once()

    assert len(error.value.exceptions) == 1
    assert isinstance(error.value.exceptions[0], RuntimeError)
    assert error.value.exceptions[0].args[0] == "somme handler error"
