# Creating handlers

```{rst-class} lead
Handlers to handle the things that need handling.
```

## Requests

A {term}`request` is a {term}`command`, {term}`event`, or {term}`query` represented as a 
self contained object. An object that you dispatch to a {term}`handler` to decouple 
invocation from implementation.

Each has different processing expectations, but all are examples of the {term}`command 
pattern`. To avoid confusion over the word "command", banshee refers to these objects as
requests.

### Request handlers

{term}`Handlers <handler>` are function or classes that can process a request. They must
be callable, and they must take a request as the single positional argument. The 
{class}`~banshee.Handler` protocol defines this contract.

If we want to handle a `GreetCommand` request.  

```py
@dataclass
class GreetCommand:
    name: str
```

The handler can be a function, taking the command as its first argument.  

```py
async def do_greeting(command: GreetCommand) -> None:
    print(f"Hello {command.name}!")
```

### Command, Query, or Event

* An {term}`event` is a notification that something happened in the past. An occurance 
  that has already happened. Events form a historic record of how and when state changed
  in an application. 

  Events can have many handlers, or none at all.

* A {term}`command` is an imperative instruction to do something, a desire to take some
  form of action. Commands express a wish for a change in the applications state to take
  place. 

  Command should have exactly one handler.

* A {term}`query` is a real-time instruction to look something up, a desire to have some
  data fetched from a store. Queries express a wish to both retrieve and return some
  part of the applications state. 

  Queries should have exactly one handler.

## Reference

```{eval-rst}
.. autoclass:: banshee.Handler
   :show-inheritance:
   :members:
   :special-members: __call__
```