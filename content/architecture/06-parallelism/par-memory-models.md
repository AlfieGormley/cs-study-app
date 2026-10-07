---
id: par-memory-models
title: Multicore memory consistency models
level: intermediate
minutes: 14
summary: Why cores can see each other's writes in surprising orders, how x86-TSO differs from ARM's weaker model, and how fences and acquire/release atomics restore sanity.
---

Cache coherence (from the memory hierarchy module) guarantees that all cores agree on the history of writes to *one* address. It says nothing about the order in which a core sees writes to *different* addresses. That second question is the job of the **memory consistency model**, and mistakes can produce intermittent, platform-dependent bugs.

## The model you expect: sequential consistency

Leslie Lamport defined **sequential consistency** (SC) in 1979. A multicore is SC if the result of any run is the same as if all cores' operations were executed in *some single interleaving*, with each core's operations appearing in program order.

Take two threads and two variables, both initially 0. This is the **store buffering** (SB) litmus test:

```
x = y = 0
Thread 1       Thread 2
x = 1          y = 1
r1 = y         r2 = x
```

Under SC, at least one store must come first in the interleaving, so at least one thread must see a 1. The possible outcomes are (r1, r2) = (0, 1), (1, 0) or (1, 1). **(0, 0) is impossible.**

The x86-TSO model permits (0, 0) for the ordinary-memory accesses described below. A particular experiment need not observe every permitted outcome; failure to observe it does not prove SC.

## Why hardware breaks SC

A store may wait for cache-line ownership or other resources. A **store buffer** can decouple execution/retirement from making committed stores globally observable, allowing independent work to continue while capacity remains. Later loads can execute while earlier stores are still waiting in the buffer.

```
 Core 1               Core 2
 [store buf: x=1]     [store buf: y=1]
      |  r1=y reads 0      |  r2=x reads 0
      v                    v
 ======== shared memory: x=0, y=0 ========
```

Both stores are sitting in buffers, invisible to the other core. Both loads read memory and get 0. Each core's own view is consistent (a same-address load in the abstract model reads its newest buffered store; real **store-to-load forwarding** can require matching size/alignment or waiting), but globally the store appears to have happened after the load.

Out-of-order execution, non-blocking caches and compilers can reorder memory operations too. SC constrains observable outcomes, not necessarily speculative internal execution. Speculation, caches and store buffers can coexist with SC if violations are prevented or detected and recovered. Weaker models allow additional observable behaviours.

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

## ARM: weakly ordered

For ordinary Normal-memory accesses to independent addresses, the AArch64 model permits all four broad reorderings unless a dependency, barrier or ordered instruction constrains them. These labels summarise observable behaviour rather than a physical implementation. The hardware is free to let a later load overtake an earlier one, or to drain stores to memory out of order.

What forces order on ARM:

- **Dependencies.** An actual machine-level address dependency can order the dependent access. A C/C++ source expression such as `p = head; v = p->val` does not by itself establish a safe inter-thread publication protocol; use appropriate atomics and lifetime rules.
- **Barriers.** For the relevant observers in the inner-shareable domain, `DMB ISH` orders the required earlier and later data accesses; it is not an instruction barrier or a general cache flush. `DMB ISHST` orders stores with stores; `DMB ISHLD` orders loads with later loads and stores.
- **Acquire and release instructions.** `LDAR` (load-acquire) prevents later accesses moving before it. `STLR` (store-release) prevents earlier accesses moving after it. FEAT_LRCPC provides `LDAPR`, an RCpc acquire with weaker ordering in some patterns than `LDAR`; instruction availability and performance depend on the target.

The classic victim is **message passing** (MP):

```
data = flag = 0
Thread 1         Thread 2
data = 42        r1 = flag
flag = 1         r2 = data
```

Can Thread 2 see r1 = 1 and r2 = 0, that is, the flag set but the data stale? On x86, no: stores leave in order, and loads are not reordered with loads. On ARM, yes: either the two stores or the two loads may be reordered. These are machine-level litmus tests. Using unsynchronised ordinary shared C/C++ objects would already be a data race and undefined behaviour on either target.

### Multi-copy atomicity

A subtler property is **other-multi-copy atomicity**: after a write becomes observable to another observer, the model requires a consistent propagation order to the remaining observers, while the issuing thread may read its own buffered write early. This is not a zero-latency physical event. The revised Armv8-A model described by Pulte et al. and x86-TSO have this property.

For the **IRIW** test, two writers independently update x and y, while two readers read them in opposite orders. If each reader’s loads are suitably ordered at the hardware level, a multicopy-atomic model forbids the readers from observing opposite write orders. A non-multicopy-atomic model can allow it. Language-level acquire operations and different hardware barriers are not interchangeable; specify the actual mapping when comparing architectures.

## Language memory models

You rarely write fences in assembly. C11/C++11, Java, Rust and Go define their own memory model, and the compiler emits whatever each CPU needs. The C/C++ model has two big rules:

1. A **data race** (potentially concurrent conflicting actions, at least one non-atomic, with neither happening before the other) is undefined behaviour.
2. **DRF-SC:** programs that use mutexes and seq_cst operations to prevent data races, and no other weaker synchronisation operations, behave as if sequentially consistent.

Weaker orderings trade simplicity for speed:

| Order | Guarantee |
|---|---|
| `relaxed` | Atomicity and per-object coherence; no publication of unrelated data |
| `release` (store) | Earlier accesses stay before it |
| `acquire` (load) | Later accesses stay after it |
| `seq_cst` | Appropriate acquire/release effects plus one order of seq_cst operations |

Here is one-shot message passing in C11. Assume exactly one producer call and one consumer call, objects initialised before the threads start, and no later concurrent modification or reuse of data. The snippet supplies the thread bodies, not thread creation. The release store "publishes" everything written before it; an acquire load that reads the published value "sees" all of it.

```c
#include <stdatomic.h>
#include <stdio.h>

int data;          /* plain variable */
atomic_int ready;  /* the flag */

void producer(void) {
  data = 42;
  atomic_store_explicit(&ready, 1,
      memory_order_release);
}

void consumer(void) {
  while (!atomic_load_explicit(&ready,
             memory_order_acquire))
    ;  /* spin */
  printf("%d\n", data);  /* always 42 */
}
```

Illustrative compiler mappings for naturally aligned, lock-free 32-bit atomics on ordinary memory (compiler, target features and whether the result is used can change them):

| C11 operation | x86-64 | ARMv8 |
|---|---|---|
| load acquire | `mov` | `ldar` / `ldapr` |
| store release | `mov` | `stlr` |
| store seq_cst | `xchg` | `stlr` |
| seq_cst fetch_add, result used | `lock xadd` | `ldaddal` with LSE, or exclusive loop |

For such x86 loads/stores, acquire/release may need no extra hardware instruction beyond MOV, but still constrain compiler transformations and carry ordinary memory-access costs. A common seq_cst-store mapping uses memory XCHG or MOV followed by MFENCE. AArch64 mappings using STLR followed by LDAR provide stronger ordering than the minimum language release/acquire requirement; this does not make all atomics cheap. LSE atomics require target support; other mappings use exclusive-load/store loops or library helpers.

> [!warning] Acquire/release does not by itself forbid store buffering
> At the C/C++ language level, both acquire loads in SB may read the initial zeros, so neither reads from the other thread’s release store. There is no synchronises-with edge connecting the threads, and (0, 0) remains permitted. A particular target mapping may be stronger and forbid it. Making all four operations seq_cst is one sufficient solution; correctly placed seq_cst fences or a suitable lock protocol are alternatives. A hardware fence alone does not repair a C/C++ data race on ordinary objects.

## Pitfalls

- **`volatile` is not a synchronisation tool in C or C++.** Volatile accesses obey their language-specific observable-access rules, but do not supply C/C++ inter-thread atomicity or synchronisation. Java volatile has different synchronisation semantics; that does not make an arbitrary racy Java program sequentially consistent.
- **The compiler reorders too.** Even on x86, plain `data = 42; flag = 1;` may be swapped by the optimiser. A correctly designed atomic protocol constrains both compiler and hardware behaviour; merely changing a variable to atomic does not fix every protocol.
- **"Works on my machine."** Testing on x86 cannot find bugs that only weak ordering exposes. Run concurrency tests on ARM, and use ThreadSanitizer to catch data races.
- **Relaxed is for counters.** An atomic fetch_add with relaxed ordering can accumulate an independent statistic without lost increments; separate load-plus-store is not an atomic increment. Publishing unrelated data through a flag needs additional synchronisation.
- **seq_cst by default.** Use the default ordering unless profiling shows the barrier matters. Measure any claimed performance benefit before weakening a proven protocol.

> [!note] Evidence limits
> Rosetta performance attribution and a version-independent Linux spinlock instruction catalogue is omitted because the exact implementation contracts and representative measurements were not reliably established; model-level ordering is taught instead.

## Key takeaways
- Coherence orders writes to one address; the consistency model orders accesses to different addresses.
- SC is an observable ordering model. Letting a later load bypass an earlier buffered store can produce non-SC outcomes.
- x86-TSO allows only store → load reordering, so the store-buffering test can return (0, 0). MFENCE or a locked instruction prevents it.
- ARMv8 allows all four reorderings for independent addresses; use dependencies, DMB, or LDAR/STLR to impose order. Message-passing code that works on x86 can fail on ARM.
- In C/C++, data races are undefined behaviour. Race-free code using mutexes and seq_cst operations, without weaker synchronisation, has the DRF-SC guarantee. A correct release/acquire protocol can publish data; acquire/release alone does not exclude SB.

## Further reading
- [x86-TSO: a rigorous and usable programmer's model (Sewell et al., CACM)](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [Weak vs strong memory models — Preshing on Programming](https://preshing.com/20120930/weak-vs-strong-memory-models/)
- [Memory reordering caught in the act — Preshing on Programming](https://preshing.com/20120515/memory-reordering-caught-in-the-act/)
- [std::memory_order — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Linux kernel memory barriers documentation](https://www.kernel.org/doc/Documentation/memory-barriers.txt)

- [Armv8 multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)

- [C++ draft: data races](https://eel.is/c++draft/intro.races)

- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
