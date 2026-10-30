---
id: pg-ticket-schema-types
title: Ticket schema, constraints and types
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Put the shop's rules in constraints and pick types for what values mean.
---

Build the ticket-shop fixture in a fresh disposable PostgreSQL database. The SQL was run on PostgreSQL 18 and also runs on versions 16 and 17. Later units reuse these exact two tables.

## Enforce rules beside the data

Create two tables. An event has available seats; a booking refers to an event and has an application-supplied request key.

```sql
-- Event-level invariants live here.
CREATE TABLE events (
  id bigint GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY,
  name text NOT NULL,
  seats_left integer NOT NULL
    CHECK (seats_left >= 0),
  starts_at timestamptz NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'
);

-- UNIQUE identifies repeated requests.
CREATE TABLE bookings (
  id bigint GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY,
  event_id bigint NOT NULL
    REFERENCES events(id),
  request_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
    DEFAULT now()
);
```

The identity column generates values, while `PRIMARY KEY` enforces uniqueness. Generated IDs can have gaps, including after an aborted transaction; do not interpret the highest ID as the number of rows. If IDs must be created outside the database, PostgreSQL 18 adds `uuidv7()`, which makes time-ordered UUIDs; an identity column is simpler when the database creates every row. A foreign key prevents a booking for a missing event. `CHECK` rejects negative availability, and `NOT NULL` separately rejects an unknown value: a check expression evaluating to NULL does not reject the row.

The unique request key will help identify retries of the same booking. Enforcing this in the database closes the race in which two requests both check for an existing key, find none, then insert duplicates.

Postgres automatically creates an index for a primary key or unique constraint. It does **not** automatically index the referencing side of every foreign key. Later, we will add an index starting with `bookings.event_id` to support lookups by event.

### Choose types for their meaning

| Value | Useful type | Reason |
|---|---|---|
| A count | `integer` | Exact whole number |
| A monetary amount | `numeric(12,2)` | Exact decimal arithmetic |
| An event instant | `timestamptz` | Represents a point in time |
| Optional attributes | `jsonb` | Queryable structured document |

`timestamptz` converts input to an instant and displays it in the session time zone. It does not preserve the original zone name. A recurring “9am Europe/London” schedule needs the named zone and scheduling rules as well as individual occurrence instants. For money, record the currency too; a decimal type cannot tell pounds from euros.

> [!analogy] Real-world analogy: a live broadcast in TV listings
> A summer football final kicks off once, at one moment. A London listings page prints it at 20:00 and a Tokyo page prints it at 04:00 the next morning. Neither listing records which city first announced the time. A weekly show "every Monday at 9am London time" is a different kind of fact: a rule that must follow the UK's clock changes.
>
> **How it maps:** the kick-off is the instant `timestamptz` stores. Each listing page is a session time zone, which changes only how the instant is displayed. The weekly rule is the named zone plus recurrence information you must store separately.
>
> **Where it stops:** a listings page can print any format it likes, but `timestamptz` stores nothing except the instant: it keeps no zone name and no original offset, and converts to the session's zone only when it displays the value.

Insert the first event and inspect the generated ID:

```sql
-- RETURNING gives the generated ID.
INSERT INTO events
  (name, seats_left, starts_at, details)
VALUES (
  'Postgres workshop',
  2,
  '2027-05-01 10:00:00+00',
  '{"format":"online"}'
)
RETURNING id, seats_left;
```

In this fresh database the ID is 1. In an application, use the returned ID instead of assuming it. `RETURNING` avoids a separate query to discover which row was created.

## Key takeaways

- Use NOT NULL as well as a CHECK: a CHECK that evaluates to NULL does not reject the row.
- Identity generates values; a primary key enforces uniqueness.
- `timestamptz` stores an instant; recurrence rules and zone names need their own columns.
- Foreign keys do not get an index automatically on the referencing side.

## Further reading

- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [PostgreSQL 18: identity columns](https://www.postgresql.org/docs/18/ddl-identity-columns.html)
- [PostgreSQL 18: date/time types](https://www.postgresql.org/docs/18/datatype-datetime.html)
- [PostgreSQL 18: numeric types](https://www.postgresql.org/docs/18/datatype-numeric.html)
- [PostgreSQL 18: UUID functions](https://www.postgresql.org/docs/18/functions-uuid.html)
