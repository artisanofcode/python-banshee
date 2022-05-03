"""
Add unique identifiers to messages.
"""

import typing
import uuid

import banshee.context
import banshee.message

T = typing.TypeVar("T")


class IdentityMiddleware(banshee.message.Middleware):
    """
    Identity middleware.

    Add unique identifiers for messages by adding an :class:`~banshee.context.Identity`
    context to each message with :attr:`~banshee.Identity.unique_id` set to a unique
    identifier.
    """

    # pylint: disable=too-few-public-methods

    async def __call__(
        self,
        message: banshee.message.Message[T],
        handle: banshee.message.HandleMessage,
    ) -> banshee.message.Message[T]:
        """
        Handle message.

        Add a unique identifier to the message and forward it to the next handler in the
        chain.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message
        """
        if not message.has(banshee.context.Identity):
            message = message.including(
                banshee.context.Identity(unique_id=uuid.uuid4())
            )

        return await handle(message)
