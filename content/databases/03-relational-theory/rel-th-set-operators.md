---
id: rel-th-set-operators
title: Set operators and an algebraic basis
level: basic
minutes: 5
sourceLesson: rel-th-algebra
summary: Union, difference and intersection on compatible relations, and why "not on LA" needs a difference, not a row filter.
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

## Set operators: union, difference, intersection

Union, difference and intersection work as they do on any sets, with one rule: the two inputs must be **union-compatible**, meaning the same attributes with the same domains.

```formula essential
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

```formula reference
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

Intersection follows the same pattern. The students on DB are 1, 2 and 3; those on AI are 1 and 3; so the students taking **both** are 1 and 3 (Ada and Cat).

In SQL these are `UNION`, `EXCEPT` and `INTERSECT`, which remove duplicates by default; `UNION ALL` and friends keep them (bag semantics).

### "On AI but not on LA": a property across rows

A tempting wrong answer is a single selection: keep enrolments where the course is AI **and** the course is not LA. That condition is tested on one enrolment at a time, and every AI enrolment trivially is not an LA enrolment, so Ada (who takes both) wrongly appears.

"Not on LA" describes the *student*, across all of their enrolments, so it needs a difference between two student sets: the students on AI ({1, 3}) minus the students on LA ({1}) leaves only Cat (3). In SQL that is `EXCEPT` or `NOT EXISTS`.

## The six primitive operators

Six operators are enough to express everything else: selection σ, projection π, rename ρ, union ∪, difference − and Cartesian product ×. The rest are shorthand:

```formula reference
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
In words: a join is a product followed by a selection; an intersection is one relation minus the part of it that is missing from the other; a semijoin is a join cut back to the first input's columns.
```

Division is also derived; the neighbouring division unit works through its construction.

This is a conventional complete basis of six operators, rather than a claim that every presentation uses this exact primitive list. A language expressing all pure-algebra queries is **relationally complete**. SQL can express them using appropriate duplicate removal and null-free inputs, and adds ordering, aggregation and recursion.

## Key takeaways

- Union, difference and intersection require compatible headings and domains.
- “On AI but not LA” describes a student across rows, so it needs a difference between student sets, not a one-row filter.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: combining queries (UNION, INTERSECT, EXCEPT)](https://www.postgresql.org/docs/18/queries-union.html)
