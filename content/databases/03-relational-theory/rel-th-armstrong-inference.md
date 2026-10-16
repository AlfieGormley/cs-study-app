---
id: rel-th-armstrong-inference
title: Inferring dependencies with Armstrong rules
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Inferring dependencies with Armstrong rules, with explicit examples and the conditions that make the reasoning valid.
---

## Armstrong's axioms

Given some FDs, which others must also hold? William Armstrong gave three inference rules in 1974. For attribute sets X, Y and Z:

1. **Reflexivity**: a set determines any subset of itself.
2. **Augmentation**: adding the same attributes to both sides keeps an FD true.
3. **Transitivity**: if X determines Y and Y determines Z, then X determines Z.

```formula
Y ⊆ X gives X → Y
X → Y gives XZ → YZ
X → Y and Y → Z gives X → Z
where
X, Y, Z: sets of attributes of one relation
⊆: is a subset of: every attribute of Y is in X
→: functionally determines
XZ, YZ: sets written side by side are combined: XZ means X ∪ Z, the attributes of X together with those of Z
∪: union: everything in either set
In words: line 1 is reflexivity, line 2 is augmentation and line 3 is transitivity.
```

The rules have **soundness** (every conclusion follows from the given FDs) and **completeness** (every FD that follows from those premises can be derived). Three useful rules follow from them: the **FD union rule**, the **decomposition rule** and **pseudotransitivity**.

```formula
X → Y and X → Z gives X → YZ
X → YZ gives X → Y and X → Z
X → Y and WY → Z gives WX → Z
where
W, X, Y, Z: sets of attributes of one relation
→: functionally determines
YZ, WY, WX: combined sets, for example YZ = Y ∪ Z
∪: union: everything in either set
In words: the FD union rule combines right sides that share a left side; decomposition splits a right side apart; pseudotransitivity chains two FDs when extra attributes W are needed on the second one's left.
```

> [!warning] The left side does not decompose
> A right side can be split, but a left side cannot. Grade depends on student *and* course together, not on either alone.

```formula
XY → Z ⇏ X → Z
{sid, cid} → grade ⇏ sid → grade
where
X, Y, Z: sets of attributes
XY: X ∪ Y, the two sets combined
∪: union
→: functionally determines
⇏: "does not imply": the left FD can hold while the right one fails
sid, cid, grade: the student-id, course-code and grade attributes
{ }: a set of attributes
In words: knowing that X and Y together determine Z tells you nothing about X alone. One student has several grades, one per course.
```

The **FD closure** contains every functional dependency implied by a given basis:

```formula
X → Y in F⁺ when F ⊨ X → Y
where
F: the set of FDs you were given
F⁺: the FD closure of F: every FD that follows logically from F, including the trivial ones
X, Y: sets of attributes
→: functionally determines
⊨: "logically implies": every relation state that satisfies all of F also satisfies X → Y
In words: F⁺ is everything you can derive from F with Armstrong's axioms.
```

F⁺ can be exponentially large, so in practice you never list it. You compute attribute closures instead.

## Key takeaways

- Reflexivity, augmentation and transitivity derive exactly the implied FDs.
- Right sides split; left sides generally do not. Counterexamples refute invalid inference.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
