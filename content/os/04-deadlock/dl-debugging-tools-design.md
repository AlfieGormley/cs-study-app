---
id: dl-debugging-tools-design
title: User-space checkers and prevention by design
level: advanced
minutes: 4
sourceLesson: dl-debugging
summary: Supported TSan runtimes and Helgrind can check observed lock-order inversions.
---

## ThreadSanitizer and friends

User space has similar tools.

**ThreadSanitizer** (`-fsanitize=thread`) primarily detects data races. Some runtimes also support an experimental lock-order detector for supported pthread primitives, reporting `lock-order-inversion (potential deadlock)`. Check the compiler/runtime and enable `TSAN_OPTIONS=detect_deadlocks=1`; do not assume all platforms, versions or custom locks support it. Clang documents typical overall TSan costs of roughly 5–15 times the running time and 5–10 times the memory use; these are broad tool estimates, not a benchmark for this example.

```c
// Fragment: include <pthread.h>.
// Compile with -fsanitize=thread.
pthread_mutex_t a =
    PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t b =
    PTHREAD_MUTEX_INITIALIZER;

// Run sequentially to observe both orders.
void *t1(void *x) {
    pthread_mutex_lock(&a);
    pthread_mutex_lock(&b);
    pthread_mutex_unlock(&b);
    pthread_mutex_unlock(&a);
    return NULL;
}

// Reverse order forms a potential cycle.
void *t2(void *x) {
    pthread_mutex_lock(&b);
    pthread_mutex_lock(&a);
    pthread_mutex_unlock(&a);
    pthread_mutex_unlock(&b);
    return NULL;
}
```

With the lock-order detector available and enabled, running `t1` to completion and then `t2` can report `a => b => a` without an actual deadlock. Both acquisition orders must be observed in the same instrumented process; separate executions do not share the graph.

Others in the same family:

- **Helgrind** (Valgrind) reports lock-order violations too, without recompiling, with workload-dependent overhead.
- **Abseil's** `absl::Mutex` checks for lock-order cycles itself in debug builds.
- The **Go race detector** is built on TSan's runtime but does *not* report lock-order inversions; Go relies on dumps and code review.

### Exploring interleavings

Order checkers only see what runs. To find bugs on paths that are hard to reach by chance, **model checkers** run a concurrent test under every (or many) possible interleavings:

- **loom** for Rust replaces `std::sync` types in tests and systematically explores schedules.
- A model checker such as the **TLC model checker** checks a design written in **TLA+** before you write implementation code; AWS has used it for S3 and DynamoDB internals.

## Designing deadlock out

Tools catch mistakes. Design makes mistakes rare. Useful rules include:

1. **Avoid nested lock acquisition.** Copy what you need, release, then act, while preserving data invariants. A single non-reentrant lock can still self-deadlock; communication and pool dependencies also matter.
2. **Never call unknown code while holding a lock.** Callbacks, listeners, virtual methods and library calls can take locks you don't know about. *Java Concurrency in Practice* calls the fix **open calls**: calls made with no locks held.
3. **Never block while holding a lock.** No I/O, `join()`, `queue.put()` on a bounded queue, or RPC inside a critical section.
4. **When you must nest, order.** Document a global order or hierarchy (the prevention lessons) and enforce it with a checker: lockdep, TSan, or a debug-mode `LevelLock`.
5. **Prefer ownership to sharing.** Exclusive ownership can remove locks around that data, though background I/O, shared state and re-entrant callbacks still require coordination. Redis largely serializes command execution while also using background work and optional I/O threads. Message passing helps, though actors that make *synchronous* requests to each other can still deadlock in a cycle.
6. **Don't wait on your own pool.** A task that submits a sub-task to the same bounded pool and waits for it can exhaust the pool (the deadlock fundamentals lessons). Use separate pools per stage, or non-blocking composition (futures, `async`).
7. **Timeouts as a backstop, not a design.** `acquire(timeout=...)`, `lock_timeout` and RPC deadlines turn a permanent hang into an error you can log and alert on.
8. **Databases**: short transactions, touch rows in a consistent order (`ORDER BY id ... FOR UPDATE`), use `NOWAIT` or `SKIP LOCKED` for queue-like workloads, and use bounded, safe whole-transaction retries when appropriate. A timeout needs explicit cleanup; InnoDB normally leaves earlier transaction locks held after a statement timeout.

> [!example] An illustrative failure pattern
> An application cache calls an `on_evict` callback while holding its internal lock. A team adds a callback that writes to a metrics registry, which takes its own lock. Elsewhere, the metrics exporter, holding the registry lock, reads application cache stats, which takes the application cache lock. Application cache → registry and registry → application cache: a deadlock under load. The fix is rule 2: collect evicted entries under the lock, release it, *then* run callbacks.

## Key takeaways
- Supported TSan runtimes and Helgrind can check observed lock-order inversions.
- Schedule exploration and design models complement ordinary execution tests.
- Avoid unknown callbacks, blocking and same-pool waits under locks; enforce necessary nested ordering.

## Further reading
- [Clang: ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [Valgrind: Helgrind lock-order checks](https://valgrind.org/docs/manual/hg-manual.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
