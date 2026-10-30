---
id: rel-th-dependency-meaning
title: What functional dependencies claim
level: intermediate
minutes: 5
sourceLesson: rel-th-functional-deps
summary: What a functional dependency claims about every pair of rows, why data can refute but never prove one, and how keys fit in.
---

Normalisation, covered in the later normal-form units, can sound like a list of rules to memorise. It is not. The normal forms 2NF, 3NF and BCNF are defined using **functional dependencies** (FDs); higher forms also involve multivalued or join dependencies. Once you can reason about FDs, each normal form becomes a question you can answer about a real table: which facts does it repeat, and which rule causes the repetition?

This unit establishes what an FD claims and how to refute a proposed one. The following units show which other rules follow, and how to find every key.

We use single capital letters for attribute names in abstract examples. Adjacent letters in a card denote an attribute set, never a numeric product; every card defines that convention locally.

## What a functional dependency says

A functional dependency is a universal rule comparing pairs of relational tuples, not a claim about one row in isolation:

> Any two tuples that agree on X must also agree on Y.

```formula reference
X → Y
for all t_1, t_2 in R:
  t_1[X] = t_2[X] gives t_1[Y] = t_2[Y]
where
X, Y: sets of attributes of R; each may be a single attribute or several
→: "functionally determines": the condition on the next two lines holds in every legal state of R
R: the relation (table) the dependency is about
t_1, t_2: any two relational tuples (rows) of R
t_1[X], t_2[X]: the values the relational tuple has for the attributes in X; t_1[Y] and t_2[Y] likewise for Y
In words: whenever two rows have the same X values, they must have the same Y values. Knowing X pins down Y.
```

Take a spreadsheet of enrolments that someone has imported as one table:

```
sid  sname  cid  ctitle      grade
 1   Ada    DB   Databases    A
 1   Ada    AI   AI Basics    B
 2   Ben    DB   Databases    C
```

The business rules say a student id identifies one name, a course code identifies one title, and there is one grade per student per course. As FDs:

```formula essential
sid → sname
cid → ctitle
{sid, cid} → grade
where
→: functionally determines: rows equal on the left side are equal on the right side
sid: the student id
sname: the student's name
cid: the course code
ctitle: the course title
grade: the grade the student got on that course
{ }: a set of attributes; {sid, cid} means "sid and cid together"
In words: the id fixes the name, the code fixes the title, and only the pair (student, course) fixes the grade.
```

An FD is a **constraint on every legal state**, exactly like a key. You get it from the domain, not from the data.

> [!analogy] Real-world analogy: number plates and car models
> A car-park log lists each car's number plate and model. If two entries share a plate, they should show the same model, because a plate is issued to one vehicle. Two entries with the same plate and different models mean the rule is broken or someone mistyped.
>
> **How it maps:** The plate is the determinant X, the model is Y, and every pair of logged sightings is checked: same plate, same model. That pairwise comparison is exactly what an FD constrains.
>
> **Where it stops:** Plates can be transferred between cars over the years, so the real rule holds only at one point in time. An FD holds in every legal state of the relation as designed; if the business rule is really "plate at a date determines model", the determinant must include the date.

> [!warning] Data can refute an FD, never prove one
> If two rows share a `cid` but have different titles, the FD from `cid` to `ctitle` is false (or the data is dirty). But if today's rows all happen to have unique surnames, that does not make surname a determinant of anything. Data-profiling tools that "discover" FDs find candidates that a human must confirm.

### Trivial and non-trivial FDs

An FD is a **trivial FD** if its right side is part of its left side: "the student id and course code together determine the student id" holds in every relation and tells you nothing. The interesting rules are non-trivial: their right side contains something new.

### Keys are FDs too

A set of attributes is a **superkey** exactly when it determines every attribute of the relation: knowing its values fixes the whole row.

In the enrolment spreadsheet, the student id and course code together determine name, title and grade, so that pair is a superkey. Neither attribute alone determines everything (one student has several grades), so the pair is also a **candidate key**: a superkey with nothing that can be removed.

The inference examples treat their stated FDs as the complete basis being analysed. Extra rules such as a singleton domain or a fixed maximum row count can imply additional dependencies; include those assumptions when deciding which states are legal.

## Key takeaways

- An FD constrains every pair of relational tuples in every legal state.
- Data can refute a proposed rule; a clean sample cannot establish it as a business constraint.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Functional dependency (Wikipedia)](https://en.wikipedia.org/wiki/Functional_dependency)
