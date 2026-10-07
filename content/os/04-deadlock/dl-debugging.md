---
id: dl-debugging
title: Debugging deadlocks and designing them out
level: advanced
minutes: 15
summary: Diagnosing a hung process with thread dumps, gdb and database lock views, catching lock-order bugs before they bite with lockdep and ThreadSanitizer, and the design rules that keep deadlock out of a codebase.
---

Many concurrency deadlocks depend on timing; others, such as recursive acquisition of a non-reentrant lock, happen deterministically. The faulty lock order can sit in the code for months until the one interleaving that triggers it happens, possibly under production load. Debugging them comes in two halves:

- **After the fact**: a process has hung. Find which threads are stuck, on which locks, held by whom.
- **Before the fact**: tools that spot a lock-order cycle the first time both code paths run, even if they never actually collide.

The second half is far cheaper. This lesson covers both, then the design rules that make the tools rarely fire.

## Step 1: is it really a deadlock?

When a service stops responding, check CPU first (lesson 1's table):

| Observation | Suspect |
|---|---|
| ~0% CPU, stacks never change | Deadlock or lost wake-up |
| High CPU, stacks repeat or change | Livelock, busy loop, or spinning deadlock |
| Some requests finish, some don't | Starvation, or a partial deadlock |
| Blocked in I/O, not locks | Slow dependency or an I/O dependency cycle |

Then take **two or three thread dumps a few seconds apart**. Repeated stacks are evidence of a persistent wait, not proof of deadlock; a legitimate long wait can look the same. Changing stacks can indicate useful progress or livelock. Confirm dependencies and application progress.

## Thread dumps, language by language

The goal is the same everywhere: for each stuck thread, find the lock it's **waiting for** and the locks it **holds**, then draw the wait-for graph by hand.

### Java

For platform threads, use `jstack -l <pid>` or `jcmd <pid> Thread.print -l`; on supported Unix HotSpot JVMs, `kill -3 <pid>` requests a dump to the JVM output. Classic dumps and management deadlock detection do not cover every virtual-thread dependency. The JVM can report current cycles involving object monitors and supported ownable synchronizers:

```
Found one Java-level deadlock:
=============================
"worker-2":
  waiting to lock monitor 0x7f3a...
  (object 0x7128..., a Account),
  which is held by "worker-1"
"worker-1":
  waiting to lock monitor 0x7f3b...
  (object 0x7130..., a Account),
  which is held by "worker-2"
```

(Abridged.) Each thread's stack also shows `- locked <0x...>` lines for the monitors it holds. `ThreadMXBean.findDeadlockedThreads()` exposes detection for platform threads using monitors and supported ownable synchronizers; it does not detect virtual-thread cycles. A watchdog can log and alert on reported cycles.

### Python

Python's `threading.Lock` doesn't record its owner, so a dump shows where threads wait but not who holds the lock. You infer the holder from which thread's stack is inside the matching `with` block.

- `py-spy dump --pid <pid>` prints every thread's Python stack from outside the process, without terminating it. Sampling may briefly pause threads; `--nonblocking` avoids pausing at the cost of potentially inconsistent samples.
- `faulthandler` can dump all threads from inside, on a signal or after a timeout:

```python
import faulthandler
import signal

# kill -USR1 <pid> dumps all threads
faulthandler.register(signal.SIGUSR1)

# watchdog: dump if still running in 60 s
faulthandler.dump_traceback_later(
    60, exit=False)
```

### Go

The runtime notices one special case itself: if the scheduler finds no runnable work or supported source of future wakeups, it may crash with `fatal error: all goroutines are asleep - deadlock!`. A partial deadlock, where some goroutines are stuck while an HTTP server keeps running, is not detected.

For those, send `SIGQUIT` (the process prints all goroutine stacks and exits) or, without killing it, fetch `/debug/pprof/goroutine?debug=2` from `net/http/pprof`. Each goroutine shows a wait reason such as `sync.Mutex.Lock`, plus how long it has waited once that exceeds a minute.

### C and C++

Attach gdb and dump every thread:

```
$ gdb -p 4242
(gdb) thread apply all bt
Thread 3 (LWP 4245):
#0 futex_wait ...
#1 __lll_lock_wait ...
#2 pthread_mutex_lock (m=0x...060)
#3 transfer (...) at bank.c:21
Thread 2 (LWP 4244):
#2 pthread_mutex_lock (m=0x...0a0)
#3 transfer (...) at bank.c:21
```

Both threads are blocked inside `pthread_mutex_lock`. For ordinary glibc mutexes, an internal owner field can help identify the holder. It is not portable POSIX API; robust, PI, elision and transient states require implementation-specific interpretation:

```
(gdb) p ((pthread_mutex_t *)
         0x...060)->__data.__owner
$1 = 4244
(gdb) p ((pthread_mutex_t *)
         0x...0a0)->__data.__owner
$2 = 4245
```

Thread 4245 waits for a mutex owned by 4244, which waits for one owned by 4245: a two-thread cycle. Without a debugger, `/proc/<pid>/task/<tid>/wchan` shows which kernel function each thread is sleeping in (a futex wait for a user-space lock), often in an interruptible sleep state for ordinary userspace futex waits. Exact state and wait-channel visibility depend on the wait type, kernel and permissions.

### The kernel itself

Some kernel waits leave tasks in state `D` (uninterruptible sleep), while spinning deadlocks may instead cause lockup warnings. With the relevant configuration enabled, the **hung task detector** checks prolonged uninterruptible waits against `kernel.hung_task_timeout_secs` (commonly 120 s); settings, exclusions and reporting limits affect what is logged. `echo w > /proc/sysrq-trigger` dumps all blocked tasks on demand.

## Databases

Databases detect deadlocks for you (lesson 4), but you still need to find out *which code* causes them.

- **PostgreSQL** logs each deadlock with the processes, the locks and the statements involved (`Process 123 waits for ShareLock on transaction 456; blocked by process 789.`). Turn on `log_lock_waits` (off by default) to also log any wait longer than `deadlock_timeout`. For live blocking:

```sql
SELECT pid,
       pg_blocking_pids(pid) AS blocked_by,
       wait_event_type,
       left(query, 60) AS query
FROM pg_stat_activity
WHERE cardinality(
        pg_blocking_pids(pid)) > 0;
```

- **MySQL InnoDB**: `SHOW ENGINE INNODB STATUS` has a *LATEST DETECTED DEADLOCK* section with both transactions, their statements and their locks. Only the latest is kept unless you set `innodb_print_all_deadlocks`, which writes every one to the error log.
- **SQL Server**: the built-in `system_health` Extended Events session captures deadlock graphs as XML.

Look for the same pair of statements recurring. That's a lock-order bug in the application, and lesson 2's fix (touch rows in a consistent order, keep transactions short) applies.

## Catching cycles before they happen: lockdep

Waiting for a deadlock to happen in production is the worst way to find it. The Linux kernel's **lockdep** (runtime locking correctness validator, `CONFIG_PROVE_LOCKING`) finds lock-order bugs the first time the *order* is observed, whether or not the threads collide.

How it works:

1. Locks are grouped into **classes**: every `inode->i_lock` is one class, however many inodes exist. That keeps the graph small and makes one observation apply to all instances.
2. Every time a task takes lock B while holding lock A, lockdep records the dependency `A → B`.
3. Before adding an edge, it checks whether the edge would close a cycle in the dependency graph. If so, it reports it immediately.

```
WARNING: possible circular locking
         dependency detected
...
 Possible unsafe locking scenario:

       CPU0            CPU1
       ----            ----
  lock(&a->lock);
                       lock(&b->lock);
                       lock(&a->lock);
  lock(&b->lock);

 *** DEADLOCK ***
```

(Abridged.) The key property: path 1 can run on Monday and path 2 on Friday, on different CPUs, never overlapping. Lockdep still connects `A → B` and `B → A` and reports the cycle.

It also checks **interrupt-context rules**. If a lock is ever taken in a hardirq handler, and elsewhere taken with interrupts *enabled*, an interrupt could arrive while the lock is held and spin on it forever on the same CPU. Lockdep flags this as an inconsistent lock state.

Costs and limits:

- Significant overhead, so it's enabled in debug and CI kernels (and by fuzzers such as syzbot), with deployment depending on overhead and diagnostic needs.
- It only knows about orders it has **seen**. Code paths that never run in testing are unchecked.
- Legitimate same-class nesting needs a real hierarchy and correctly mapped annotations such as `mutex_lock_nested()`. Incorrect annotations can hide genuine bugs as well as create false reports.

## ThreadSanitizer and friends

User space has similar tools.

**ThreadSanitizer** (`-fsanitize=thread`) primarily detects data races. Some runtimes also support an experimental lock-order detector for supported pthread primitives, reporting `lock-order-inversion (potential deadlock)`. Check the compiler/runtime and enable `TSAN_OPTIONS=detect_deadlocks=1`; do not assume all platforms, versions or custom locks support it. Clang documents typical overall TSan costs of 5–15× runtime and 5–10× memory; these are broad tool estimates, not a benchmark for this example.

```c
// Fragment: include <pthread.h>.
// Compile with -fsanitize=thread.
pthread_mutex_t a =
    PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t b =
    PTHREAD_MUTEX_INITIALIZER;

void *t1(void *x) {
    pthread_mutex_lock(&a);
    pthread_mutex_lock(&b);
    pthread_mutex_unlock(&b);
    pthread_mutex_unlock(&a);
    return NULL;
}

void *t2(void *x) {
    pthread_mutex_lock(&b);
    pthread_mutex_lock(&a);
    pthread_mutex_unlock(&a);
    pthread_mutex_unlock(&b);
    return NULL;
}
```

With the lock-order detector available and enabled, running `t1` to completion and then `t2` can report `a => b => a` without an actual deadlock. Both orders must be observed in the same instrumented process; separate executions do not share the graph.

Others in the same family:

- **Helgrind** (Valgrind) reports lock-order violations too, without recompiling, with workload-dependent overhead.
- **Abseil's** `absl::Mutex` checks for lock-order cycles itself in debug builds.
- The **Go race detector** is built on TSan's runtime but does *not* report lock-order inversions; Go relies on dumps and code review.

### Exploring interleavings

Order checkers only see what runs. To find bugs on paths that are hard to reach by chance, **model checkers** run a concurrent test under every (or many) possible interleavings:

- **loom** for Rust replaces `std::sync` types in tests and systematically explores schedules.
- A model checker such as **TLC** checks a design written in **TLA+** before you write implementation code; AWS has used it for S3 and DynamoDB internals.

## Designing deadlock out

Tools catch mistakes. Design makes mistakes rare. Useful rules include:

1. **Avoid nested lock acquisition.** Copy what you need, release, then act, while preserving data invariants. A single non-reentrant lock can still self-deadlock; communication and pool dependencies also matter.
2. **Never call unknown code while holding a lock.** Callbacks, listeners, virtual methods and library calls can take locks you don't know about. *Java Concurrency in Practice* calls the fix **open calls**: calls made with no locks held.
3. **Never block while holding a lock.** No I/O, `join()`, `queue.put()` on a bounded queue, or RPC inside a critical section.
4. **When you must nest, order.** Document a global order or hierarchy (lesson 2) and enforce it with a checker: lockdep, TSan, or a debug-mode `LevelLock`.
5. **Prefer ownership to sharing.** Exclusive ownership can remove locks around that data, though background I/O, shared state and re-entrant callbacks still require coordination. Redis largely serializes command execution while also using background work and optional I/O threads. Message passing helps, though actors that make *synchronous* requests to each other can still deadlock in a cycle.
6. **Don't wait on your own pool.** A task that submits a sub-task to the same bounded pool and waits for it can exhaust the pool (lesson 1). Use separate pools per stage, or non-blocking composition (futures, `async`).
7. **Timeouts as a backstop, not a design.** `acquire(timeout=...)`, `lock_timeout` and RPC deadlines turn a permanent hang into an error you can log and alert on.
8. **Databases**: short transactions, touch rows in a consistent order (`ORDER BY id ... FOR UPDATE`), use `NOWAIT` or `SKIP LOCKED` for queue-like workloads, and use bounded, safe whole-transaction retries when appropriate. A timeout needs explicit cleanup; InnoDB normally leaves earlier transaction locks held after a statement timeout.

> [!example] An illustrative failure pattern
> A cache calls an `on_evict` callback while holding its internal lock. A team registers a callback that writes to a metrics registry, which takes its own lock. Elsewhere, the metrics exporter, holding the registry lock, reads cache stats, which takes the cache lock. Cache → registry and registry → cache: a deadlock under load. The fix is rule 2: collect evicted entries under the lock, release it, *then* run callbacks.

## Key takeaways
- Use multiple dumps and progress measurements to investigate; confirm a dependency cycle rather than diagnosing from CPU use alone.
- Every runtime can dump threads: `jstack` (which also reports Java-level deadlocks), `py-spy dump` or `faulthandler`, Go's `SIGQUIT` or pprof, gdb's `thread apply all bt` with glibc's `__owner` field.
- Go detects some global no-progress states; timers, network waits and runtime modes affect detection. Investigate partial deadlocks with dumps.
- Databases log deadlocks; use `pg_blocking_pids`, `SHOW ENGINE INNODB STATUS` or deadlock graphs to find the code paths involved.
- Lockdep and supported TSan lock-order detectors can report observed order cycles without an actual collision. Unobserved paths and unsupported primitives remain unchecked.
- Design rules beat tools: one lock at a time, no unknown code or blocking under a lock, a documented and enforced order, ownership over sharing, and timeouts as a safety net.

## Further reading
- [Runtime locking correctness validator (lockdep) — Linux kernel docs](https://docs.kernel.org/locking/lockdep-design.html)
- [ThreadSanitizer — Clang documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [jstack — Java SE 21 tool reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jstack.html)
- [py-spy — sampling profiler for Python](https://github.com/benfred/py-spy)
- [faulthandler — Python docs](https://docs.python.org/3/library/faulthandler.html)
- [Helgrind: a thread error detector — Valgrind manual](https://valgrind.org/docs/manual/hg-manual.html)
- [PostgreSQL docs: System Information Functions (pg_blocking_pids)](https://www.postgresql.org/docs/current/functions-info.html)
- [OSTEP: Common Concurrency Problems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
