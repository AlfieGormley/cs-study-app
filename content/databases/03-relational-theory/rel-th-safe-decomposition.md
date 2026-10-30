---
id: rel-th-safe-decomposition
title: Lossless joins and dependency preservation
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Two checks for any table split: can a join rebuild the data exactly, and can each rule still be enforced locally?
---

## Decomposing safely

Splitting a relation has two possible costs, and you should check both.

### Lossless join

A decomposition has a **lossless join** if joining the parts always gives back exactly the original relation, in every legal state. If not, the join invents **spurious tuples**. The test for two parts:

```formula essential
(R_1 ∩ R_2) → R_1
  or (R_1 ∩ R_2) → R_2
where
R_1, R_2: the attribute sets of the two parts, together covering the original heading
∩: intersection: the attributes the two parts share
→: functionally determines; here the rule must follow from the given functional dependencies
In words: a two-way split has a lossless join exactly when the shared attributes determine every attribute of at least one part, that is, when they are a superkey of that part.
```

This exact two-part test assumes the only constraints are functional dependencies. The intuition: if the shared attributes identify a single row of one part, each row of the other part can match at most one partner, so the join cannot invent combinations.

Split Teaching badly into `(student, course)` and `(course, teacher)`:

```
student course | course teacher
Ann     DB     | DB     Smith
Bob     DB     | DB     Jones
```

Joining on `course` produces four rows, including `Ann, DB, Jones`, which never happened. Then try the split into `(teacher, course)` and `(student, teacher)` instead.

In the bad split the parts share only `course`, and course determines neither part (a course has several students and, here, two teachers), so the split is lossy. In the good split the parts share `teacher`, and a teacher determines their course, which covers the whole `(teacher, course)` part, so the join is lossless.

> [!analogy] Real-world analogy: a wedding seating plan
> A planner records which table each guest sits at, and separately which meal each table is served. If every table gets one menu, joining the two lists on table number tells each guest their meal exactly. If table 4 mixes fish and vegetarian, the join assigns every guest at table 4 both meals, and nobody can tell who actually ordered what.
>
> **How it maps:** The two lists are the two parts of a decomposition, table number is the shared attribute, and "one menu per table" is the dependency that makes the shared attribute a key of the table–meal part. Without it, the extra guest–meal pairs are spurious tuples.
>
> **Where it stops:** At a wedding someone would notice the mix-up. A database cannot: a lossy join returns invented rows silently, and the lossless guarantee must come from a rule holding in every legal state, not from how today's tables happen to be seated.

### Dependency preservation

A decomposition **preserves dependencies** if the FDs that hold inside each part, taken together, imply every original FD:

```formula reference
(F_1 ∪ F_2 ∪ ... ∪ F_n)⁺ = F⁺
where
F: the original FDs
F⁺: every FD implied by F
n: the number of parts
F_1, F_2, F_n: the FDs from F⁺ that mention only attributes of part 1, part 2, ..., part n
...: and so on, for every part in between
∪: union: all the FDs together
In words: every original rule can still be enforced one table at a time, without joining the parts back together.
```

Enforcing those local dependencies then suffices without checking a join; an original FD can follow transitively across several local dependencies rather than literally fit in one part. The lossless-join BCNF split of Teaching loses the rule that a student and course together fix the teacher: the projected local FDs do not imply that original rule. For example, local keys still allow Ann to reference Smith and Jones while both teach DB. Merely observing that no part contains all three attributes is not a proof of non-preservation: some dependencies can follow transitively across parts.

## Key takeaways

- Losslessness concerns reconstructing every legal relation without invented relational tuples.
- Dependency preservation concerns whether projected local FDs together imply the original rules.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
