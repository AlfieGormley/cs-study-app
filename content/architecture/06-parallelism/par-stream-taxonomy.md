---
id: par-stream-taxonomy
title: Classifying parallel instruction and data streams
level: basic
minutes: 3
sourceLesson: par-flynn-amdahl
summary: Flynn classifies instruction and data streams; one machine can combine classes.
---

Clock scaling and microarchitectural improvements contributed to single-thread performance growth. Power and thermal constraints made rapid clock increases harder in the mid-2000s; clock rates and single-core performance did not stop improving. Designers also pursued more cores, vector execution and specialised accelerators.

Parallel hardware only helps if the work can be split. These units give you two tools. **Flynn's taxonomy** is a vocabulary for *how* hardware is parallel. **Amdahl's law** and **Gustafson's law** tell you *how much* that parallelism can buy.

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
- **SIMT** (single instruction, multiple threads) is NVIDIA's term for GPUs. You write scalar code for one thread; the hardware groups 32 threads into a **GPU warp** and issues instructions to active threads within it. Divergence and independent thread scheduling mean software must never assume implicit lockstep synchronisation. The later warp lessons examine that execution model.
- A CPU can combine MIMD across cores with SIMD within cores. A hypothetical 16-core design sustaining one 512-bit float32 add per core per cycle would produce 256 additions per cycle (16 cores with 16 lanes each). ISA width alone does not specify instruction throughput.

## Key takeaways
- Flynn classifies instruction and data streams; one machine can combine classes.
- SPMD describes a program organisation; SIMT describes NVIDIA thread execution.

## Further reading
- [Flynn’s original stream classification](https://users.cs.utah.edu/~hari/teaching/paralg/Flynn72.pdf)
- [Amdahl’s original argument](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf)
- [Gustafson’s scaled-speedup paper](https://course.ece.cmu.edu/~ece600/fall16/references/gustafson.pdf)
- [Karp and Flatt’s measurement paper](https://parallelcomp.github.io/speedup-karp-flatt-cacm90.pdf)
