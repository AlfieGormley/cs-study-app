---
id: rel-th-products-and-joins
title: Products and joins
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Products pair everything; joins keep matching pairs. Natural, outer, semi and anti joins and their SQL forms.
---

## Local relations

```
Student            Enrolled     Course
sid name year      sid cid      cid dept
 1  Ada   2         1  DB       DB  CS
 2  Ben   1         1  AI       AI  CS
 3  Cat   2         1  LA       LA  MA
 4  Dev   3         2  DB
                    3  DB
                    3  AI
```

Four students, three courses, six enrolments. Dev is not enrolled on anything. (Course also has a `title` column, left out here for width.) `sid` is the student id, `cid` the course code, and `dept` the department that runs the course.

## Product and joins

The **Cartesian product** pairs every relational tuple of one relation with every tuple of another, carrying the attributes of both. Its size is therefore the product of the two sizes: 4 students × 3 courses gives 12 pairs, whether or not anyone is enrolled. The attribute counts add instead: 3 + 3 = 6 attributes, which is why the two headings must not share names (rename first if they do).

On its own the product is rarely what you want; it is the raw material for joins.

A **theta join** is a product followed by a selection:

```formula reference
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

```formula reference
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
 1  Ada   2   AI
 1  Ada   2   LA
 2  Ben   1   DB
 3  Cat   2   DB
 3  Cat   2   AI
```

Dev vanishes: an inner join keeps only tuples with a partner. The extended algebra adds **outer joins**, which keep unmatched tuples padded with NULLs, plus the **semijoin** and **antijoin**, which optimisers use constantly:

```formula reference
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

In SQL terms:

- A **semijoin** ("rows of R that have a match") is `WHERE EXISTS`.
- An **antijoin** ("rows of R with no match") is `WHERE NOT EXISTS`.
- A **left outer join** ("all of R, padded where unmatched") is `LEFT JOIN`.

> [!analogy] Real-world analogy: laying out outfits
> Lay every shirt next to every pair of trousers and you have all possible outfits, most of them clashing. A sensible wardrobe rule, such as "the colours must match", keeps only some of those pairs.
>
> **How it maps:** Shirts and trousers are two relations; laying out every pairing is the Cartesian product; the colour rule is the join condition θ, so the surviving outfits are a theta join. A natural join is the special rule "match on every label the two items share".
>
> **Where it stops:** You can see a clash at a glance without laying out the whole wardrobe, and a database is also not required to build the full product: the product-then-filter description defines the result, while hash, merge or index joins usually avoid generating the rejected pairs.

> [!warning] Natural join is fragile
> Natural join matches on every shared column name. If someone later adds `updated_at` to both Student and Enrolled, `NATURAL JOIN` silently starts requiring equal timestamps and returns almost nothing. Production SQL should spell out `JOIN ... ON` or `USING (sid)`.

For a natural join, shared attribute names must have compatible domains. With no shared names, the matching condition is vacuously true, and the result is the Cartesian product: four students paired with three courses give twelve tuples. Adding a same-named column later changes a SQL `NATURAL JOIN` predicate, so explicit join conditions are safer in application SQL. The outer-join operators above belong to an extension with missing-value markers, rather than the null-free algebra.

## Key takeaways

- A product contains every pair; a theta join retains pairs satisfying its predicate.
- Natural joins match all shared names; outer joins preserve unmatched rows with missing-value markers.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: joined tables](https://www.postgresql.org/docs/18/queries-table-expressions.html)
