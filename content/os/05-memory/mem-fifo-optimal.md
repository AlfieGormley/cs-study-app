---
id: mem-fifo-optimal
sourceLesson: mem-page-replacement
title: Tracing FIFO and the optimal benchmark
level: intermediate
minutes: 4
summary: A reference string and frame budget let replacement policies be compared consistently.
---

Demand paging and swap (earlier units) let processes use more memory than the machine has. The price is a decision the kernel must make constantly: when a page fault needs a free frame and none is left, **which page do we evict?**

Choose well and the evicted page is not needed for a long time. Choose badly and you evict something that is needed a microsecond later, potentially paying a storage-backed refault to bring it back.

This is the same problem as cache eviction, with two differences that shape the answers:

- **A miss is enormous.** A storage-backed fault can be much slower than a resident memory access, so it is worth spending CPU on a good choice.
- **The hardware gives almost no help.** The CPU does not tell the OS about every access; it just sets the **accessed (A)** bit in a PTE. Practical policies can combine access-bit sampling with refault history, software-observed accesses and other signals.

## The setup

We measure policies on a **reference string**: the sequence of pages a program touches. With a fixed number of frames, count the **page faults**. Fewer is better. With initially empty frames and no prefetching, the first touch of each page faults (a *compulsory* miss); the policies differ on the rest.

Throughout, we use this string and **3 frames**:

```
1 2 3 1 4 1 2 5
```

## FIFO

Evict the page that has been in memory longest. It is trivial to implement as a queue.

| Ref | Frames | Fault? |
|---|---|---|
| 1 | 1 | F |
| 2 | 1 2 | F |
| 3 | 1 2 3 | F |
| 1 | 1 2 3 | hit |
| 4 | 2 3 4 | F (evict 1) |
| 1 | 3 4 1 | F (evict 2) |
| 2 | 4 1 2 | F (evict 3) |
| 5 | 1 2 5 | F (evict 4) |

**7 faults.** FIFO's flaw is visible at reference 4: it evicted page 1, the most popular page, simply because it arrived first. Age of arrival says nothing about usefulness.

## OPT: the optimal policy

**Belady's optimal algorithm (OPT or MIN)**: evict the page whose next use is *furthest in the future*. It provably gives the fewest faults possible.

| Ref | Frames | Fault? |
|---|---|---|
| 1, 2, 3 | 1 2 3 | F F F |
| 1 | 1 2 3 | hit |
| 4 | 1 2 4 | F (3 never used again) |
| 1 | 1 2 4 | hit |
| 2 | 1 2 4 | hit |
| 5 | 2 4 5 | F (any page) |

**5 faults.** OPT needs to know the future, so no real OS can run it. Its use is as a **yardstick**: simulate a trace offline and see how close a real policy gets.

## Key takeaways
- A reference string and frame budget let replacement policies be compared consistently.
- FIFO evicts by arrival, while OPT uses future accesses as an offline lower bound.

## Further reading
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
