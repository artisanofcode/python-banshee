"""
Messages associating requests with extra context.
"""

import abc
import collections.abc
import dataclasses
import typing

#: Context Type
CT = typing.TypeVar("CT")

#: Request Type
T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True, slots=True)
class Message(typing.Generic[T]):
    """
    Message.

    Associates extra context with a request.

    :param request: request to be dispatched
    :param contexts: additional context about the request
    """

    request: T

    contexts: tuple[typing.Any, ...] = dataclasses.field(
        default_factory=tuple,
        kw_only=True,
    )

    @typing.overload
    def get(self, key: type[CT]) -> CT | None:
        """
        Get context.

        :param key: context type
        :returns: requested context or `None`
        """

    @typing.overload
    def get(self, key: type[CT], default: CT) -> CT:
        """
        Get context.

        :param key: context type
        :param default: value to return when not found

        :returns: requested context or default
        """

    def get(self, key: type[CT], default: CT | None = None) -> CT | None:
        """
        Get context.

        :param key: context type
        :param default: value to return if no value found

        :returns: requested context or default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def all(self, key: type[CT]) -> collections.abc.Iterable[CT]:
        """
        All contexts.

        :param key: context type

        :returns: sequence of context objects
        """
        return (v for v in self.contexts if isinstance(v, key))

    def has(self, key: type) -> bool:
        """
        Has context.

        :param key: context type

        :returns: whether context exists
        """
        return key in self

    def __getitem__(self, key: type[CT]) -> CT:
        for value in reversed(self.contexts):
            if isinstance(value, key):
                return value

        raise KeyError(key)

    def __contains__(self, key: type) -> bool:
        return any(isinstance(value, key) for value in reversed(self.contexts))

    def including(self, *values: object) -> "Message[T]":
        """
        Include context.

        Create a clone of the object with the added context object.

        :param values: context object to add

        :returns: clone of message with updated context
        """
        if not values:
            return self

        return dataclasses.replace(self, contexts=self.contexts + tuple(values))

    def excluding(self, *key: type) -> "Message[T]":
        """
        Exclude context.

        Create a clone of the object with instances of the context types removed.

        :param key: context type to remove

        :returns: clone of message with updated context
        """
        contexts = tuple(v for v in self.contexts if not isinstance(v, key))

        if self.contexts == contexts:
            return self

        return dataclasses.replace(self, contexts=contexts)


def message_for(
    request: T | Message[T],
    contexts: collections.abc.Iterable[typing.Any] | None = None,
) -> Message[T]:
    """
    Wrap request.

    Creates a new message unless request is already a message, and then attaches the
    passed context objects.

    :param request: the request
    :param contexts: additional context objects

    :returns: a message for the request and context objects
    """
    if not isinstance(request, Message):
        return Message(request, contexts=tuple(contexts) if contexts else tuple())

    if not contexts:
        return request

    return request.including(*tuple(contexts))


class HandleMessage(typing.Protocol):
    """
    Handle message protocol.

    Handle the message with the next middleware in the chain.
    """

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    async def __call__(self, message: Message[T]) -> Message[T]:
        """
        Handle.

        :param message: message to process

        :returns: processed message
        """


@typing.runtime_checkable
class Middleware(typing.Protocol):
    """
    Middleware protocol.

    A link in the chain of middleware.
    """

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    async def __call__(self, message: Message[T], handle: HandleMessage) -> Message[T]:
        """
        Handle message.

        Perform any processing on the message and forward it to the next handler in the
        chain.

        :param message: message to process
        :param handle: next middleware invoker

        :returns: processed message
        """


class MiddlewareChain(HandleMessage):
    """
    Middleware chain.

    Dispatch a message by recursively calling middleware.

    :param iterator: iterator of middleware instances
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, iterator: collections.abc.Iterator[Middleware]) -> None:
        self.iterator = iterator

    async def _final(self, message: Message[T], handle: HandleMessage) -> Message[T]:
        return message

    async def __call__(self, message: Message[T]) -> Message[T]:
        return await next(self.iterator, self._final)(message, self)
