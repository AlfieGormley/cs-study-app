---
id: conc-threads-shared-memory
title: Threads and shared memory
level: basic
minutes: 11
summary: The default concurrency model of most languages, why `counter += 1` is not safe, what a language memory model promises, and how locks, atomics and the GIL fit in.
---

Many languages offer shared-memory concurrency: several **threads** running inside one process, all able to read and write the same variables. Java, C, C++, C#, Python, Go and Rust all offer it. It is the model the hardware most directly supports, though synchronization and contention affect performance. Shared mutable state also creates opportunities for concurrency bugs.

This lesson looks at threads from the *language's* point of view: what your code is allowed to assume when two threads touch the same memory. (How the kernel schedules threads and implements locks is covered in the Operating Systems subject.)

## The intuition

Picture two cooks sharing one kitchen and one notepad of orders. Each can read and scribble on the notepad whenever they like. That is efficient: nobody has to copy orders around. But if both glance at "pancakes: 3", both add one, and both write "4", one order has vanished.

Threads are the cooks and the heap is the notepad. Shared access avoids some copying, but cache coherence and synchronization have costs.

## Starting threads

For example, Python exposes threads and joining through threading:

```python
import threading

def work(n):
    print("working on", n)

t = threading.Thread(target=work, args=(1,))
t.start()   # runs concurrently from here
t.join()    # wait for it to finish
```

Java has `new Thread(r).start()`, C++ has `std::thread`, Rust has `std::thread::spawn`. Each thread has its own execution stack, while process memory can be shared. Local variables can also become shared through references in languages that permit it; storage on a stack does not itself enforce isolation.

## The lost update

Here is the classic bug. Four threads each add one to a shared counter 1,000 times:

```python
import threading, time

counter = 0

def work():
    global counter
    for _ in range(1000):
        tmp = counter      # read
        time.sleep(0)      # let others run
        counter = tmp + 1  # write

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
```

You would hope for 4000. It can print less than 4000. sleep(0) increases opportunities for interleaving but does not guarantee a lost update or a different result on every run.

The problem is that "add one" is really three steps: **read, modify, write**. If two threads interleave those steps, one update overwrites the other:

```
Thread 1          Thread 2      counter
read 7                            7
                  read 7          7
write 8                           8
                  write 8         8
                  (one lost)
```

Even counter += 1 is conceptually read-modify-write; its exact CPython bytecode and interruption points depend on version and operand behavior. It often *happens* to give the right answer on a GIL build, but nothing guarantees it. Java can lose updates without synchronization. In C, a data race on a non-atomic counter is undefined behavior, so enumerating load/store interleavings is not a complete language-level model.

> [!note] Race condition vs data race
> A **race condition** is any bug where the result depends on timing, like the lost update. A **data race** is narrower: potentially concurrent conflicting accesses lack the required happens-before ordering, with language-specific atomic-access exceptions. They need not occur at exactly the same physical instant. Languages define the second precisely, because it decides whether your program has any meaning at all.

## The fix: mutual exclusion

A **lock** (mutex) ensures only one thread runs a **critical section** at a time:

```python
lock = threading.Lock()

def work():
    global counter
    for _ in range(1000):
        with lock:
            tmp = counter
            time.sleep(0)
            counter = tmp + 1
```

This reliably prints 4000. The `with` block releases the lock even if an exception is thrown. Java's `synchronized` blocks, C#'s `lock` statement and C++'s `std::lock_guard` give the same scoped guarantee.

For a single counter, an atomic read-modify-write can avoid a separate lock in user code. Its implementation may use one instruction, a retry loop or internal locking; neither lower cost nor lock-freedom is universal.

```java
AtomicInteger counter =
    new AtomicInteger();
counter.incrementAndGet(); // atomic
```

C++ has `std::atomic<int>`, Go has `sync/atomic`, Rust has `AtomicUsize`. Python's standard library has no general atomics; you use a lock.

## Visibility: the bug that is not about interleaving

Locks are not only about taking turns. They are also about **visibility**: making one thread's writes visible to another.

```java
class Worker {
  boolean stop = false;  // not volatile

  void run() {
    while (!stop) { }    // may spin forever
  }
}
```

Another thread sets `stop = true`, yet the loop may never end. Nothing in the loop body writes `stop`, so the JIT compiler is allowed to read it once and hoist the check out of the loop. Separately, CPUs buffer writes and caches can make them appear late, or out of order, to other cores.

Java volatile imposes synchronization-order visibility and prevents treating the field as loop-invariant. Correctly using the same lock for both reads and writes, or AtomicBoolean, also provides ordering. This is not a wall-clock latest-value or scheduling guarantee.

## Memory models: the contract

Compilers reorder instructions and CPUs execute them out of order, because that is how they get fast. A language's **memory model** is the contract that says which reorderings your program can observe. The central idea is **happens-before**:

- Everything a thread does before **releasing** a lock happens-before everything another thread does after **acquiring** that same lock.
- A Java volatile write synchronizes with subsequent reads in synchronization order. A C++ release-store synchronizes with an acquire-load that reads from it (or the qualifying release sequence).
- Starting a thread happens-before its first action; a thread's last action happens-before `join()` returns.

Happens-before constrains which writes a read may observe; intervening writes matter. In C++, conflicting accesses form a data race when they are potentially concurrent, unordered, and at least one is non-atomic.

Java and Go provide a data-race-free sequential-consistency guarantee. For C++, race freedom alone is insufficient when weaker atomics are used: a race-free program restricted to mutexes and sequentially consistent atomics supports the simple interleaving model, while relaxed atomics can permit non-SC outcomes. What happens when you *do* race differs sharply:

| Language | Data race means |
|---|---|
| C, C++ | Undefined behaviour |
| Java | Defined but weird: stale or reordered values |
| Go | Mostly like Java; races on multi-word values can corrupt memory |
| Rust (safe) | Type/ownership rules prevent data races, assuming sound unsafe dependencies |
| CPython with GIL | Python operations still need synchronization; native extensions have their own obligations |

"Undefined behaviour" in C++ really means anything: the optimiser may assume races never happen and transform your code in surprising ways. Java chose to keep even racy programs memory-safe, because the JVM must never let you forge a pointer. Even so, Java allows a non-volatile `long` or `double` write to be split into two 32-bit halves (a torn 64-bit value), so another thread can see half of each value.

## Python and the GIL

CPython has historically had a **Global Interpreter Lock**: only one thread executes Python bytecode at a time. Consequences:

- **CPU-bound** Python threads do not run in parallel. Threads do not provide multicore bytecode parallelism in one GIL-bound interpreter; total timing depends on overhead and workload. Use `multiprocessing` or a native library that releases the GIL (NumPy does for many operations).
- **I/O-bound** threads work well, because the GIL is released while a thread waits on a socket or file.
- A bytecode can invoke user code or release the GIL, so bytecode boundaries are not a universal atomicity contract. The lost update above still happens.

PEP 703 added an optional **free-threaded** build (`python3.13t`), experimental in 3.13 and officially supported (though not the default) from 3.14. Without a GIL, threads run Python in parallel, and code that leaned on the GIL by accident is exposed.

## Where shared-memory threads hurt

- **Composability.** Two correct lock-using modules can deadlock when combined, if they take locks in different orders.
- **Invisible contracts.** In many APIs the lock discipline is a convention; type systems, annotations and wrappers can make parts of that discipline explicit.
- **Testing.** Races are timing-dependent. A test can pass a million times and fail in production under load. Tools help: Go's `-race` flag, Clang's ThreadSanitizer, Java's jcstress harness.
- **Cost per thread.** OS threads consume stack reservations and scheduler resources. No universal stack-size range, switch time or maximum count is supplied because these depend on platform, configuration and workload. That pressure drives the lighter models in the next lessons.

The rest of this module is, in a sense, a tour of escape routes. Single-thread event loops reduce simultaneous shared-memory access; async tasks can also run on multithreaded runtimes. Channels and actors encourage message passing but may still transmit shared references. Rust keeps shared memory but makes the compiler check it.

## Key takeaways
- Threads share the heap; each has its own stack. Sharing is fast but coordination is the programmer's job.
- `x += 1` is read-modify-write, not atomic. Interleaving loses updates; use a lock or an atomic.
- Locks provide **mutual exclusion** and **visibility**. Without them, compilers and CPUs may hide or reorder writes.
- A memory model defines **happens-before**. Java and Go provide DRF-SC; C++ also requires suitable synchronization restrictions for the simple SC model.
- Data races are undefined behaviour in C/C++, subject to weaker guarantees in Java, and prevented by safe Rust under sound implementation assumptions.
- CPython's GIL stops CPU-bound threads running in parallel but does not make your code race-free; a free-threaded build now exists.

## Further reading
- [Chapter 17: Threads and Locks — Java Language Specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [The Go Memory Model](https://go.dev/ref/mem)
- [Memory model — cppreference](https://en.cppreference.com/w/cpp/language/memory_model)
- [Acquire and Release Semantics — Preshing on Programming](https://preshing.com/20120913/acquire-and-release-semantics/)
- [threading — Python docs](https://docs.python.org/3/library/threading.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [Primary verification source 1](https://eel.is/c++draft/intro.races)
- [Primary verification source 2](https://eel.is/c++draft/atomics.order)
