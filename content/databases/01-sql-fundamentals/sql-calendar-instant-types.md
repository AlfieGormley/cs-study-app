---
id: sql-calendar-instant-types
title: Represent dates and instants consistently
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: PostgreSQL date stores calendar dates; timestamptz stores instants.
---

Choosing a column type also determines how dates, instants and text will compare. The shop started with zero-padded ordered_on text; these examples distinguish SQLite representations from PostgreSQL's dedicated types.

### Dates and times

PostgreSQL has real types. Use `date` for calendar dates and `timestamptz` (timestamp with time zone) for moments in time. `timestamptz` stores an absolute instant, internally in UTC, and converts to the session's time zone on display. Plain `timestamp` stores a wall-clock reading with no zone, which becomes ambiguous the moment two servers or users disagree on time zone or a daylight-saving clock change happens. PostgreSQL's own wiki says to prefer `timestamptz`.

> [!analogy] Real-world analogy: "3 pm" on a sticky note versus a flight time
> A sticky note saying "call at 3 pm" is clear to you, but a colleague in another country can't tell when to call. An airline ticket pins its times to a named airport's time zone, so everyone can work out the same moment.
>
> **How it maps:** Plain `timestamp` is the sticky note: a wall-clock reading with no zone attached. `timestamptz` is the ticket: it identifies one absolute instant, which PostgreSQL can display in whichever time zone the session uses.
>
> **Where it stops:** A ticket keeps showing the departure airport's zone, but `timestamptz` does not remember the zone it was entered in; it stores only the instant. If you need the original local zone, store it in a separate column.

SQLite has no date type. Store ISO-8601 text (`'2026-03-09'`, or `'2026-03-09T14:30:00Z'` in UTC). It only sorts correctly if every value uses the same zero-padded format:

```sql
-- Mixed padding breaks chronological
-- sorting.
-- '2026-3-9' vs '2026-03-10'
CREATE TABLE dt (t TEXT);
INSERT INTO dt VALUES
  ('2026-3-9'), ('2026-03-10');
SELECT t FROM dt ORDER BY t;
-- 2026-03-10
-- 2026-3-9    (wrong!)
```

A CHECK can reject badly formatted values at write time, but beware the NULL lesson. SQLite's `date('2026-3-9')` returns NULL, so `CHECK (d = date(d))` is UNKNOWN and **passes**. Use the NULL-safe form:

```sql
-- SQLite column definition in CREATE TABLE.
d TEXT NOT NULL
  CHECK (d IS date(d))
```

This rejects `'2026-3-9'`, and also `'2026-02-30'`, which `date()` turns into `'2026-03-02'`.

### Text

In PostgreSQL, `text` and `varchar(n)` are stored the same way and perform the same. `varchar(n)` just adds a length check. Use `text`, and add a `CHECK (length(name) <= 200)` where a limit is a real business rule. Avoid `char(n)`, which pads with spaces.

## Key takeaways
- PostgreSQL date stores calendar dates; timestamptz stores instants.
- Consistent zero-padded UTC text sorts correctly in SQLite.
- Use a NULL-safe date check to reject unparseable input.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [Don't do this — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
