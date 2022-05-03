# Handle After

```{rst-class} lead
Handle requests after the current handler.
```

```{note}
Middleware uses {class}`~contextvars.ContextVar` to store state per thread or async
tasks.
```

## Usage

Postpone marked requests handling until after the current handler has finished.

This is useful for dispatching requests from inside a transactional context. The middleware will pause proceessing  the middleware chain further and return. Proceessing the middleware chain will resume after the current request finishes.

The result of any postponed handlers will not be accessible.

### Registration

Add the middleware to your bus.  

```py
bus = (
    banshee.builder()
    .with_middleware(banshee.HandleAfterMiddleware())
    .with_locator(registry)
    .build()
)
```

### Context

You trigger this middleware with the HandleAfter context.

```py
bus.handle(request, contexts=[banshee.HandleAfter()])
```

## Reference

```{eval-rst}
.. autoclass:: banshee.HandleAfter
   :show-inheritance:
   :members:

.. autoclass:: banshee.HandleAfterMiddleware
   :show-inheritance:
   :members: __call__
```