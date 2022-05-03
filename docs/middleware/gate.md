# Gate

```{rst-class} lead
Gate access to a middleware.
```

## Usage

Gates access to a {term}`middleware` behind a callback, if the result of the
callback is {data}`True` then the inner middleware will be inserted next into
the chain, otherwise the chain will continue as normal.

The gate callback will be called with the current message.

### Registration

Add the middleware to your bus.

```py
def gate(message: banshee.Message[typing.Any]) -> bool:
   return isinstance(message.request, FooMixin)

bus = (
    banshee.builder()
    .with_middleware(banshee.GateMiddleware(FooHandler(), gate))
    .with_locator(registry)
    .build()
)
```

## Reference

```{eval-rst}
.. autoclass:: banshee.Gate 
   :show-inheritance:
   :special-members: __call__

.. autoclass:: banshee.GateMiddleware
   :show-inheritance:
   :members: __call__
```