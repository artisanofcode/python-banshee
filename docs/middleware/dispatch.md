# Dispatch

```{rst-class} lead
The core of the command dispatcher.
```

```{attention}
You do not have to add this middleware yourself, the {class}`~bansheee.Builder` will add
it for you.
```

## Usage

The dispatch middleware actually handles the dispatching of requests to their handlers. 
It should be the last middleware in the chain.

### Registration

You do not have to add this middleware yourself, the {class}`~banshee.Builder` will add
it for you.  

Instead you setup the middleware using {meth}`~banshee.Builder.with_locator` and 
{meth}`~banshee.Builder.with_factory` to provide its dependencies.

### Context

We add a {class}`~banshee.Dispatch` context instance for each handler executed. It will
contain the result of the function call and the name of the handler.

```py
result = message[banshee.Dispatch].result
name = message[banshee.Dispatch].name
```

## Reference

```{eval-rst}
.. autoclass:: banshee.Dispatch
   :show-inheritance:
   :members:

.. autoclass:: banshee.DispatchMiddleware
   :show-inheritance:
   :members: __call__
```

```{exception} banshee.DispatchError(message, exceptions)
Dispatch error.

There was an error while handling a request.
```