# Overview

```{rst-class} lead
A {term}`command dispatcher` and message bus implementation for python.
```

Banshee draws inspiration from [Brighter](https://www.goparamore.io) and 
[Symfony Messenger](https://symfony.com/doc/current/components/messenger.html). It 
allows you to decouple an interface such as an MVC controller from domain logic it 
triggers.

By decoupling domain logic from interface, both can evolve without impacting the other. 
You can add, remove, or change {term}`handlers <handler>` without having to change the 
interface. You can also swap the interface out completely without touching the 
domain logic.

Though not required, the library functions well in a hexagonal or clean architecture. It
can isolate the external services and allows a clean domain model. Defining the 
interface of the domain as a set of Commands and Events.