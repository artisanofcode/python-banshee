"""
Tools for tracing messages.
"""

import collections.abc
import dataclasses
import datetime
import inspect
import typing

import banshee.bus
import banshee.message

#: Request Type
T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True)
class MessageInfo:
    """
    Message information.

    Contains information about the handling of as specific message.

    :param request: request object
    :param contexts: request message contexts
    :param filename: filename where call originated
    :param function: function where call originated
    :param lineno: line in file where call originated
    :param timestamp: timestamp of call
    :param result_contexts: result message contexts
    """

    #: request object
    request: object

    #: request message contexts
    contexts: tuple[object, ...]

    #: filename where call originated
    filename: str

    #: function where call originated
    function: str

    #: line in file where call originated
    lineno: int

    #: timestamp of call
    timestamp: datetime.datetime

    #: result message contexts
    result_contexts: tuple[object, ...] | None = None


class TraceableBus(banshee.bus.Bus):
    """
    Traceable bus.

    A :class:`~banshee.Bus` decorator that stores information about the processing of
    each message passed to the wrapped instance.

    :param inner: decorated instance
    """

    def __init__(self, inner: banshee.bus.Bus) -> None:
        self.inner = inner
        self._messages: list[MessageInfo] = []

    @property
    def messages(self) -> collections.abc.Sequence[MessageInfo]:
        """
        Messages.

        :returns: sequence containing information about each message processed.
        """
        return tuple(self._messages)

    def reset(self) -> None:
        """
        Reset.

        Clear everything in :attr:`messages`.
        """
        self._messages = []

    def _get_caller_frame(self) -> inspect.FrameInfo:
        stack = inspect.stack()

        for frame_info in stack:
            name = frame_info.frame.f_globals.get("__name__", "")

            if name.startswith("banshee."):
                continue

            return frame_info

        # something went wrong so default to frame before caller.
        return stack[1]  # pragma: no cover

    async def handle(
        self,
        request: T | banshee.message.Message[T],
        contexts: collections.abc.Iterable[typing.Any] | None = None,
    ) -> banshee.message.Message[T]:
        message = banshee.message.message_for(request, contexts)

        frame_info = self._get_caller_frame()

        info = MessageInfo(
            request=message.request,
            contexts=message.contexts,
            filename=frame_info.filename,
            function=frame_info.function,
            lineno=frame_info.lineno,
            timestamp=datetime.datetime.utcnow(),
        )

        try:
            message = await self.inner.handle(message)

            info = dataclasses.replace(info, result_contexts=message.contexts)
        finally:
            self._messages.append(info)

        return message
