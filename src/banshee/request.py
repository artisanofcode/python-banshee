"""
Handlers and wiring.
"""

import abc
import collections.abc
import dataclasses
import typing

import banshee.message

#: T
T = typing.TypeVar("T")
P = typing.ParamSpec("P")

#: T
T_contra = typing.TypeVar("T_contra", contravariant=True)


@dataclasses.dataclass
class HandlerReference(typing.Generic[T]):
    """
    Handler reference.

    A reference to a type or callable, including a unique name for said type or
    callable, that when passed to a :class:`~banshee.HandlerFactory` will result in an
    instantiated :class:`Handler`.

    :param name: unique handler name
    :param handler: handler type or callable
    """

    # pylint: disable=too-few-public-methods

    name: str
    handler: type | collections.abc.Callable[..., typing.Any]


class Handler(typing.Protocol[T_contra]):
    """
    Handler protocol.

    Callable to process a request.
    """

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    async def __call__(self, request: T_contra, /) -> typing.Any:
        """
        Execute.

        Perform any business logic applicable to the request.

        :param request: request object

        :returns: result processing request
        """


class HandlerLocator(typing.Protocol):
    """
    Handler locator protocol.

    Locates handlers that can process the messages request.
    """

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def subscribers_for(
        self,
        message: banshee.message.Message[T],
    ) -> collections.abc.Iterable[HandlerReference[T]]:
        """
        Get subscribers for message.

        Returns references to handlers for the passed messages request.

        :param message: message of request

        :returns: list of references to handlers for the message
        """


class HandlerFactory(typing.Protocol):
    """
    Handler factory protocol.

    Returns a concrete handler for the given reference.
    """

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def __call__(self, reference: HandlerReference[T], /) -> Handler[T]:
        """
        Get handler.

        Returns a concrete handler for the given reference.

        :param reference: reference to a handler

        :returns: concrete handler instance
        """


class SimpleHandlerFactory(HandlerFactory):
    """
    Simple handler factory.

    This factory assumes that the reference is itself a valid handler, allowing
    handlers to be directly registered with the registry.

    .. code-block:: python

        @registry.subscribe_to(GreetCommand)
        def do_greet(command: GreetCommand):
            print(f"hello {command.name}!")
    """

    # pylint: disable=too-few-public-methods

    def __call__(self, reference: HandlerReference[T], /) -> Handler[T]:
        handler = reference.handler

        if isinstance(handler, type):
            handler = handler()

        return typing.cast(Handler[T], handler)
