"""
Pipeline related fixtures.
"""

import typing
import unittest.mock

import banshee

T = typing.TypeVar("T")


def mock_handler(return_value: typing.Any = None) -> typing.Any:
    """
    Mock handle message.
    """

    async def handler(_: typing.Any, /) -> typing.Any:
        ...  # pragma: no cover

    mock = unittest.mock.create_autospec(handler, spec_set=True)
    mock.return_value = return_value

    return mock


def mock_factory() -> typing.Any:
    """
    Mock factory.
    """

    def factory(reference: banshee.HandlerReference[T], /) -> banshee.Handler[T]:
        return reference.handler

    return unittest.mock.create_autospec(factory, spec_set=True, side_effect=factory)


def mock_locator(
    return_value: list[banshee.HandlerReference[typing.Any]] | None = None,
) -> typing.Any:
    """
    Mock locator.
    """
    mock = unittest.mock.create_autospec(banshee.HandlerLocator, spec_set=True)
    mock.subscribers_for.return_value = return_value or []

    return mock
