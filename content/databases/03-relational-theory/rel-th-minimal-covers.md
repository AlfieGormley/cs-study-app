---
id: rel-th-minimal-covers
title: Minimal FD covers and FD equivalence
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Minimal FD covers and FD equivalence, with explicit examples and the conditions that make the reasoning valid.
---

## Minimal FD cover

Two FD sets can say the same thing with different amounts of redundancy. A **minimal FD cover** here means an equivalent set with singleton right sides and no remaining redundancy. Some texts call a grouped-right-side version a canonical FD cover; these presentation conventions differ, while the implied dependencies agree. Our singleton convention requires:

1. Every right side is a single attribute.
2. No left side has an **extraneous determinant attribute** (one you could drop and still derive the FD).
3. No FD is **redundant** (derivable from the others).

The card below starts with a dependency fixing two right-side attributes, a duplicate implied dependency, and an unnecessarily large determinant. Work through it in three stages:

1. Split the two-attribute right side into two dependencies; merge the duplicate dependency fixing B from A.
2. Test B in the two-attribute determinant. A alone already reaches C through B, so B adds nothing to that determinant. Reducing it produces another duplicate.
3. The remaining one-step functional dependency from A to C is implied by the two-step chain through B, so remove it.

```formula
F = {A → BC, B → C, A → B, AB → C}
F_1 = {A → B, A → C, B → C, AB → C}
A⁺ = {A, B, C}
F_2 = {A → B, A → C, B → C}
F_3 = {A → B, B → C}
where
A, B, C: attributes
F: the original set of FDs
BC, AB: the sets {B, C} and {A, B}
→: functionally determines
F_1: F after splitting every right side into single attributes
A⁺: the attribute closure of A; it contains C, so B is extraneous in AB → C
F_2: F_1 with AB → C reduced to A → C (now a duplicate, so merged)
F_3: F_2 without A → C, which follows from A → B and B → C by transitivity
{ }: a set
In words: four FDs reduce to two with exactly the same meaning: F_3 is a minimal FD cover of F.
```

The two dependencies in the final card line form a minimal FD cover. Four FDs became two, with exactly the same meaning. The 3NF synthesis algorithm in the next lesson starts from a minimal FD cover, which is why this step matters. Minimal FD covers are not always unique; different removal orders can give different, equally valid answers.

## Key takeaways

- A singleton-right-side minimal FD cover removes extraneous left attributes and redundant dependencies.
- Equivalent covers have the same implications and need not be unique.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
