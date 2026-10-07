---
id: par-flynn-amdahl
title: Flynn's taxonomy, Amdahl and Gustafson
level: basic
minutes: 11
summary: The four classic ways hardware can be parallel, and the two laws that tell you how much faster more cores can actually make a program.
---

Clock scaling and microarchitectural improvements contributed to single-thread performance growth. Power and thermal constraints made rapid clock increases harder in the mid-2000s; clock rates and single-core performance did not stop improving. Designers also pursued more cores, vector execution and specialised accelerators.

Parallel hardware only helps if the work can be split. This lesson gives you two tools. **Flynn's taxonomy** is a vocabulary for *how* hardware is parallel. **Amdahl's** and **Gustafson's laws** tell you *how much* that parallelism can buy.

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

- **SPMD** (single program, multiple data) is a *programming* style in which participants run the same program on different data, potentially following different control paths. It can be used on MIMD CPUs or SIMT GPUs; MPI also supports other programming styles.
- **SIMT** (single instruction, multiple threads) is NVIDIA's term for GPUs. You write scalar code for one thread; the hardware groups 32 threads into a **warp** and issues instructions to active threads within it. Divergence and independent thread scheduling mean software must not assume implicit lockstep synchronisation. Lesson 4 covers it.
- A CPU can combine MIMD across cores with SIMD within cores. A hypothetical 16-core design sustaining one 512-bit float32 add per core per cycle would produce 16 × 16 = 256 additions per cycle. ISA width alone does not specify instruction throughput.

## Speedup and efficiency

Before the laws, two definitions. If a program takes T(1) on one processor and T(n) on n processors:

```
speedup    S(n) = T(1) / T(n)
efficiency E(n) = S(n) / n
```

Linear speedup means S(n) = n and E(n) = 1. Efficiency may fall as n grows because of serial work, communication, load imbalance or shared resources. It need not decrease monotonically.

## Amdahl's law: the serial part wins

Gene Amdahl's 1967 argument is simple. Split a program's single-core run time into a fraction **p** that can be parallelised and a fraction **1 − p** that cannot (start-up, reading input, a final merge, anything inherently sequential). For a fixed amount of work, assume equally fast processors, unchanged serial time, perfect division of the parallel work and no new overhead. Then only the parallel part shrinks:

```
T(n) = T(1) x ((1 - p) + p / n)

            1
S(n) = -------------
       (1 - p) + p/n
```

For p < 1, as n goes to infinity the speedup approaches **1 / (1 − p)**. For p = 1, this ideal model gives S(n) = n with no finite ceiling.

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

With 90% of the work parallel, the ceiling is 1 / 0.1 = 10×. Going from 64 to 1,024 cores, sixteen times the hardware, takes you from 8.8× to 9.9×.

> [!example] Where the time goes
> p = 0.9, one-core time 100 s. On 8 cores: serial part 10 s, parallel part 90 / 8 = 11.25 s, total 21.25 s, speedup 100 / 21.25 ≈ 4.7×. Efficiency is 4.7 / 8 ≈ 59%. The 10 s serial part is now nearly half the run.

As the parallel portion shrinks, the serial portion can become more important. Profile again and compare achievable total-time reductions, including new overhead and implementation cost.

### Amdahl beyond cores

The law applies to any optimisation that speeds up only part of the work. If a GPU makes 60% of a job 20× faster, the overall gain is 1 / (0.4 + 0.6/20) = 1 / 0.43 ≈ 2.3×. The actual benefit must also cover transfer and setup costs; even a smaller offloaded fraction can be worthwhile if its saving justifies those costs.

## Gustafson's law: grow the problem

Amdahl assumes a **fixed problem size** (strong scaling). In 1988 John Gustafson, working on a 1,024-processor machine at Sandia, described workloads that use larger machines to solve **bigger problems** in approximately the same time: finer weather grids, larger simulations, more training data.

Gustafson measures fractions on the *parallel* run instead. Let **s** be the fraction of the n-processor run time spent in serial code, and 1 − s the parallel part. Assume the serial duration is unchanged, all processors have equal speed and the measured parallel interval contains perfectly divided useful work rather than added overhead. Running that same scaled work on one processor would take s + (1 − s) × n in units of the parallel run time, so:

```
S(n) = s + (1 - s) x n
     = n - s x (n - 1)
```

This is the **scaled speedup**. It is linear in n when the parallel-run serial fraction s is held fixed. With s = 0.1 on 64 processors: S = 0.1 + 0.9 × 64 = 57.7×.

### Are they contradictory?

No. They answer different questions.

| | Amdahl | Gustafson |
|---|---|---|
| Problem size | Fixed | Grows with n |
| Scaling view | Strong scaling | Scaled work; related to weak scaling |
| Fraction measured on | 1-core run | n-core run |
| Model result | Ceiling for p < 1 | Linear for fixed s |

The key is that in many real problems the serial work (reading a config, setting up) stays roughly constant while the parallel work grows with the data. So the *serial fraction shrinks* as the problem grows. For example, if serial work stays fixed and parallel work grows 1,000-fold, an original 10% serial fraction becomes 0.1 / (0.1 + 900) ≈ 0.0111% of the one-processor work.

- If your goal is **latency** (render this one frame faster), Amdahl rules. Think of a web request or a compile.
- If your goal is **throughput or capability** (simulate a bigger system in an hour), Gustafson is the better model. Think of HPC and ML training.

## Why real speedups differ from the models

Both laws are optimistic. They assume the parallel part splits perfectly. Real code also pays for:

- **Communication and synchronisation.** Locks, barriers and message passing add time that often *grows* with n.
- **Load imbalance.** The slowest worker sets the finish time.
- **Shared resources.** Cores share memory bandwidth and the last-level cache. A loop may stop scaling once available memory bandwidth is saturated; the core count depends on the machine, access pattern and memory placement.
- **Coherence traffic.** Cores writing to the same cache line, even different variables in it (false sharing), bounce the line between caches.

A useful diagnostic is the **Karp–Flatt metric**, the experimentally determined serial fraction:

```
     1/S - 1/n
e = -----------
      1 - 1/n
```

For n > 1 and comparable fixed-work measurements, compute e at several n. A constant value is consistent with an Amdahl-style limit, not proof of its cause. Rising e motivates checking added overhead, imbalance, bandwidth, frequency changes and measurement conditions. If S > n, e is negative and is not a literal fraction of serial source code.

> [!warning] Superlinear speedup
> Occasionally S(n) > n. One possible cause is improved cache residency when data is divided among cores. Other causes include changed algorithmic work or baseline differences. If cache residency is the cause, growing each partition beyond cache capacity may reduce that benefit; disappearance is not guaranteed from speedup alone.

> [!note] Evidence limits
> A hardware-specific saturation-core count and a definitive catalogue of MISD products is omitted because comparable measurements and a consistent stream-level classification were not reliably established here.

## Key takeaways
- Flynn classifies instruction and data streams as SISD, SIMD, MISD and MIMD. Machines can combine models at different levels.
- Amdahl: for a fixed problem, speedup is 1 / ((1 − p) + p/n), capped at 1 / (1 − p) for p < 1 under its assumptions. With 5% fixed serial time, that model’s limit is 20×.
- Gustafson: scaled speedup is s + (1 − s)n under ideal work-scaling assumptions; it is linear for fixed s.
- Amdahl measures fractions on the one-core run, Gustafson on the n-core run. Fixed work versus scaled work; the latter is related to weak scaling.
- Real speedups also lose to communication, imbalance and shared bandwidth. A rising Karp–Flatt metric motivates investigating changing overhead or execution conditions.

## Further reading
- [Flynn's taxonomy — Wikipedia](https://en.wikipedia.org/wiki/Flynn%27s_taxonomy)
- [Amdahl's law — Wikipedia](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Gustafson's law — Wikipedia](https://en.wikipedia.org/wiki/Gustafson%27s_law)
- [Speedup — Wikipedia](https://en.wikipedia.org/wiki/Speedup)

- [Gustafson original scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)

- [Karp and Flatt original metric paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
