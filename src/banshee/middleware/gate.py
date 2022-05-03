"""
Conditionally invoke a middleware.
"""

import typing

import banshee.message

T = typing.TypeVar("T")


class Gate(typing.Protocol):
    """
    Gate.

    Check whether the decorated middleware should be used.
    """

    # pylint: disable=too-few-public-methods

    def __call__(self, message: banshee.message.Message[typing.Any]) -> bool:
        """
        Check.

        Check whether a message should be processed by the inner middleware.  :param
        message: the message being processed  :returns: whether to process the message
        """


class GateMiddleware(banshee.message.Middleware):
    """
    Gate middleware.

    A :class:`~banshee.Middleware` decorator to conditionally invoke the decorated
    middleware depending on the result of a gate callback.

    When the callback passes, decorated middleware will be inserted next in the
    chain before processing continues.

    :param inner: inner handler
    :param gate: gate callback
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, inner: banshee.message.Middleware, gate: Gate) -> None:
        super().__init__()

        self.inner = inner
        self.gate = gate

    async def __call__(
        self,
        message: banshee.message.Message[T],
        handle: banshee.message.HandleMessage,
    ) -> banshee.message.Message[T]:
        """
        Handle message.

        Forward the message to the inner middleware or the next handler in the chain
        based on the check callback result.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message
        """
        if self.gate(message):
            return await self.inner(message, handle)

        return await handle(message)
