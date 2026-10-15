---
id: para-declarative-pipelines
title: Declarative pipelines and optimisation
level: basic
minutes: 3
sourceLesson: para-imperative-declarative
summary: A pipeline states transformations without a hand-managed accumulator.
---

A pipeline describes which values to keep, how to transform them and how to combine the results. Compare that description with the explicit accumulator from the previous unit.

## Declarative programming

A declarative program states the relationship between input and output and leaves the execution strategy to a runtime, compiler or engine.

The same task in a declarative style:

```python
# Select evens before summing squares.
total = sum(n * n for n in nums
            if n % 2 == 0)
```

```sql
-- COALESCE handles no matching rows.
SELECT COALESCE(SUM(n * n), 0)
FROM nums
WHERE n % 2 = 0;
```

```haskell
-- Filter before squaring and summing.
total = sum [n * n | n <- nums, even n]
```

```javascript
// Keep, transform, then aggregate.
const total = nums
  .filter(n => n % 2 === 0)
  .map(n => n * n)
  .reduce((a, b) => a + b, 0);
```

There is no loop counter and no accumulator you update by hand. You say *which* numbers and *what* to do with them.

Declarative languages are everywhere, often not recognised as programming languages at all:

| Language | You declare | Engine decides |
|---|---|---|
| SQL | The rows you want | Join order, indexes |
| HTML/CSS | Structure, style | Layout, painting |
| Regex | A pattern | Matching algorithm |
| Make | Targets, deps | What to rebuild |
| Terraform | Infrastructure | API calls to make |

Functional and logic programming are two important declarative families explored in the following units. The Python, Haskell and JavaScript examples assume `nums` contains the same finite integers used in the earlier imperative example; the SQL version assumes a table `nums` with a numeric column `n`. These are small values, so language-specific integer limits do not affect this example.

## Why declarative code can be faster

Giving up control of *how* sounds like it would make code slower. Often the opposite is true, because the engine is free to choose a better strategy than you would.

A SQL query does not say "loop over the orders table, then for each row look up the customer". The database's **query planner** looks at table sizes, indexes and statistics and picks a plan: perhaps a hash join, perhaps an index scan, perhaps a parallel scan across 8 workers. If you add an index tomorrow, the planner may use it to accelerate suitable queries without rewriting them; an index does not guarantee a faster plan.

```
  SQL text
     |
     v
  parser -> planner -> executor
             ^   (chooses join order,
             |    index, parallelism)
        statistics
```

The same idea appears elsewhere:

- A Java parallel stream `list.parallelStream().mapToInt(f).sum()` can split work across cores because you never said "in this order, one at a time".
- A spreadsheet can use dependencies to avoid unnecessary recalculation; volatile formulas and full recalculation modes are exceptions.
- Haskell's compiler can fuse `map f (map g xs)` into a single pass with no intermediate list.

The general principle: the less you over-specify, the more freedom the system has to optimise.

## Key takeaways
- A pipeline states transformations without a hand-managed accumulator.
- Planners and fusion can exploit freedom, subject to semantics.

## Further reading
- [PostgreSQL: understanding execution plans](https://www.postgresql.org/docs/17/using-explain.html)
- [GHC: rewrite rules and fusion](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/rewrite_rules.html)
