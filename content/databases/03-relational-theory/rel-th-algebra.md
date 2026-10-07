---
id: rel-th-algebra
title: Relational algebra
level: basic
minutes: 13
summary: Selection, projection, joins, set operators and division as operators on relations, how SQL maps onto them, and why algebraic rewrites are the basis of every query optimiser.
---

Relational algebra is a small set of operators that each take one or two relations and return a new relation. That last part is the whole trick: because the output is always a relation, you can feed it into another operator, and build any query by **composing** a few simple pieces.

You never type relational algebra into Postgres. But the database translates your SQL into a tree of algebra-like operators, rewrites that tree into a cheaper equivalent, and then executes it. Read an `EXPLAIN` plan and you are reading relational algebra.

## The running example

```
Student            Enrolled     Course
sid name year      sid cid      cid dept
 1  Ada   2         1  DB       DB  CS
 2  Ben   1         1  OS       OS  CS
 3  Cat   2         1  LA       LA  MA
 4  Dev   3         2  DB
                    3  DB
                    3  OS
```

Four students, three courses, six enrolments. Dev is not enrolled on anything. (Course also has a `title` column, left out here for width.)

## Unary operators: σ, π, ρ

**Selection** σ keeps the tuples that satisfy a condition. It filters *rows*.

```
σ year=2 (Student)

sid name year
 1  Ada   2
 3  Cat   2
```

**Projection** π keeps only the named attributes. It chooses *columns*, and because the result is a set, duplicates disappear.

```
π cid (Enrolled)  ->  { DB, OS, LA }
```

Six enrolments, but only three tuples in the result. SQL's `SELECT cid FROM enrolled` returns six rows; you need `SELECT DISTINCT cid` to match the algebra.

**Rename** ρ changes a relation's or attribute's name, written ρ S(R) or ρ newname←oldname (R). It matters when you join a relation with itself, so the two copies can be told apart.

> [!note] Name clash: σ is not SELECT
> SQL's `SELECT` list is a **projection**. The selection σ corresponds to `WHERE`. The names are a historical accident that confuses almost everyone once.

## Set operators: ∪, −, ∩

Union, difference and intersection work as they do on any sets, with one rule: the two inputs must be **union-compatible**, meaning the same attributes with the same domains.

Students who are not enrolled on anything:

```
π sid (Student) − π sid (Enrolled)

{1,2,3,4} − {1,2,3}  =  {4}
```

Students taking both DB and OS:

```
π sid (σ cid='DB' (Enrolled))
  ∩ π sid (σ cid='OS' (Enrolled))

{1,2,3} ∩ {1,3}  =  {1,3}
```

In SQL these are `UNION`, `EXCEPT` and `INTERSECT`, which remove duplicates by default; `UNION ALL` and friends keep them (bag semantics).

## Product and joins

The **Cartesian product** R × S pairs every tuple of R with every tuple of S. Student × Course has 4 × 3 = 12 tuples. On its own it is rarely what you want; it is the raw material for joins.

A **theta join** R ⋈θ S is a product followed by a selection:

```
R ⋈θ S  ≡  σθ (R × S)
```

When θ uses only equality it is an **equijoin**. A **natural join** R ⋈ S is the equijoin on *all* attributes with the same name, keeping one copy of each.

```
Student ⋈ Enrolled   (joins on sid)

sid name year cid
 1  Ada   2   DB
 1  Ada   2   OS
 1  Ada   2   LA
 2  Ben   1   DB
 3  Cat   2   DB
 3  Cat   2   OS
```

Dev vanishes: an inner join keeps only tuples with a partner. The extended algebra adds **outer joins** (⟕, ⟖, ⟗) that keep unmatched tuples padded with NULLs, plus two that optimisers use constantly:

- **Semijoin** R ⋉ S: tuples of R that have at least one match in S. This is `WHERE EXISTS`.
- **Antijoin** R ▷ S: tuples of R that have no match. This is `WHERE NOT EXISTS`.

> [!warning] Natural join is fragile
> Natural join matches on every shared column name. If someone later adds `updated_at` to both Student and Enrolled, `NATURAL JOIN` silently starts requiring equal timestamps and returns almost nothing. Production SQL should spell out `JOIN ... ON` or `USING (sid)`.

## The minimal set and what is derived

Six operators are enough to express everything else: **σ, π, ρ, ∪, −, ×**. The rest are shorthand:

| Operator | Defined as |
|---|---|
| R ⋈θ S | σθ(R × S) |
| R ∩ S | R − (R − S) |
| R ⋉ S | π attrs(R) (R ⋈ S) |
| R ÷ S | see below |

A query language that can express everything these operators can is called **relationally complete**. SQL is (and more, since it adds aggregation, ordering and recursion).

## Division: "for all"

Division answers questions with *every* in them: which students take **all** CS courses?

```
Enrolled ÷ π cid (σ dept='CS' (Course))
```

The divisor is `{DB, OS}`. A student qualifies if, for every course in the divisor, the pair (student, course) appears in Enrolled. Ada (1) and Cat (3) take both; Ben takes only DB. Result: `{1, 3}`.

Division is derived from the basic operators, which shows how "for all" becomes "there is no counterexample":

```
A = π sid (Enrolled)
B = π cid (σ dept='CS' (Course))

all pairs that should exist: A × B
missing pairs:  (A × B) − Enrolled
students with a missing pair:
                π sid ((A × B) − Enrolled)
answer:         A − that
```

SQL has no division operator. The standard idiom is a double `NOT EXISTS`: there is no CS course that the student is not enrolled on.

```sql
SELECT s.sid FROM student s
WHERE NOT EXISTS (
  SELECT 1 FROM course c
  WHERE c.dept = 'CS'
    AND NOT EXISTS (
      SELECT 1 FROM enrolled e
      WHERE e.sid = s.sid
        AND e.cid = c.cid));
```

> [!example] The empty divisor
> If the CS department had no courses, the inner condition is vacuously true, and the SQL above returns **every** student, including Dev. The algebraic version returns only students in `π sid (Enrolled)`. Both are logically defensible ("all of nothing" is true), but they differ. Decide which you mean before shipping a "customers who bought every item in the promotion" report.

## From SQL to an expression tree

A simple SQL block maps onto algebra almost mechanically:

```sql
SELECT DISTINCT s.name
FROM student s JOIN enrolled e
  ON s.sid = e.sid
WHERE e.cid = 'DB';
```

```
π name
  |
σ cid='DB'
  |
  ⋈ sid
 / \
S   E
```

Read bottom-up: join, filter, project. The result is `{Ada, Ben, Cat}`.

## Equivalences: why optimisers work

Because operators have precise meanings, there are rules that transform one expression into another that is guaranteed to give the same result. A few of the most important:

1. **Cascade selections**: σ p∧q (R) ≡ σ p (σ q (R)).
2. **Commute joins**: R ⋈ S ≡ S ⋈ R, and joins are associative, so join order is free to choose.
3. **Push selection below a join**: if p mentions only R's attributes, σ p (R ⋈ S) ≡ σ p (R) ⋈ S.
4. **Push projection down**: drop columns early, keeping any needed by later joins or filters.

Rule 3 is the big one. Take the tree above with 10,000 students and 200,000 enrolments, 1,000 of them for DB:

```
naive:   join 10k with 200k
         -> 200k rows, then filter -> 1k
pushed:  filter E first -> 1k rows
         join 10k with 1k -> 1k rows
```

The pushed plan feeds 1,000 enrolments into the join instead of 200,000. Every cost-based optimiser (Postgres, SQL Server, Oracle, the Spark SQL Catalyst optimiser) applies these rewrites, then uses statistics to choose among the equivalent trees. The query processing module covers how it picks.

## Pitfalls and limits

- **Bags versus sets.** SQL works on bags, so some algebraic equivalences need care. For sets, R ∪ R ≡ R; in SQL, `R UNION ALL R` has twice as many rows. An optimiser may only apply a rewrite if it holds under bag semantics, or if a `DISTINCT` makes the difference invisible.
- **NULL.** The pure algebra has no NULL. SQL's three-valued logic means σ p (R) ∪ σ NOT p (R) does not always give back R: rows where p is *unknown* appear in neither.
- **Aggregation is an extension.** Grouping (written γ) is not part of Codd's original algebra; textbooks add it as an extended operator.
- **No recursion.** Plain relational algebra cannot compute transitive closure (all ancestors in a parent table) for arbitrary depth. SQL added `WITH RECURSIVE` for that.

## Key takeaways
- Every operator takes relations and returns a relation, so queries are built by composition.
- σ filters rows (`WHERE`), π picks columns and removes duplicates (`SELECT DISTINCT`), ρ renames, and ∪, −, ∩ need union-compatible inputs.
- Joins are products followed by selections; semijoin and antijoin are `EXISTS` and `NOT EXISTS`.
- σ, π, ρ, ∪, −, × form a complete basis; ∩, ⋈ and ÷ are derived. Division expresses "for all", which SQL writes as a double `NOT EXISTS`.
- Algebraic equivalences such as pushing selections below joins are what let optimisers turn your SQL into a fast plan.

## Further reading
- [Relational algebra — Wikipedia](https://en.wikipedia.org/wiki/Relational_algebra)
- [Join (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Join_(SQL))
- [Combining queries (UNION, INTERSECT, EXCEPT) — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-union.html)
- [Relational calculus — Wikipedia](https://en.wikipedia.org/wiki/Relational_calculus)
- [Query optimization — Wikipedia](https://en.wikipedia.org/wiki/Query_optimization)
