---
id: cplx-intermediate-numeric
title: "Intermediate problems and numeric hardness"
level: intermediate
minutes: 3
summary: "Ladner’s theorem gives NP-intermediate problems if P differs from NP."
sourceLesson: cplx-np-completeness
---

## Not everything is P or NP-complete

**Ladner's theorem (1975)**: if P and NP are different, there are problems in NP that are neither in P nor NP-complete (**NP-intermediate**).

The theorem's examples are artificial. Natural candidates include bounded-factor decision and graph isomorphism, but nobody can prove them intermediate, because a problem in NP but not in P would itself prove that P and NP differ.

**Weak versus strong.** Subset sum and knapsack are NP-complete with unrestricted binary numbers, while a polynomial bound on their values makes their pseudo-polynomial DP polynomial-time. This is a statement about restricted input families, not a claim every large-number instance is difficult. They are *weakly* NP-complete. Problems like 3-partition and TSP stay NP-complete even when numeric values have a polynomial bound in input length: *strongly* NP-complete.

## Key takeaways

- Ladner’s theorem gives NP-intermediate problems if P differs from NP.
- Factoring decision and graph isomorphism are candidates, not proven intermediate problems.
- Weak and strong NP-completeness distinguish whether small numeric bounds remove hardness.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
