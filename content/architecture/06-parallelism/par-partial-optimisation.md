---
id: par-partial-optimisation
title: Accelerating only part of a program
level: basic
minutes: 3
sourceLesson: par-flynn-amdahl
summary: A local improvement must be weighted by its fraction of the original total time.
---

### Amdahl beyond cores

Amdahl’s law applies to any optimisation that speeds up only part of the work, not just to adding cores. Replace “divided across processors” with “made a specified number of times faster”:

```formula
S = 1 / ((1 − f) + f / k)
S = 1 / ((1 − 0.6) + 0.6 / 20)
S = 1 / (0.4 + 0.03) = 1 / 0.43 ≈ 2.3
where
S: the overall speedup of the whole job, a plain ratio
f: the fraction of the original run time that the change speeds up, from 0 to 1; here 0.6
k: how many times faster that part becomes (its local speedup); here 20
≈: approximately equal to
In words: if a GPU makes 60% of a job 20 times faster, the untouched 40% still dominates, and the whole job is only about 2.3 times faster.
```

The actual benefit must also cover transfer and setup costs; even a smaller offloaded fraction can be worthwhile if its saving justifies those costs.

## Comparing two investments

Suppose a batch job spends 30 seconds reading from storage and 70 seconds computing. Those intervals do not overlap. A faster storage device cuts the reading part to three seconds, so the complete run still takes 73 seconds. A code change that halves computation instead leaves 30 seconds of reading plus 35 seconds of computation: 65 seconds total. The second proposal wins even though its local improvement is much smaller.

The comparison depends on the measured fractions. If storage time overlaps computation, adding the original durations double-counts elapsed time. If a change adds allocation, conversion or transfer work, include it in the new total. Profile the complete workload again after the change; the old fraction is a description of the baseline, not a permanent property of the program.

For GPU offloading, also decide which result matters: the GPU kernel time, the complete request time or sustained throughput across many requests. A faster GPU kernel can still make a single request slower if moving the data dominates. A pipeline that overlaps copies and computation needs a dependency-aware timing model rather than simply adding all component durations.

## Key takeaways
- A local improvement must be weighted by its fraction of the original total time.
- Include transfers and setup when evaluating an offload.

## Further reading
- [Flynn’s original stream classification](https://users.cs.utah.edu/~hari/teaching/paralg/Flynn72.pdf)
- [Amdahl’s original argument](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf)
- [Gustafson’s scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)
- [Karp and Flatt’s measurement paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
