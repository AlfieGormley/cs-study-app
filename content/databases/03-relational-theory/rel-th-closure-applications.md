---
id: rel-th-closure-applications
title: Applying attribute closure
level: intermediate
minutes: 2
sourceLesson: rel-th-functional-deps
summary: Applying attribute closure, with complete worked examples and local definitions.
---

## Three jobs for attribute closure

1. **Does F imply a given FD?** Compute the attribute closure of its left side and check that the right side is inside it.
2. **Is X a superkey?** Yes exactly when its attribute closure is every attribute of R.
3. **Are F and G equivalent?** Yes if every FD in G follows from F, and every FD in F follows from G.

```formula
F ⊨ X → Y iff Y ⊆ X⁺
X⁺ = R
F ≡ G iff F⁺ = G⁺
{A, D}⁺ = ABCDE, so F ⊨ AD → E
A⁺ = {A, B, C}, so F ⊭ A → E
where
F, G: two sets of FDs over the same relation
X, Y: sets of attributes
→: functionally determines
⊨: logically implies; ⊭: does not imply
⊆: is a subset of
X⁺: the attribute closure of X under F
R: here, the set of all attributes of the relation (A, B, C, D, E in the example, with F = {A → B, B → C, CD → E})
≡: equivalent: F and G imply exactly the same FDs
F⁺, G⁺: the FD closures of F and G: every FD each one implies
A⁺, {A, D}⁺: the attribute closures of A and of {A, D} under F
A, B, C, D, E: the attributes of R
ABCDE, AD: the sets {A, B, C, D, E} and {A, D}
In words: line 1: F implies X → Y exactly when every attribute of Y is in the attribute closure of X ("iff" means "if and only if"). Line 2: X is a superkey exactly when its attribute closure is all of R. Line 3: F and G are equivalent exactly when they imply the same FDs. In the example, A and D together reach E, so AD → E follows from F; A alone only reaches A, B and C, so A → E does not.
```

In practice you test equivalence FD by FD: compute each FD's left-side attribute closure under the other set, rather than ever listing F⁺.

## Key takeaways

- The attribute closure of a determinant tests both implication and superkeys.
- Two FD sets are equivalent exactly when each derives all dependencies of the other.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
