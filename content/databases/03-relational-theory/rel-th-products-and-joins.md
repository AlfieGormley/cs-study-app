---
id: rel-th-products-and-joins
title: Products and joins
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Products and joins, with explicit examples and the conditions that make the reasoning valid.
---

## Local relations

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

Four students, three courses, six enrolments. Dev is not enrolled on anything. (Course also has a `title` column, left out here for width.) `sid` is the student id, `cid` the course code, and `dept` the department that runs the course.

## Product and joins

The **Cartesian product** pairs every relational tuple of one relation with every relational tuple of another, so its size is the product of the two sizes:

```formula
|R × S| = |R| × |S|
|Student × Course| = 4 × 3 = 12
where
R, S: two relations with disjoint attribute names, renaming first if necessary
× (between relations): the Cartesian product: one output relational tuple for every pairing of a relational tuple of R with a relational tuple of S, carrying the attributes of both
× (between numbers): ordinary multiplication
| |: the cardinality of the relation inside the bars: its number of relational tuples
Student: the relation of students, 4 relational tuples
Course: the relation of courses, 3 relational tuples
In words: pairing 4 students with 3 courses in every possible way gives 12 relational tuples.
```

On its own the product is rarely what you want; it is the raw material for joins.

A **theta join** is a product followed by a selection:

```formula
R ⋈θ S ≡ σθ (R × S)
where
R, S: two relations with disjoint attribute names, renaming first if necessary
⋈: join (the "bow-tie" symbol): combine relational tuples of R and S that satisfy a condition
θ: theta, the join condition written under or after the bow-tie, such as R.a = S.b or R.a < S.b
σ: selection: keep only the relational tuples for which a condition is true
×: the Cartesian product: every relational tuple of R paired with every relational tuple of S
≡: is equivalent to: always gives exactly the same result
In words: a theta join is "pair everything, then keep the pairs that satisfy θ". This defines the result, not a required execution algorithm. A database can avoid enumerating rejected pairs with an index or hash join; a cross join or some nested-loop plans can still enumerate every pair.
```

When θ uses only equality it is an **equijoin**. A **natural join**, written with a bare bow-tie and no condition, is the equijoin on *all* attributes with the same name, keeping one copy of each:

```formula
Student ⋈ Enrolled
where
⋈: natural join (a bow-tie with no condition): pair the relational tuples that have equal values on every attribute name the two relations share, and keep one copy of each shared attribute
Student: the relation (sid, name, year)
Enrolled: the relation (sid, cid); the only shared attribute name is sid
In words: attach to each student the courses they are enrolled on, matching on sid.
```

```
sid name year cid
 1  Ada   2   DB
 1  Ada   2   OS
 1  Ada   2   LA
 2  Ben   1   DB
 3  Cat   2   DB
 3  Cat   2   OS
```

Dev vanishes: an inner join keeps only relational tuples with a partner. The extended algebra adds **outer joins**, which keep unmatched relational tuples padded with NULLs, plus the **semijoin** and **antijoin**, which optimisers use constantly:

```formula
R ⟕ S
R ⟖ S
R ⟗ S
R ⋉ S
R ▷ S
where
R, S: two relations with compatible shared domains; these bare symbols use natural matching on shared attribute names
⟕: left outer join: the join, plus every relational tuple of R with no partner, padded with NULL for S's attributes
⟖: right outer join: the same, keeping unmatched relational tuples of S instead
⟗: full outer join: keeps unmatched relational tuples from both sides
⋉: semijoin: the relational tuples of R that have at least one match in S, with R's attributes only
▷: antijoin: the relational tuples of R that have no match in S
In words: outer joins keep the rows a join would drop; semijoin asks "does a match exist?" and antijoin asks "is there no match?".
```

- **Semijoin** R ⋉ S is SQL's `WHERE EXISTS`.
- **Antijoin** R ▷ S is SQL's `WHERE NOT EXISTS`.
- **Left outer join** R ⟕ S is SQL's `LEFT JOIN`.

> [!warning] Natural join is fragile
> Natural join matches on every shared column name. If someone later adds `updated_at` to both Student and Enrolled, `NATURAL JOIN` silently starts requiring equal timestamps and returns almost nothing. Production SQL should spell out `JOIN ... ON` or `USING (sid)`.

For a natural join, shared attribute names must have compatible domains. With no shared names, the matching condition is vacuously true, and the result is the Cartesian product: four students paired with three courses give twelve relational tuples. Adding a same-named column later changes a SQL `NATURAL JOIN` predicate, so explicit join conditions are safer in application SQL. The outer-join operators above belong to an extension with missing-value markers, rather than the null-free algebra.

## Key takeaways

- A product contains every pair; a theta join retains pairs satisfying its predicate.
- Natural joins match all shared names; outer joins preserve unmatched rows with missing-value markers.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
