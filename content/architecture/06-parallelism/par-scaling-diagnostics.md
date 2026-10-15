---
id: par-scaling-diagnostics
title: Diagnosing scaling losses and superlinear gains
level: basic
minutes: 3
sourceLesson: par-flynn-amdahl
summary: Karp–Flatt is an implied serial fraction, not a direct source-code measurement.
---

## Why real speedups differ from the models

The ideal Amdahl and Gustafson models are optimistic. They assume the parallel part splits perfectly. Real code also pays for:

- **Communication and synchronisation.** Locks, barriers and message passing add time that often *grows* with processor count.
- **Load imbalance.** The slowest worker decides when the whole job finishes.
- **Shared resources.** Cores share memory bandwidth and the last-level cache. A loop may stop scaling once the memory bandwidth on offer is saturated; the core count depends on the machine, access pattern and memory placement.
- **Coherence traffic.** Cores writing to the same cache line, even different variables in it (false sharing), bounce the line between caches.

A useful diagnostic is the **Karp–Flatt metric**, the experimentally determined serial fraction. It runs Amdahl's law backwards: take a measured speedup and ask what serial fraction would have produced it. Writing Amdahl's law with the serial fraction e (so the parallel fraction is 1 − e) and solving for e gives:

```formula
1 / S = e + (1 − e) / n
e = (1/S − 1/n) / (1 − 1/n)
where
e: the Karp–Flatt metric: the serial fraction that would make Amdahl's law reproduce the measured speedup, normally between 0 and 1
S: the speedup you measured on n processors, a plain ratio
n: the number of processors, more than 1
In words: the metric is the serial fraction implied by a measured speedup; a value that stays constant as you add processors fits Amdahl's model, and one that rises means something else is costing time.
```

For example, a 6× speedup on 8 processors gives:

```formula
e = (1/6 − 1/8) / (1 − 1/8)
e ≈ 0.0417 / 0.875 ≈ 0.048
where
e: the Karp–Flatt metric (0.048 means the program behaves as if about 4.8% of it were serial)
≈: approximately equal to
In words: a 6× speedup on 8 processors is what Amdahl's law predicts for a program that is about 4.8% serial.
```

For comparable fixed-work measurements, compute e at several processor counts. A constant value is consistent with an Amdahl-style limit, not proof of its cause. Rising e motivates checking added overhead, imbalance, bandwidth, frequency changes and measurement conditions. If measured speedup exceeds processor count, the implied serial fraction is negative and is not a literal fraction of serial source code.

> [!warning] Superlinear speedup
> Occasionally the speedup is larger than the number of processors. One possible cause is improved cache residency when data is divided among cores. Other causes include changed algorithmic work or baseline differences. If cache residency is the cause, growing each partition beyond cache capacity may reduce that benefit; disappearance is not guaranteed from speedup alone.

> [!note] Evidence limits
> A hardware-specific saturation-core count and a definitive catalogue of MISD products is omitted because comparable measurements and a consistent stream-level classification were not reliably established here.

## Key takeaways
- Karp–Flatt is an implied serial fraction, not a direct source-code measurement.
- Changing overhead, bandwidth, cache behaviour and baselines require investigation.

## Further reading
- [Flynn’s original stream classification](https://users.cs.utah.edu/~hari/teaching/paralg/Flynn72.pdf)
- [Amdahl’s original argument](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf)
- [Gustafson’s scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)
- [Karp and Flatt’s measurement paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
