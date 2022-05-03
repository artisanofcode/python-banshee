"""
A builder for :class:`~banshee.message_bus.MessageBus` instances.
"""

import dataclasses

import banshee.bus
import banshee.message
import banshee.middleware.dispatch
import banshee.registry
import banshee.request


@dataclasses.dataclass(frozen=True, slots=True)
class Builder:
    """
    Builder.

    Provides a chained interface to construct an instance of
    {class}`banshee.Bus`.
    """

    middleware: tuple[banshee.message.Middleware, ...] = dataclasses.field(
        default_factory=tuple
    )
    locator: banshee.request.HandlerLocator | None = None
    factory: banshee.request.HandlerFactory | None = None

    def with_middleware(self, middleware: banshee.message.Middleware) -> "Builder":
        """
        With middleware.

        Add a middleware to the message bus.

        :param middleware: middleware instance

        :returns: builder instance with middleware added
        """
        return dataclasses.replace(self, middleware=self.middleware + (middleware,))

    def with_locator(self, locator: banshee.request.HandlerLocator) -> "Builder":
        """
        With locator.

        Set locator for the message bus.

        :param locator: handler locator instance

        :returns: builder instance with locator
        """
        return dataclasses.replace(self, locator=locator)

    def with_factory(self, factory: banshee.request.HandlerFactory) -> "Builder":
        """
        With factory.

        Set factory for the message bus.

        :param factory: handler factory instance

        :returns: builder instance with factory
        """
        return dataclasses.replace(self, factory=factory)

    def build(self) -> banshee.bus.Bus:
        """
        Build.

        Assemble the message bus instance

        :returns: a message bus instance

        :raises banshee.ConfigurationError: when bus is incorrectly configured
        """
        locator = self.locator

        if not locator:
            raise banshee.errors.ConfigurationError("No locator provided.")

        middleware = list(self.middleware)

        factory = self.factory or banshee.request.SimpleHandlerFactory()

        middleware.append(
            banshee.middleware.dispatch.DispatchMiddleware(locator, factory)
        )

        return banshee.bus.MessageBus(middleware)
