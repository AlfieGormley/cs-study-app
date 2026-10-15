---
id: par-gpu-resource-occupancy
title: Registers, shared capacity and occupancy
level: intermediate
minutes: 3
sourceLesson: par-gpu
summary: Occupancy is resident warps divided by the target’s maximum.
---

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
N_blk = ⌊164 KiB / (48 KiB)⌋ = 3
where
N_blk: the most blocks that fit by shared-memory capacity
M_SM: the GPU shared memory available for blocks on the SM, in kibibytes (KiB); 164 KiB here
M_blk: the GPU shared memory each block allocates, in KiB; 48 KiB here
KiB: kibibyte, 1,024 bytes
⌊ ⌋: floor: round down to a whole number, because a block cannot be partly resident
In words: three 48 KiB blocks use 144 KiB; a fourth would need 192 KiB, more than the 164 KiB available.
```

Higher occupancy can help hide latency when it exposes more useful independent work. It is not worth maximising for its own sake: additional registers or GPU shared memory per thread may improve reuse enough to outweigh fewer resident warps.

## Key takeaways
- Occupancy is resident warps divided by the target’s maximum.
- Whole blocks, allocation granularity and several resource limits can bind before ideal register arithmetic.

## Further reading
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
