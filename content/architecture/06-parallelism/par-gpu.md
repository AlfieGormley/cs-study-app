---
id: par-gpu
title: GPU architecture: SIMT, warps and memory
level: intermediate
minutes: 15
summary: How a GPU runs tens of thousands of threads by grouping them into warps, why branch divergence and uncoalesced memory access hurt, and how the GPU memory hierarchy shapes fast kernels.
---

CPUs and GPUs make different trade-offs among latency, throughput, control and data movement. This lesson describes CUDA on NVIDIA GPUs, focusing on exposing enough independent work to keep execution units busy. The sketch is conceptual, not a transistor-area measurement.

```
CPU core              GPU SM
+----------------+    +----------------+
| control | big  |    |ALU ALU ALU ALU |
| logic   | cache|    |ALU ALU ALU ALU |
|---------+------|    |ALU ALU ALU ALU |
| ALU  ALU  ALU  |    |ALU ALU ALU ALU |
+----------------+    | small cache    |
 latency-optimised    +----------------+
                       throughput-optimised
```

NVIDIA groups execution resources into **streaming multiprocessors** (SMs). SM counts, execution throughput, cache sizes and memory bandwidth vary by product and configuration. A marketing “core” count is not directly comparable with a CPU core count.

## The programming model

In CUDA you write a **kernel**: a function that describes what *one* thread does. You then launch it over a **grid** of **thread blocks**.

```cpp
#include <stddef.h>

__global__ void saxpy(size_t n, float a,
                      const float *x,
                      float *y) {
  size_t i = (size_t)blockIdx.x * blockDim.x
           + threadIdx.x;
  if (i < n)            /* guard tail */
    y[i] = a * x[i] + y[i];
}

/* 256 threads per block */
size_t blocks = n / 256 + (n % 256 != 0);
if (n != 0) {
  /* require blocks <= device grid limit */
  saxpy<<<(unsigned)blocks, 256>>>(
      n, 2.0f, dx, dy);
}
```

- Each thread computes a global index from its block and thread IDs, and handles one element.
- A **block** executes on a single SM. Its size must satisfy device and kernel limits. Threads can use block shared memory and a correctly participating block-wide `__syncthreads()` barrier.
- Ordinary blocks must be schedulable independently and may run in any order. Explicit cooperative and thread-block-cluster facilities add separate synchronisation contracts.
- `dx` and `dy` must designate at least n GPU-accessible floats. The output must not overlap input at a shifted index; otherwise threads can race. Unified or mapped memory can also be GPU-accessible. This launch fragment assumes allocated, initialised storage, a checked grid limit and a supported 256-thread block. Production code must check launch errors and completion before consuming results.

## Warps and SIMT

CUDA forms each block’s threads into **warps** of 32 consecutive linear thread IDs. A warp instruction is issued to an active subset of its logical threads; a partially filled warp has fewer active participants. Thirty-two logical threads do not imply 32 dedicated physical ALUs or one-cycle execution of every instruction.

NVIDIA calls this **SIMT** (single instruction, multiple threads). You write per-thread code while hardware tracks thread state and participation. Independent thread scheduling means implicit lockstep is not a valid synchronisation contract.

### Branch divergence

What happens when threads in one warp disagree at a branch?

```cpp
if (threadIdx.x % 2 == 0)
  a();   /* even threads */
else
  b();   /* odd threads */
```

In a simplified masked-execution model, the warp issues the a-path instructions for even lanes and the b-path instructions for odd lanes. Each path uses half the logical lanes. The functions here stand for arbitrary branch bodies; actual scheduling, predication and elapsed cost depend on the code and target.

```
time ->   a() a() a()  b() b() b()
even ln   ### ### ###  ... ... ...
odd ln    ... ... ...  ### ### ###
```

A warp-uniform condition can avoid within-warp path divergence when that transformation preserves the algorithm. Branching on `threadIdx.x / 32 % 2` illustrates this for a one-dimensional block; it does not make all branch overhead disappear.

Since Volta, **independent thread scheduling** tracks per-thread execution state. It can make older implicit warp-synchronous code **unsafe**. Communicating threads must use the appropriate synchronisation primitive, such as `__syncwarp(mask)`, and obey its participant-mask and memory-ordering rules. It is not enough to assume that two threads belong to the same warp.

## Hiding latency with many warps

Long-latency memory operations need not stall every resident warp. The SM retains execution state for several warps and can issue work from a ready warp while another waits. This avoids an operating-system context switch; it does not make scheduling physically free or guarantee that every cycle has an issuable instruction. Resident-warp limits and issue resources depend on the target.

```
cycle:  1  2  3  4  5  6  7  8
warp 0  ld .  .  .  .  .  .  add
warp 1  .  ld .  .  .  .  .  .
warp 2  .  .  mul mul ld .  .  .
warp 3  .  .  .  .  .  mul mul .
```

Under a steady-state model with consistently defined byte throughput B and average residence time L, **Little's law** gives B × L average bytes in flight. More resident warps can expose additional independent requests, but do not guarantee them.

### Occupancy

**Occupancy** is resident warps divided by the maximum. It is limited by whichever resource runs out first:

- **Registers.** In a hypothetical SM with 65,536 32-bit registers and a 64-warp limit, 64 registers per thread give a register-capacity upper bound of 1,024 threads or 32 warps (50%). Allocation granularity, block size and other limits can lower occupancy; 32 registers per thread does not guarantee 100%.
- **Shared memory.** With 164 KiB actually available for blocks and 48 KiB allocated per block, shared capacity permits at most three blocks, before other constraints.
- **Block size and limits.** Resident-block limits and the placement of whole blocks can bind before register or thread limits.

Higher occupancy can help hide latency when it exposes more useful independent work. It is not an optimisation goal by itself: additional registers or shared memory per thread may improve reuse enough to outweigh fewer resident warps.

## The memory hierarchy

| Storage | Typical CUDA visibility |
|---|---|
| Registers | Per-thread values; spills may use memory |
| Shared memory | Block-local, with explicit cluster extensions |
| L1 / L2 caches | Hardware-managed; scope and policy depend on target |
| Global memory | Addressable across the grid under memory-ordering rules |

On supported architectures, thread-block clusters provide **distributed shared memory**, allowing access to another block’s shared memory within the cluster. Correct cluster synchronisation and storage lifetimes are required; ordinary non-cluster blocks do not get that access.

### Coalescing

For the 32-byte-sector coalescing model used here, assume 32 active threads, one 4-byte load each, a 32-byte-aligned base and a first global index that is a multiple of 32. Consecutive x[i] accesses touch four sectors. These are requested sectors, not necessarily DRAM transfers: caches can satisfy requests. Misalignment can increase the count.

| Pattern | Sectors per warp |
|---|---|
| `x[i]` | 4 |
| `x[2 * i]` | 8 |
| `x[32 * i]` | 32 |
| random | up to 32 |

With a stride of 32, each thread's float lands in its own sector, so the request covers 32 × 32 = 1,024 sector bytes for 128 useful bytes, or 12.5% utilisation. That is why GPU code prefers structure-of-arrays layouts and why you transpose data on the way into shared memory.

### Shared memory and bank conflicts

Shared memory is a programmer-managed scratchpad; its latency advantage depends on the target, access pattern and compared cache/memory path. A classic pattern is **tiling**: each block loads a tile of a matrix into shared memory once, then every thread reuses it many times.

In the bank model here, successive 4-byte words map across **32 banks**. If the 32 threads of a warp hit 32 different banks, the access takes one pass. If several threads hit *different addresses in the same bank*, the request needs multiple bank-service passes; same-word reads can instead broadcast. These are logical passes, not a universal cycle count. Reading a column of a `float tile[32][32]` has every thread in the same bank: a 32-way conflict. Padding the row to 33 floats (`tile[32][33]`) shifts each row by one bank and removes it.

## Real-world use and trade-offs

- **Matrix units.** Supported GPUs provide specialised matrix operations with specific shape, dtype and numerical contracts. Their operation counts are not directly comparable with arbitrary scalar arithmetic workloads.
- **Data transfer.** Include transfers, synchronisation and launch overhead in the end-to-end timing. Keeping data resident across kernels can amortise movement; asynchronous overlap needs suitable hardware, buffers and dependencies.
- **Launch overhead.** Tiny kernels can be dominated by launch and scheduling costs. Fusion or CUDA Graphs may help, but should be measured.
- **Access patterns.** Serial pointer chains, divergent work and scattered addresses can limit GPU performance. Algorithm and layout transformations may change that outcome.
- **Precision.** Check the selected device and operation’s supported precision, accuracy and throughput; no generic FP64-to-FP32 ratio applies to all GPUs.

> [!note] Evidence limits
> A complete A100/H100 and AMD configuration catalogue, generic launch/latency timings and universal throughput ratios is omitted because those version- and workload-specific values were not comprehensively verified here; the retained arithmetic examples state their hypothetical assumptions.

## Key takeaways
- GPUs expose substantial throughput through parallel work; execution and memory resources depend on the target.
- Kernels are written per thread and launched as a grid of blocks; each block runs on one SM and shares its shared memory.
- CUDA warps contain 32 logical threads. Instructions run on active subsets; use explicit synchronisation rather than assuming lockstep.
- Latency is hidden by switching between many resident warps; occupancy is limited by registers, shared memory and block limits.
- Make warps read contiguous memory (coalescing), avoid shared-memory bank conflicts, and keep data on the GPU to avoid PCIe transfers.

## Further reading
- [CUDA C++ Programming Guide — NVIDIA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html)
- [CUDA C++ Best Practices Guide — NVIDIA](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [How to access global memory efficiently in CUDA kernels — NVIDIA blog](https://developer.nvidia.com/blog/how-access-global-memory-efficiently-cuda-c-kernels/)
- [Using shared memory in CUDA — NVIDIA blog](https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/)
- [Single instruction, multiple threads — Wikipedia](https://en.wikipedia.org/wiki/Single_instruction,_multiple_threads)

- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)

- [CUDA warp-level primitives](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
