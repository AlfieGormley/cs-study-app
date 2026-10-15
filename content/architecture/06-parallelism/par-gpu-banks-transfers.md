---
id: par-gpu-banks-transfers
title: Shared-memory banks and end-to-end GPU costs
level: intermediate
minutes: 4
sourceLesson: par-gpu
summary: Padding a 32-float row to 33 shifts successive rows across banks in the stated model.
---

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
- Padding a 32-float row to 33 shifts successive rows across banks in the stated model.
- Include transfers, launch overhead and numerical requirements in end-to-end decisions.

## Further reading
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
