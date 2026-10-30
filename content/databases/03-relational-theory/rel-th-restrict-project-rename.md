---
id: rel-th-restrict-project-rename
title: Restrict, project and rename
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Selection keeps rows, projection keeps columns and removes duplicates, and rename makes self-joins possible.
---

Relational algebra is a small set of operators that each take one or two relations and return a new relation. That last part is the whole trick: because the output is always a relation, you can feed it into another operator, and build any query expressible in ordinary relational algebra by **composing** a few simple pieces.

You never type relational algebra into Postgres. But the database translates your SQL into a tree of algebra-like operators, transforms that tree into a cheaper equivalent, and then executes it. An `EXPLAIN` plan shows physical implementations of algebra-like operations, along with SQL extensions such as sorting and aggregation.

Each operator has a one-character symbol, mostly Greek letters. Every symbol is explained in the formula card where it first appears, and again in each card that uses it, so you can read any card on its own.

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

## Unary operators: selection, projection and rename

A unary operator takes one relation as input. There are three.

**Selection (σ)** keeps the relational tuples that satisfy a condition. It filters *rows*. It is written σ, the Greek letter sigma, followed by the condition and then the input relation in brackets:

```formula essential
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

```formula essential
π cid (Enrolled) = {DB, AI, LA}
where
π: projection (the Greek letter pi; here it has nothing to do with the circle constant 3.14159): keep only the attributes listed straight after it, then remove any duplicate relational tuples
cid: the course-code attribute
Enrolled: the relation recording which student is enrolled on which course, with attributes sid and cid (six relational tuples in the running example)
{ }: a set: a collection of distinct values, with no order
DB, AI, LA: the three course codes in the running example
In words: list the course codes that appear in Enrolled, each once.
```

Six enrolments, but only three tuples in the result. SQL's `SELECT cid FROM enrolled` returns six rows; you need `SELECT DISTINCT cid` to match the algebra.

**Rename (ρ)** changes a relation's or an attribute's name. It is written with the Greek letter ρ (rho), in one of two forms:

```formula reference
ρ S (R)
ρ b←a (R)
where
ρ: rename (the Greek letter rho): give the input a new name without changing its relational tuples
R: the input relation
S: the new name for the whole relation, in the first form
a: an attribute's current name, in the second form
b: the new name for attribute a
←: "takes the place of": the name on the left replaces the name on the right
In words: rename either gives a whole relation a new name or gives one of its attributes a new name; the relational tuples themselves never change.
```

Rename matters most for a **self-join**, where a relation is combined with a copy of itself. In a named-attribute algebra the two copies must have different attribute names, otherwise the result would contain two attributes called `year`. Renaming every attribute of each copy (written here as `S1.year`, `S2.year` and so on) makes the headings distinct. Giving the relation alone a new label is not enough.

> [!note] Name clash: σ is not SELECT
> SQL's `SELECT` list is a **projection (π)**. The selection σ corresponds to `WHERE`. The names are a historical accident that confuses almost everyone once.

### A self-join in words

"Which pairs of students are in the same year?" pairs two renamed copies of Student, keeps pairs whose years are equal, and also requires the first student id to be smaller than the second. That last condition removes each student paired with themselves and the mirror-image copy of each pair.

On the local data, the 4 × 4 = 16 possible pairs shrink to 6 with equal years (four self-pairs, plus Ada–Cat and Cat–Ada), and the id condition leaves just one: Ada with Cat. The SQL form is the familiar self-join:

```sql
SELECT s1.name, s2.name
FROM student s1
JOIN student s2
  ON s1.year = s2.year
 AND s1.sid < s2.sid;
-- one row: Ada | Cat
```

## Key takeaways

- Selection keeps rows; projection keeps attributes and removes duplicate relational tuples.
- Give self-join copies distinct attribute names before forming a product.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [Relational algebra (Wikipedia)](https://en.wikipedia.org/wiki/Relational_algebra)
