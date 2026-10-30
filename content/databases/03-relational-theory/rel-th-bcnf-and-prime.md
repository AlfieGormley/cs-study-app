---
id: rel-th-bcnf-and-prime
title: BCNF and prime attributes
level: intermediate
minutes: 2
sourceLesson: rel-th-normal-forms
summary: Boyce–Codd normal form, and the overlapping-keys case where 3NF passes but redundancy remains.
---

## Boyce–Codd normal form (BCNF)

A relation is in BCNF when, for every non-trivial FD that holds in it, **the left side is a superkey**. BCNF drops 3NF's escape clause "or the determined attribute is prime":

```formula reference
for every X → Y in F⁺ with Y ⊄ X:
  X⁺ = R
where
F⁺: every FD that holds on the relation
X, Y: sets of attributes, the left and right sides
→: functionally determines
⊄: is not a subset of; Y ⊄ X makes the FD non-trivial
X⁺: the attribute closure of X
R: the set of all attributes of the relation
In words: every non-trivial dependency must come from a superkey, with no exception for key attributes.
```

A relation can pass 3NF yet fail BCNF only if it has at least two candidate keys that are both composite (made of several attributes) and overlap (share at least one attribute), a condition proved by Vincent and Srinivasan (1993). The condition is necessary, not sufficient: many relations with overlapping composite candidate keys are in BCNF. The classic example: each teacher teaches one course, and each student has one teacher per course. Teaching records student, course and teacher:

```formula reference
{student, course} → teacher
teacher → course
where
student, course, teacher: the three attributes of Teaching
→: functionally determines
{ }: a set of attributes
In words: a student and course fix the teacher, and a teacher fixes the course.
```

Student can never be derived, so it is in every key. Student with course is a key (it gives the teacher); student with teacher is also a key (the teacher gives the course). The two candidate keys overlap on student, so all three attributes are prime. Teacher alone reaches only itself and its course, so it is not a superkey.

- The FD from `teacher` to `course` has a left side that is not a superkey, so **BCNF fails**.
- But `course` is prime (it is in the first candidate key), so **3NF holds**.

The redundancy is real: "Smith teaches DB" is repeated for every student Smith teaches. If Smith switches to teaching AI, every one of those rows must change together, the same update anomaly 3NF was meant to prevent. Fixing it means splitting the table, which the next unit shows has a price.

## Key takeaways

- BCNF requires a superkey determinant for every non-trivial FD.
- Teaching passes 3NF through a prime course attribute while still failing BCNF.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
