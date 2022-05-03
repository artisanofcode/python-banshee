"""
Add causation and correlation identifiers to messages.
"""

import contextvars
import dataclasses
import logging
import typing
import uuid

import banshee.context
import banshee.message

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")


@dataclasses.dataclass
class _CausationState:
    stack: list[tuple[uuid.UUID, uuid.UUID]] = dataclasses.field(default_factory=list)


class CausationMiddleware(banshee.message.Middleware):
    """
    Causation middleware.

    Add causation and correlation identifiers to messages based on the messages
    :class:`~banshee.Identity` context.

    The :attr:`~banshee.Causation.correlation_id` will be set based on the first
    message in a chains :attr:`~banshee.Identity.unique_id`, and the
    :attr:`~banshee.Causation.causation_id` will be set based on the previous message
    in a chains :attr:`~banshee.Identity.unique_id`.

    When no :class:`~banshee.Identity` context is present this handler will pass the
    message unchanged.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        super().__init__()

        self._state: contextvars.ContextVar[_CausationState]
        self._state = contextvars.ContextVar("_state")

    def _get_state(self) -> _CausationState:
        if not self._state.get(None):
            self._state.set(_CausationState())

        return self._state.get()

    async def __call__(
        self,
        message: banshee.message.Message[T],
        handle: banshee.message.HandleMessage,
    ) -> banshee.message.Message[T]:
        """
        Handle message.

        Add causation and correlation identifiers to the message and forward it to the
        next handler in the chain.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message
        """
        extra = {"request_class": type(message.request).__name__}

        identity = message.get(banshee.context.Identity)

        if not identity:
            # correlation and causation ids rely on the events having an identity

            logger.info("no identity for %(request_class)s found.", extra=extra)

            return await handle(message)

        state = self._get_state()

        context = message.get(banshee.context.Causation)

        if not context:
            # create a new context object as no existing one was found
            if not state.stack:
                correlation_id = identity.unique_id
                causation_id = identity.unique_id
            else:
                causation_id, correlation_id = state.stack[-1]

            context = banshee.context.Causation(
                causation_id=causation_id,
                correlation_id=correlation_id,
            )

        message = message.including(context)

        state.stack.append((identity.unique_id, correlation_id))

        try:
            return await handle(message)
        finally:
            state.stack.pop()
