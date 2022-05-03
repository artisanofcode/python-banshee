# Causation

```{rst-class} lead
The core of the command dispatcher.
```

```{note}
Middleware uses {class}`~contextvars.ContextVar` to store state per thread or async
tasks.
```

## Usage

Tracks the requests that trigger other request. The middleware will add a causation and
correlation identifier to every message.

*   The causation identifier relates to the request that triggered this request.
*   The correlation identifier relates to the original request that triggered all parent
    requests. The request passed to the message bus.

This middleware relies on the {class}`~banshee.Identity` context added by the 
{class}`~banshee.IdentityMiddleware`. 

### Registration

Add the middleware to your bus. This middleware should come after the 
{class}`~banshee.IdentityMiddleware`.

```py
bus = (
    banshee.builder()
    .with_middleware(banshee.IdentityMiddleware())
    .with_middleware(banshee.CausationMiddleware())
    .with_locator(registry)
    .build()
)
```

### Context

A {class}`~banshee.Causation` context instance stores the causation and correlation 
identifiers for the message. 

```py
causation_id = message[banshee.Causation].causation_id
correlation_id = message[banshee.Causation].correlation_id
```

## Reference

```{eval-rst}
.. autoclass:: banshee.Causation
   :show-inheritance:
   :members:

.. autoclass:: banshee.CausationMiddleware
   :show-inheritance:
   :members: __call__
```