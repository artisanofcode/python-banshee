# Glossary

```{glossary}
bus
    A class responsible for routing {term}`requests <request>` to where they need to be
    in order to be handled.

    Forms the top level entry point to the {term}`command dispatcher` implementation.

builder pattern
    A creational design pattern to provide a flexible solution to constructing complex
    objects from their representation.

command
    A {term}`request` that represents an action to be performed and should be executed
    exactly once.

command pattern
    A behavioral design pattern describing an object that contains all information
    needed to perform an action.

command dispatcher
    A design pattern to decouple the implementation of a command from its invoker. The
    invoker doesn't need to know how the execution of the command is implemented, only
    that the command exists.

context
    Additional information used by the {term}`middleware` chain to decide how to 
    dispatch a {term}`message`.

dependency injection
    Giving an object instances of its dependencies rather than having the object 
    instantiate them itself.

event
    A {term}`request` that represents an occurrence that might trigger something to
    happen elsewhere in the application.

fluent interface
    An object orientated API which relies on method chaining to create a domain specific
    language and increase legibility.

handler
    A callable that takes a {term}`request` as its singular positional argument and 
    performs an action.

handler factory
    A class responsible for converting {term}`handler reference` into a 
    concrete {term}`handler` instance, often via {term}`dependency
    injection`.

handler reference
    A reference to a callable which when pre-processed by a {term}`handler
    factory` can process a {term}`request`.

message
    An container for a {term}`request` and any additional {term}`context`.

middleware
    A class representing a link in the chain that forms a processing pipeline and
    defines part of how a {term}`message` is dispatched.

query
    A {term}`request` that represents a query for a result and should be executed
    exactly once and return a value.

request
    A {term}`command`, {term}`event`, or {term}`query` to be sent to a {term}`bus` for
    processing by {term}`handlers <handler>`.

    Requests are an example of the {term}`command pattern`.

subscription
    An association between a handler and the request type it wishes to process.
```