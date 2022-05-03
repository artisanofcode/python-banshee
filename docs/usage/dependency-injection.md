# Dependency injection

```{rst-class} lead
Wiring dependencies to handlers for extra handling.
```

## Handler factories

Subscribing to a {term}`request` will create a handler reference. The reference is an 
instance of the {class}`~banshee.HandlerReference` class. A {term}`handler factory` 
creates a concrete handler from the reference. The {class}`~banshee.HandlerFactory` 
protocol defines this contract.

The reference will be to the class or function used in the subscription. Which may or
may not be a handler. The factory tries to coerce these classes and functions into the 
{class}`~banshee.Handler` protocol.

### Providing dependencies

To perform the business logic a handler represents, it often needs other dependencies.

Banshee has no opinions about on how you manage your dependencies. You can use a custom
factory to provide them to handlers any way you like. 

```py
import functools
import inspect
import typing

import banshee

T = typing.TypeVar("T")


DEPENDENCIES = {
   "user_repository": UserRepository()
}

def kwargs_factory(self, reference: HandlerReference[T]) -> Handler[T]:
   expected = inspect.signature(reference.handler).parameters.keys()

   kwargs = {k: v for k, v in DEPENDENCIES.items() if k in keys}

   return functools.partial(reference.handler, **kwargs)
```

The above uses values based on argument name. It is a crude example. In production we 
recommend that you consider using a proper {term}`dependency injection` framework. See 
our [injector](../extra/injector.md) integration for example.

### Default behaviour

The {class}`~banshee.SimpleHandlerFactory` is the default used when a factory is not
provided. It will return a function as is, and try to create an instance for class based
handlers.

## Reference

```{eval-rst}
.. autoclass:: banshee.HandlerFactory
   :show-inheritance:
   :members: __call__

.. autoclass:: banshee.SimpleHandlerFactory
   :show-inheritance:
   :members: __call__
```