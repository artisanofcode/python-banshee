# Quick start

```{rst-class} lead
On your mark, get set, GO!
```

## Greeter

An example script to greet people via a dispatched command.

### Define a command

A command encapsulates all information needed to process it. It can be any object but a frozen dataclass  works best.

```py
@dataclasses.dataclass(frozen=True, slots=True)
class GreetCommand:
    """
    Greet command.

    :param name: persons name
    """

    name: str
```

### Define a handler

The registry stores the connection between requests and handlers. You can decorate a handlers with it.


```py
registry = banshee.Registry()

@registry.subscribe_to(GreetCommand)
async def do_greeting(command: GreetCommand) -> None:
    """
    Do greeting.

    Greet a person.

    :param command: command object
    """
    print(f"Hello {command.name}!")
```

### Create a bus

You create a bus via a builder, and pass in the registry we defined earlier.

```py
bus = (
    banshee.Builder()
    .with_locator(registry)
    .build()
)
```

### Handle the command

With all the pieces in place, you can dispatch your first command.

```py
await bus.handle(GreetCommand(name="Joe"))
```