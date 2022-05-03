"""
Postpone handling of nested requests.
"""

import collections
import contextvars
import dataclasses
import itertools
import typing

import banshee.context
import banshee.errors
import banshee.message

T = typing.TypeVar("T")


@dataclasses.dataclass
class _HandleAfterState:
    """
    Context local state.
    """

    is_processing: bool = False
    queue: collections.deque[
        tuple[banshee.message.Message[typing.Any], banshee.message.HandleMessage]
    ] = dataclasses.field(default_factory=collections.deque)


class HandleAfterMiddleware(banshee.message.Middleware):
    """
    Handle after middleware.

    Postpone handling of specific messages until after the current handler has
    finished processing.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        super().__init__()

        self._state: contextvars.ContextVar[_HandleAfterState]
        self._state = contextvars.ContextVar("_state")

    def _get_state(self) -> _HandleAfterState:
        if not self._state.get(None):
            self._state.set(_HandleAfterState())

        return self._state.get()

    async def __call__(
        self,
        message: banshee.message.Message[T],
        handle: banshee.message.HandleMessage,
    ) -> banshee.message.Message[T]:
        """
        Handle message.

        Perform any processing on the message and forward it to the next handler in the
        chain.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message

        :raises banshee.errors.MultipleErrors: when the postponed handlers raise errors
        """
        state = self._get_state()

        if state.is_processing and message.has(banshee.context.HandleAfter):
            # message was sent from inside a handler and is deferrable, so add it to
            # the queue and exit early
            message = message.excluding(banshee.context.HandleAfter)

            state.queue.append((message, handle))

            return message

        message = message.excluding(banshee.context.HandleAfter)

        if state.is_processing:
            # message was sent from inside a handler is not deferrable so default to
            # nested processing

            return await handle(message)

        # if we made it here, we can set the processing flag and start deferring
        state.is_processing = True

        try:
            # handle the message as normal
            result = await handle(message)
        except:
            # we only process the messages a handler handles when the handler was run
            # successfully, when an error occurs we discard the queue and the dependent
            # messages it contains.

            state.queue = collections.deque()
            state.is_processing = False

            raise

        # all done, time to process all the deferred messages

        errors: list[Exception] = []

        while state.queue:  # pylint: disable=while-used
            queued_message, queued_handle = state.queue.popleft()

            count = len(state.queue)

            try:
                await queued_handle(queued_message)
            except Exception as error:  # pylint: disable=broad-except
                errors.append(error)

                # drop any messages generated in the failed handler
                state.queue = collections.deque(itertools.islice(state.queue, count))

        # all done, unset the processing flag and stop deferring
        state.is_processing = False

        if errors:
            raise banshee.errors.MultipleErrors(
                "errors while handling postponed messages.",
                errors,
            )

        return result
