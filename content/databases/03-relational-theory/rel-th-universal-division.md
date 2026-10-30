---
id: rel-th-universal-division
title: Division and universal conditions
level: basic
minutes: 4
sourceLesson: rel-th-algebra
summary: Answering "every" questions: division as "no missing pair", the double NOT EXISTS idiom and the empty-divisor trap.
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

## Division: "for all"

Division answers questions with *every* in them: which students take **all** CS courses?

```formula reference
Enrolled ÷ π cid (σ dept='CS' (Course))
  = {1, 3}
where
÷: division: the values of the left relation's remaining attributes (here sid) that are paired, in the left relation, with every relational tuple of the right relation
Enrolled: the relation of enrolments (sid, cid)
π: projection: keep only the listed attribute, removing duplicates
cid: the course-code attribute
σ: selection: keep relational tuples where the condition holds; dept='CS' keeps courses run by the CS department
dept: the attribute of Course naming the department
Course: the relation of courses (cid, title, dept)
{ }: a set of distinct values
In words: the divisor relation is the set of CS courses, {DB, AI}; the result is every student id enrolled on all of them.
```

A student qualifies if, for every course in the divisor relation, the pair (student, course) appears in Enrolled. Ada (1) and Cat (3) take both; Ben takes only DB. Result: `{1, 3}`.

Division is not a primitive. It is built from the basic operators by turning "for all" into "there is no counterexample":

1. Take the *candidates*: every student id that appears in Enrolled ({1, 2, 3}).
2. Pair every candidate with every required course to get the pairs that *would* exist if everyone took everything.
3. Subtract the pairs that really exist. What is left are the *missing pairs*: here only (Ben, AI).
4. Remove every candidate that has a missing pair. Ben drops out, leaving Ada and Cat.

```formula reference
M = (A × B) − Enrolled
Enrolled ÷ B = A − π sid (M)
where
A: the candidates, every student id with at least one enrolment
B: the divisor relation: the required course codes
M: the missing pairs: required (student, course) pairs absent from Enrolled
Enrolled: the enrolment relation (sid, cid)
×: Cartesian product: every pairing of a value of A with a value of B
−: difference: what is on the left but not on the right
π: projection: keep only the listed attribute, removing duplicates
sid: the student-id attribute
÷: division
In words: list every pair that "taking every required course" would need, find the pairs that are missing, and remove any student with a missing pair.
```

> [!analogy] Real-world analogy: a museum passport
> A city runs a museum passport: collect a stamp from every museum on this year's list and you win a prize. The organisers do not check which stamps you have; they look for a museum on the list whose stamp is missing.
>
> **How it maps:** Stamps are rows of Enrolled, the list of museums is the divisor relation, and "no museum on the list is missing from your passport" is the double negation behind division. If this year's list is empty, nothing can be missing, so every entrant qualifies: the empty-divisor case below.
>
> **Where it stops:** A prize scheme also decides who counts as an entrant, and so must a query. Algebraic division only considers students who appear in Enrolled, while a SQL query driven from `student` considers everyone, which is why the two differ when the divisor is empty.

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

## Key takeaways

- Division removes candidates with any missing required pair.
- An empty divisor qualifies every candidate; choose whether candidates come from enrolments or all students.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [Relational algebra, including division (Wikipedia)](https://en.wikipedia.org/wiki/Relational_algebra)
