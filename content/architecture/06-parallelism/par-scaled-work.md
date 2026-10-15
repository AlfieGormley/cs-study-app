---
id: par-scaled-work
title: Gustafson: using more hardware for more work
level: basic
minutes: 4
sourceLesson: par-flynn-amdahl
summary: Gustafson measures the serial fraction on the parallel run.
---

## Gustafson's law: grow the problem

Amdahl assumes a **fixed problem size** (strong scaling). In 1988 John Gustafson, working on a 1,024-processor machine at Sandia, described workloads that use larger machines to solve **bigger problems** in approximately the same time: finer weather grids, larger simulations, more training data.

Gustafson measures fractions on the *parallel* run instead: the **serial fraction of the parallel run**. Assume the serial duration is unchanged, all processors have equal speed and the measured parallel interval contains perfectly divided useful work rather than added overhead. Now ask how long one processor would need for that same, larger job. The serial part takes the same time, but the parallel part, which kept n processors busy, would take n times as long:

```formula
T(n) = s + (1 − s) = 1
T(1) = s + (1 − s)n
S(n) = T(1) / T(n) = s + (1 − s)n
S(n) = n − s(n − 1)
where
T(n): the run time on n processors, used as the unit of time (so it equals 1)
T(1): the time one processor would need for the same scaled job, in units of the n-processor run time
s: the serial fraction measured on the n-processor run, from 0 to 1
1 − s: the parallel fraction of the n-processor run
n: the number of processors
S(n): the scaled speedup on n processors, a plain ratio
In words: one processor would need the serial time plus n copies of the parallel time, so the speedup grows in a straight line with the number of processors, minus a small loss for the serial part.
```

This is the **scaled speedup**. It is linear in n when the parallel-run serial fraction s is held fixed. For example, with 10% serial time on 64 processors:

```formula
S(64) = 0.1 + (1 − 0.1) × 64
S(64) = 0.1 + 57.6 = 57.7
where
S(64): the scaled speedup on 64 processors, a plain ratio
0.1: the serial fraction measured on the 64-processor run
In words: a job that is 10% serial on 64 processors would take about 57.7 times as long on one processor.
```

### Are they contradictory?

No. They answer different questions.

| | Amdahl | Gustafson |
|---|---|---|
| Problem size | Fixed | Grows with processor count |
| Scaling view | Strong scaling | Scaled work; related to weak scaling |
| Fraction measured on | 1-core run | Parallel run |
| Model result | Ceiling unless all work is parallel | Linear for a fixed serial fraction |

The key is that in many real problems the serial work (reading a config, setting up) stays roughly constant while the parallel work grows with the data. So the *serial fraction shrinks* as the problem grows. For example, if serial work stays fixed and parallel work grows 1,000-fold, an original 10% serial fraction becomes:

```formula
f_s = t_s / (t_s + t_p)
f_s = 0.1 / (0.1 + 0.9 × 1,000)
f_s = 0.1 / 900.1 ≈ 0.000111
where
f_s: the serial fraction of the one-processor work after the problem has grown (0.000111 is 0.0111%)
t_s: the serial work, unchanged at 0.1 of the original one-processor run time
t_p: the parallel work: 0.9 of the original run, grown 1,000-fold
≈: approximately equal to
In words: when only the parallel work grows, the fixed serial part becomes a tiny share of the total, here about one ten-thousandth.
```

- If your goal is **latency** (render this one frame faster), Amdahl rules. Think of a web request or a compile.
- If your goal is **throughput or capability** (simulate a bigger system in an hour), Gustafson is the better model. Think of HPC and ML training.

## Key takeaways
- Gustafson measures the serial fraction on the parallel run.
- Fixed-work and scaled-work speedups answer different questions.

## Further reading
- [Flynn’s original stream classification](https://users.cs.utah.edu/~hari/teaching/paralg/Flynn72.pdf)
- [Amdahl’s original argument](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf)
- [Gustafson’s scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)
- [Karp and Flatt’s measurement paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
