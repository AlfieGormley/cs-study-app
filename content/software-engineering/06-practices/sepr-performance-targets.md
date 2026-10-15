---
id: sepr-performance-targets
title: Choose a target and calculate the ceiling
level: intermediate
minutes: 4
summary: Use user-facing metrics and Amdahl’s law to decide which performance change can matter.
sourceLesson: sepr-profiling
---

A useful rule for performance work is: **measure before you change anything**. Intuition can misidentify where time goes. In a hypothetical profile, a suspected loop might take only 2% of runtime while a database call hidden inside a helper dominates. Those figures illustrate a possibility, rather than measurements from this course.

This lesson covers a disciplined workflow: define the goal, measure, find the bottleneck, change one thing, and measure again.

## When to optimise
Donald Knuth's famous line, from a 1974 paper, is usually quoted only in part:

> We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%.

The point is not "never optimise". It is: do not contort code for speed before you know it matters, and when it does matter, measure which parts matter and work there. The quoted percentages are rhetorical guidance, not measured proportions for every program.

Start with a **concrete target** tied to users or cost:

- **Latency**: "p99 of `/search` under 300 ms" (the 99th percentile, roughly 1% of observations lie above it, depending on ties and the percentile convention).
- **Completion time**: "the nightly import finishes within its 2-hour window". A throughput target would instead name work per unit time, such as rows imported per second.
- **Resources**: "fit in a 512 MB container", "halve the CPU bill".

Without a target you cannot tell when to stop, and performance work has no natural end.

> [!tip] Use percentiles, not averages
> A mean of 80 ms can hide a p99 of 2 seconds. Users making more requests have more opportunities to encounter slow requests, though request types and latency dependence also matter.

## Amdahl's law: where the ceiling is
**Amdahl's law** (Gene Amdahl, 1967) answers the question "if I speed up one part of a program, how much faster does the whole thing get?" It applies to a fixed amount of work, assuming the rest of the runtime is unchanged. Suppose a function takes 30% of runtime and you make it 10 times faster:

```formula
S = 1 / ((1 − p) + p / s)
S = 1 / ((1 − 0.3) + 0.3 / 10)
S = 1 / (0.7 + 0.03)
S = 1 / 0.73 ≈ 1.37
where
S: the overall speedup: old total runtime divided by new total runtime, a plain ratio ("1.37 times faster")
p: the fraction of the original runtime spent in the part you improve, between 0 and 1; here 0.3 (30%)
1 − p: the fraction of runtime you do not touch; here 0.7
s: how many times faster you make that part; here 10
≈: approximately equal to
In words: the untouched 70% still takes as long as before, so a tenfold speedup of the other 30% only makes the whole program about 1.37 times faster.
```

The untouched part sets a ceiling. Even if the improved part became infinitely fast, its time would shrink to nothing and only the untouched part would remain:

```formula
S_max = 1 / (1 − p)
S_max = 1 / 0.7 ≈ 1.43
where
S_max: the largest possible overall speedup, reached as the improved part's time approaches zero
p: the fraction of the original runtime spent in the part you improve; here 0.3
≈: approximately equal to
In words: if 70% of the runtime is untouched, no amount of work on the other 30% can make the program more than about 1.43 times faster.
```

The 70% you did not touch caps the gain. The lesson: work on the biggest slice first, and a profiler tells you which slice that is.

## Key takeaways
- Define a concrete latency, completion-window or resource target before optimising.
- Amdahl’s law assumes a fixed workload and an unchanged remainder.
- Improving a small runtime fraction has a strict ceiling under that model.

## Further reading
- [Amdahl’s law — NVIDIA CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#strong-scaling-and-amdahl-s-law)
- [Structured Programming with go to Statements — Donald Knuth](https://gwern.net/doc/cs/algorithm/1974-knuth.pdf)
