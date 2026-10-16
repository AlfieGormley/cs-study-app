---
id: rel-th-universal-division
title: Division and universal conditions
level: basic
minutes: 4
sourceLesson: rel-th-algebra
summary: Division and universal conditions, with explicit examples and the conditions that make the reasoning valid.
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

## Division: "for all"

Division answers questions with *every* in them: which students take **all** CS courses?

```formula
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
In words: the divisor relation is the set of CS courses, {DB, course labelled OS}; the result is every student id enrolled on all of them.
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
σ: selection: keep relational tuples where the condition holds
×: Cartesian product: every pairing of a value of A with a value of B
−: difference: what is on the left but not on the right
÷: division, as defined above
sid, cid, dept: the student-id, course-code and department attributes
DB, OS: the codes of the two CS courses
Enrolled, Course: the relations of the running example
{ }: a set; (2, course labelled OS) is one pair, a relational tuple of student 2 and course course labelled OS
In words: list every pair that "taking all CS courses" would need, find the pairs that are missing, and remove any student with a missing pair. Ben (2) is missing course labelled OS, so only Ada and Cat remain.
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

## Key takeaways

- Division removes candidates with any missing required pair.
- An empty divisor qualifies every candidate; choose whether candidates come from enrolments or all students.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
