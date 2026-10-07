---
id: asql-interview-problems
title: Common interview SQL problems
level: advanced
minutes: 16
summary: The handful of patterns behind most SQL interview questions, from Nth highest and top-N per group to relational division, de-duplication, gaps and islands, and medians, with the edge cases interviewers probe.
---

SQL interviews reuse a small set of patterns in different costumes. "Second-highest salary", "latest order per customer" and "longest login streak" are each one pattern plus edge cases. Learn the patterns and, more importantly, the questions to ask before you write anything:

1. **Ties**: if two rows share the top value, do you want one or both?
2. **NULLs and empties**: what should happen with no data? A NULL row, or no row?
3. **Distinct**: is "second highest" the second row or the second distinct value?

Examples below use the shop data from this module.

> [!note] Content gap: execution provenance
> The original execution records were not available to this audit, so the claim that every query was run is omitted. Results are worked examples for the stated fixtures. Order totals are 200, 120, 90, 60, 60, 45, 45 and 30.

## 1. The Nth highest value

"Find the second-highest order total." Three standard answers:

```sql
-- A: nested MAX
SELECT MAX(total) AS second
FROM orders
WHERE total < (SELECT MAX(total)
               FROM orders);

-- B: DISTINCT + OFFSET
SELECT DISTINCT total
FROM orders
ORDER BY total DESC
LIMIT 1 OFFSET 1;

-- C: DENSE_RANK
WITH r AS (
  SELECT total, DENSE_RANK() OVER (
    ORDER BY total DESC) AS dr
  FROM orders)
SELECT DISTINCT total
FROM r WHERE dr = 2;
```

All three give 120 for the non-NULL totals shown. To ignore missing totals on arbitrary data, filter `total IS NOT NULL` before OFFSET or ranking; PostgreSQL DESC sorts NULLs first by default. Now the probes:

- **Generalise to N.** A doesn't generalise. B becomes `OFFSET N - 1`. C becomes `dr = N`. For N = 4, B and C give 60.
- **Forgot DISTINCT?** With ties, the 5th highest via `ORDER BY total DESC LIMIT 1 OFFSET 4` without `DISTINCT` lands on the second 60 rather than 45. `ROW_NUMBER` makes the same mistake; `DENSE_RANK` is the ranking that means "Nth distinct value".
- **Fewer than N values.** A returns one row containing NULL. B and C return **no rows**. If the spec says "return NULL", wrap it as a scalar subquery: `SELECT (SELECT DISTINCT total ... OFFSET 8) AS nth` gives a single NULL.

## 2. Top N per group

"Top two products by revenue in each category." Product revenue: Rug 360, Kettle 120, Mug 80, Toaster 50, Lamp 40, Vase 0.

```sql
WITH rev AS (
  SELECT p.category, p.name,
    SUM(i.qty * p.price) AS revenue
  FROM products p
  JOIN order_items i
    ON i.product_id = p.id
  GROUP BY p.id
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY category
    ORDER BY revenue DESC) AS rn
  FROM rev
)
SELECT category, name, revenue
FROM ranked WHERE rn <= 2;
```

| category | name | revenue |
|---|---|---|
| Home | Rug | 360 |
| Home | Lamp | 40 |
| Kitchen | Kettle | 120 |
| Kitchen | Mug | 80 |

Vase doesn't appear at all because the inner join drops products with no sales. If unsold products should compete (with revenue 0), use a `LEFT JOIN` and `COALESCE`.

Swap `ROW_NUMBER` for `RANK` or `DENSE_RANK` depending on the tie rule you agreed. Postgres offers two more tools:

```sql
-- Latest order per customer, Postgres
SELECT DISTINCT ON (customer_id)
  customer_id, id, ordered_on
FROM orders
ORDER BY customer_id,
         ordered_on DESC;
```

`DISTINCT ON` keeps the first row of each group according to the `ORDER BY`. It's concise but Postgres-only.

```sql
-- Top 2 per category, Postgres
SELECT c.category, t.name
FROM (SELECT DISTINCT category
      FROM products) AS c
CROSS JOIN LATERAL (
  SELECT name
  FROM product_rev r -- a view
  WHERE r.category = c.category
  ORDER BY revenue DESC
  LIMIT 2
) AS t;
```

Here `product_rev` is the `rev` query above saved as a view. The `LATERAL` form runs the inner query once per group. An ordinary aggregate view cannot itself have an index on its computed revenue. If product_rev is instead a maintained table or materialized view with an index on `(category, revenue DESC)`, each group can seek to its highest rows and stop after two visible matches. Obtaining the category list and computing or refreshing revenue also have a cost.

> [!note] Ties at the cut-off
> For the global top N, Postgres 13+ supports `FETCH FIRST 4 ROWS WITH TIES`. On our totals that returns 5 rows (200, 120, 90, 60, 60) because the 4th and 5th tie.

## 3. Relational division: "all of"

"Customers who bought **both** Kettle and Mug." A `WHERE name = 'Kettle' AND name = 'Mug'` can never be true on one row. Filter to the candidates, group, and count:

```sql
SELECT c.name
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
JOIN order_items i
  ON i.order_id = o.id
JOIN products p
  ON p.id = i.product_id
WHERE p.name IN ('Kettle', 'Mug')
GROUP BY c.id
HAVING COUNT(DISTINCT p.name) = 2;
-- Ana, Cat
```

`DISTINCT` matters: Ana bought Kettle in two different orders, so a plain `COUNT` gives her 3 and wrongly excludes her. Worse, a customer who bought Kettle twice and no Mug would count 2 and wrongly pass.

The same shape answers "customers who ordered in **every** month that had orders":

```sql
SELECT c.name
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id
HAVING COUNT(DISTINCT
  strftime('%Y-%m', o.ordered_on))
  = (SELECT COUNT(DISTINCT
       strftime('%Y-%m', ordered_on))
     FROM orders);
-- Ana
```

The textbook alternative is a double `NOT EXISTS` ("there's no month in which this customer has no order"). The counting version returns only customers represented by the inner join. If there are no required months, it returns nobody, whereas double NOT EXISTS returns every customer (the empty requirement is vacuously satisfied). Choose the intended empty-set behaviour.

## 4. Duplicates

"Find emails that appear more than once, then delete all but the earliest."

```sql
SELECT email, COUNT(*)
FROM signups
GROUP BY email
HAVING COUNT(*) > 1;
```

With six signups where `a@x.io` appears three times and `b@x.io` twice, that returns those two emails. Assume email is NOT NULL and id is a non-NULL primary key. To delete, keep the lowest `id` per email (this means earliest only if ids encode insertion order):

```sql
DELETE FROM signups
WHERE id NOT IN (
  SELECT MIN(id)
  FROM signups
  GROUP BY email);
-- ids 1, 2, 4 survive
```

`NOT IN` is safe here because `MIN(id)` of a primary key is never NULL. A Postgres-idiomatic version uses a self-join:

```sql
DELETE FROM signups a
USING signups b
WHERE a.email = b.email
  AND a.id > b.id;
```

Every row with a lower-id twin is deleted. Then add a `UNIQUE` constraint so the duplicates can't come back, which is the answer interviewers actually want to hear. Without it, two concurrent sign-ups can still race past an application-level check.

## 5. Gaps and islands

"Find each user's streaks of consecutive login days." User 1 logged in on 1, 2, 3, 5, 6 and 9 March.

The trick: subtract a row number from the date. Within a run of consecutive days, both go up by one each row, so the difference is constant. A gap changes it.

| day | rn | day - rn |
|---|---|---|
| 03-01 | 1 | 02-28 |
| 03-02 | 2 | 02-28 |
| 03-03 | 3 | 02-28 |
| 03-05 | 4 | 03-01 |
| 03-06 | 5 | 03-01 |
| 03-09 | 6 | 03-03 |

Group by that difference:

```sql
WITH g AS (
  SELECT day,
    date(day, '-' || ROW_NUMBER()
      OVER (ORDER BY day) || ' days')
      AS grp
  FROM logins
  WHERE user_id = 1
)
SELECT MIN(day) AS start,
       MAX(day) AS finish,
       COUNT(*) AS len
FROM g
GROUP BY grp;
```

| start | finish | len |
|---|---|---|
| 2026-03-01 | 2026-03-03 | 3 |
| 2026-03-05 | 2026-03-06 | 2 |
| 2026-03-09 | 2026-03-09 | 1 |

In Postgres, date minus integer is a date, so the group key is just `day - ROW_NUMBER() OVER (ORDER BY day)::int`. For several users, add `PARTITION BY user_id` and group by `(user_id, grp)`.

The trick assumes **one row per day**. Two logins on the same day would break the arithmetic, so de-duplicate first (`SELECT DISTINCT user_id, day`). DENSE_RANK also fixes the island key with repeated days, but COUNT(*) would still count logins; use COUNT(DISTINCT day) for streak length.

An alternative that also handles "gaps of up to N days" is to compare each row with `LAG(day)`, flag a new island when the gap exceeds the limit, and take a running `SUM` of the flags as the island id.

## 6. Running totals and thresholds

"On what date did cumulative revenue first reach 400?"

```sql
WITH r AS (
  SELECT ordered_on,
    SUM(total) OVER (
      ORDER BY ordered_on) AS running
  FROM orders
)
SELECT MIN(ordered_on) FROM r
WHERE running >= 400;
-- 2026-02-14 (running = 425)
```

The window must be computed before filtering, hence the CTE. If two orders could share a date, decide whether the running total should step per order (`ROWS`, with a tie-breaker) or per day (the default `RANGE`).

## 7. Median

Postgres has an ordered-set aggregate:

```sql
SELECT percentile_cont(0.5)
  WITHIN GROUP (ORDER BY total)
FROM orders;
-- 60
```

`percentile_cont` interpolates between the two middle values; `percentile_disc` returns an actual value from the data. The SQLite/PostgreSQL version below assumes non-NULL totals and averages the middle one or two rows. Filter NULL totals before numbering to match percentile_cont, which ignores them; other SQL engines may require explicit integer division:

```sql
WITH s AS (
  SELECT total,
    ROW_NUMBER() OVER (
      ORDER BY total) AS rn,
    COUNT(*) OVER () AS n
  FROM orders
)
SELECT AVG(total) AS median
FROM s
WHERE rn IN ((n + 1) / 2,
             (n + 2) / 2);
```

With n = 8, integer division gives positions 4 and 5 (both 60), so the median is 60. With n = 7, both expressions give 4, the single middle row.

## 8. The LEFT JOIN filter trap

"List every customer with their orders over 100." Where the filter goes changes the answer:

```sql
-- Filter in ON: keeps all customers
SELECT c.name, o.total
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
 AND o.total > 100;
```

This returns all five customers: Ana 120, Cat 200, and NULLs for Ben, Dev and Eve. Move `o.total > 100` to WHERE and the join first includes every real order plus Eve's padded row. WHERE rejects Ben and Dev's small orders and Eve's NULL, leaving Ana and Cat. This NULL-rejecting predicate makes the result equivalent to an inner join; other WHERE predicates can preserve padded rows.

## Key takeaways
- Before writing, pin down ties, NULL/empty behaviour and whether "Nth" means distinct values.
- Nth highest: `DENSE_RANK` or `DISTINCT ... OFFSET`; a scalar subquery turns "no row" into NULL.
- Top N per group: `ROW_NUMBER` in a subquery; Postgres adds `DISTINCT ON` and `LATERAL ... LIMIT`.
- "All of" questions are relational division: filter, group, and compare `COUNT(DISTINCT ...)`.
- Gaps and islands: value minus `ROW_NUMBER` is constant within a run.
- Filters on the optional side of a `LEFT JOIN` belong in `ON`, not `WHERE`.

## Further reading
- [Top-N queries — Use The Index, Luke](https://use-the-index-luke.com/sql/partial-results/top-n-queries)
- [SELECT (DISTINCT ON, LATERAL) — PostgreSQL docs](https://www.postgresql.org/docs/current/sql-select.html)
- [LIMIT and OFFSET — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-limit.html)
- [Aggregate functions (percentile_cont) — PostgreSQL docs](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Window functions — SQLite docs](https://www.sqlite.org/windowfunctions.html)
