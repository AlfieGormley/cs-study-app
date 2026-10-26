---
id: cx-operation-budgets
sourceLesson: cx-in-practice
title: Estimating a feasible input budget
level: advanced
minutes: 2
summary: Use an explicitly assumed operation rate to screen algorithm choices.
---

Complexity helps reject implausible designs before implementing them. It does not supply a universal number of operations a machine can perform each second.

## Build a workload-specific budget

Start with the largest expected input, the actual operation being counted and the time available. A comparison of two small integers is different from a network request or comparison of long strings. Use measured throughput for representative data, or label a hypothetical rate clearly.

| Candidate | What to investigate |
|---|---|
| All pairs | whether quadratic growth fits the largest input |
| Sort then scan | comparison cost, allocation and input mutation |
| Hash-based scan | memory, hash quality and equality cost |
| Exhaustive subsets | candidate count and cost of checking each |

A quadratic design can look fine on a sample and fail when an upload grows substantially. Sorting or hashing may avoid most of those comparisons. Conversely, exhaustive search can be the simplest exact solution for a tightly bounded small input. There is no universal "twenty to twenty-five items" limit: pruning, per-candidate work, parallelism and the time budget alter feasibility.

## Treat an estimate as a model to validate

Dividing counted work by a representative operations-per-second rate gives an estimated runtime. A range of observed rates produces a range of predicted times. Do not substitute CPU clock frequency for measured iteration throughput.

If the larger input crosses a cache or memory boundary, the old rate may no longer apply. Include allocation, parsing, output and peak memory when those are part of the job. Leave headroom instead of relying on a model that only just fits.

Big-O is an upper growth bound with hidden constants, not an exact operation count. A label alone cannot justify a particular one-second deadline. Use the mechanism to screen candidates, then benchmark the actual implementation and workload.

## Key takeaways
- Feasibility depends on input bounds, operation cost and available time.
- Exhaustive search has no universal practical item cutoff.
- Use estimates to choose what to measure, not to replace measurement.

## Further reading
- [Python timeit](https://docs.python.org/3.14/library/timeit.html)
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
