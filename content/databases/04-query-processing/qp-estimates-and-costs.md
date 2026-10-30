---
id: qp-estimates-and-costs
title: Unknown expressions, joins and scan costs
level: intermediate
minutes: 4
sourceLesson: qp-statistics-optimiser
summary: The planner's fixed guesses for expressions it cannot analyse, how it estimates join sizes, and how its cost units add up for a sequential scan.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

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

```formula reference
s_join ≈ 1 / max(d_R, d_S)
where
s_join: the join selectivity: the fraction of all possible (order, customer) pairs that satisfy the join condition
max: the larger of the values in brackets
d_R: the number of distinct join-key values in the first input, here about 91,709 customer IDs in orders
d_S: the number of distinct join-key values in the second input, here 100,000 customer IDs
≈: approximately equal to
In words: of all possible pairs, about one in (the larger distinct-key count) matches. A million orders times 100,000 customers, divided by 100,000, gives about a million joined rows: one per order.
```

This assumes every key value on the side with fewer distinct values has a match on the other side, which is exactly true for a foreign key. A PostgreSQL 18.6 run estimated `rows=1000000` for this join.

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

A sequential scan pays for every page it reads, every row it processes and every condition it evaluates on each row:

```formula reference
C_seq = P × c_page
      + n × c_tuple
      + n × q × c_op
where
C_seq: the estimated total cost of the sequential scan, in planner cost units (1 unit = one sequential page read)
P: the number of pages in the table
c_page: `seq_page_cost`, default 1.0 per page read in order
n: the number of rows in the table
c_tuple: `cpu_tuple_cost`, default 0.01 per row processed
q: the number of operators (comparisons) in the filter evaluated on each row
c_op: `cpu_operator_cost`, default 0.0025 per operator or function call
In words: pages, plus a small charge per row, plus a smaller charge per condition per row. For `orders` with `status = 'pending'` that is 7,353 for pages, 10,000 for a million rows and 2,500 for one test on each: 19,853.
```

For a million narrow rows, the row work costs more than the page reads. EXPLAIN for that query shows `cost=0.00..19853.00`, exactly this sum. An index scan's cost depends on how many index and heap pages it expects to touch, charged at `random_page_cost`, discounted by physical-order correlation and `effective_cache_size` (the planner's guess of how much data is cached).

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

