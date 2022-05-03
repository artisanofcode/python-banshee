# Dispatching requests

```{rst-class} lead
Transporting requests to their destined handlers.
```

## Buses

The {class}`~banshee.Bus` protocol wraps a {term}`command dispatcher` and message bus 
implementation. The bus routes requests to their subscribed {term}`handlers <handler>` via a 
composable chain of {term}`middleware`.

### Subscriptions

A {term}`bus` must be able to find the handlers for a request to dispatch it. 
Subscriptions hold the connection from a {term}`handler` to a {term}`request`. 

The {class}`~banshee.Registry` manages subscriptions, and provides them via the 
{class}`~banshee.HandlerLocator` protocol.

Subscribe a handler to a request via a manual definition or using a decorator.

```py
import banshee

registry = banshee.Registry()
registry.subscribe(do_greeting, to=GreetCommand)

# or via a decorator

@registry.subscribe_to(GreetCommand)
async def do_greeting(command: GreetCommand) -> None:
    print(f"Hello {command.name}!")
```

### Building a bus

You use the {class}`~banshee.Builder` class to construct a bus instance. Builder is an 
example of the builder pattern and uses a {term}`fluent interface` to define a bus.

```py
import banshee

bus = (
  banshee.Builder()
  .with_locator(registry)
  .build()
)
```

### Sending a request

Once you have registered your handlers, you can dispatch requests to them via the bus.

```py
await bus.handle(GreetCommand(name="Joe"))
```

### Querying

You can get a result back from a handler by sending a query.

```py
@dataclasses.dataclass(freeze=True)
class GetUserQuery:
   user_id: int

@registry.subscribe_to(GetUserQuery)
async def do_greeting(query: GetUserQuery) -> User:
    return user_store.get(query.user_id)

user = await bus.query(GetUserQuery(user_id=1))
```


## Reference

```{eval-rst}
.. autoclass:: banshee.Builder
   :show-inheritance:
   :members:

.. autoclass:: banshee.Bus
   :show-inheritance:
   :members:

.. autoclass:: banshee.HandlerLocator
   :show-inheritance:
   :members:

.. autoclass:: banshee.HandlerReference
   :show-inheritance:
   :members:

.. autoclass:: banshee.Registry
   :show-inheritance:
   :members:
```

```{exception} banshee.ConfigurationError(message)
Configuration error.

There was an error in how banshee was configured.
```

```{exception} banshee.MultipleErrors(message, exceptions)
Multiple errors.

Multiple errors were produced.
```