"""
Dispatch requests to handlers.
"""

import logging
import typing

import banshee.context
import banshee.message
import banshee.request

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")


class DispatchMiddleware(banshee.message.Middleware):
    """
    Dispatch middleware.

    Implements the :term:`command dispatcher` design pattern to route requests to their
    configured handlers.

    Uses the pre-configured  :class:`~banshee.HandlerLocator` to retrieve a all
    associated :class:`~banshee.HandlerReference` instances, before passing the
    references one by one to a :class:`~banshee.HandlerFactory` in order to get
    and :class:`~banshee.Handler` instance to call.

    A :class:`~banshee.Dispatch` context will be added to the message for each
    successful handler.

    :param locator: locator to lookup associated handlers for a message
    :param factory: factory to instantiate a concrete handler from a reference
    """

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        locator: banshee.request.HandlerLocator,
        factory: banshee.request.HandlerFactory,
    ) -> None:
        super().__init__()

        self.locator = locator
        self.factory = factory

    async def __call__(
        self,
        message: banshee.message.Message[T],
        handle: banshee.message.HandleMessage,
    ) -> banshee.message.Message[T]:
        """
        Handle message.

        Dispatch the request to all associated handlers and store the results.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message

        :raises banshee.errors.DispatchError: when one or more handlers fails
        """
        extra = {"request_class": type(message.request).__name__}

        errors = []

        for reference in self.locator.subscribers_for(message):
            if any(
                context.name == reference.name
                for context in message.all(banshee.context.Dispatch)
            ):
                continue

            try:
                handler = self.factory(reference)
                result = await handler(message.request)

                message = message.including(
                    banshee.context.Dispatch(
                        name=reference.name,
                        result=result,
                    )
                )
            except Exception as error:  # pylint: disable=broad-except
                errors.append(error)

        if not message.has(banshee.context.Dispatch) and not errors:
            logger.info("no handlers for %(request_class)s found.", extra=extra)

        if errors:
            raise banshee.errors.DispatchError(
                f"handling {extra['request_class']} failed.",
                errors,
            )

        return await handle(message)
