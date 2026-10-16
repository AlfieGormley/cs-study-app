---
id: rel-th-restrict-project-rename
title: Restrict, project and rename
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Restrict, project and rename, with explicit examples and the conditions that make the reasoning valid.
---

Relational algebra is a small set of operators that each take one or two relations and return a new relation. That last part is the whole trick: because the output is always a relation, you can feed it into another operator, and build any query expressible in ordinary relational algebra by **composing** a few simple pieces.

You never type relational algebra into Postgres. But the database translates your SQL into a tree of algebra-like operators, transforms that tree into a cheaper equivalent, and then executes it. An `EXPLAIN` plan shows physical implementations of algebra-like operations, along with SQL extensions such as sorting and aggregation.

Each operator has a one-character symbol, mostly Greek letters. Every symbol is explained in the formula card where it first appears, and again in each card that uses it, so you can read any card on its own.

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

## Unary operators: selection, projection and rename

A unary operator takes one relation as input. There are three.

**Selection (σ)** keeps the relational tuples that satisfy a condition. It filters *rows*. It is written σ, the Greek letter sigma, followed by the condition and then the input relation in brackets:

```formula
σ year=2 (Student)
where
σ: selection (the Greek letter sigma): keep only the relational tuples for which the condition written straight after it is true
year: the attribute of Student holding the student's year of study, an integer from 1 to 4
Student: the relation of students, with attributes sid, name and year (four relational tuples in the running example)
In words: from Student, keep just the students who are in year 2.
```

```
sid name year
 1  Ada   2
 3  Cat   2
```

The result has the same attributes as the input; only rows have gone.

**Projection (π)** keeps only the named attributes. It chooses *columns*, and because the result is a set, duplicates disappear. It is written with the Greek letter π (pi), followed by the attributes to keep:

```formula
π cid (Enrolled) = {DB, OS, LA}
where
π: projection (the Greek letter pi; here it has nothing to do with the circle constant 3.14159): keep only the attributes listed straight after it, then remove any duplicate relational tuples
cid: the course-code attribute
Enrolled: the relation recording which student is enrolled on which course, with attributes sid and cid (six relational tuples in the running example)
{ }: a set: a collection of distinct values, with no order
DB, OS, LA: the three course codes in the running example
In words: list the course codes that appear in Enrolled, each once.
```

Six enrolments, but only three relational tuples in the result. SQL's `SELECT cid FROM enrolled` returns six rows; you need `SELECT DISTINCT cid` to match the algebra.

**Rename (ρ)** changes a relation's or an attribute's name. It is written with the Greek letter ρ (rho), in one of two forms:

```formula
ρ S (R)
ρ b←a (R)
where
ρ: rename (the Greek letter rho): give the input a new name without changing its relational tuples
R: the input relation
S: the new name for the whole relation, in the first form
a: an attribute's current name, in the second form
b: the new name for attribute a
←: "takes the place of": the name on the left replaces the name on the right
In words: the first form calls relation R by the new name S; the second keeps the relation but renames its attribute a to b.
```

For a self-join, make the two headings distinct before a Cartesian product. Here we use qualified names as shorthand for renaming every attribute in each copy: the first has `S1.sid`, `S1.name`, `S1.year`; the second has the corresponding `S2` names. Merely giving a relation a new label is insufficient in a strictly named-attribute algebra.

> [!note] Name clash: σ is not SELECT
> SQL's `SELECT` list is a **projection (π)**. The selection σ corresponds to `WHERE`. The names are a historical accident that confuses almost everyone once.

```formula
σ S1.year=S2.year ∧ S1.sid<S2.sid
  (ρ S1 (Student) × ρ S2 (Student))
where
Student: the four local student relational tuples
ρ: qualify every attribute with the following copy name
S1, S2: the two disjointly named copies
S1.year, S2.year: each copy’s study-year attribute
S1.sid, S2.sid: each copy’s student-id attribute
σ: keep only relational tuples satisfying the predicate
∧: both conditions must hold
<: less than
×: Cartesian product, every pair of students
In words: There are sixteen pairs before filtering. Equal years leave six pairs; increasing student id removes self-pairs and reverse copies, leaving Ada with Cat once.
```

## Key takeaways

- Selection keeps rows; projection keeps attributes and removes duplicate relational tuples.
- Give self-join copies distinct attribute names before forming a product.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
