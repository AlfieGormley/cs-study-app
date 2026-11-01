---
id: sea-hexagonal-ports
sourceLesson: sea-hexagonal
title: Ports, adapters and dependency inversion
level: intermediate
minutes: 4
summary: Distinguish driving and driven ports and separate runtime calls from source dependencies.
---

The layering units ended with a problem: if the domain depends "downwards" on storage, business rules come bundled with database code. In a 2005 article Alistair Cockburn proposed a different picture. His stated goal was an application that could run without either a UI or a database, so that automated regression tests could drive it. Put the application in the **middle**, and treat the database, the web UI, the test suite and the message queue as interchangeable things plugged in around the edge.

He called it **hexagonal architecture**, or more descriptively **ports and adapters**. Cockburn says the six sides have no meaning: the shape just leaves room to draw ports and adapters, unlike a one-dimensional stack of layers. He expected a small number of ports, typically two, three or four; four was the most he had met at the time.

## The picture

```
          HTTP      CLI      tests
            \        |        /
        [adapter][adapter][adapter]
             \       |       /
          +---- driving ports ----+
          |                       |
          |   application core    |
          |   (use cases +        |
          |    domain model)      |
          |                       |
          +---- driven ports -----+
             /       |       \
        [adapter][adapter][adapter]
            /        |        \
       Postgres    SMTP    payment API
```

- The **core** holds the domain model and the use cases. It imports no framework, driver or SDK.
- A **hexagonal port** is an interface the core defines, in its own terms.
- A **hexagonal adapter** converts between a port and some specific technology.

There are two kinds of port:

| Kind | Who calls whom | Examples |
|---|---|---|
| Driving (primary) | Outside calls core | Use case API |
| Driven (secondary) | Core calls outside | Repository, mailer |

A Flask view is a **driving adapter**: it turns an HTTP request into a call on the core. A Postgres repository is a **driven adapter**: it implements a port the core needs. Cockburn relates the distinction to use cases' primary and secondary actors: the question is who starts the conversation.

## The trick: dependency inversion

The core *calls* the database, but it must not *import* the database code. The way out is the dependency inversion principle (the D in SOLID): the core owns an abstract interface, and the adapter depends on that interface.

```
 Classic:     domain ---> SqlRepo
 Hexagonal:   domain ---> OrderRepo (port)
                              ^
                              |  implements
                           SqlRepo (adapter)
```

The runtime call still goes from core to database. The *source code* dependency now points inwards. That is the whole idea.

## Key takeaways
- The application core owns ports expressed in its own language.
- Driving adapters call the core; driven adapters implement services the core calls.
- Runtime calls may go out while source-code dependencies point inward.

## Further reading
- [Hexagonal Architecture — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
