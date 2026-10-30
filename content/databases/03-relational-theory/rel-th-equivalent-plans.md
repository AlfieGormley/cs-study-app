---
id: rel-th-equivalent-plans
title: Equivalent query plans
level: basic
minutes: 4
sourceLesson: rel-th-algebra
summary: How a query becomes an operator tree, and the equivalence rules optimisers use to find a cheaper tree.
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

## From SQL to an expression tree

A simple SQL block maps onto algebra almost mechanically:

```sql
SELECT DISTINCT s.name
FROM student s JOIN enrolled e
  ON s.sid = e.sid
WHERE e.cid = 'DB';
```

Written as one algebra expression, read from the inside out, it joins, filters and then projects:

```formula reference
π name (σ cid='DB' (Student ⋈ Enrolled))
where
π: projection: keep only the listed attribute, removing duplicates (SQL's SELECT DISTINCT)
name: the student-name attribute
σ: selection: keep relational tuples where the condition holds (SQL's WHERE)
cid: the course-code attribute
⋈: natural join: pair relational tuples with equal values on the shared attribute, here sid (SQL's JOIN ... ON s.sid = e.sid)
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

```formula reference
σ p∧q (R) ≡ σ p (σ q (R))
R ⋈ S ≡ S ⋈ R
(R ⋈ S) ⋈ T ≡ R ⋈ (S ⋈ T)
σ p (R ⋈ S) ≡ σ p (R) ⋈ S
π L (R ⋈ S)
  ≡ π L (π L_R (R) ⋈ π L_S (S))
where
R, S, T: any relations
σ: selection: keep relational tuples where the condition holds
p, q: conditions on attributes. In the fourth line, p must mention only R's attributes
∧: and: both conditions must be true
⋈: natural join
≡: is equivalent to: gives exactly the same result for every possible contents of R, S and T
π: projection: keep only the listed attributes
L: the attributes the final result needs
L_R, L_S: the attributes of R (and of S) that are in L or are needed for the join
In words: splitting an "and" into two filters, swapping or regrouping the inputs of joins, filtering one input before a join when the condition only mentions that input, and dropping columns early while keeping those still needed never change the result.
```

Rule 3 is the big one. Take the tree above with 10,000 students and 200,000 enrolments, 1,000 of them for DB:

```
naive:   join 10k with 200k
         -> 200k rows, then filter -> 1k
pushed:  filter E first -> 1k rows
         join 10k with 1k -> 1k rows
```

The pushed plan feeds 1,000 enrolments into the join instead of 200,000.

> [!analogy] Real-world analogy: grading fruit at the farm
> A supermarket wants only grade-A apples. The farm can ship every apple to the depot and grade them there, or grade them at the farm and ship only grade-A fruit. The shelves end up the same; the second plan moves far less.
>
> **How it maps:** The farm's crates are the Enrolled input, the grade check is the selection on `cid`, and the trip to the depot is the join. Pushing the selection below the join is grading before shipping: same final result, much less work in the expensive step.
>
> **Where it stops:** Grading early is only allowed when the check uses the crate's own information. A condition that needs both inputs, such as comparing an order total with the customer's credit limit, cannot be pushed to one side, and an optimiser estimates costs from statistics rather than seeing the fruit.

Every cost-based optimiser (Postgres, SQL Server, Oracle, the Spark SQL Catalyst optimiser) applies these algebraic rewrites, then uses statistics to choose among the equivalent trees. The query processing module covers how it picks.

## Key takeaways

- Rewrites must preserve values, multiplicities and the output heading under the intended semantics.
- Push one-input filters below inner joins and keep needed join and output attributes.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational model and algebra](https://www.db-book.com/slides-dir/PDF-dir/ch2.pdf)
- [PostgreSQL 18: using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)
