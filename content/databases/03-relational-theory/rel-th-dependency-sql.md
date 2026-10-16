---
id: rel-th-dependency-sql
title: Dependencies in PostgreSQL queries
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Dependencies in PostgreSQL queries, with explicit examples and the conditions that make the reasoning valid.
---

## Where FDs show up in real systems

- **Keys and UNIQUE constraints** directly enforce key-based dependencies. SQL has no general FUNCTIONAL DEPENDENCY declaration for an arbitrary dependency between two sets of columns; some special dependencies can be enforced with CHECK or exclusion constraints, and others need triggers or schema decomposition. Normalisation avoids storing the same dependent fact in many rows.
- **Postgres uses FDs in GROUP BY.** If you group by a table's primary key, PostgreSQL 16–18 lets you select that table's other columns without listing them, because it knows the key determines them:

```sql
SELECT c.id, c.name, COUNT(*)
FROM customer c
JOIN orders o ON o.customer_id = c.id
-- Grouping the PK fixes the name.
GROUP BY c.id;
```

- **Optimisers use FDs** to drop redundant grouping or sorting columns and to prove that a join cannot multiply rows.
- **Data-quality checks** test candidate FDs against stored rows. With both `cid` and `ctitle` constrained `NOT NULL`, grouping by course code and requiring more than one distinct title finds violations. `COUNT(DISTINCT ...)` ignores NULLs; do not silently treat its result as an FD proof when missing titles are allowed.

```sql
-- Find codes with conflicting titles.
SELECT cid FROM sheet
GROUP BY cid
HAVING COUNT(DISTINCT ctitle) > 1;
```

## Common mistakes

- **Reading FDs off sample data.** A coincidence in 50 rows is not a rule.
- **Splitting the left side.** Two attributes determining a third together does not imply that either one does alone.
- **Forgetting transitivity.** When asked for keys, compute the attribute closure; do not eyeball it. Chains through two FDs are easy to miss.
- **Stopping at one key.** A relation can have several candidate keys, and normal-form tests depend on all of them.

```formula
XY → Z ⇏ X → Z
D → A and AB → C gives BD → C
where
X, Y, Z: sets of attributes
XY: X ∪ Y, the two sets combined
∪: union
→: functionally determines
⇏: does not imply
A, B, C, D: single attributes
AB, BD: the sets {A, B} and {B, D}
In words: the first line is the left-side mistake; the second is an easily missed chain: D gives A, and then A with B gives C.
```

## Key takeaways

- PostgreSQL recognises its base-table primary-key grouping rule, not every logically inferable FD.
- Distinct-value checks can refute an FD when missing values are handled explicitly.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
