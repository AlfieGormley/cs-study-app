---
id: rel-th-algebra-limits
title: Where pure algebra stops
level: basic
minutes: 3
sourceLesson: rel-th-algebra
summary: Where pure algebra stops, with explicit examples and the conditions that make the reasoning valid.
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

## Pitfalls and limits

- **Bags versus sets.** SQL works on bags, so some algebraic equivalences need care. For sets, a relation unioned with itself is unchanged; in SQL, `R UNION ALL R` has twice as many rows. An optimiser may only apply a rewrite if it holds under bag semantics, or if a `DISTINCT` makes the difference invisible.
- **NULL.** The pure algebra has no NULL. SQL's three-valued logic means "the rows where p is true" plus "the rows where p is false" does not always give back the whole table: rows where p is *unknown* appear in neither.
- **Aggregation is an extension.** Grouping (written with the Greek letter γ, gamma) is not part of Codd's original algebra; textbooks add it as an extended operator.
- **No recursion.** A fixed finite expression in ordinary relational algebra cannot compute reachability for arbitrary graph size or unbounded depth. A known fixed depth can be expanded into a fixed number of joins; `WITH RECURSIVE` handles the unbounded case.

```formula
R ∪ R ≡ R
σ p (R) ∪ σ ¬p (R) ≡ R
γ year, COUNT(sid) (Student)
where
R: any relation
∪: union: relational tuples in either input, each listed once in pure algebra
≡: is equivalent to: always gives the same result. Both of the first two lines hold in pure algebra. In SQL the first fails under bag semantics (R UNION ALL R doubles the rows), and the second fails when p is unknown for some row because of a NULL
σ: selection: keep relational tuples where the condition is true
p: a condition, such as discount > 0.1
¬: not: ¬p is true exactly when p is false. In SQL, when p is unknown (because of a NULL), ¬p is unknown too
γ: grouping and aggregation (the Greek letter gamma): group by the attributes listed first, then compute the aggregates listed after them
year: the grouping attribute
COUNT: the aggregate that counts the values in each group
sid: the student-id attribute being counted
Student: the relation of students
In words: in pure algebra, a union with itself changes nothing and "p or not p" covers every relational tuple; the last line counts students per year, giving (1, 1), (2, 2) and (3, 1) for the running example.
```

## Key takeaways

- Bag multiplicities and NULL can invalidate pure-set identities.
- Aggregation extends the algebra; unbounded reachability needs recursion.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
