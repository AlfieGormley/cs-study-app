---
id: pg-clients-backends-pools
title: Clients, backends and connection pools
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: The server enforces constraints for every client.
---

PostgreSQL, usually called **Postgres**, is an open-source relational database server. SQL is the language you send it; Postgres is the system that stores rows, enforces constraints, coordinates concurrent sessions and recovers after a crash. It also supports JSON documents, extensible types and PostgreSQL extensions, but those features do not remove the need to design your data carefully.

This module brings the pieces together around a small ticket shop. Read the SQL fundamentals first. This module divides the original ticket-shop walkthrough into short, separately completed units. The examples use PostgreSQL 18-compatible SQL; plans and timings depend on your data and installation. Run the examples in order in a fresh, disposable database, not an existing application database.

## Follow a database request

Your application uses a database driver to connect to the server. `psql` is another client: a terminal for sending SQL and inspecting the results. An ORM is another layer above a driver; it does not replace the database.

A PostgreSQL **database cluster** means a collection of databases managed by a server installation. It does not necessarily involve several machines. A connection selects one database. Inside it, PostgreSQL schemas such as `public` are namespaces containing tables, functions and other objects. `public.orders` names a table in a PostgreSQL schema, not a different database.

Postgres normally uses a separate backend process for each client connection. Those processes share memory and coordinate access to storage. Connection pools reuse a bounded number of connections, avoiding a new backend process for every web request. Increasing the connection limit is not a substitute for measuring CPU, memory, lock waits and throughput.

A typical request follows this path; responses travel back to the client:

```flow
Application sends parameterised SQL
Driver obtains a pooled connection
Postgres backend plans and executes
Result returns through the driver
Connection returns to the pool
```

With transaction pooling, the next transaction may use a different backend process. Do not assume session settings or temporary objects will persist on the connection your application receives next.

To connect to a database that already exists locally:

```sh
psql -d postgres_study
```

Inside `psql`, `\conninfo` shows the connection, `\dt` lists tables and `\d events` describes a table. SQL statements end with a semicolon; these backslash commands are client commands. Use a PostgreSQL non-superuser role for the application with only the required database privileges, and bind user values through driver parameters rather than joining them into SQL strings.

## Key takeaways

- The server enforces constraints for every client.
- A PostgreSQL cluster can be one server installation.
- Transaction pooling requires care with session state.

## Further reading

- [PostgreSQL 18: tutorial arch](https://www.postgresql.org/docs/18/tutorial-arch.html)
- [PostgreSQL 18: connect estab](https://www.postgresql.org/docs/18/connect-estab.html)
- [PostgreSQL 18: app psql](https://www.postgresql.org/docs/18/app-psql.html)
- [PostgreSQL 18: role attributes](https://www.postgresql.org/docs/18/role-attributes.html)
