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

In CUDA you write a **GPU kernel**: a function that describes what *one* thread does. You then launch it over a **CUDA grid** of **CUDA blocks** (thread blocks).

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

- Each thread computes a global index from its block and thread indices, and handles one element (the formulas follow this list).
- A **thread block** executes on a single SM. Its size must satisfy device and GPU kernel limits. Threads can use block shared memory and a correctly participating block-wide `__syncthreads()` barrier.
- Ordinary blocks must be schedulable independently and may run in any order. Explicit cooperative and thread-block-cluster facilities add separate synchronisation contracts.
- `dx` and `dy` must designate at least n GPU-accessible floats. The output must never overlap input at a shifted index; otherwise threads can race. Unified or mapped memory can also be GPU-accessible. This launch fragment assumes allocated, initialised storage, a checked grid limit and a supported 256-thread block. Production code must check launch errors and completion before consuming results.

The index each thread computes places the blocks one after another along the array:

```formula
i = b × N_b + t
i = 3 × 256 + 10 = 778
where
i: the thread's global index: which array element it handles
b: the block's index within the grid, counting from 0 (blockIdx.x in CUDA); here 3
N_b: the number of threads per block (blockDim.x); here 256
t: the thread's index within its own block, from 0 to N_b − 1 (threadIdx.x); here 10
In words: skip over all the earlier blocks, each N_b threads long, then count along to your own position in your block.
```

The launch needs enough blocks to cover every element, so the block count is rounded up. The code's `n / 256 + (n % 256 != 0)` is integer division plus one extra block when there is a remainder:

```formula
N_blocks = ⌈n / N_b⌉
N_blocks = ⌈1,000 / 256⌉ = ⌈3.9⌉ = 4
where
N_blocks: the number of blocks launched
n: the number of array elements; 1,000 in the example
N_b: the number of threads per block; 256
⌈ ⌉: ceiling: round up to the next whole number
In words: launch enough blocks that blocks times threads per block is at least the element count; the surplus threads (here 4 × 256 − 1,000 = 24) fail the i < n guard and do nothing.
```

## Warps and SIMT

CUDA forms each block’s threads into **GPU warps** of 32 consecutive linear thread indices. A warp instruction is issued to an active subset of its logical threads; a partially filled warp has fewer active participants. Thirty-two logical threads do not imply 32 dedicated physical ALUs or one-cycle execution of every instruction.

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

How many memory requests must be outstanding to keep the memory system busy? **Little's law**, a result from queueing theory that holds for any system in steady state, answers it: the average amount in the system equals the rate it flows through times the average time each piece spends inside.

```formula
D = R × t_res
D = 10^12 B/s × 400 × 10^-9 s
D = 4 × 10^5 B = 400 KB
where
D: the average number of bytes in flight: requested but not yet delivered, in bytes (B)
R: the byte throughput, in bytes per second (B/s); 1 TB/s = 10^12 B/s in the example
t_res: the average residence time: how long each request is outstanding, in seconds (s); 400 ns = 400 × 10^-9 s
B: byte, 8 bits
s: second
KB: kilobyte, 1,000 bytes
In words: to stream 1 TB/s when each request takes 400 ns to come back, about 400 KB of requests must be in flight at any moment.
```

The law needs a steady state and a consistent definition of bytes and time. More resident warps can expose additional independent requests, but do not guarantee them.

### Occupancy

**GPU occupancy** is the number of warps resident on an SM divided by the most it can hold. Registers are one limit: every resident thread needs its own registers from the SM's register file, so the more registers each thread uses, the fewer threads fit. In a hypothetical SM with 65,536 32-bit registers and a 64-warp limit, 64 registers per thread give:

```formula
O = W_res / W_max
N_t = R_SM / r
N_t = 65,536 / 64 = 1,024
W_res = N_t / 32 = 1,024 / 32 = 32
O = 32 / 64 = 0.5
where
O: occupancy, from 0 to 1 (0.5 is 50%)
W_res: the number of warps resident on the SM at once
W_max: the most warps the SM can hold; 64 here
N_t: the most threads the register file can hold
R_SM: the number of 32-bit registers in the SM's register file; 65,536 here
r: the registers each thread of the GPU kernel uses; 64 here
32: the number of threads in a warp
In words: 64 registers per thread let only 1,024 threads, or 32 warps, fit in the register file, which is half of the SM's 64-warp limit.
```

Occupancy is limited by whichever resource runs out first:

- **Registers**, as above. Allocation granularity, thread-block size and other limits can lower occupancy; 32 registers per thread does not guarantee 100%.
- **GPU shared memory.** With 164 KiB actually available for blocks and 48 KiB allocated per block, shared capacity permits at most three blocks, before other constraints (worked below).
- **Thread-block size and limits.** Resident-block limits and the placement of whole blocks can bind before register or thread limits.

```formula
N_blk = ⌊M_SM / M_blk⌋
N_blk = ⌊164 KiB / 48 KiB⌋ = ⌊3.4⌋ = 3
where
N_blk: the most blocks that fit by shared-memory capacity
M_SM: the GPU shared memory available for blocks on the SM, in kibibytes (KiB); 164 KiB here
M_blk: the GPU shared memory each block allocates, in KiB; 48 KiB here
KiB: kibibyte, 1,024 bytes
⌊ ⌋: floor: round down to a whole number, because a block cannot be partly resident
In words: three 48 KiB blocks use 144 KiB; a fourth would need 192 KiB, more than the 164 KiB available.
```

Higher occupancy can help hide latency when it exposes more useful independent work. It is not worth maximising for its own sake: additional registers or GPU shared memory per thread may improve reuse enough to outweigh fewer resident warps.

## The memory hierarchy

| Storage | Typical CUDA visibility |
|---|---|
| Registers | Per-thread values; spills may use memory |
| GPU shared memory | Block-local, with explicit cluster extensions |
| L1 / L2 caches | Hardware-managed; scope and policy depend on target |
| Global memory | Addressable across the grid under memory-ordering rules |

On supported architectures, thread-block clusters provide **distributed shared memory**, allowing access to another block’s GPU shared memory within the cluster. Correct cluster synchronisation and storage lifetimes are required; ordinary non-cluster blocks do not get that access.

### Coalescing

For the 32-byte-sector coalescing model used here, assume 32 active threads, one 4-byte load each, a 32-byte-aligned base and a first global index that is a multiple of 32. Consecutive x[i] accesses touch four sectors. These are requested sectors, not necessarily DRAM transfers: caches can satisfy requests. Misalignment can increase the count.

| Pattern | Sectors per warp |
|---|---|
| `x[i]` | 4 |
| `x[2 * i]` | 8 |
| `x[32 * i]` | 32 |
| random | up to 32 |

With a stride of 32, each thread's float lands in its own sector. Utilisation compares the bytes the threads wanted with the bytes in the sectors fetched:

```formula
U = N_use / N_sec
N_use = 32 × 4 B = 128 B
N_sec = 32 × 32 B = 1,024 B
U = 128 B / 1,024 B = 0.125
where
U: sector utilisation: the fraction of requested sector bytes the warp actually uses (0.125 is 12.5%)
N_use: useful bytes: 32 threads × one 4-byte float each
N_sec: requested sector bytes: 32 sectors × 32 bytes each
B: byte, 8 bits
In words: each thread wants 4 bytes but drags in a whole 32-byte sector, so only one byte in eight is useful.
```

That is why GPU code prefers structure-of-arrays layouts and why you transpose data on the way into GPU shared memory.

### GPU shared memory and bank conflicts

GPU shared memory is a programmer-managed scratchpad; its latency advantage depends on the target, access pattern and compared cache/memory path. A classic pattern is **tiling**: each block loads a tile of a matrix into GPU shared memory once, then every thread reuses it many times.

In the bank model here, successive 4-byte words map across 32 **shared-memory banks**. If the 32 threads of a warp hit 32 different banks, the access takes one pass. If several threads hit *different addresses in the same bank*, the request needs multiple bank-service passes; same-word reads can instead broadcast. These are logical passes, not a universal cycle count. Reading a column of a `float tile[32][32]` has every thread in the same bank: a 32-way conflict. Padding the row to 33 floats (`tile[32][33]`) shifts each row by one bank and removes it. The bank arithmetic shows why:

```formula
m = (a / 4) mod 32
m_32 = (32 × r + c) mod 32 = c
m_33 = (33 × r + c) mod 32
m_33 = (r + c) mod 32
where
m: the bank holding the 4-byte word at byte address a, from 0 to 31
a: the byte address of the word within GPU shared memory; the tile is assumed to start at address 0 (bank 0), so element [r][c] of a 32-float-row tile is word 32 × r + c
4: each bank is 4 bytes wide, so a / 4 is the word number
32: the number of banks
mod: the remainder after whole-number division (40 mod 32 = 8)
r: the row of the tile element; in a column read, thread r of the warp reads row r
c: the column being read, the same for every thread
m_32: the bank of element [r][c] when each row holds 32 floats
m_33: the bank of element [r][c] when each row is padded to 33 floats
In words: with 32-float rows every element of a column lands in the same bank, c; with 33-float rows each row moves one bank along, so the 32 threads hit 32 different banks.
```

## Real-world use and trade-offs

- **Matrix units.** Supported GPUs provide specialised matrix operations with specific shape, dtype and numerical contracts. Their operation counts are not directly comparable with arbitrary scalar arithmetic workloads.
- **Data transfer.** Include transfers, synchronisation and launch overhead in the end-to-end timing. Keeping data resident across GPU kernels can amortise movement; asynchronous overlap needs suitable hardware, buffers and dependencies.
- **Launch overhead.** Tiny GPU kernels can be dominated by launch and scheduling costs. Fusion or CUDA Graphs may help, but should be measured.
- **Access patterns.** Serial pointer chains, divergent work and scattered addresses can limit GPU performance. Algorithm and layout transformations may change that outcome.
- **Precision.** Check the selected device and operation’s supported precision, accuracy and throughput; no generic FP64-to-FP32 ratio applies to all GPUs.

> [!note] Evidence limits
> A complete A100/H100 and AMD configuration catalogue, generic launch/latency timings and universal throughput ratios is omitted because those version- and workload-specific values were not comprehensively verified here; the retained arithmetic examples state their hypothetical assumptions.

## Key takeaways
- GPUs expose substantial throughput through parallel work; execution and memory resources depend on the target.
- GPU kernels are written per thread and launched as a grid of blocks; each block runs on one SM and uses that SM's GPU shared memory.
- CUDA warps contain 32 logical threads. Instructions run on active subsets; use explicit synchronisation rather than assuming lockstep.
- Latency is hidden by switching between many resident warps; occupancy is limited by registers, GPU shared memory and block limits.
- Make warps read contiguous memory (coalescing), avoid shared-memory bank conflicts, and keep data on the GPU to avoid PCIe transfers.

## Further reading
- [CUDA C++ Programming Guide — NVIDIA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html)
- [CUDA C++ Best Practices Guide — NVIDIA](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [How to access global memory efficiently in CUDA kernels — NVIDIA blog](https://developer.nvidia.com/blog/how-access-global-memory-efficiently-cuda-c-kernels/)
- [Using shared memory in CUDA — NVIDIA blog](https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/)
- [Single instruction, multiple threads — Wikipedia](https://en.wikipedia.org/wiki/Single_instruction,_multiple_threads)

- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)

- [CUDA warp-level primitives](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
