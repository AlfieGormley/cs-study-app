---
id: par-fixed-work-scaling
title: Amdahl: scaling a fixed job
level: basic
minutes: 5
sourceLesson: par-flynn-amdahl
summary: Speedup compares the same job; efficiency divides speedup by processor count.
---

## Speedup and efficiency

Before the laws, two definitions. Both compare the time the same job takes on one processor with the time it takes on several. **Speedup** says how many times faster the parallel run is; **parallel efficiency** says how much of that speedup each processor contributes.

```formula
S(n) = T(1) / T(n)
E(n) = S(n) / n
where
S(n): the speedup on n processors: how many times faster the n-processor run finishes than the one-processor run (a plain ratio, no unit)
T(1): the run time of the job on one processor, in seconds (s)
T(n): the run time of the same job on n processors, in seconds (s)
n: the number of processors (for example CPU cores) used
E(n): the parallel efficiency on n processors: speedup per processor, normally between 0 and 1 (often given as a percentage)
In words: speedup is old time divided by new time, and efficiency divides that speedup by the number of processors you paid for.
```

For example, a job taking 100 seconds on one core and 20 seconds on eight cores has a speedup of five and efficiency of 62.5%. These numbers describe completion time; they do not mean every core was busy for exactly that fraction of every second.

**Linear speedup** means the speedup equals the number of processors, so efficiency is 1 (100%). Efficiency may fall as processors are added because of serial work, communication, load imbalance or shared resources. It need not decrease monotonically.

## Amdahl's law: the serial part wins

Gene Amdahl's 1967 argument is simple. Split a program's single-core run time into a **parallel fraction** that can be spread across processors and a **serial fraction** that cannot (start-up, reading input, a final merge, anything inherently sequential). For a fixed amount of work, assume equally fast processors, unchanged serial time, perfect division of the parallel work and no new overhead. Then only the parallel part shrinks, and dividing the old time by the new time gives the speedup:

```formula
T(n) = T(1) × ((1 − p) + p / n)
S(n) = T(1) / T(n)
S(n) = 1 / ((1 − p) + p / n)
where
T(n): the run time on n processors, in seconds (s)
T(1): the run time on one processor, in seconds (s)
p: the parallel fraction: the share of the one-processor run time that can be split across processors, from 0 to 1 (0.9 means 90%)
1 − p: the serial fraction, the share that cannot be split and keeps its full length
n: the number of processors
S(n): the speedup on n processors, a plain ratio
In words: the serial part keeps its full length while the parallel part is divided by the number of processors, and the speedup is one over the new, shorter, total.
```

Add processors and the parallel contribution shrinks towards zero, but the serial contribution never does. That sets a ceiling:

```formula
S_max = 1 / (1 − p)
S_max = 1 / (1 − 0.9) = 1 / 0.1 = 10
where
S_max: the highest speedup reachable: the value S(n) approaches as the number of processors n grows without limit
S(n): Amdahl's speedup on n processors
p: the parallel fraction of the one-processor run time, from 0 to 1; here 0.9
n: the number of processors
In words: however many processors you add, the speedup can never beat one over the serial fraction; with 10% serial work the limit is 10×.
```

The ceiling exists only while some work is serial. If the parallel fraction were one, this ideal model would give linear speedup with no finite ceiling. Here is the same formula as code:

```python
def amdahl(p, n):
    if not 0 <= p <= 1:
        raise ValueError("p outside [0, 1]")
    if type(n) is not int or n < 1:
        raise ValueError("invalid n")
    # Serial stays; parallel work is split.
    return 1 / ((1 - p) + p / n)

# Each line shows cores then ideal speedup.
for n in [2, 8, 64, 1024]:
    print(n, round(amdahl(0.9, n), 2))
# 2 1.82
# 8 4.71
# 64 8.77
# 1024 9.91
```

With 90% of the work parallel, the ceiling is 10×. Going from 64 to 1,024 cores, sixteen times the hardware, takes you from 8.8× to 9.9×.

**Example: where the time goes.** Take a job that is 90% parallel and takes 100 s on one core, and run it on 8 cores:

```formula
T(8) = 100 s × ((1 − 0.9) + 0.9 / 8)
T(8) = 10 s + 11.25 s = 21.25 s
S(8) = 100 s / 21.25 s ≈ 4.7
E(8) = 4.7 / 8 ≈ 0.59
where
T(8): the run time on 8 cores, in seconds (s)
S(8): the speedup on 8 cores, a plain ratio
E(8): the parallel efficiency on 8 cores (0.59 means 59%)
s: second, the unit of time
≈: approximately equal to (the result is rounded)
In words: the 10 s serial part stays 10 s, the 90 s parallel part drops to 11.25 s, so the job runs about 4.7 times faster and each core is used about 59% effectively.
```

The 10 s serial part is now nearly half the run.

As the parallel portion shrinks, the serial portion can become more important. Profile again and compare achievable total-time reductions, including new overhead and implementation cost.

## Key takeaways
- Speedup compares the same job; efficiency divides speedup by processor count.
- A fixed serial duration limits ideal fixed-work speedup.

## Further reading
- [Flynn’s original stream classification](https://users.cs.utah.edu/~hari/teaching/paralg/Flynn72.pdf)
- [Amdahl’s original argument](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf)
- [Gustafson’s scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)
- [Karp and Flatt’s measurement paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
