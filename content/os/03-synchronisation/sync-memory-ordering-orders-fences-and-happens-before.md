---
id: sync-memory-ordering-orders-fences-and-happens-before
title: Orderings, fences and happens-before
level: advanced
minutes: 4
summary: Choose counter ordering and trace synchronisation edges across threads.
sourceLesson: sync-memory-ordering
---

Memory order is part of the algorithm’s correctness argument. The store-buffering test starts two atomic variables at zero; each thread stores one to its own variable and then loads the other.

## The C11 orderings

| Order | Guarantee | Use |
|---|---|---|
| `relaxed` | atomic only | counters |
| `acquire` | later ops stay later | lock, read flag |
| `release` | earlier ops stay earlier | unlock, publish |
| `acq_rel` | both, for RMW | CAS in a lock |
| `seq_cst` | one global order | default |

C11 also defines `memory_order_consume`. Mainstream compiler implementations have generally strengthened it to acquire; avoid relying on a cheaper dependency-only mapping without checking the compiler and language version.

**Sequentially consistent** (`seq_cst`) is the default for every atomic operation without `_explicit`. All `seq_cst` operations appear in a single total order agreed by every thread. Using seq_cst for all four operations in this litmus test forbids both loads seeing zero. Other correctly constructed synchronization protocols or fence placements can also forbid it. For ordinary scalar atomics, x86 compilers commonly implement a sequentially consistent store using `xchg` or a suitable fenced sequence. Costs depend on hardware, contention and surrounding code; no universal timing ratio is asserted.

Relaxed is fine when you need the value to be correct but nothing else to be ordered with it, such as a statistics counter read after all threads are joined.

> [!tip] Default to seq_cst
> Use the default orderings until a profiler proves the fence matters. Weaker orderings are an optimisation with a high cost in reasoning, and bugs in them often appear only on one architecture under load.

## Fences

A **fence** (memory barrier) orders memory operations without being attached to a particular variable: `atomic_thread_fence(memory_order_seq_cst)` in C11. Hardware equivalents include x86 `mfence` and ARM `dmb ish`. The Linux kernel has its own family (`smp_mb()`, `smp_wmb()`, `smp_rmb()`, `smp_store_release()`, `smp_load_acquire()`), documented at length in `memory-barriers.txt`.

There is also a **compiler-only barrier**, such as `asm volatile("" ::: "memory")` in GCC, which stops the compiler moving accesses across it but emits no instruction.

## Happens-before

The formal model ties this together. The **happens-before** relation is built from:

1. **Sequenced-before**: within one thread, program order.
2. **Synchronises-with**: a release store and an acquire load that reads its value; an unlock and a later lock of the same mutex; `pthread_create` and the start of the new thread; a thread's end and `pthread_join` returning.
3. **Transitivity**: happens-before chains, as the formula below shows.

Writing an arrow for "happens-before":

```formula
A → B and B → C gives A → C
where
A: an operation in some thread, such as a write, a read, a lock or an unlock
B: a second operation
C: a third operation, possibly in yet another thread
→: happens-before: the operation on the left is guaranteed to be ordered before, and visible to, the operation on the right
In words: ordering links join up, so if A is ordered before B and B before C, then A is ordered before C, even when A and C share no direct synchronisation.
```

The earlier message-passing unit supplies one such chain. The write `data = 42` is sequenced-before the release store; the release store synchronises-with the acquire load that reads 1; the acquire load is sequenced-before the read of `data`. Chaining the three edges gives "the write of 42 happens-before the read", so if the consumer reaches the print, it prints 42.

The rule that matters: if a write happens-before a read of the same location (and no other write intervenes), the read sees that write. If two conflicting accesses are **not** ordered by happens-before and are not both atomic, you have a data race, and in C, C++ and Rust that is undefined behaviour. Java and Go define similar happens-before rules; Java gives racy programs weaker but defined semantics rather than UB.

## Key takeaways

- Relaxed counters need no payload-publication edge when the final read follows thread joins.
- Using sequentially consistent operations throughout the store-buffering test excludes the both-zero result.
- Happens-before chains through sequenced-before and synchronises-with; elapsed time alone supplies no edge.

## Further reading

- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Linux memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)
- [The Double-Checked Locking declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Java memory model specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [The Go memory model](https://go.dev/ref/mem)
