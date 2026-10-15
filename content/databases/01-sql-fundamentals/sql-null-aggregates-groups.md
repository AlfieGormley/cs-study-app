---
id: sql-null-aggregates-groups
title: Distinguish unknown ratings from zero ratings
level: intermediate
minutes: 3
sourceLesson: sql-null
summary: AVG divides by the number of known inputs.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## NULL in aggregates

`SUM`, `AVG`, `MIN`, `MAX` and `COUNT(column)` skip NULLs. This is not universal: PostgreSQL `array_agg` includes NULL elements. That is usually what you want, but it changes what an average means. Suppose we add a `rating` column where only three products have been rated:

| name | rating |
|---|---|
| Kettle | 5 |
| Toaster | 3 |
| Lamp | NULL |
| Rug | NULL |
| Mug | 4 |

| expression | result |
|---|---|
| `AVG(rating)` | 4.0 |
| `SUM(rating)*1.0/COUNT(*)` | 2.4 |
| `AVG(COALESCE(rating, 0))` | 2.4 |

The two answers divide the same total by different counts:

```formula
mean_k = S / n_k = 12 / 3 = 4.0
mean_z = S / n_all = 12 / 5 = 2.4
where
mean_k: the average of the known ratings, what AVG(rating) returns, in stars
mean_z: the average if every unrated product counted as 0 stars
S: the sum of the known ratings, 5 + 3 + 4 = 12 stars (SUM skips NULLs)
n_k: how many ratings are known (not NULL), here 3, which is COUNT(rating)
n_all: how many products there are, rated or not, here 5, which is COUNT(*)
In words: AVG divides by the number of known values only, so leaving a value NULL keeps it out of the average, while turning it into 0 pulls the average down.
```

`AVG` is the mean of the ratings we know. Treating unrated products as 0 gives the lower figure. Neither is wrong, but they answer different questions, so decide which one you mean. Replacing NULL with 0 is a claim that the value is zero, and it is often false.

Recall from the previous lesson that `SUM` over no rows returns NULL, not 0.

## Grouping, DISTINCT and sorting

Here SQL switches rules. For grouping and duplicate removal, NULLs are treated as **equal to each other**:

- `SELECT DISTINCT referred_by` gives NULL, 1, 2: one NULL, not two.
- `GROUP BY city` puts all NULL cities in one group.

For sorting, NULLs are treated as either smaller or larger than every value. As the SELECT units showed, SQLite puts them **first** in ascending order and PostgreSQL puts them **last**. `NULLS FIRST` and `NULLS LAST` make it explicit.

`MIN` and `MAX` ignore NULLs: `MIN(city)` is Bristol, not NULL.

## Key takeaways
- AVG divides by the number of known inputs.
- Replacing NULL with zero changes the question being answered.
- Grouping and duplicate removal gather NULLs together, while sorting is engine-dependent.

## Further reading
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [NULL handling in SQLite versus other database engines](https://www.sqlite.org/nulls.html)
