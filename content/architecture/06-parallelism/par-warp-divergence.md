---
id: par-warp-divergence
title: Warps, divergence and explicit synchronisation
level: intermediate
minutes: 3
sourceLesson: par-gpu
summary: A CUDA warp contains 32 logical threads, not a promise of 32 simultaneous physical ALUs.
---

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

## Key takeaways
- A CUDA warp contains 32 logical threads, not a promise of 32 simultaneous physical ALUs.
- Use explicit primitives rather than assuming implicit lockstep communication.

## Further reading
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
