---
id: par-flynn-amdahl
title: Flynn's taxonomy, Amdahl and Gustafson
level: basic
minutes: 11
summary: The four classic ways hardware can be parallel, and the two laws that tell you how much faster more cores can actually make a program.
---

Clock scaling and microarchitectural improvements contributed to single-thread performance growth. Power and thermal constraints made rapid clock increases harder in the mid-2000s; clock rates and single-core performance did not stop improving. Designers also pursued more cores, vector execution and specialised accelerators.

Parallel hardware only helps if the work can be split. This lesson gives you two tools. **Flynn's taxonomy** is a vocabulary for *how* hardware is parallel. **Amdahl's law** and **Gustafson's law** tell you *how much* that parallelism can buy.

## Flynn's taxonomy

Flynn’s taxonomy classifies computers by two questions. How many **instruction streams** run at once? And how many **data streams** does each one act on?

| Class | Instr. | Data | Example |
|---|---|---|---|
| SISD | 1 | 1 | Classic single core |
| SIMD | 1 | Many | AVX, NEON, vector units |
| MISD | Many | 1 | Abstract multiple-instruction/single-data class |
| MIMD | Many | Many | Multicore CPUs, clusters |

```
SISD             SIMD
 I -> [PU] <- D   I -> [PU] <- D0
                     -> [PU] <- D1
                     -> [PU] <- D2
MIMD
 I0 -> [PU] <- D0
 I1 -> [PU] <- D1
 I2 -> [PU] <- D2
```

- **SISD** (single instruction, single data): one instruction operates on one piece of data at a time. This is the mental model of a simple CPU, even though real cores pipeline and overlap work internally.
- **SIMD** (single instruction, multiple data): one instruction applies the same operation to many data elements. The 256-bit YMM form of AVX `vaddps` adds eight pairs of float32 values; narrower and wider forms differ.
- **MISD** (multiple instruction, single data): several different operations on the same data. Its classification depends on the instruction and data streams being modelled. Redundant voting systems are not automatically MISD: identical replicated instruction streams do not establish multiple different instruction streams.
- **MIMD** (multiple instruction, multiple data): processors with independent instruction streams operating on multiple data streams. They may execute the same program and share data; ordinary multicore CPUs can provide MIMD execution.

### Modern refinements

Flynn's four boxes are coarse. Real machines mix them, and some extra terms are common:

- **SPMD** (single program, multiple data) is a *programming* style in which participants run the same program on different data, potentially taking different branches. It can be used on MIMD CPUs or SIMT GPUs; MPI also supports other programming styles.
- **SIMT** (single instruction, multiple threads) is NVIDIA's term for GPUs. You write scalar code for one thread; the hardware groups 32 threads into a **GPU warp** and issues instructions to active threads within it. Divergence and independent thread scheduling mean software must never assume implicit lockstep synchronisation. Lesson 4 covers it.
- A CPU can combine MIMD across cores with SIMD within cores. A hypothetical 16-core design sustaining one 512-bit float32 add per core per cycle would produce 16 cores × 16 lanes = 256 additions per cycle. ISA width alone does not specify instruction throughput.

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

For example, a job that takes 100 s on one core and 20 s on 8 cores has a speedup of 100 / 20 = 5× and an efficiency of 5 / 8 = 0.625, or 62.5%.

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

Add processors and the parallel term p / n shrinks to almost nothing, but the serial term never does. That sets a ceiling:

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

The ceiling exists only while some work is serial. If all of it were parallel (p = 1), this ideal model would give a speedup equal to n, with no finite ceiling. Here is the same formula as code:

```python
def amdahl(p, n):
    if not 0 <= p <= 1:
        raise ValueError("p outside [0, 1]")
    if type(n) is not int or n < 1:
        raise ValueError("invalid n")
    return 1 / ((1 - p) + p / n)

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

### Amdahl beyond cores

The law applies to any optimisation that speeds up only part of the work, not just to adding cores. Replace "divided across n processors" with "made k times faster":

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

## Gustafson's law: grow the problem

Amdahl assumes a **fixed problem size** (strong scaling). In 1988 John Gustafson, working on a 1,024-processor machine at Sandia, described workloads that use larger machines to solve **bigger problems** in approximately the same time: finer weather grids, larger simulations, more training data.

Gustafson measures fractions on the *parallel* run instead: the **serial fraction of the parallel run**. Assume the serial duration is unchanged, all processors have equal speed and the measured parallel interval contains perfectly divided useful work rather than added overhead. Now ask how long one processor would need for that same, larger job. The serial part takes the same time, but the parallel part, which kept n processors busy, would take n times as long:

```formula
T(n) = s + (1 − s) = 1
T(1) = s + (1 − s) × n
S(n) = T(1) / T(n) = s + (1 − s) × n
S(n) = n − s × (n − 1)
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

## Why real speedups differ from the models

Both laws are optimistic. They assume the parallel part splits perfectly. Real code also pays for:

- **Communication and synchronisation.** Locks, barriers and message passing add time that often *grows* with n.
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
e = 0.0417 / 0.875 ≈ 0.048
where
e: the Karp–Flatt metric (0.048 means the program behaves as if about 4.8% of it were serial)
≈: approximately equal to
In words: a 6× speedup on 8 processors is what Amdahl's law predicts for a program that is about 4.8% serial.
```

For comparable fixed-work measurements, compute e at several processor counts. A constant value is consistent with an Amdahl-style limit, not proof of its cause. Rising e motivates checking added overhead, imbalance, bandwidth, frequency changes and measurement conditions. If S > n, e is negative and is not a literal fraction of serial source code.

> [!warning] Superlinear speedup
> Occasionally the speedup is larger than the number of processors. One possible cause is improved cache residency when data is divided among cores. Other causes include changed algorithmic work or baseline differences. If cache residency is the cause, growing each partition beyond cache capacity may reduce that benefit; disappearance is not guaranteed from speedup alone.

> [!note] Evidence limits
> A hardware-specific saturation-core count and a definitive catalogue of MISD products is omitted because comparable measurements and a consistent stream-level classification were not reliably established here.

## Key takeaways
- Flynn classifies instruction and data streams as SISD, SIMD, MISD and MIMD. Machines can combine models at different levels.
- Amdahl: for a fixed problem, the serial fraction caps speedup at one divided by that fraction, however many processors you add. With 5% fixed serial time, that model’s limit is 20×.
- Gustafson: under ideal work-scaling assumptions, scaled speedup grows linearly with the number of processors when the parallel run's serial fraction is fixed.
- Amdahl measures fractions on the one-core run, Gustafson on the n-core run. Fixed work versus scaled work; the latter is related to weak scaling.
- Real speedups also lose to communication, imbalance and shared bandwidth. A rising Karp–Flatt metric motivates investigating changing overhead or execution conditions.

## Further reading
- [Flynn's taxonomy — Wikipedia](https://en.wikipedia.org/wiki/Flynn%27s_taxonomy)
- [Amdahl's law — Wikipedia](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Gustafson's law — Wikipedia](https://en.wikipedia.org/wiki/Gustafson%27s_law)
- [Speedup — Wikipedia](https://en.wikipedia.org/wiki/Speedup)

- [Gustafson original scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)

- [Karp and Flatt original metric paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
