---
id: par-x86-tso
title: The scope and guarantees of x86-TSO
level: intermediate
minutes: 3
sourceLesson: par-memory-models
summary: The stated TSO model covers ordinary aligned same-size write-back accesses.
---

## x86-TSO: only one relaxation

x86 implements **total store order** (TSO), formalised by Sewell, Owens and colleagues as x86-TSO. Here the model covers aligned, same-size ordinary loads/stores in coherent write-back memory, excluding non-temporal accesses, MMIO, mixed-size overlap and self-modifying code. It is essentially "SC plus a FIFO store buffer per hardware thread":

- Stores leave each core's buffer **in program order** and enter a single global order visible to other threads. This is an abstract ordering guarantee, not zero propagation delay or wall-clock simultaneity.
- A load can complete while older stores to *other* addresses are still buffered. So **store → load** reordering is visible.
- Loads are not reordered with older loads; stores are not reordered with older loads or older stores.

| Reordering | x86-TSO | ARMv8 |
|---|---|---|
| Load → load | No | Yes |
| Load → store | No | Yes |
| Store → store | No | Yes |
| Store → load | **Yes** | Yes |

To forbid store → load reordering on x86, insert `MFENCE` (drain the store buffer before later loads) or use any `LOCK`-prefixed instruction such as `lock xadd`, or `xchg` with memory, which is implicitly locked. All of these act as full barriers.

## Tracing the store-buffering outcome

Start with both shared words zero. Each hardware thread places its store in its own abstract FIFO buffer. Before either buffered store drains, each thread loads the other word from memory. Both loads can therefore return zero. A later drain makes both words one, but that does not retroactively change the values already read.

A load of the same word instead sees the issuing thread's newest buffered value in this abstract model. The different-address qualification matters: a store buffer is not permission for a thread to ignore its own earlier write to the same word.

This matters to two-participant algorithms such as Peterson's lock. The source order “publish my flag, then inspect the other flag” is insufficient at this hardware level if the inspection can bypass the buffered publication. A correctly positioned full barrier can establish the missing store-before-load order. The complete algorithm must also satisfy its language's atomicity and ordering rules; an assembly argument does not legalise unsynchronised C or C++ objects.

The release direction is different: earlier ordinary loads and stores already precede a later ordinary store in the stated TSO model. That is why a compiler can implement a suitable language release store using a plain MOV while still preserving the required compiler ordering.

## Key takeaways
- The stated TSO model covers ordinary aligned same-size write-back accesses.
- Store-to-load reordering needs a suitable fence or locked operation when the algorithm requires that order.

## Further reading
- [Lamport’s original sequential-consistency paper](https://lamport.azurewebsites.net/pubs/multi.pdf)
- [The x86-TSO model](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [The revised Arm multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)
- [C++ draft: races](https://eel.is/c++draft/intro.races)
- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
