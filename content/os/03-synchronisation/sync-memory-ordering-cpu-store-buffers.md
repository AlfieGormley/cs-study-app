---
id: sync-memory-ordering-cpu-store-buffers
title: Store buffers and weak ordering
level: advanced
minutes: 3
summary: Compare a sequentially consistent store-buffering trace with hardware-permitted outcomes.
sourceLesson: sync-memory-ordering
---

CPU memory ordering and the C language memory model answer different questions. A literal assembly litmus test can demonstrate a hardware-permitted result without making a racing C translation valid.

### The CPU

Modern cores execute out of order, and each core has a **store buffer**: writes are queued there and drained to cache later, so the core does not stall on every store. Loads can complete before earlier stores have left the buffer.

This simplified table concerns ordinary accesses to coherent normal cacheable memory, not every memory type, special instruction or dependency rule:

| Reordering | x86-64 | ARMv8 |
|---|---|---|
| load → load | no | yes |
| load → store | no | yes |
| store → store | no | yes |
| store → load | **yes** | yes |

x86's model is called **TSO** (total store order): the only visible reordering is a later load passing an earlier store to a different address. ARM and POWER are **weakly ordered**, allowing more independent-access reorderings under their specified memory types, dependencies and barriers. Code that "works on my laptop" (x86) can break on ARM servers or phones.

## Two litmus tests

### Store buffering

```
x = y = 0
Thread 1        Thread 2
x = 1           y = 1
r1 = y          r2 = x
```

Under sequential consistency at least one thread sees the other's write, so `r1 == 0 && r2 == 0` is impossible. On real x86 it **happens**: both stores sit in store buffers while both loads read 0 from cache. This can break a literal load/store implementation of Peterson’s algorithm; the earlier plain C version already has data races.

In the machine-code model, a full fence between the store and load in each thread forbids that result (for example mfence on x86). In C, first use valid atomic accesses; a hardware fence does not legalize races on plain objects.

## Key takeaways

- The hardware table assumes ordinary coherent normal cacheable memory and independent accesses.
- Store buffering can permit both loads to see zero on x86 as well as weaker targets.
- Language-level C data races remain undefined even when a hardware trace looks plausible.

## Further reading

- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Linux memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)
- [The Double-Checked Locking declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Java memory model specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [The Go memory model](https://go.dev/ref/mem)
