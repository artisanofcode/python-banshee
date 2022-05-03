"""
Pipeline related fixtures.
"""

import asyncio
import collections.abc
import typing
import unittest.mock

import banshee

T = typing.TypeVar("T")


def mock_handle_message() -> typing.Any:
    """
    Mock handle message.
    """

    async def handle(message: banshee.Message[T]) -> banshee.Message[T]:
        # release the event loop, useful in tests that test for task isolation
        await asyncio.sleep(0)

        return message

    return unittest.mock.create_autospec(handle, spec_set=True, side_effect=handle)


def mock_recursive_handle_message(
    iterator: collections.abc.Iterator[banshee.Message[typing.Any]],
    middleware: banshee.Middleware,
) -> typing.Any:
    """
    Mock handle message.
    """

    async def handle(message: banshee.Message[T]) -> banshee.Message[T]:
        # release the event loop, useful in tests that test for task isolation
        await asyncio.sleep(0)

        if next_message := next(iterator, None):
            await middleware(next_message, mock)

        return message

    mock = unittest.mock.create_autospec(handle, spec_set=True, side_effect=handle)

    return mock


def mock_middleware() -> typing.Any:
    """
    Mock middleware.
    """

    async def middleware(
        message: banshee.Message[T],
        handle: banshee.HandleMessage,  # pylint: disable=unused-argument
    ) -> banshee.Message[T]:
        return message

    return unittest.mock.create_autospec(
        middleware,
        spec_set=True,
        side_effect=middleware,
    )
