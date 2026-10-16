---
id: qp-estimates-and-costs
title: Unknown expressions, joins and scan costs
level: intermediate
minutes: 5
sourceLesson: qp-statistics-optimiser
summary: Unknown expressions, joins and scan costs with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Missing expression statistics and join estimates

The worked estimates use an illustrative million-row orders table and 100,000 customers; IDs are non-NULL and each order references exactly one customer.

### When there are no statistics

For conditions the planner can't analyse, it uses fixed default selectivities:

| Condition | Default | Example |
|---|---|---|
| `expr = const` | 0.5% | `lower(email) = '...'`: 500 of 100,000 |
| `expr < const` | 1/3 | `price * 2 > 100`: 3,333 of 10,000 |

The planner has stats on the `email` column, but not on `lower(email)`. An **expression index** on `lower(email)` allows expression statistics as a side effect, because ANALYZE then gathers statistics on the indexed expression.

### Join estimates

For an equijoin (a join on `=`), the selectivity is the fraction of all possible row pairs that match. Postgres estimates it from the distinct counts of the two join keys, refined using MCV lists where it has them. For `orders o JOIN customers c ON o.customer_id = c.id`:

```formula
s_join ≈ 1 / max(d_R, d_S)
n_est = n_R × n_S × s_join
n_est = 1,000,000 × 100,000 / 100,000
n_est = 1,000,000
where
s_join: the join selectivity: the fraction of all (order, customer) pairs that satisfy the join condition
max: the larger of the values in brackets
d_R: the number of distinct values of the join key in orders, here 91,709 customer ids
d_S: the number of distinct values of the join key in customers, here 100,000 ids
n_R: the number of rows in orders, 1,000,000
n_S: the number of rows in customers, 100,000
n_est: the estimated number of rows the join produces
≈: approximately equal to
In words: every order matches one customer out of 100,000, so the join produces one row per order: about a million.
```

The formula assumes every key value on the side with fewer distinct values has a match on the other side, which is exactly true for a foreign key.

Errors **multiply** as they go up the tree. If each of three joins is out by a factor of 3, the final estimate can be out by 27, and the join algorithm choices near the top are made on wrong numbers.

## The cost model

Postgres costs are in arbitrary units anchored on one sequential page read = 1.0:

| Parameter | Default | Charged for |
|---|---|---|
| `seq_page_cost` | 1.0 | Page read in order |
| `random_page_cost` | 4.0 | Page read at random |
| `cpu_tuple_cost` | 0.01 | Each row processed |
| `cpu_index_tuple_cost` | 0.005 | Each index entry |
| `cpu_operator_cost` | 0.0025 | Each operator or function call |

A sequential scan pays for every page it reads, every row it processes and every condition it evaluates on each row. For `orders` with `status = 'pending'`:

```formula
C_seq = P × c_page
      + n × c_tuple
      + n × q × c_op
C_seq = 7,353 × 1.0
      + 1,000,000 × 0.01
      + 1,000,000 × 1 × 0.0025
C_seq = 7,353 + 10,000 + 2,500
C_seq = 19,853
where
C_seq: the estimated total cost of the sequential scan, in planner cost units (1 unit = one sequential page read)
P: the number of pages in the table, here 7,353
c_page: `seq_page_cost`, default 1.0 per page read in order
n: the number of rows in the table, here 1,000,000
c_tuple: `cpu_tuple_cost`, default 0.01 per row processed
q: the number of operators (comparisons) in the filter evaluated on each row, here 1 for status = 'pending'
c_op: `cpu_operator_cost`, default 0.0025 per operator or function call
In words: read 7,353 pages, process a million rows and test one condition on each; the row work costs more than the page reads.
```

EXPLAIN shows `cost=0.00..19853.00`: exactly this. An index scan's cost depends on how many index and heap pages it expects to touch, charged at `random_page_cost`, discounted by physical-order correlation and `effective_cache_size` (the planner's guess of how much data is cached).

> [!tip] Tune random_page_cost for SSDs
> The default of 4.0 dates from spinning disks. On SSDs, or when most data is cached, many teams set it to around 1.1 so the planner is less reluctant to use indexes. Test the change on your workload first.

## Key takeaways
- Missing expression statistics can trigger defaults; indexed expressions can collect statistics after ANALYZE.
- Planner costs combine page and CPU terms in relative cost units, rather than milliseconds.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)

