---
id: rel-th-minimal-covers
title: Minimal FD covers and FD equivalence
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Removing redundancy from a set of dependencies without changing what it means.
---

## Minimal FD cover

Two FD sets can say the same thing with different amounts of redundancy. A **minimal FD cover** here means an equivalent set with singleton right sides and no remaining redundancy. Some texts call a grouped-right-side version a canonical FD cover; these presentation conventions differ, while the implied dependencies agree. Our singleton convention requires:

1. Every right side is a single attribute.
2. No left side has an **extraneous determinant attribute** (one you could drop and still derive the FD).
3. No FD is **redundant** (derivable from the others).

Why bother? Every dependency in a design is a rule someone must enforce or check. A redundant rule is enforced twice, and an oversized left side makes a rule look weaker than it is. A minimal cover states the business rules with nothing redundant, and the 3NF synthesis algorithm starts from one.

### A worked reduction

Start with four stated rules: A fixes B and C together; B fixes C; A fixes B (again); and A with B fixes C.

1. **Split right sides.** "A fixes B and C" becomes "A fixes B" and "A fixes C". The repeated "A fixes B" merges with its copy.
2. **Remove extraneous left-side attributes.** In "A with B fixes C", is B needed? A alone already reaches B, and through B reaches C, so B adds nothing. The rule shrinks to "A fixes C", a duplicate of one we already have.
3. **Remove redundant rules.** "A fixes C" follows from "A fixes B" and "B fixes C" by transitivity, so drop it.

What remains is two rules, A fixes B and B fixes C, with exactly the same meaning as the original four.

```formula reference
F = {A → BC, B → C, A → B, AB → C}
F_min = {A → B, B → C}
where
A, B, C: attributes
F: the original set of FDs
BC, AB: the sets {B, C} and {A, B}
→: functionally determines
F_min: a minimal FD cover of F: an equivalent set with single-attribute right sides, no extraneous left-side attributes and no redundant rules
{ }: a set
In words: the four original rules and the two remaining ones imply exactly the same dependencies, so the shorter set says everything the longer one did.
```

Always re-check equivalence after a reduction: each removed rule must still follow from what remains. Minimal FD covers are not always unique; different removal orders can give different, equally valid answers.

## Key takeaways

- A singleton-right-side minimal FD cover removes extraneous left attributes and redundant dependencies.
- Equivalent covers have the same implications and need not be unique.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Canonical cover (Wikipedia)](https://en.wikipedia.org/wiki/Canonical_cover)
