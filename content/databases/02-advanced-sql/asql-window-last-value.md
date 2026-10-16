---
id: asql-window-last-value
title: LAST_VALUE and practical window plans
level: intermediate
minutes: 3
summary: LAST_VALUE reads the end of the current frame, not automatically the partition.
sourceLesson: asql-window-functions
---

The shop has eight orders with unique dates. The first is order 101, total 120; the last is order 108, total 30. With an ordered window and no explicit frame, the frame ends at the current row’s last peer.

### The LAST_VALUE trap

```sql
-- Frame end determines the last value.
LAST_VALUE(total) OVER (
  ORDER BY ordered_on)
```

You might expect the last order's total (30) on every row. Here dates are unique, so each row returns *its own* total. With tied dates, the default frame also includes peers and LAST_VALUE can come from another tied row. With unique dates, the current row is the end of that frame. Fix it by extending the frame:

```sql
-- Frame end determines the last value.
LAST_VALUE(total) OVER (
  ORDER BY ordered_on
  ROWS BETWEEN UNBOUNDED PRECEDING
       AND UNBOUNDED FOLLOWING)
```

FIRST_VALUE with this default frame reaches the partition’s first row. Explicitly bounded or excluded frames can change that, so reason from the frame rather than the function’s name.

## SQLite and Postgres differences

Window function semantics are standard and match closely (SQLite added them in 3.25, 2018). The differences you hit are in surrounding types:

| Topic | SQLite | Postgres |
|---|---|---|
| `AVG` of ints | float, `82.5` | numeric, `82.5000...` |
| `ROUND(x, n)` | any number | numeric only |
| Window in `WHERE` | error | error |
| `QUALIFY` | no | no |

In Postgres, `ROUND(some_double, 1)` fails with `function round(double precision, integer) does not exist`; cast to `numeric` first.

## Performance notes

- Each distinct `PARTITION BY`/`ORDER BY` combination typically needs a sort. Several windows sharing one definition (use `WINDOW w`) can share the sort.
- An index matching `(partition cols, order cols)` can let Postgres skip the sort.
- Top-N per group via `ROW_NUMBER` may still read or sort many input rows, although PostgreSQL 15+ can stop computing window values when an eligible run condition fails. For a few rows per group over a large table, a `LATERAL` join with `LIMIT` on an index can be far cheaper (see the interview problems lesson).

## Key takeaways
- LAST_VALUE reads the end of the current frame, not automatically the partition.
- An index may avoid a window sort; inspect the plan before assuming it does.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
