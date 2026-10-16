---
id: rel-th-safe-decomposition
title: Lossless joins and dependency preservation
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Lossless joins and dependency preservation, with explicit examples and the conditions that make the reasoning valid.
---

## Decomposing safely

Splitting a relation has two possible costs, and you should check both.

### Lossless join

A decomposition of R into R1 and R2 has a **lossless join** if joining the parts always gives back exactly R. If not, the join invents **spurious tuples**. The test for two parts:

```formula
r = π R_1 (r) ⋈ π R_2 (r)
  for every r in L
iff (R_1 ∩ R_2) → R_1 in F⁺
  or (R_1 ∩ R_2) → R_2 in F⁺
where
r: an instance of the original relation
L: all finite instances on the original heading satisfying the given functional dependencies
R_1, R_2: attribute sets covering the original heading
F: the given functional dependencies; this exact binary criterion assumes constraints consist of FDs
π: projection onto the following attribute set
⋈: natural join: match relational tuples on the shared attributes
∩: intersection: the attributes the two parts share
→: functionally determines
F⁺: every FD that holds on R
In words: the split has a lossless join when the shared attributes are a superkey of at least one side.
```

Split Teaching badly into `(student, course)` and `(course, teacher)`:

```
student course | course teacher
Ann     DB     | DB     Smith
Bob     DB     | DB     Jones
```

Joining on `course` produces four rows, including `Ann, DB, Jones`, which never happened. Then try the split into `(teacher, course)` and `(student, teacher)`:

```formula
R_1 ∩ R_2 = {course}
course⁺ = {course}
R_3 ∩ R_4 = {teacher}
teacher⁺ = {teacher, course}
where
R_1, R_2: the bad split, (student, course) and (course, teacher)
R_3, R_4: the good split, (teacher, course) and (student, teacher)
student, course, teacher: the attributes of Teaching
∩: intersection: the shared attributes
{ }: a set of attributes
course⁺, teacher⁺: attribute closures under {student, course} → teacher and teacher → course
→: functionally determines
In words: in the bad split the shared attribute course determines neither side, so the split is lossy. In the good split teacher determines course, which covers the whole of (teacher, course), so it gives a lossless join.
```

### Dependency preservation

A decomposition **preserves dependencies** if the FDs that hold inside each part, taken together, imply every FD in F:

```formula
(F_1 ∪ F_2 ∪ ... ∪ F_n)⁺ = F⁺
where
F: the original FDs
F⁺: every FD implied by F
n: the number of parts
F_1, F_2, F_n: the FDs from F⁺ that mention only attributes of part 1, part 2, ..., part n
...: and so on, for every part in between
∪: union: all the FDs together
In words: everything F says can still be checked one table at a time, without joining.
```

Enforcing those local dependencies then suffices without checking a join; an original FD can follow transitively across several local dependencies rather than literally fit in one part. The lossless-join BCNF split of Teaching loses the rule that a student and course together fix the teacher: the projected local FDs do not imply that original rule. For example, local keys still allow Ann to reference Smith and Jones while both teach DB. Merely observing that no part contains all three attributes is not a proof of non-preservation: some dependencies can follow transitively across parts.

## Key takeaways

- Losslessness concerns reconstructing every legal relation without invented relational tuples.
- Dependency preservation concerns whether projected local FDs together imply the original rules.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
