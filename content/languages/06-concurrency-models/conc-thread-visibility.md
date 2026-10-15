---
id: conc-thread-visibility
title: Publishing writes between Java threads
level: basic
minutes: 3
sourceLesson: conc-threads-shared-memory
summary: A plain stop flag can stay invisible to another thread.
---

Mutual exclusion is only one job of synchronization. This unit studies whether a different Java thread may observe a write, using the Java Language Specification’s ordering rules.

## Visibility: the bug that is not about interleaving

Locks are not only about taking turns. They are also about **memory visibility**: making one thread's writes visible to another.

```java
// Plain reads have no publication edge.
class Worker {
  boolean stop = false;  // not volatile

  void run() {
    while (!stop) { }    // may spin forever
  }
}
```

Another thread sets `stop = true`, yet the loop may never end. Nothing in the loop body writes `stop`, so the JIT compiler is allowed to read it once and move the loop-invariant check outside the loop. Separately, CPUs buffer writes and caches can make them appear late, or out of order, to other cores.

For example, declare the shared field `volatile boolean stop = false`, then write it from the controlling thread. Java volatile imposes synchronization-order visibility and prevents treating the field as loop-invariant. Correctly using the same lock for both reads and writes, or AtomicBoolean, also provides ordering. This is not a wall-clock latest-value or scheduling guarantee.

## Publishing more than a flag

Suppose a producer writes a plain integer `data`, then sets a Java volatile flag `ready` to true. A consumer checks `ready`, and only if it reads true does it print `data`. If the producer is the only writer, starts from data zero and publishes data 42 once, that branch prints 42: program order and volatile synchronization carry the earlier data write across threads. The consumer may instead read false and skip the branch.

The flag protects publication; it does not make later mutations to the data safe. Reusing a boolean flag for repeated hand-offs needs a protocol that prevents a producer overwriting data while a consumer still uses it. Nor does volatile guarantee that the operating system schedules a waiting thread promptly. Keep language ordering, task progress and wall-clock latency as separate questions.

## Key takeaways
- A plain stop flag can stay invisible to another thread.
- Java volatile publishes earlier writes without making compound updates atomic.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/threading.html)
- [Primary source: docs.oracle.com](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Primary source: go.dev](https://go.dev/ref/mem)
- [Primary source: eel.is](https://eel.is/c++draft/intro.races)
