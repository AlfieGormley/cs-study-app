---
id: rel-th-set-operators
title: Set operators and an algebraic basis
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Set operators and an algebraic basis, with explicit examples and the conditions that make the reasoning valid.
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

## Set operators: union, difference, intersection

Union, difference and intersection work as they do on any sets, with one rule: the two inputs must be **union-compatible**, meaning the same attributes with the same domains.

```formula
R ∪ S
R − S
R ∩ S
where
R, S: two union-compatible relations (same attribute names, same domains)
∪: union: every relational tuple that is in R, in S, or in both, listed once
−: difference: the relational tuples of R that are not in S. Order matters: R − S is not the same as S − R
∩: intersection: the relational tuples that are in both R and S
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

Students taking both DB and course labelled OS:

```formula
π sid (σ cid='DB' (Enrolled))
  ∩ π sid (σ cid='OS' (Enrolled))
{1, 2, 3} ∩ {1, 3} = {1, 3}
where
σ: selection: keep the relational tuples where the condition is true; here cid='DB' keeps enrolments on the course with code DB (quoted values are literal text)
π: projection: keep only the listed attribute, removing duplicates
sid: the student-id attribute
cid: the course-code attribute
Enrolled: the relation of enrolments (sid, cid)
∩: intersection: the values that appear on both sides
{ }: a set of distinct values
In words: the students on DB are 1, 2 and 3; those on course labelled OS are 1 and 3; the students on both are 1 and 3 (Ada and Cat).
```

In SQL these are `UNION`, `EXCEPT` and `INTERSECT`, which remove duplicates by default; `UNION ALL` and friends keep them (bag semantics).

## The six primitive operators

Six operators are enough to express everything else: selection σ, projection π, rename ρ, union ∪, difference − and Cartesian product ×. The rest are shorthand:

```formula
R ⋈θ S = σθ (R × S)
R ∩ S = R − (R − S)
R ⋉ S = π A_R (R ⋈ S)
where
R, S: relations with disjoint headings for the theta-join line, union-compatible headings for the intersection line, and compatible shared domains for the natural semijoin line
⋈θ: theta join with condition θ; a bare ⋈ is the natural join
θ: theta, the join condition
σ: selection: keep relational tuples where a condition holds
×: Cartesian product: every pairing of a relational tuple of R with a relational tuple of S
∩: intersection: relational tuples in both R and S
−: difference: relational tuples in the left input but not the right
⋉: semijoin: the relational tuples of R with at least one match in S
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

Division is also derived; the neighbouring division unit works through its construction.

This is a conventional complete basis of six operators, rather than a claim that every presentation uses this exact primitive list. A language expressing all pure-algebra queries is **relationally complete**. SQL can express them using appropriate duplicate removal and null-free inputs, and adds ordering, aggregation and recursion.

## Key takeaways

- Union, difference and intersection require compatible headings and domains.
- “On course labelled OS but not LA” needs a difference between student sets, not a contradictory row predicate.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
