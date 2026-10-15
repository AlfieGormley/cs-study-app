---
id: sync-memory-ordering-atomicity-and-compiler
title: Atomicity and compiler assumptions
level: advanced
minutes: 3
summary: Distinguish atomic updates from volatile accesses and a data-racing polling loop.
sourceLesson: sync-memory-ordering
---

So far, locks have hidden a question you can no longer ignore: when one thread writes memory, **when, and in what order, do other threads see those writes?**

You might assume each thread's operations happen in program order and every core sees one shared, up-to-date memory. That model is called **sequential consistency** (Lamport, 1979). Uncoordinated accesses do not generally provide that model; language rules and hardware ordering permit optimizations. The performance effect of stronger ordering depends on the target and workload. This lesson explains what they do instead, and how to get back the guarantees you need.

## Atomic operations

An **atomic operation** is indivisible: no other thread can observe it half done. C11 provides them in `<stdatomic.h>`:

```c
#include <stdatomic.h>

atomic_int hits = 0;

void on_request(void) {
    // One atomic read-modify-write per
    // request.
    atomic_fetch_add(&hits, 1);
}
```

For supported scalar atomic types, compilers commonly use `lock xadd` or `lock add` on x86 and an LL/SC loop or LSE `ldadd` on AArch64. Unlike `hits++` on a plain `int`, it never loses an update and is not a data race.

For some atomic types, an implementation may use internal locks; the atomic API does not universally promise lock-free machine instructions. Atomicity solves indivisible access to the atomic object. It does **not**, on its own, say anything about the order in which *other* memory operations become visible. That is memory ordering.

## Who reorders, and why

### The compiler

Within one thread, the compiler may reorder, merge or delete memory accesses as long as the single-threaded result is unchanged. It assumes there are no data races, because a data race is undefined behaviour.

```c
int ready = 0;     // plain int: a bug

void wait_ready(void) {
    while (!ready)
        ;   // compiler may load once
}
```

In an invalid program that concurrently writes this plain flag without synchronisation, the behaviour is undefined. Hoisting its load is one illustrative compiler transformation; the resulting behaviour is not restricted to that symptom.

C/C++ `volatile` constrains access to volatile objects according to the implementation’s documented rules, but supplies **no inter-thread atomicity or synchronisation** for these plain accesses. It is meant for memory-mapped hardware, not threads. (Java's `volatile` is different and does provide ordering.)

## Key takeaways

- Atomic read-modify-write avoids lost counter updates, subject to representing the result.
- C volatile does not supply the atomicity or synchronisation needed for shared-thread state.
- A data-racing plain polling loop has undefined behaviour; a particular assembly symptom is only illustrative.

## Further reading

- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Linux memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)
- [The Double-Checked Locking declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Java memory model specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [The Go memory model](https://go.dev/ref/mem)
