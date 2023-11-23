"""
Integrations with :mod:`injector`.
"""

import functools
import inspect
import typing

import injector

import banshee

T = typing.TypeVar("T")


class InjectorHandlerFactory(banshee.HandlerFactory):
    """
    Injector handler factory.

    This factory will use a pre-configured dependency injection container from the
    :mod:`injector` module to instantiate handlers.

    References are assumed to be functions where the first positional argument of the
    function is the request, or classes who provide a `__call__` method, taking a single
    positional argument.

    Dependencies will be automatically added to the handler, before calling, and
    can even insert the :class:`~banshee.Bus` for recursive calls.

    .. code-block::python

        @registry.subscribe_to(GreetCommand)
        def do_greet(command: GreetCommand, bus: Bus) -> None:
            name = bus.query(UserNameQuery(user_id=command.user_id))

            print(f"hello {name}!")
    """

    # pylint: disable=too-few-public-methods

    @injector.inject
    def __init__(self, container: injector.Injector):
        self.container = container

    def __call__(
        self,
        reference: banshee.HandlerReference[T],
    ) -> banshee.request.Handler[T]:
        if not isinstance(reference.handler, type):
            if not injector.is_decorated_with_inject(reference.handler):
                injector.inject(reference.handler)

            @functools.wraps(reference.handler)
            async def _handler(request: T) -> typing.Any:
                return await self.container.call_with_injection(
                    callable=reference.handler,
                    args=(request,),
                )

            return _handler

        # we only apply inject when constructor has arguments
        if (
            hasattr(reference.handler, "__init__")
            and not injector.is_decorated_with_inject(
                typing.cast(typing.Any, reference.handler).__init__
            )
            and inspect.signature(reference.handler).parameters
        ):
            injector.inject(reference.handler)

        return self.container.create_object(reference.handler)


class BansheeModule(injector.Module):
    """
    Banshee module.

    A module to configure default bindings for various banshee related classes.

    This module will configure a :class:`~banshee.Bus` instance with sensible
    defaults for local use.

    :param registry: optional registry to bind
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, registry: banshee.Registry | None = None) -> None:
        super().__init__()

        self.registry = registry

    def configure(self, binder: injector.Binder) -> None:
        if self.registry:
            # https://github.com/python/mypy/issues/4717
            binder.bind(
                banshee.HandlerLocator,  # type: ignore
                to=injector.InstanceProvider(self.registry),
            )

        return super().configure(binder)

    @injector.singleton
    @injector.provider
    def _provide_factory(self, container: injector.Injector) -> banshee.HandlerFactory:
        return InjectorHandlerFactory(container)

    @injector.singleton
    @injector.provider
    def _provide_message_bus(self, container: injector.Injector) -> banshee.Bus:
        return (
            banshee.Builder()
            .with_middleware(container.get(banshee.IdentityMiddleware))
            .with_middleware(container.get(banshee.CausationMiddleware))
            .with_middleware(container.get(banshee.HandleAfterMiddleware))
            # https://github.com/python/mypy/issues/4717
            .with_locator(container.get(banshee.HandlerLocator))  # type: ignore
            .with_factory(container.get(banshee.HandlerFactory))  # type: ignore
            .build()
        )
