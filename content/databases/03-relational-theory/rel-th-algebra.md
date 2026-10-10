---
id: rel-th-algebra
title: Relational algebra
level: basic
minutes: 18
summary: Selection, projection, joins, set operators and division as operators on relations, how SQL maps onto them, and why algebraic rewrites are the basis of every query optimiser.
---

Relational algebra is a small set of operators that each take one or two relations and return a new relation. That last part is the whole trick: because the output is always a relation, you can feed it into another operator, and build any query by **composing** a few simple pieces.

You never type relational algebra into Postgres. But the database translates your SQL into a tree of algebra-like operators, transforms that tree into a cheaper equivalent, and then executes it. Read an `EXPLAIN` plan and you are reading relational algebra.

Each operator has a one-character symbol, mostly Greek letters. Every symbol is explained in the formula card where it first appears, and again in each card that uses it, so you can read any card on its own.

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

Four students, three courses, six enrolments. Dev is not enrolled on anything. (Course also has a `title` column, left out here for width.) `sid` is the student id, `cid` the course code, and `dept` the department that runs the course.

## Unary operators: selection, projection and rename

A unary operator takes one relation as input. There are three.

**Selection (σ)** keeps the tuples that satisfy a condition. It filters *rows*. It is written σ, the Greek letter sigma, followed by the condition and then the input relation in brackets:

```formula
σ year=2 (Student)
where
σ: selection (the Greek letter sigma): keep only the tuples for which the condition written straight after it is true
year: the attribute of Student holding the student's year of study, an integer from 1 to 4
Student: the relation of students, with attributes sid, name and year (four tuples in the running example)
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
π: projection (the Greek letter pi; here it has nothing to do with the circle constant 3.14159): keep only the attributes listed straight after it, then remove any duplicate tuples
cid: the course-code attribute
Enrolled: the relation recording which student is enrolled on which course, with attributes sid and cid (six tuples in the running example)
{ }: a set: a collection of distinct values, with no order
DB, OS, LA: the three course codes in the running example
In words: list the course codes that appear in Enrolled, each once.
```

Six enrolments, but only three tuples in the result. SQL's `SELECT cid FROM enrolled` returns six rows; you need `SELECT DISTINCT cid` to match the algebra.

**Rename (ρ)** changes a relation's or an attribute's name. It is written with the Greek letter ρ (rho), in one of two forms:

```formula
ρ S (R)
ρ b←a (R)
where
ρ: rename (the Greek letter rho): give the input a new name without changing its tuples
R: the input relation
S: the new name for the whole relation, in the first form
a: an attribute's current name, in the second form
b: the new name for attribute a
←: "takes the place of": the name on the left replaces the name on the right
In words: the first form calls relation R by the new name S; the second keeps the relation but renames its attribute a to b.
```

Rename matters when you join a relation with itself, so the two copies can be told apart: ρ S1 (Student) and ρ S2 (Student) give two copies whose attributes are S1.year, S2.year and so on.

> [!note] Name clash: σ is not SELECT
> SQL's `SELECT` list is a **projection (π)**. The selection σ corresponds to `WHERE`. The names are a historical accident that confuses almost everyone once.

## Set operators: union, difference, intersection

Union, difference and intersection work as they do on any sets, with one rule: the two inputs must be **union-compatible**, meaning the same attributes with the same domains.

```formula
R ∪ S
R − S
R ∩ S
where
R, S: two union-compatible relations (same attribute names, same domains)
∪: union: every tuple that is in R, in S, or in both, listed once
−: difference: the tuples of R that are not in S. Order matters: R − S is not the same as S − R
∩: intersection: the tuples that are in both R and S
In words: union combines two relations, difference removes one from the other, and intersection keeps what they share.
```

Students who are not enrolled on anything:

```formula
π sid (Student) − π sid (Enrolled)
{1, 2, 3, 4} − {1, 2, 3} = {4}
where
π: projection: keep only the listed attribute, removing duplicates
sid: the student-id attribute, present in both Student and Enrolled
Student: the relation of students (sid, name, year)
Enrolled: the relation of enrolments (sid, cid)
−: difference: the values on the left that are not on the right
{ }: a set of distinct values
In words: take every student id, remove the ids that appear in Enrolled, and only Dev (id 4) is left.
```

Students taking both DB and OS:

```formula
π sid (σ cid='DB' (Enrolled))
  ∩ π sid (σ cid='OS' (Enrolled))
{1, 2, 3} ∩ {1, 3} = {1, 3}
where
σ: selection: keep the tuples where the condition is true; here cid='DB' keeps enrolments on the course with code DB (quoted values are literal text)
π: projection: keep only the listed attribute, removing duplicates
sid: the student-id attribute
cid: the course-code attribute
Enrolled: the relation of enrolments (sid, cid)
∩: intersection: the values that appear on both sides
{ }: a set of distinct values
In words: the students on DB are 1, 2 and 3; those on OS are 1 and 3; the students on both are 1 and 3 (Ada and Cat).
```

In SQL these are `UNION`, `EXCEPT` and `INTERSECT`, which remove duplicates by default; `UNION ALL` and friends keep them (bag semantics).

## Product and joins

The **Cartesian product** pairs every tuple of one relation with every tuple of another, so its size is the product of the two sizes:

```formula
|R × S| = |R| × |S|
|Student × Course| = 4 × 3 = 12
where
R, S: any two relations
× (between relations): the Cartesian product: one output tuple for every pairing of a tuple of R with a tuple of S, carrying the attributes of both
× (between numbers): ordinary multiplication
| |: the cardinality of the relation inside the bars: its number of tuples
Student: the relation of students, 4 tuples
Course: the relation of courses, 3 tuples
In words: pairing 4 students with 3 courses in every possible way gives 12 tuples.
```

On its own the product is rarely what you want; it is the raw material for joins.

A **theta join** is a product followed by a selection:

```formula
R ⋈θ S ≡ σθ (R × S)
where
R, S: any two relations
⋈: join (the "bow-tie" symbol): combine tuples of R and S that satisfy a condition
θ: theta, the join condition written under or after the bow-tie, such as R.a = S.b or R.a < S.b
σ: selection: keep only the tuples for which a condition is true
×: the Cartesian product: every tuple of R paired with every tuple of S
≡: is equivalent to: always gives exactly the same result
In words: a theta join is "pair everything, then keep the pairs that satisfy θ". Databases never actually build the full product; this is a definition, not an algorithm.
```

When θ uses only equality it is an **equijoin**. A **natural join**, written with a bare bow-tie and no condition, is the equijoin on *all* attributes with the same name, keeping one copy of each:

```formula
Student ⋈ Enrolled
where
⋈: natural join (a bow-tie with no condition): pair the tuples that have equal values on every attribute name the two relations share, and keep one copy of each shared attribute
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

Dev vanishes: an inner join keeps only tuples with a partner. The extended algebra adds **outer joins**, which keep unmatched tuples padded with NULLs, plus the **semijoin** and **antijoin**, which optimisers use constantly:

```formula
R ⟕ S
R ⟖ S
R ⟗ S
R ⋉ S
R ▷ S
where
R, S: any two relations
⟕: left outer join: the join, plus every tuple of R with no partner, padded with NULL for S's attributes
⟖: right outer join: the same, keeping unmatched tuples of S instead
⟗: full outer join: keeps unmatched tuples from both sides
⋉: semijoin: the tuples of R that have at least one match in S, with R's attributes only
▷: antijoin: the tuples of R that have no match in S
In words: outer joins keep the rows a join would drop; semijoin asks "does a match exist?" and antijoin asks "is there no match?".
```

- **Semijoin** R ⋉ S is SQL's `WHERE EXISTS`.
- **Antijoin** R ▷ S is SQL's `WHERE NOT EXISTS`.
- **Left outer join** R ⟕ S is SQL's `LEFT JOIN`.

> [!warning] Natural join is fragile
> Natural join matches on every shared column name. If someone later adds `updated_at` to both Student and Enrolled, `NATURAL JOIN` silently starts requiring equal timestamps and returns almost nothing. Production SQL should spell out `JOIN ... ON` or `USING (sid)`.

## The minimal set and what is derived

Six operators are enough to express everything else: selection σ, projection π, rename ρ, union ∪, difference − and Cartesian product ×. The rest are shorthand:

```formula
R ⋈θ S = σθ (R × S)
R ∩ S = R − (R − S)
R ⋉ S = π A_R (R ⋈ S)
where
R, S: any two relations (union-compatible for the ∩ line)
⋈θ: theta join with condition θ; a bare ⋈ is the natural join
θ: theta, the join condition
σ: selection: keep tuples where a condition holds
×: Cartesian product: every pairing of a tuple of R with a tuple of S
∩: intersection: tuples in both R and S
−: difference: tuples in the left input but not the right
⋉: semijoin: the tuples of R with at least one match in S
π: projection: keep only the listed attributes
A_R: the list of R's attributes
In words: a join is a product then a selection; the intersection is "R minus the part of R that is not in S"; a semijoin is a join cut back to R's columns.
```

Check the intersection rule on small sets of numbers:

```formula
R = {1, 2, 3} and S = {2, 3, 4}
R − S = {1}
R − (R − S) = {2, 3} = R ∩ S
where
R, S: two small example sets
{ }: a set of distinct values
−: difference: what is in the left set but not the right
∩: intersection: what is in both
In words: removing from R the part that is not in S leaves exactly what R and S share.
```

Division (÷) is derived too, below.

A query language that can express everything these six operators can is called **relationally complete**. SQL is (and more, since it adds aggregation, ordering and recursion).

## Division: "for all"

Division answers questions with *every* in them: which students take **all** CS courses?

```formula
Enrolled ÷ π cid (σ dept='CS' (Course))
  = {1, 3}
where
÷: division: the values of the left relation's remaining attributes (here sid) that are paired, in the left relation, with every tuple of the right relation
Enrolled: the relation of enrolments (sid, cid)
π: projection: keep only the listed attribute, removing duplicates
cid: the course-code attribute
σ: selection: keep tuples where the condition holds; dept='CS' keeps courses run by the CS department
dept: the attribute of Course naming the department
Course: the relation of courses (cid, title, dept)
{ }: a set of distinct values
In words: the divisor relation is the set of CS courses, {DB, OS}; the result is every student id enrolled on all of them.
```

A student qualifies if, for every course in the divisor relation, the pair (student, course) appears in Enrolled. Ada (1) and Cat (3) take both; Ben takes only DB. Result: `{1, 3}`.

Division is derived from the basic operators, which shows how "for all" becomes "there is no counterexample":

```formula
A = π sid (Enrolled) = {1, 2, 3}
B = π cid (σ dept='CS' (Course))
B = {DB, OS}
M = (A × B) − Enrolled = {(2, OS)}
Enrolled ÷ B = A − π sid (M)
Enrolled ÷ B = {1, 2, 3} − {2} = {1, 3}
where
A: every student id that has at least one enrolment (the candidates)
B: the divisor relation: the CS course codes
M: the missing pairs: every (student, CS course) pair that should exist if everyone took everything, minus the pairs that do exist
π: projection: keep only the listed attribute, removing duplicates
σ: selection: keep tuples where the condition holds
×: Cartesian product: every pairing of a value of A with a value of B
−: difference: what is on the left but not on the right
÷: division, as defined above
sid, cid, dept: the student-id, course-code and department attributes
DB, OS: the codes of the two CS courses
Enrolled, Course: the relations of the running example
{ }: a set; (2, OS) is one pair, a tuple of student 2 and course OS
In words: list every pair that "taking all CS courses" would need, find the pairs that are missing, and remove any student with a missing pair. Ben (2) is missing OS, so only Ada and Cat remain.
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

> [!example] The empty divisor relation
> If the CS department had no courses, the inner condition is vacuously true, and the SQL above returns **every** student, including Dev. The algebraic version returns only the students in A, those with at least one enrolment. Both are logically defensible ("all of nothing" is true), but they differ. Decide which you intend before shipping a "customers who bought every item in the promotional bundle" report.

## From SQL to an expression tree

A simple SQL block maps onto algebra almost mechanically:

```sql
SELECT DISTINCT s.name
FROM student s JOIN enrolled e
  ON s.sid = e.sid
WHERE e.cid = 'DB';
```

Written as one algebra expression, read from the inside out:

```formula
π name (σ cid='DB' (Student ⋈ Enrolled))
where
π: projection: keep only the listed attribute, removing duplicates (SQL's SELECT DISTINCT)
name: the student-name attribute
σ: selection: keep tuples where the condition holds (SQL's WHERE)
cid: the course-code attribute
⋈: natural join: pair tuples with equal values on the shared attribute, here sid (SQL's JOIN ... ON s.sid = e.sid)
Student, Enrolled: the relations of the running example
In words: join students to their enrolments, keep the DB enrolments, then list the distinct names.
```

The same expression as a tree, with S for Student and E for Enrolled:

```
π name
  |
σ cid='DB'
  |
  ⋈ sid
 / \
S   E
```

Read from the bottom up: join, filter, project. The result is `{Ada, Ben, Cat}`.

## Equivalences: why optimisers work

Because operators have precise meanings, there are rules that transform one expression into another that is guaranteed to give the same result. Four of the most important:

1. **Cascade selections**: a selection on two conditions joined by "and" is the same as two selections, one after the other.
2. **Commute joins**: the order of a join's inputs does not matter, and joins are associative, so join order is free to choose.
3. **Push selection below a join**: if a condition mentions only one input's attributes, filter that input before joining.
4. **Push projection down**: drop columns early, keeping any needed by later joins or filters.

```formula
σ p∧q (R) ≡ σ p (σ q (R))
R ⋈ S ≡ S ⋈ R
(R ⋈ S) ⋈ T ≡ R ⋈ (S ⋈ T)
σ p (R ⋈ S) ≡ σ p (R) ⋈ S
π L (R ⋈ S)
  ≡ π L (π L_R (R) ⋈ π L_S (S))
where
R, S, T: any relations
σ: selection: keep tuples where the condition holds
p, q: conditions on attributes. In the fourth line, p must mention only R's attributes
∧: and: both conditions must be true
⋈: natural join
≡: is equivalent to: gives exactly the same result for every possible contents of R, S and T
π: projection: keep only the listed attributes
L: the attributes the final result needs
L_R, L_S: the attributes of R (and of S) that are in L or are needed for the join
In words: line 1 is rule 1, lines 2 and 3 are rule 2, line 4 is rule 3 and the last line is rule 4.
```

Rule 3 is the big one. Take the tree above with 10,000 students and 200,000 enrolments, 1,000 of them for DB:

```
naive:   join 10k with 200k
         -> 200k rows, then filter -> 1k
pushed:  filter E first -> 1k rows
         join 10k with 1k -> 1k rows
```

The pushed plan feeds 1,000 enrolments into the join instead of 200,000. Every cost-based optimiser (Postgres, SQL Server, Oracle, the Spark SQL Catalyst optimiser) applies these algebraic rewrites, then uses statistics to choose among the equivalent trees. The query processing module covers how it picks.

## Pitfalls and limits

- **Bags versus sets.** SQL works on bags, so some algebraic equivalences need care. For sets, a relation unioned with itself is unchanged; in SQL, `R UNION ALL R` has twice as many rows. An optimiser may only apply a rewrite if it holds under bag semantics, or if a `DISTINCT` makes the difference invisible.
- **NULL.** The pure algebra has no NULL. SQL's three-valued logic means "the rows where p is true" plus "the rows where p is false" does not always give back the whole table: rows where p is *unknown* appear in neither.
- **Aggregation is an extension.** Grouping (written with the Greek letter γ, gamma) is not part of Codd's original algebra; textbooks add it as an extended operator.
- **No recursion.** Plain relational algebra cannot compute the transitive closure of a relation (all ancestors in a parent table) for arbitrary depth. SQL added `WITH RECURSIVE` for that.

```formula
R ∪ R ≡ R
σ p (R) ∪ σ ¬p (R) ≡ R
γ year, COUNT(sid) (Student)
where
R: any relation
∪: union: tuples in either input, each listed once in pure algebra
≡: is equivalent to: always gives the same result. Both of the first two lines hold in pure algebra. In SQL the first fails under bag semantics (R UNION ALL R doubles the rows), and the second fails when p is unknown for some row because of a NULL
σ: selection: keep tuples where the condition is true
p: a condition, such as discount > 0.1
¬: not: ¬p is true exactly when p is false. In SQL, when p is unknown (because of a NULL), ¬p is unknown too
γ: grouping and aggregation (the Greek letter gamma): group by the attributes listed first, then compute the aggregates listed after them
year: the grouping attribute
COUNT: the aggregate that counts the values in each group
sid: the student-id attribute being counted
Student: the relation of students
In words: in pure algebra, a union with itself changes nothing and "p or not p" covers every tuple; the last line counts students per year, giving (1, 1), (2, 2) and (3, 1) for the running example.
```

## Key takeaways
- Every operator takes relations and returns a relation, so queries are built by composition.
- Selection σ filters rows (`WHERE`), projection π picks columns and removes duplicates (`SELECT DISTINCT`), rename ρ renames, and union ∪, difference − and intersection ∩ need union-compatible inputs.
- Joins (⋈) are products followed by selections; semijoin and antijoin are `EXISTS` and `NOT EXISTS`.
- σ, π, ρ, ∪, −, × form a complete basis; intersection, join and division (÷) are derived. Division expresses "for all", which SQL writes as a double `NOT EXISTS`.
- Algebraic equivalences such as pushing selections below joins are what let optimisers turn your SQL into a fast plan.

## Further reading
- [Relational algebra — Wikipedia](https://en.wikipedia.org/wiki/Relational_algebra)
- [Join (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Join_(SQL))
- [Combining queries (UNION, INTERSECT, EXCEPT) — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-union.html)
- [Relational calculus — Wikipedia](https://en.wikipedia.org/wiki/Relational_calculus)
- [Query optimization — Wikipedia](https://en.wikipedia.org/wiki/Query_optimization)
