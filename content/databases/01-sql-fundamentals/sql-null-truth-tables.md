---
id: sql-null-truth-tables
title: Compare unknown values and trace three-valued logic
level: intermediate
minutes: 5
sourceLesson: sql-null
summary: Ordinary scalar comparisons with NULL give UNKNOWN.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

NULL often makes a correct-looking query return the wrong rows. Treat **NULL as a missing or unknown value**, rather than zero or an empty string. An application may use it for "unknown" or "not applicable"; SQL does not record which interpretation you intended.

If Chloe's city is unknown, is she in London? We don't know. Is she *not* in London? We don't know that either. SQL encodes that "don't know" as a third truth value, **UNKNOWN**, alongside TRUE and FALSE.

The shop schema has three kinds of NULL that this lesson uses: Chloe's `city`, the `referred_by` of Asha and Erin, and the `customer_id` of guest order 106.

## Comparisons with NULL are unknown

The ordinary scalar comparisons used here, such as `=` and `<>`, give UNKNOWN if either operand is NULL (SQL shows UNKNOWN as NULL). Arithmetic and the `||` operator in these examples also propagate NULL:

```sql
-- Each expression propagates the unknown.
SELECT NULL = NULL,   -- NULL
       NULL <> 1,     -- NULL
       NULL + 1,      -- NULL
       'a' || NULL;   -- NULL
```

Even `NULL = NULL` is unknown: two unknown values might or might not be equal. So this finds nobody:

```sql
-- Ordinary equality cannot find a NULL
-- city.
SELECT name FROM customers
WHERE city = NULL;     -- 0 rows
```

Use the dedicated predicates instead:

```sql
-- Alternative WHERE clauses, not one query.
WHERE city IS NULL       -- Chloe
WHERE city IS NOT NULL   -- other 4
```

## Three-valued logic

`AND`, `OR` and `NOT` extend naturally. Treat UNKNOWN as "could be either" and ask whether the answer would change:

| AND | T | F | U |
|---|---|---|---|
| **T** | T | F | U |
| **F** | F | F | F |
| **U** | U | F | U |

| OR | T | F | U |
|---|---|---|---|
| **T** | T | T | T |
| **F** | T | F | U |
| **U** | T | U | U |

`NOT U` is U. The short-cuts are worth memorising: `FALSE AND anything` is FALSE, and `TRUE OR anything` is TRUE. In both cases the unknown side can't change the result.

There is a compact way to remember both tables. Assign zero to FALSE, one half to UNKNOWN and one to TRUE; the three operators then become simple arithmetic:

```formula
a AND b = min(a, b)
a OR b = max(a, b)
NOT a = 1 − a
where
a, b: two truth values written as numbers: FALSE = 0, UNKNOWN = ½, TRUE = 1
AND: SQL's "both must hold" operator
OR: SQL's "at least one must hold" operator
NOT: SQL's negation operator
min: the smaller of its inputs
max: the larger of its inputs
In words: AND gives the weakest of its inputs, OR gives the strongest, and NOT flips a value around the middle, which leaves UNKNOWN where it is.
```

For example, pairing TRUE with UNKNOWN gives UNKNOWN under AND, while pairing FALSE with UNKNOWN gives FALSE. NOT leaves UNKNOWN unchanged. This numerical encoding describes Kleene's three-valued logic for AND, OR and NOT; it is a memory aid, not SQL's internal storage format. The ordinary scalar equality comparisons in this unit return UNKNOWN whenever either side is NULL.

WHERE keeps only TRUE rows. It discards UNKNOWN just as it discards FALSE. To trace a nested condition, evaluate its comparisons first, then AND or OR, then an enclosing NOT. For Erin, `referred_by = 1` is UNKNOWN but `city = 'London'` is FALSE. Their AND is therefore FALSE, and negating that AND gives TRUE. For Chloe the pair is TRUE and UNKNOWN, so its AND and its negation are both UNKNOWN. The quiz uses this contrast.

## Key takeaways
- Ordinary scalar comparisons with NULL give UNKNOWN.
- FALSE AND UNKNOWN is FALSE; TRUE OR UNKNOWN is TRUE.
- NOT UNKNOWN stays UNKNOWN.

## Further reading
- [Null (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Null_(SQL))
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [Three-valued logic — Modern SQL](https://modern-sql.com/concept/three-valued-logic)
