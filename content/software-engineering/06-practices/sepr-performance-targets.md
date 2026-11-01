---
id: sepr-performance-targets
title: Choose a target and find the ceiling
level: intermediate
minutes: 5
summary: Use user-facing metrics and Amdahl’s law to decide which performance change can matter.
sourceLesson: sepr-profiling
---

A useful rule for performance work is: **measure before you change anything**. Intuition often picks the wrong culprit: the loop everyone suspects may take a tiny share of the runtime while a database call hidden inside a helper dominates.

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
**Amdahl's law** (Gene Amdahl, 1967) answers the question "if I speed up one part of a program, how much faster does the whole thing get?" The part you do not touch still takes as long as before, so it sets a ceiling on the overall gain.

```formula essential
S = 1 / ((1 − p) + p / s)
S_max = 1 / (1 − p)
where
S: the overall speedup: old total runtime divided by new total runtime, a plain ratio ("1.37 times faster")
p: the fraction of the original runtime spent in the part you improve, between 0 and 1
1 − p: the fraction of runtime you do not touch
s: how many times faster you make that part
S_max: the largest possible overall speedup, reached as the improved part's time shrinks towards zero
In words: the untouched share of the runtime still has to run, so speeding up the rest can never make the whole program faster than one divided by that untouched share.
```

Suppose a function takes 30% of runtime and you make it 10 times faster. The untouched 70% still takes as long as before, so the whole program gets only about 1.37 times faster. Even making that function infinitely fast would cap the gain at about 1.43 times, because the 70% remains.

The law assumes a fixed amount of work and an unchanged remainder. In practice a change can also shift work elsewhere (a faster parser feeding a slower database harder), so always re-measure. The practical lesson: work on the biggest slice first, and let a profiler tell you which slice that is.

> [!analogy] Real-world analogy: a faster train on a door-to-door journey
> Your commute is a 15-minute walk to the station, a 30-minute train ride and a 5-minute walk at the other end. A new express halves the train time, but you still walk for 20 minutes, so the whole journey drops from 50 to 35 minutes, not to 25.
>
> **How it maps:** The train is the part you optimised (p is 30 of the 50 minutes) and the walks are the untouched remainder. Even a train that took no time at all would leave a 20-minute journey: that is the ceiling.
>
> **Where it stops:** Walks and trains do not affect each other, but parts of a program can. Speeding one part up can push extra load onto another (more queries per second at the database), so the remainder is not always unchanged.

## Key takeaways
- Define a concrete latency, completion-window or resource target before optimising.
- Amdahl’s law assumes a fixed workload and an unchanged remainder.
- The untouched share of the runtime sets a ceiling: improving a small fraction can never give a large overall speedup.

## Further reading
- [Amdahl’s law — NVIDIA CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#strong-scaling-and-amdahl-s-law)
- [Program optimization, including Knuth's 1974 remark — Wikipedia](https://en.wikipedia.org/wiki/Program_optimization)
