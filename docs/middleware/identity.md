# Identity

```{rst-class} lead
Add unique identifiers to messages.
```

## Usage

Assigns a unique identifier to every {term}`message` that passes through the handler.

The {term}`middleware` will not touch any messages with an existing identifier. It will
send them to the successive middleware without change.

### Registration

Add the middleware to your bus.

```py
bus = (
    banshee.builder()
    .with_middleware(banshee.IdentityMiddleware())
    .with_locator(registry)
    .build()
)
```

### Context

An {class}`~banshee.Identity` context instance stores the unique identifier for a message.

```py
unique_id = message[banshee.Identity].unique_id
```

## Reference

```{eval-rst}
.. autoclass:: banshee.Identity
   :show-inheritance:
   :members:

.. autoclass:: banshee.IdentityMiddleware
   :show-inheritance:
   :members: __call__
```