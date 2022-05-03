# Injector

```{rst-class} lead
Python dependency injection framework, inspired by Guice.
```

## Integration

The [injector](https://pypi.org/project/injector/) library is a dependency injection
framework for python.

You define dependencies of a project as a series of modules and use them to create an 
{class}`~injector.Injector` instance. Banshee can use this instance to manage 
dependencies in a {term}`handler factory`.

### Installation

The following CLI command will add the python dependencies to your project.

```sh
poetry add banshee[injector]
```

### Example

```py
import banshee
import banshee.extra.injector
import injector

...

class MyModule(injector.Module):
    @injector.singleton
    @injector.provider
    def provide_bus(self, container: injector.Injector) -> banshee.Bus:
        return (
            banshee.Builder()
            .with_middleware(container.get(banshee.IdentityMiddleware))
            .with_middleware(container.get(banshee.CausationMiddleware))
            .with_middleware(container.get(banshee.HandleAfterMiddleware))
            .with_locator(container.get(banshee.HandlerLocator))
            .with_factory(container.get(banshee.HandlerFactory))
            .build()
        )

registry = banshee.Registry()

...

container = injector.Injector((
    banshee.extra.injector.BansheeModule(registry),
    MyModule(),
))

bus = container.get(banshee.Bus)
bus.handle(SomeCommand())
```

## Reference

```{eval-rst}
.. autoclass:: banshee.extra.injector.BansheeModule
   :show-inheritance:
   :members:
   :inherited-members:

.. autoclass:: banshee.extra.injector.InjectorHandlerFactory
   :show-inheritance:
   :members:
   :inherited-members:
```