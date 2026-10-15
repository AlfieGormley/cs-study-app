---
id: sync-locks-amdahl-limit
title: A global lock limits speed-up
level: intermediate
minutes: 3
summary: Apply Amdahl’s idealised model to a serial critical section.
sourceLesson: sync-locks
---

Before dividing a lock, estimate how much work it serialises. Amdahl’s law describes a fixed-work idealisation, rather than a hardware benchmark.

## Contention and granularity

A correctly implemented lock still needs a correct application protocol: all relevant accesses must participate, lifetimes must be valid and lock ordering must avoid deadlock. Performance then depends partly on contention.

No reproducible uncontended-lock timing is supplied here. When it is heavily contended, threads queue, sleep and wake, and the critical section becomes a serial bottleneck.

**Amdahl's law** puts a number on that bottleneck. It answers "how much faster can more cores make this program?" when part of the work must run one thread at a time, as everything under a single lock does:

```formula
S(N) = 1 / (s + (1 − s) / N)
S_max = 1 / s   as N → ∞, for s > 0
where
S(N): the speed-up on N cores: how many times faster the program runs than on 1 core (a plain ratio with no unit)
s: the serial fraction: the share of the single-core running time that can only run one thread at a time, for example under one global lock; a number from 0 to 1
1 − s: the parallel fraction, the share that spreads perfectly across cores
N: the number of cores running the work in parallel
S_max: the best possible speed-up, however many cores you add
→: tends towards, as N keeps growing
∞: infinity: N growing without any limit
In words: the serial part never gets faster, so it sets a ceiling of 1 / s on the speed-up; adding cores only shrinks the parallel part.
```

For example, if ten percent of the single-core work is serial and there are sixteen cores:

```formula
S(16) = 1 / (0.1 + 0.9 / 16)
S(16) = 1 / (0.1 + 0.05625)
S(16) = 1 / 0.15625 = 6.4
S_max = 1 / 0.1 = 10
where
S(16): the speed-up on 16 cores, as a plain ratio (6.4 means 6.4 times faster than 1 core)
S_max: the ceiling with unlimited cores
In words: with a tenth of the work serialised by one lock, 16 cores give only about 6.4 times the single-core speed, and no number of cores can beat 10 times.
```

The law assumes the parallel part splits perfectly and ignores the extra cost of contention itself (cache-line transfers, sleeping and waking). For lock-bound programs, treat its figure as an optimistic upper estimate: real ones usually do worse.

## Key takeaways

- The serial fraction does not shrink when more cores share a fixed amount of work.
- With ten percent serial work, sixteen ideal cores give a speed-up of 6.4.
- Contention and scheduling overhead can make actual performance worse than the model.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
