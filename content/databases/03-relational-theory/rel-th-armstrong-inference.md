---
id: rel-th-armstrong-inference
title: Inferring dependencies with Armstrong rules
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Which dependencies follow from others: Armstrong's rules, the rules derived from them, and the left-side trap.
---

## Armstrong's axioms

Given some FDs, which others must also hold? William Armstrong gave three inference rules in 1974. For attribute sets X, Y and Z:

1. **Reflexivity**: a set determines any subset of itself.
2. **Augmentation**: adding the same attributes to both sides keeps an FD true.
3. **Transitivity**: if X determines Y and Y determines Z, then X determines Z.

```formula reference
Y ⊆ X gives X → Y
X → Y gives XZ → YZ
X → Y and Y → Z gives X → Z
where
X, Y, Z: sets of attributes of one relation
⊆: is a subset of: every attribute of Y is in X
→: functionally determines
XZ, YZ: sets written side by side are combined: XZ means X ∪ Z, the attributes of X together with those of Z
∪: union: everything in either set
In words: a set determines its own parts (reflexivity); adding the same attributes to both sides keeps a rule true (augmentation); and rules chain (transitivity).
```

The rules have **soundness** (every conclusion follows from the given FDs) and **completeness** (every FD that follows from those premises can be derived). Three useful rules follow from them:

- The **FD union rule**: if X determines Y and X determines Z, X determines both together.
- The **decomposition rule**: if X determines Y and Z together, it determines each of them.
- **Pseudotransitivity**: if X determines Y, and W together with Y determines Z, then W together with X determines Z. Chains still work when the second rule needs extra attributes.

```formula reference
X → Y and X → Z gives X → YZ
X → YZ gives X → Y and X → Z
X → Y and WY → Z gives WX → Z
where
W, X, Y, Z: sets of attributes of one relation
→: functionally determines
YZ, WY, WX: combined sets, for example YZ = Y ∪ Z
∪: union: everything in either set
In words: the FD union rule combines right sides that share a left side; decomposition splits a right side apart; pseudotransitivity chains two FDs even when the second one needs extra attributes on its left.
```

> [!warning] The left side does not decompose
> A right side can be split, but a left side cannot. Grade depends on student *and* course together, not on either alone. One counterexample settles it: student 1 with grade A in DB and grade B in AI satisfies "student and course fix the grade" but breaks "student alone fixes the grade".

The **FD closure** of a set of dependencies contains every dependency that set implies, trivial ones included. It can be exponentially large, so in practice you never list it. To answer "does this rule follow?", you compute the attribute closure of one left side instead: the next unit.

## Key takeaways

- Reflexivity, augmentation and transitivity derive exactly the implied FDs.
- Right sides split; left sides generally do not. Counterexamples refute invalid inference.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Armstrong's axioms (Wikipedia)](https://en.wikipedia.org/wiki/Armstrong%27s_axioms)
