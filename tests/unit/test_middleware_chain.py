"""
Tests for :class:`banshee.message.MiddlewareChain`
"""

import pytest

import banshee
import banshee.message

import tests.fixture


@pytest.mark.asyncio
async def test_it_should_call_middleware_in_order() -> None:
    """
    it should call middleware in order
    """

    middleware_list = [tests.fixture.mock_middleware() for _ in range(10)]

    message = banshee.message_for(object())

    chain = banshee.message.MiddlewareChain(iter(middleware_list))

    for i in range(len(middleware_list)):
        result = await chain(message)

        print(i)
        for middleware in middleware_list[0:i]:
            middleware.assert_awaited_once_with(message, chain)

        for middleware in middleware_list[i + 1 :]:
            middleware.assert_not_awaited()

        assert result == message

    # ensure successive calls just return the message
    assert (await chain(message)) == message
    assert (await chain(message)) == message
    assert (await chain(message)) == message
