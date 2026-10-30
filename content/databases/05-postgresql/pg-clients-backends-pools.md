---
id: pg-clients-backends-pools
title: Clients, backends and connection pools
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Every client talks to its own server process, and the server enforces the rules for all of them.
---

PostgreSQL, usually called **Postgres**, is an open-source relational database server. SQL is the language you send it; Postgres is the system that stores rows, enforces constraints, coordinates concurrent sessions and recovers after a crash. It also supports JSON documents, extensible types and PostgreSQL extensions, but those features do not remove the need to design your data carefully.

This module follows a small ticket shop through schema design, concurrency, indexing, maintenance and recovery. Read the SQL fundamentals first. The examples were run on PostgreSQL 18.6. In October 2026, 18 was the current major release and PostgreSQL 19 had reached its first release candidate, so check the release notes for changed defaults when you upgrade. Plans and timings depend on your data and installation. Run them in a fresh, disposable database, never an application database.

## Follow a database request

Your application uses a database driver to connect to the server. `psql` is another client: a terminal for sending SQL and inspecting the results. An ORM is a layer above a driver; it does not replace the database. Because every client ends up talking to the same server, rules such as constraints and row locking are enforced there, for all clients, including ones that bypass your ORM.

A PostgreSQL **database cluster** means a collection of databases managed by one server installation. It does not necessarily involve several machines. A connection selects one database. Inside it, PostgreSQL schemas such as `public` are namespaces containing tables, functions and other objects. `public.orders` names a table in a PostgreSQL schema, not a different database.

Postgres starts a separate **backend process** for each client connection. A supervisor process accepts the connection and starts the backend, which then parses, plans and executes that client's SQL. Backends share memory and coordinate access to storage. Starting a process per connection costs time and memory, so applications normally use a connection pool: a bounded set of open connections that requests borrow and return.

A typical request follows this path; responses travel back to the client:

```flow
Application sends parameterised SQL
Driver obtains a pooled connection
Postgres backend plans and executes
Result returns through the driver
Connection returns to the pool
```

The server's connection limit, `max_connections`, defaults to 100. Raising it is not a substitute for measuring CPU, memory, lock waits and throughput: each backend uses memory of its own, and many more active backends than CPU cores mostly compete for the same CPU, memory and locks.

With transaction pooling, an external pooler gives each transaction whichever server connection is free, so the next transaction may use a different backend process. Do not assume session settings or temporary objects will persist on the connection your application receives next.

> [!analogy] Real-world analogy: a restaurant with dedicated waiters
> In this restaurant, every table that sits down gets its own waiter, who takes the order to a shared kitchen. Hiring and training a new waiter for every walk-in diner is slow, so a busy restaurant keeps a fixed team and seats parties at whichever waiter is free.
>
> **How it maps:** each waiter is a backend process serving one connection; the shared kitchen is the shared memory and storage. Keeping a fixed team is a connection pool. Seating a party with a different waiter for each course is transaction pooling, so a note left with the first waiter (a session setting or temporary table) may not reach the next.
>
> **Where it stops:** real waiters often cover several tables, but a backend serves exactly one connection for its whole life. Hiring more waiters helps a restaurant until the kitchen is full; with Postgres, extra backends compete for the same CPU, memory and locks, so throughput can fall.

To connect to a database that already exists locally:

```sh
psql -d postgres_study
```

Inside `psql`, `\conninfo` shows the connection, `\dt` lists tables and `\d events` describes a table. SQL statements end with a semicolon; these backslash commands are client commands. Use a PostgreSQL non-superuser role for the application with only the required database privileges, and bind user values through driver parameters rather than joining them into SQL strings.

## Key takeaways

- The server enforces constraints and row locking for every client, not the ORM or pool.
- Each connection gets its own backend process, so pools reuse a bounded number of them.
- A cluster can be one server installation holding several databases.
- Transaction pooling means session state may not follow your next transaction.

## Further reading

- [PostgreSQL 18: architectural fundamentals](https://www.postgresql.org/docs/18/tutorial-arch.html)
- [PostgreSQL 18: how connections are established](https://www.postgresql.org/docs/18/connect-estab.html)
- [PostgreSQL 18: psql](https://www.postgresql.org/docs/18/app-psql.html)
- [PostgreSQL 18: role attributes](https://www.postgresql.org/docs/18/role-attributes.html)
