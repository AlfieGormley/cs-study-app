---
id: asql-conditional-pivots
title: Conditional aggregates and empty matches
level: intermediate
minutes: 4
summary: A portable pivot gives each output category its own conditional aggregate.
sourceLesson: asql-set-ops-pivot
---

The shop has products in Kitchen and Home. orders holds the date; order_items holds quantity; products holds the unit price. Revenue below is the sum of line quantities times those listed product prices, not the independently stored order total.

## Pivoting: rows to columns

Reports often want categories across the top. Revenue by month and category:

```sql
-- Each condition fills one report cell.
SELECT
  strftime('%Y-%m', o.ordered_on)
    AS month,
  SUM(CASE WHEN p.category = 'Kitchen'
      THEN i.qty * p.price
      ELSE 0 END) AS kitchen,
  SUM(CASE WHEN p.category = 'Home'
      THEN i.qty * p.price
      ELSE 0 END) AS home
FROM orders o
JOIN order_items i
  ON i.order_id = o.id
JOIN products p
  ON p.id = i.product_id
GROUP BY month;
```

| month | kitchen | home |
|---|---|---|
| 2026-01 | 75 | 90 |
| 2026-02 | 125 | 180 |
| 2026-03 | 50 | 130 |

This is **conditional aggregation**: each output column is an aggregate over only the rows matching its condition. It works on every SQL database, which is why it is the portable way to pivot.

Each cell of the pivot is a sum over just the order lines that match its month and its column's category:

```formula
R(m, g) = Σ q_l × p_l for all l in L(m, g)
R(Jan, Kitchen) = 1 × 30 + 1 × 25 + 2 × 10
R(Jan, Kitchen) = 75
where
R(m, g): the revenue shown in month m's row, under category g's column
m: a month, the GROUP BY value
g: a category, the value tested in the column's CASE
L(m, g): the order lines in month m whose product is in category g
l: one order line
q_l: the quantity on line l (qty)
p_l: the unit price of line l's product (price)
Σ: sigma, "add up" the term after it for every line l listed
Jan, Kitchen: January and the Kitchen category
In words: a pivot cell adds up quantity times price for only the lines in that month and that category; every other line contributes 0 through ELSE 0.
```

Check that cell against the data: January's Kitchen revenue is order 101's Kettle (30) plus order 102's Toaster (25) and two Mugs (20), giving 75.

### FILTER: the cleaner spelling

Both Postgres (9.4+) and SQLite (3.30+) support the standard `FILTER` clause:

```sql
-- Each condition fills one report cell.
SUM(i.qty * p.price)
  FILTER (WHERE p.category = 'Home')
  AS home
```

One difference: if an existing group has rows but none match, FILTER with SUM gives NULL while CASE with ELSE 0 contributes zeros. Over entirely empty input, an ungrouped SUM returns NULL even with CASE ELSE 0, because there is no row on which to evaluate CASE. Neither grouped form creates a missing month. `COUNT(*) FILTER (...)` gives 0 either way.

### ELSE 0 versus no ELSE

Counting orders per customer per month with a `LEFT JOIN` from customers:

| name | jan | feb | mar |
|---|---|---|---|
| Ana | 1 | 1 | 1 |
| Dev | 0 | 1 | 0 |
| Eve | 0 | NULL | NULL |

The `jan` column used `SUM(CASE ... THEN 1 ELSE 0 END)`, so Eve's NULL-padded row counts as 0. The others used `SUM(o.ordered_on LIKE '2026-02%')`, which relies on SQLite treating booleans as 0/1. For Eve, the `LIKE` on NULL is NULL, so the sum is NULL. With ordered_on as PostgreSQL date, use a date-range condition or to_char before LIKE; PostgreSQL also rejects SUM(boolean) outright (`function sum(boolean) does not exist`); write `COUNT(*) FILTER (WHERE ...)` or cast with `::int`.

## Key takeaways
- A portable pivot gives each output category its own conditional aggregate.
- FILTER plus SUM can produce NULL; COUNT with FILTER produces zero.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
