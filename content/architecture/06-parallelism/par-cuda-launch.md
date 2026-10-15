---
id: par-cuda-launch
title: CUDA kernels, blocks and array indices
level: intermediate
minutes: 4
sourceLesson: par-gpu
summary: A thread computes a global index; a tail guard excludes surplus launch threads.
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
  /* Skip all earlier blocks. */
  size_t i = (size_t)blockIdx.x * blockDim.x
           + threadIdx.x;
  /* Exclude surplus launch threads. */
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
N_blocks = ⌈1,000 / 256⌉
N_blocks = ⌈3.90625⌉ = 4
where
N_blocks: the number of blocks launched
n: the number of array elements; 1,000 in the example
N_b: the number of threads per block; 256
⌈ ⌉: ceiling: round up to the next whole number
In words: launch enough blocks that blocks times threads per block is at least the element count; the surplus threads (here 4 × 256 − 1,000 = 24) fail the i < n guard and do nothing.
```

## Key takeaways
- A thread computes a global index; a tail guard excludes surplus launch threads.
- Ordinary blocks must be independently schedulable; barrier participation matters.

## Further reading
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
