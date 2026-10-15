---
id: par-gpu-coalescing
title: GPU memory visibility and coalesced sectors
level: intermediate
minutes: 3
sourceLesson: par-gpu
summary: Contiguous aligned loads can touch fewer requested sectors than strided loads.
---

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

## Key takeaways
- Contiguous aligned loads can touch fewer requested sectors than strided loads.
- Requested sectors are distinct from physical DRAM traffic when caches satisfy accesses.

## Further reading
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
