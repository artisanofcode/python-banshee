"""
Injector with functions example
"""

import asyncio
import dataclasses
import pprint
import typing

import injector

import banshee
import banshee.extra.injector

#######################################################################################
# data model
#######################################################################################


@dataclasses.dataclass
class User:
    """
    User model
    """

    first_name: str
    last_name: str


UserStore = typing.NewType("UserStore", dict[int, User])


#######################################################################################
# business logic
#######################################################################################

# the registry stores the connection between requests and handlers

registry = banshee.Registry()

# define a command


@dataclasses.dataclass(frozen=True, slots=True)
class GetUserQuery:
    """
    Get user query.

    :param user_id: identifier
    """

    user_id: int


@dataclasses.dataclass(frozen=True, slots=True)
class GreetCommand:
    """
    Greet command.

    :param user_id: identifier
    """

    user_id: int


# define a handlers


@registry.subscribe_to(GetUserQuery)
async def get_user(query: GetUserQuery, store: UserStore) -> User | None:
    """
    Get user.

    Fetch user from store.

    :param query: query object

    :returns: user instance
    """
    return store.get(query.user_id)


@registry.subscribe_to(GreetCommand)
async def do_greeting(command: GreetCommand, bus: banshee.Bus) -> None:
    """
    Do greeting.

    Fetch user and greet them.

    :param command: command object
    :param bus: message bus
    """
    if user := await bus.query(GetUserQuery(user_id=command.user_id)):
        print(f"Hello {user.first_name}!")


#######################################################################################
# dependency injection
#######################################################################################


class MyModule(injector.Module):
    """
    Message bus module

    An Injector module to build a custom message bus instance.
    """

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(
            UserStore,
            to=UserStore(
                {
                    1: User(first_name="Joe", last_name="Bloggs"),
                }
            ),
        )

        return super().configure(binder)

    # singleton because we want to reuse the same bus each time

    @injector.singleton
    @injector.provider
    def provide_message_bus(self, container: injector.Injector) -> banshee.Bus:
        """
        Provide message bus

        Provides an customised instance of a message bus.

        The :class:`~banshee.contrib.injector.BansheeModule` will provide a message bus
        with sensible defaults, but you may want to over-ride to customise middleware.

        :param container: the container itself to pull dependencies from

        :returns: an instance of a message bus
        """
        bus = (
            banshee.Builder()
            .with_middleware(container.get(banshee.IdentityMiddleware))
            .with_middleware(container.get(banshee.CausationMiddleware))
            .with_middleware(container.get(banshee.HandleAfterMiddleware))
            .with_locator(container.get(banshee.HandlerLocator))
            .with_factory(container.get(banshee.HandlerFactory))
            .build()
        )

        return banshee.TraceableBus(bus)


async def main():
    """
    Main entry-point.
    """

    ###################################################################################
    # setup
    ###################################################################################

    # we use the modules to setup the dependency injection container

    container = injector.Injector(
        [
            banshee.extra.injector.BansheeModule(registry),
            MyModule(),
        ]
    )

    # and use the container to get our message bus instance

    bus = container.get(banshee.Bus)

    ###################################################################################
    # run things
    ###################################################################################

    # run a command
    await bus.handle(GreetCommand(user_id=1))

    # print info on the messages we handled
    pprint.pprint(bus.messages)


if __name__ == "__main__":
    asyncio.run(main())
