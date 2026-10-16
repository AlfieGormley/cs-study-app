---
id: rel-th-bcnf-and-prime
title: BCNF and prime attributes
level: intermediate
minutes: 2
sourceLesson: rel-th-normal-forms
summary: BCNF and prime attributes, with explicit examples and the conditions that make the reasoning valid.
---

## Boyce–Codd normal form (BCNF)

A relation is in BCNF when, for every non-trivial FD that holds in it, **the left side is a superkey**. BCNF drops 3NF's escape clause "or A is prime":

```formula
for every X → Y in F⁺ with Y ⊄ X:
  X⁺ = R
where
F⁺: every FD that holds on the relation
X, Y: sets of attributes, the left and right sides
→: functionally determines
⊄: is not a subset of; Y ⊄ X makes the FD non-trivial
X⁺: the attribute closure of X
R: the set of all attributes of the relation
In words: every real dependency must come from a superkey, with no exceptions.
```

3NF and BCNF differ only when a relation has overlapping candidate keys. The classic example: each teacher teaches one course, and each student has one teacher per course. Teaching records student, course and teacher:

```formula
{student, course} → teacher
teacher → course
K_1 = {student, course}
K_2 = {student, teacher}
teacher⁺ = {teacher, course}
where
student, course, teacher: the three attributes of Teaching
→: functionally determines
{ }: a set of attributes
K_1, K_2: the two candidate keys; they overlap on student
teacher⁺: the attribute closure of teacher
In words: a student and course fix the teacher, and a teacher fixes the course. teacher reaches only itself and course, so it is not a superkey.
```

- The FD from `teacher` to `course` has a left side that is not a superkey, so **BCNF fails**.
- But `course` is prime (it is in the first candidate key), so **3NF holds**.

The redundancy is real: "Smith teaches DB" is repeated for every student Smith teaches.

## Key takeaways

- BCNF requires a superkey determinant for every non-trivial FD.
- Teaching passes 3NF through a prime course attribute while still failing BCNF.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
