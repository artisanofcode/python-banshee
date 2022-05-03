"""
Tests for :class:`banshee.GateMiddleware`
"""

import typing
import unittest.mock

import pytest

import banshee

import tests.fixture

T = typing.TypeVar("T")


def mock_gate(return_value: bool) -> typing.Any:
    """
    Mock gate.

    :param return_value: result of check
    """
    # pylint: disable=unused-argument

    def gate(message: banshee.Message[typing.Any]) -> bool:
        return return_value

    return unittest.mock.create_autospec(gate, spec_set=True, side_effect=gate)


@pytest.mark.asyncio
async def test_it_should_call_gate_with_message() -> None:
    """
    it should call gate with message.
    """
    message = banshee.message_for(object())

    gate = mock_gate(True)

    middleware = banshee.GateMiddleware(tests.fixture.mock_middleware(), gate)

    await middleware(message, tests.fixture.mock_handle_message())

    gate.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_it_should_call_inner_handler_when_gate_passes() -> None:
    """
    it should call inner middleware when gate passes.
    """
    message = banshee.message_for(object())

    fake_handle = tests.fixture.mock_handle_message()
    inner = tests.fixture.mock_middleware()

    middleware = banshee.GateMiddleware(inner, mock_gate(True))

    result = await middleware(message, fake_handle)

    inner.assert_awaited_once_with(message, fake_handle)
    fake_handle.assert_not_awaited()

    assert result == message


@pytest.mark.asyncio
async def test_it_should_call_fake_handle_when_gate_fails() -> None:
    """
    it should call fake_handle when gate fails.
    """
    message = banshee.message_for(object())

    fake_handle = tests.fixture.mock_handle_message()
    inner = tests.fixture.mock_middleware()

    middleware = banshee.GateMiddleware(inner, mock_gate(False))

    result = await middleware(message, fake_handle)

    inner.assert_not_awaited()
    fake_handle.assert_awaited_once_with(message)

    assert result == message
