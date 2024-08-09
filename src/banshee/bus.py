"""
A command / event / query bus implementation.
"""

import abc
import collections.abc
import typing

import banshee.context
import banshee.errors
import banshee.message

#: T
T = typing.TypeVar("T")

#: Return Type
ReturnType_co = typing.TypeVar(  # pylint: disable=invalid-name
    "ReturnType_co",
    covariant=True,
)


class Query(typing.Protocol[ReturnType_co]):  # pylint: disable=too-few-public-methods
    """
    Query.

    A generic type for specifying the return type of a request.
    """


@typing.runtime_checkable
class Bus(typing.Protocol):
    """
    Bus protocol.

    An command/event/query bus for dispatching requests to handlers.
    """

    @abc.abstractmethod
    async def handle(
        self,
        request: T | banshee.message.Message[T],
        contexts: collections.abc.Iterable[typing.Any] | None = None,
    ) -> banshee.message.Message[T]:
        """
        Handle.

        Process a message.

        :param request: request instance
        :param contexts: additional context objects
        """

    async def query(
        self,
        query: Query[T],
        contexts: collections.abc.Iterable[typing.Any] | None = None,
    ) -> T:
        """
        Query.

        Send a query to the message bus and return the result.

        :param query: query instance
        :param contexts: additional context objects

        :returns: the result of the query

        :raises banshee.ConfigurationError: query does not map to exactly one handler
        """
        message = await self.handle(query, contexts)

        dispatch_contexts = tuple(message.all(banshee.context.Dispatch))

        if not dispatch_contexts:
            raise banshee.errors.ConfigurationError(
                f"no handler for {type(message.request).__name__} found"
            )

        if len(dispatch_contexts) > 1:
            raise banshee.errors.ConfigurationError(
                f"multiple handlers for {type(message.request).__name__} found"
            )

        return typing.cast(T, dispatch_contexts[0].result)


class MessageBus(Bus):
    """
    Message bus.

    Composable message/query/command bus for processing requests.

    :param chain: iterable of middleware
    """

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        middleware: collections.abc.Iterable[banshee.message.Middleware],
    ) -> None:
        self.middleware = tuple(middleware)

    async def handle(
        self,
        request: T | banshee.message.Message[T],
        contexts: collections.abc.Iterable[typing.Any] | None = None,
    ) -> banshee.message.Message[T]:
        message = banshee.message.message_for(request, contexts)

        handle = banshee.message.MiddlewareChain(iter(self.middleware))

        return await handle(message)
