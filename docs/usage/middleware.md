# Middleware

```{rst-class} lead
Composable processing for requests.
```

## Chain

Banshee processes {term}`requests <request>` using a nested chain of {term}`middleware`.
Each link in the chain does a single step in the processing. You arrange these links to
work how you want them to. We provide a set of standard middleware, and it's easy to 
create your own.

### Context

Middleware communicate via context classes. A context can be any class but a we 
recommend a frozen {obj}`~dataclasses.dataclass` for their immutability. Middleware 
can add or remove contexts as messages move along the chain.

```py
import dataclasses

@dataclasses.dataclass(frozen=True)
class Count:
    number: int
```

### Messages

The {class}`~banshee.Message` class associates a request with related context objects
from processing it. It provides methods to add, remove, and get contexts by class.

```py
message = banshee.message_for(requset)

message = message.including(Count(number=10))

assert message[Count].number == 10
```

### Registering

We execute middleware in the order you register them. You add them via the 
{class}`~banshee.Builder`. The builder always adds a {class}`~banshee.Dispatch` 
middleware as the inner most middleware. 

```py
bus = (
    banshee.Builder()
    .with_locator(registry)
    .with_middleware(banshee.IdentityMiddleware())
    .with_middleware(banshee.CausationMiddleware())
    .with_middleware(banshee.HandleAfterMiddleware())
    .build()
)
```

### Custom middleware

You can add custom middleware to the chain. The {class}`~banshee.Middleware` protocol
defines them. You can use either a callable class or a simple function. 

```py
T = typing.TypeVar("T")

class CountMiddleware:
    def __init__(self) -> None:
        self.number = 0

    async def __call__(
        message: banshee.Message[T], 
        handle: banshee.HandleMessage
    ) -> banshee.Message[T]:
        self.number += 1

        message = message.including(Count(number=self.number))

        return await handle(message)

async def filter_middleware(
    message: banshee.Message[T], 
    handle: banshee.HandleMessage
) -> banshee.Message[T]:
    context = message.get(Count)

    if context and context.number % 2 == 1:
        return message

    return await handle(message)
```

We defined two middleware above. A class based `CountMiddleware` named that adds the 
count to each message. And another function based `filter_middleware` that will refuse 
to process every other message.

## Reference

```{eval-rst}
.. autoclass:: banshee.HandleMessage
   :show-inheritance:
   :members: __call__

.. autoclass:: banshee.Message
   :show-inheritance:
   :members:

.. autoclass:: banshee.Middleware
   :show-inheritance:
   :members: __call__
```