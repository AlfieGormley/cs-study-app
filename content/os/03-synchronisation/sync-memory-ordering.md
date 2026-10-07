---
id: sync-memory-ordering
title: Atomics and memory ordering
level: advanced
minutes: 16
summary: Atomic operations, how compilers and CPUs reorder memory accesses, memory barriers, acquire/release and sequential consistency in C11, happens-before, and why double-checked locking was broken for years.
---

So far, locks have hidden a question you can no longer ignore: when one thread writes memory, **when, and in what order, do other threads see those writes?**

You might assume each thread's operations happen in program order and every core sees one shared, up-to-date memory. That model is called **sequential consistency** (Lamport, 1979). Uncoordinated accesses do not generally provide that model; language rules and hardware ordering permit optimizations. The performance effect of stronger ordering depends on the target and workload. This lesson explains what they do instead, and how to get back the guarantees you need.

## Atomic operations

An **atomic** operation is indivisible: no other thread can observe it half done. C11 provides them in `<stdatomic.h>`:

```c
#include <stdatomic.h>

atomic_int hits = 0;

void on_request(void) {
    atomic_fetch_add(&hits, 1);
}
```

`atomic_fetch_add` compiles to `lock xadd` (or `lock add`) on x86 and to an LL/SC loop or `ldadd` on ARM. Unlike `hits++` on a plain `int`, it never loses an update and is not a data race.

For some atomic types, an implementation may use internal locks; the atomic API does not universally promise lock-free machine instructions. Atomicity solves "half-done" operations. It does **not**, on its own, say anything about the order in which *other* memory operations become visible. That is memory ordering.

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

Since nothing in the loop writes `ready`, the compiler may load it once into a register and spin forever. This is a legal optimisation.

`volatile` forces a real load each time, but in C and C++ it gives **no atomicity and no ordering** relative to other variables. It is meant for memory-mapped hardware, not threads. (Java's `volatile` is different and does provide ordering.)

### The CPU

Modern cores execute out of order, and each core has a **store buffer**: writes are queued there and drained to cache later, so the core does not stall on every store. Loads can complete before earlier stores have left the buffer.

This simplified table concerns ordinary accesses to coherent normal cacheable memory, not every memory type, special instruction or dependency rule:

| Reordering | x86-64 | ARMv8 |
|---|---|---|
| load → load | no | yes |
| load → store | no | yes |
| store → store | no | yes |
| store → load | **yes** | yes |

x86's model is called **TSO** (total store order): the only visible reordering is a later load passing an earlier store to a different address. ARM and POWER are **weakly ordered**: almost anything can be reordered unless you say otherwise. Code that "works on my laptop" (x86) can break on ARM servers or phones.

## Two litmus tests

### Store buffering

```
x = y = 0
Thread 1        Thread 2
x = 1           y = 1
r1 = y          r2 = x
```

Under sequential consistency at least one thread sees the other's write, so `r1 == 0 && r2 == 0` is impossible. On real x86 it **happens**: both stores sit in store buffers while both loads read 0 from cache. This is exactly why Peterson's algorithm from lesson 1 fails.

In the machine-code model, a full fence between the store and load in each thread forbids that result (for example mfence on x86). In C, first use valid atomic accesses; a hardware fence does not legalize races on plain objects.

### Message passing

```c
int data = 0;
atomic_int ready = 0;

// producer
data = 42;
atomic_store_explicit(&ready, 1,
    memory_order_relaxed);

// consumer
while (!atomic_load_explicit(&ready,
          memory_order_relaxed))
    ;
printf("%d\n", data);  // 42? maybe not
```

The plain data accesses lack a happens-before edge and therefore race: the C program has undefined behavior, not merely a choice between 0 and 42. Weakly ordered machine traces explain one possible stale-read symptom but do not bound C behavior.

## Acquire and release

The fix for message passing is the most important pattern in this lesson:

```c
// producer
data = 42;
atomic_store_explicit(&ready, 1,
    memory_order_release);

// consumer
while (!atomic_load_explicit(&ready,
          memory_order_acquire))
    ;
printf("%d\n", data);  // always 42
```

- A **release** store: no memory access before it (in program order) may be moved after it. Everything the thread wrote earlier is "published" with it.
- An **acquire** load: no memory access after it may be moved before it.
- If an acquire load **reads the value written by** a release store, the two **synchronise**: everything before the release is visible to everything after the acquire.

```
producer            consumer
data = 42
  |  (stays above)
release ready=1 ---> acquire sees 1
                       | (stays below)
                     read data -> 42
```

The names come from locks. Taking a lock is an acquire (the critical section cannot leak upwards out of it); releasing it is a release (the critical section cannot leak downwards). Correct standard mutex use supplies the synchronization needed for protected accesses. Applications must still coordinate object lifetime, initialization and all access paths; having a lock somewhere is not enough.

On x86, acquire loads and release stores are plain `mov` instructions, because TSO already provides that ordering; only the compiler is restrained. On ARMv8 they become `ldar` and `stlr`.

## The C11 orderings

| Order | Guarantee | Use |
|---|---|---|
| `relaxed` | atomic only | counters |
| `acquire` | later ops stay later | lock, read flag |
| `release` | earlier ops stay earlier | unlock, publish |
| `acq_rel` | both, for RMW | CAS in a lock |
| `seq_cst` | one global order | default |

(`memory_order_consume` also exists but compilers treat it as acquire, and its use is discouraged.)

**Sequentially consistent** (`seq_cst`) is the default for every atomic operation without `_explicit`. All `seq_cst` operations appear in a single total order agreed by every thread. Using seq_cst for all four operations in this litmus test forbids both loads seeing zero. Other correctly constructed synchronization protocols or fence placements can also forbid it. On x86, a `seq_cst` store compiles to `xchg` (or `mov` plus `mfence`), which is noticeably more expensive than a plain `mov`.

Relaxed is fine when you need the value to be correct but nothing else to be ordered with it, such as a statistics counter read after all threads are joined.

> [!tip] Default to seq_cst
> Use the default orderings until a profiler proves the fence matters. Weaker orderings are an optimisation with a high cost in reasoning, and bugs in them often appear only on one architecture under load.

## Fences

A **fence** (barrier) orders memory operations without being attached to a particular variable: `atomic_thread_fence(memory_order_seq_cst)` in C11. Hardware equivalents include x86 `mfence` and ARM `dmb ish`. The Linux kernel has its own family (`smp_mb()`, `smp_wmb()`, `smp_rmb()`, `smp_store_release()`, `smp_load_acquire()`), documented at length in `memory-barriers.txt`.

There is also a **compiler-only** barrier, such as `asm volatile("" ::: "memory")` in GCC, which stops the compiler moving accesses across it but emits no instruction.

## Happens-before

The formal model ties this together. The **happens-before** relation is built from:

1. **Sequenced-before**: within one thread, program order.
2. **Synchronises-with**: a release store and an acquire load that reads its value; an unlock and a later lock of the same mutex; `pthread_create` and the start of the new thread; a thread's end and `pthread_join` returning.
3. **Transitivity**: if A happens-before B and B happens-before C, then A happens-before C.

The rule that matters: if a write happens-before a read of the same location (and no other write intervenes), the read sees that write. If two conflicting accesses are **not** ordered by happens-before and are not both atomic, you have a data race, and in C, C++ and Rust that is undefined behaviour. Java and Go define similar happens-before rules; Java gives racy programs weaker but defined semantics rather than UB.

## The double-checked locking bug

Lazy initialisation of a shared singleton is a classic. To avoid locking an already-initialized fast path, programmers wrote:

```c
Singleton *instance = NULL;   // plain

Singleton *get(void) {
    if (instance == NULL) {          // 1
        lock(&m);
        if (instance == NULL)        // 2
            instance = make();       // 3
        unlock(&m);
    }
    return instance;
}
```

The idea: check without the lock (fast path); if it looks uninitialised, take the lock and check again.

It is broken: the unlocked plain pointer read races with publication in C. One illustrative failure is incomplete publication. Line 3 performs two kinds of write: the writes inside `make()` that fill in the object's fields, and the write of the pointer into `instance`. Nothing stops the pointer store becoming visible to another thread **before** the field stores (the compiler can reorder them, and so can a weakly ordered CPU). A second thread then passes check 1, sees a non-null pointer, skips the lock entirely, and reads uninitialised fields.

The famous "Double-Checked Locking is Broken" declaration, signed by Bill Pugh and a group of Java and concurrency researchers, showed that no clever variation could fix it under the old Java memory model. The fixes all add the missing acquire/release pair:

- **C11**: make `instance` an `_Atomic(Singleton *)`, load it with `memory_order_acquire`, store it with `memory_order_release`.
- **Java 5+**: declare the field `volatile` (JSR-133 gave volatile acquire/release semantics).
- **C++11**: just use a function-local `static`; its initialisation is guaranteed thread-safe ("magic statics").
- **POSIX**: `pthread_once`.
- **Python**: initialise at module import, or use a lock; `functools.cache` alone does not promise the function runs only once under concurrency.

```c
_Atomic(Singleton *) instance;

Singleton *get(void) {
    Singleton *p = atomic_load_explicit(
        &instance, memory_order_acquire);
    if (p == NULL) {
        lock(&m);
        p = atomic_load_explicit(&instance,
            memory_order_relaxed);
        if (p == NULL) {
            p = make();
            atomic_store_explicit(&instance,
                p, memory_order_release);
        }
        unlock(&m);
    }
    return p;
}
```

The inner load can be relaxed because the mutex already orders it after any previous initialiser's unlock.

## What this means for Python

Python has no `memory_order`. CPython with the GIL behaves close to sequentially consistent for pure Python code, because only one thread executes bytecode at a time and acquiring the GIL acts as a barrier. Free-threaded CPython currently uses internal locking for many built-ins, but that is not a blanket language-level atomicity contract. In both cases use documented threading and queue protocols for shared invariants. Python does not specify the complete C11 memory model described above.

## Key takeaways
- Atomic means indivisible; ordering is a separate question about when other memory operations become visible.
- Compilers reorder freely in race-free code; CPUs reorder via store buffers and out-of-order execution. x86 only lets loads pass earlier stores; ARM allows nearly everything.
- Release on the publishing store and acquire on the observing load guarantee that everything before the release is visible after the acquire. Locks provide exactly this.
- `seq_cst` (the default) gives one global order and rules out both-zero in this test when all four operations use it; use weaker orders only with evidence.
- Double-checked locking without atomics is broken because the pointer can be published before the object's fields; an acquire/release pair, `pthread_once` or a magic static fixes it.

## Further reading
- [memory_order — cppreference (C)](https://en.cppreference.com/w/c/atomic/memory_order)
- [Acquire and release semantics — Jeff Preshing](https://preshing.com/20120913/acquire-and-release-semantics/)
- [The happens-before relation — Jeff Preshing](https://preshing.com/20130702/the-happens-before-relation/)
- [Linux kernel memory barriers](https://www.kernel.org/doc/Documentation/memory-barriers.txt)
- [The "Double-Checked Locking is Broken" declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Memory barrier — Wikipedia](https://en.wikipedia.org/wiki/Memory_barrier)
- [The Go memory model](https://go.dev/ref/mem)
