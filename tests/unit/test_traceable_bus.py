"""
Tests for :class:`banshee.TraceableBus`
"""

import datetime
import typing
import unittest.mock

import conjecture
import freezegun
import pytest
import typeguard

import banshee

import tests.fixture


class _Request:  # pylint: disable=too-few-public-methods
    pass


def mock_bus() -> typing.Any:
    """
    Mock bus.
    """
    return unittest.mock.create_autospec(banshee.Bus, spec_set=True)


@pytest.mark.asyncio
async def test_handle_should_forward_calls_to_inner_bus() -> None:
    """
    handle() should forward calls to inner bus
    """
    request = _Request()

    context1 = tests.fixture.Dummy1()

    inner = mock_bus()

    bus = banshee.TraceableBus(inner)

    result = await bus.handle(request, contexts=[context1])

    inner.handle.assert_awaited_once_with(
        banshee.message_for(request, contexts=[context1])
    )

    assert result == inner.handle.return_value


@pytest.mark.asyncio
async def test_query_should_return_handler_result() -> None:
    """
    query() should return handler result
    """
    expected = object()

    request = _Request()
    context1 = tests.fixture.Dummy1()

    inner = mock_bus()
    inner.handle.return_value = banshee.message_for(
        request,
        contexts=[banshee.Dispatch(name="test", result=expected)],
    )

    bus = banshee.TraceableBus(inner)

    result = await bus.query(request, contexts=[context1])

    inner.handle.assert_awaited_once_with(
        banshee.message_for(request, contexts=[context1])
    )

    assert result is expected


@pytest.mark.asyncio
async def test_query_should_raise_when_not_handled() -> None:
    """
    query() should raise when not handled
    """

    inner = mock_bus()
    inner.handle.return_value = banshee.message_for(_Request())

    bus = banshee.TraceableBus(inner)

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

    inner = mock_bus()
    inner.handle.return_value = banshee.message_for(
        _Request(),
        contexts=[
            banshee.Dispatch(name="test1", result=None),
            banshee.Dispatch(name="test2", result=None),
        ],
    )

    bus = banshee.TraceableBus(inner)

    with pytest.raises(
        banshee.ConfigurationError,
        match="multiple handlers for _Request found",
    ):
        await bus.query(_Request())


@pytest.mark.asyncio
async def test_handle_should_record_calls() -> None:
    """
    handle() should record calls
    """
    request = _Request()

    now = datetime.datetime.now()

    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy1()

    inner = mock_bus()
    inner.handle.return_value = banshee.message_for(request, contexts=[context2])

    bus = banshee.TraceableBus(inner)

    with freezegun.freeze_time(now):
        await bus.handle(request, contexts=[context1])

    print(bus.messages, __file__)
    assert len(bus.messages) == 1
    assert bus.messages[0].contexts == (context1,)
    assert bus.messages[0].filename in {
        __file__,
        typeguard.__file__,  # needed for when plug-in is enabled due to decorator...
    }
    assert bus.messages[0].function in {"test_handle_should_record_calls", "wrapper"}
    assert bus.messages[0].lineno == (
        conjecture.instance_of(int) & conjecture.greater_than(0)
    )
    assert bus.messages[0].request == request
    assert bus.messages[0].result_contexts == (context2,)
    assert bus.messages[0].timestamp == now


@pytest.mark.asyncio
async def test_reset_clears_recorded_calls() -> None:
    """
    reset() clears recorded calls
    """
    request = _Request()

    inner = mock_bus()
    bus = banshee.TraceableBus(inner)

    await bus.handle(request)
    await bus.handle(request)
    await bus.handle(request)
    await bus.handle(request)

    assert len(bus.messages) == 4

    bus.reset()

    assert len(bus.messages) == 0
