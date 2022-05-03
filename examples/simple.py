"""
Simple example
"""

import asyncio
import dataclasses
import pprint

import banshee

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


user_store = {
    1: User(first_name="Joe", last_name="Bloggs"),
}


#######################################################################################
# business logic
#######################################################################################

# the registry stores the connection between requests and handlers

registry = banshee.Registry()

# define a command


@dataclasses.dataclass(frozen=True, slots=True)
class GreetCommand:
    """
    Greet command.

    :param user_id: identifier
    """

    user_id: int


# define a handlers


@registry.subscribe_to(GreetCommand)
async def do_greeting(command: GreetCommand) -> None:
    """
    Do greeting.

    Fetch user and greet them.

    :param command: command object
    """
    if user := user_store.get(command.user_id):
        print(f"Hello {user.first_name}!")


async def main():
    """
    Main entry-point.
    """

    ###################################################################################
    # setup
    ###################################################################################

    # build the message bus
    inner = (
        banshee.Builder()
        .with_middleware(banshee.IdentityMiddleware())
        .with_middleware(banshee.CausationMiddleware())
        .with_middleware(banshee.HandleAfterMiddleware())
        .with_locator(registry)
        .build()
    )

    # wrap the bus in a TraceableBus which will let us introspect the messages
    bus = banshee.TraceableBus(inner)

    ###################################################################################
    # run things
    ###################################################################################

    # run a command
    await bus.handle(GreetCommand(user_id=1))

    # print info on the messages we handled
    pprint.pprint(bus.messages)


if __name__ == "__main__":
    asyncio.run(main())
