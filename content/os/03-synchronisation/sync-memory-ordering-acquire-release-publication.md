---
id: sync-memory-ordering-acquire-release-publication
title: Publish data with release and acquire
level: advanced
minutes: 3
summary: Use an observing acquire load to order access to a plain payload.
sourceLesson: sync-memory-ordering
---

To publish an object, atomic access to its flag is only part of the protocol. The reader also needs the ordering edge that makes the earlier payload writes safe to read.

### The message-passing test

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
// No synchronisation orders the plain data.
// This deliberately broken C example has
// UB.
printf("%d\n", data);  // no promised value
```

Assume one producer and one consumer, initialised globals and no other accesses. The plain data accesses lack a happens-before edge and therefore race: the C program has undefined behavior, not merely a choice between 0 and 42. Weakly ordered machine traces explain one possible stale-read symptom but do not bound C behavior.

## Acquire and release

With one producer and one consumer, initialised globals and no other accesses, the fix uses an observing acquire. If the consumer reaches the print, the payload is 42:

```c
// producer
data = 42;
atomic_store_explicit(&ready, 1,
    memory_order_release);

// consumer
while (!atomic_load_explicit(&ready,
          memory_order_acquire))
    ;
// If this line is reached, the observing
// acquire orders the earlier payload write.
printf("%d\n", data);  // 42
```

The following movement rules are a useful reasoning model for observable ordering, not a ban on every compiler transformation that preserves the language contract.

- A **release store** orders earlier writes before accesses after a matching observing acquire. Think of those earlier accesses as staying before publication.
- An **acquire load** orders its later accesses after the release it observes. Think of those later accesses as staying after observation.
- If an acquire load **reads the value written by** a release store, the two establish a **synchronises-with** edge: everything before the release is visible to everything after the acquire.

```
producer            consumer
data = 42
  |  (stays above)
release ready=1 ---> acquire sees 1
                       | (stays below)
                     read data -> 42
```

The names come from locks. Taking a lock is an acquire (the critical section cannot leak upwards out of it); releasing it is a release (the critical section cannot leak downwards). Correct standard mutex use supplies the synchronization needed for protected accesses. Applications must still coordinate object lifetime, initialization and every piece of code that touches the data; having a lock somewhere is not enough.

For ordinary supported scalar atomics on coherent normal memory, x86 compilers commonly use plain `mov` for acquire loads and release stores. AArch64 commonly uses `ldar` and `stlr`; exact code generation depends on type, target and compiler.

## Key takeaways

- A relaxed flag alone does not order plain payload accesses.
- An acquire that observes the release publication links earlier writes to later reads.
- Assuming successful one-time publication and no competing accesses, the consumer prints 42 if it reaches the print.

## Further reading

- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Linux memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)
- [The Double-Checked Locking declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Java memory model specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [The Go memory model](https://go.dev/ref/mem)
