---
id: conc-thread-updates
title: Lost updates and one shared lock
level: basic
minutes: 4
sourceLesson: conc-threads-shared-memory
summary: Preserve a shared invariant by protecting the entire update with the same lock.
---

The previous unit established which memory threads share. Here the question is how to preserve a shared invariant when several threads update it.

## The lost update

Here is the classic bug. Four threads each add one to a shared counter 1,000 times:

```python
# Split read/write permits lost updates.
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

You would hope for 4000: every increment that survives adds exactly one, so the right answer is the number of threads times the increments each makes. Every update that gets overwritten takes one off that total:

```formula
C_expected = T × k
C_expected = 4 × 1000 = 4000
C_printed = C_expected − L
where
C_expected: the final value of the counter if no update is ever lost
T: the number of threads, here 4
k: the number of increments each thread performs, here 1,000
C_printed: the value the program actually prints
L: the number of lost updates: increments whose effect was wiped out because another thread wrote back a value computed from an older read
In words: four threads adding one a thousand times each should leave 4,000, and every lost update makes the printed number one smaller.
```

For example, if 37 increments are lost on one run, the program prints 3,963. So it can print less than 4000, and the shortfall varies: `time.sleep(0)` increases opportunities for interleaving but does not guarantee a lost update or a different result on every run.

The problem is that "add one" is really three steps: **read, modify, write**. If two threads interleave those steps, one update overwrites the other:

```
Thread 1          Thread 2      counter
read 7                            7
                  read 7          7
write 8                           8
                  write 8         8
                  (one lost)
```

Even `counter += 1` is conceptually read-modify-write; its exact CPython bytecode and interruption points depend on version and operand behavior. It often *happens* to give the right answer on a GIL build, but nothing guarantees it. Java can lose updates without synchronization. In C, a data race on a non-atomic counter is undefined behavior, so enumerating load/store interleavings is not a complete language-level model.

> [!note] Race condition vs data race
> A **race condition** is any bug where the result depends on timing, like the lost update. A **data race** is narrower: potentially concurrent conflicting accesses lack the required happens-before ordering, with language-specific atomic-access exceptions. They need not occur at exactly the same physical instant. Languages define the second precisely, because it decides whether your program has any meaning at all.

## The fix: mutual exclusion

A **lock** (mutex) ensures at most one thread holds that lock at a time. Every access that protects the same invariant must use that same lock:

```python
# One lock protects the entire update.
lock = threading.Lock()

def work():
    global counter
    for _ in range(1000):
        with lock:
            tmp = counter
            time.sleep(0)
            counter = tmp + 1
```

With `counter` reset to zero and the same four-thread start/join harness shown above, this prints 4000 after all workers finish. The `with` block releases the lock even if an exception is thrown. Java's `synchronized` blocks, C#'s `lock` statement and C++'s `std::lock_guard` give the same scoped guarantee.

For a single counter, an atomic read-modify-write can avoid a separate lock in user code. Its implementation may use one instruction, a retry loop or internal locking; neither lower cost nor lock-freedom is universal.

```java
// One indivisible counter update.
AtomicInteger counter =
    new AtomicInteger();
counter.incrementAndGet(); // atomic
```

C++ has `std::atomic<int>`, Go has `sync/atomic`, Rust has `AtomicUsize`. Python’s standard library does not expose a general atomic-variable API analogous to these types; use a lock for this shared counter. An atomic container operation also does not make a separate check-then-act sequence atomic: two threads can both observe a missing cache entry and both compute it before either inserts. Protect the whole sequence, or use an API with the required compound guarantee.

## Key takeaways
- Read-modify-write sequences can lose updates when their steps overlap.
- Use the same lock around every access needed to preserve one invariant.
- Internal container safety does not make a separate check and insert atomic.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/threading.html)
- [Primary source: docs.oracle.com](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Primary source: go.dev](https://go.dev/ref/mem)
- [Primary source: eel.is](https://eel.is/c++draft/intro.races)
