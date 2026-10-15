---
id: cplx-hardness-membership
title: "NP-hardness versus NP-completeness"
level: intermediate
minutes: 3
summary: "NP-complete means both NP-hard and in NP."
sourceLesson: cplx-np-completeness
---

## NP-hard and NP-complete

- A problem B is **NP-hard** if *every* problem in NP reduces to it.
- B is **NP-complete** if it is NP-hard **and** in NP.

In symbols:

```formula
A ≤_p B   for every A ∈ NP
B ∈ NP
where
A: any problem in NP
B: the problem being classified
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer
∈: "is a member of" (belongs to the class)
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
In words: the first line alone makes B NP-hard: every NP problem translates into B. Add the second line, that B is itself in NP, and B is NP-complete.
```

The consequence: if any single NP-complete problem is in P, then every NP problem is in P, so P and NP are the same class. Conversely, if they differ, no NP-complete problem has a polynomial-time algorithm.

```formula
B ∈ NPC and B ∈ P  gives  P = NP
P ≠ NP  gives  B ∉ P  for every B ∈ NPC
where
B: a decision problem
NPC: the set of NP-complete problems (in NP, and every NP problem reduces to them)
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
∈: "is a member of"; ∉: "is not a member of"
≠: "is not equal to": here, the two classes contain different problems
In words: one NP-complete problem with a polynomial-time algorithm would make P and NP equal; if they are different, every NP-complete problem lacks one.
```

> [!warning] NP-hard does not mean "in NP and hard"
> The halting problem is NP-hard (any NP problem reduces to it: build a machine that halts iff the instance is a yes) but is not in NP; it isn't even decidable. Optimisation problems like "find the shortest tour" are called NP-hard because they aren't yes/no problems, so they can't be in NP.

## Key takeaways

- NP-complete means both NP-hard and in NP.
- An undecidable problem may be NP-hard, and optimisation uses a different problem type.
- One NP-complete decision problem in P would imply P equals NP.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
