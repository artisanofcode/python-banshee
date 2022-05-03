# Testing

```{rst-class} lead
See the requests a bus dispatches.
```

## Traceable bus

A decorator for a Bus that records all requests that it handles. This is useful in testing and debugging a usage of the bus.

###  Usage

Wrap an existing bus in the traceable bus, and use it as normal.

```py
bus = banshee.TraceableBus(
   banshee.Builder()
   .with_registry()
   .build()
)

await bus.handle(GreetCommand(name="joe"))

print(bus.messages)
```

## Reference

```{eval-rst}
.. autoclass:: banshee.TraceableBus
   :show-inheritance:
   :members:

.. autoclass:: banshee.MessageInfo
   :show-inheritance:
   :members:
```