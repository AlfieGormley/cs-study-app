---
id: sql-patterns-date-ranges
title: Match text and include whole date ranges
level: basic
minutes: 3
sourceLesson: sql-select-basics
summary: LIKE case behaviour depends on the database and collation.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

### Case sensitivity differs

With the ordinary case-sensitive text collations used for these examples, `'Kettle' = 'kettle'` is false in both databases. Text equality can change with a case-insensitive collation. `LIKE` also differs:

- In **SQLite**, `LIKE` ignores case for ASCII letters by default, so `name LIKE 'k%'` finds Kettle.
- In **PostgreSQL**, `LIKE` is case-sensitive with a deterministic collation using case-sensitive text rules; PostgreSQL 18 also supports `LIKE` with nondeterministic collations such as case-insensitive ones. Use `ILIKE`, or `lower(name) LIKE 'k%'`.

Moving a query from SQLite in tests to PostgreSQL in production can therefore change its results.

### Dates as text

SQLite has no date type. This schema stores ISO-8601 text like `'2026-02-14'`, which sorts and compares correctly as a string. Watch the upper bound once times appear, though:

```sql
-- The upper date string ends at midnight.
SELECT '2026-02-28 14:00'
  BETWEEN '2026-02-01' AND '2026-02-28';
-- 0 (false)
```

The string with a time comes after `'2026-02-28'`, so the last afternoon of February falls outside the range. The robust pattern is a **half-open range**, which works for consistently formatted SQLite text and PostgreSQL `date` and `timestamp` columns. This WHERE fragment follows `SELECT * FROM orders`:

```sql
-- WHERE fragment after SELECT from orders.
WHERE ordered_on >= '2026-02-01'
  AND ordered_on <  '2026-03-01'
```

It selects orders 102 and 103 from the shop fixture. The lower bound includes midnight on 1 February; the upper bound excludes midnight on 1 March. Every time on 28 February is inside the interval. Adjacent monthly ranges meet at a boundary without a gap or overlap.

In PostgreSQL, a bare date-like string compared with a `timestamp` is converted to midnight at the start of that date. With `timestamptz`, decide the reporting time zone explicitly: local calendar months and UTC months can start at different instants. The half-open range pattern still applies, but its bounds must represent the intended instants.

SQLite's LIKE case folding is limited to ASCII by default. It does not make all Unicode upper- and lower-case letters equivalent. PostgreSQL ILIKE follows the active locale; it is not a guarantee of identical Unicode behaviour across engines. Choose a collation and test representative names before treating either pattern as a general case-insensitive search.

## Key takeaways
- LIKE case behaviour depends on the database and collation.
- Consistently formatted ISO date text sorts chronologically.
- Use an inclusive start and exclusive start of the next reporting period for timestamp ranges.

## Further reading
- [Pattern matching (LIKE, ILIKE) — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-matching.html)
- [The SELECT statement — SQLite documentation](https://www.sqlite.org/lang_select.html)
- [Quirks, caveats and gotchas in SQLite](https://www.sqlite.org/quirks.html)
