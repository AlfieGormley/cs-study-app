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

These are separate obligations: hardness transfers the difficulty of other problems; membership supplies a polynomial-size certificate and polynomial-time checker.

The consequence: if any single NP-complete problem is in P, then every NP problem is in P, so P and NP are the same class. Conversely, if they differ, no NP-complete problem has a polynomial-time algorithm.

> [!warning] NP-hard does not mean "in NP and hard"
> The halting problem is NP-hard (any NP problem reduces to it: build a machine that halts iff the instance is a yes) but is not in NP; it isn't even decidable. An optimisation problem such as finding a shortest tour is NP-hard because solving it would solve an NP-hard decision problem. Merely being an optimisation problem does not make it hard. NP membership itself is defined for decision problems.

## Key takeaways

- NP-complete means both NP-hard and in NP.
- An undecidable problem may be NP-hard, and optimisation uses a different problem type.
- One NP-complete decision problem in P would imply P equals NP.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
