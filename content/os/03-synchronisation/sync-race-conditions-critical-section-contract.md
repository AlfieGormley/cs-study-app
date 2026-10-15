---
id: sync-race-conditions-critical-section-contract
title: Critical-section guarantees
level: basic
minutes: 3
summary: Check mutual exclusion, progress and bounded waiting before trusting a locking protocol.
sourceLesson: sync-race-conditions
---

A critical section protects a shared invariant across several operations. Protecting only one read or write is insufficient when another thread could invalidate the decision between them.

## Critical sections

A **critical section** is a piece of code that accesses shared state and must never be executed by more than one thread at a time. In the counter example, the load-add-store is the critical section.

The general shape of a solution:

```
while (true) {
    entry section    // ask permission
    critical section // touch shared data
    exit section     // give it back
    remainder section
}
```

Any correct solution to the critical-section problem must satisfy three requirements:

1. **Mutual exclusion.** At most one thread is in the critical section at any time.
2. **Critical-section progress.** If no thread is in the critical section and some want to enter, one of them must be allowed in, and the decision cannot be postponed forever. Only threads trying to enter take part in deciding.
3. **Bounded waiting.** Once a thread has asked to enter, there is a limit on how many times other threads can enter ahead of it. No thread waits forever (no **starvation**).

In practice we also care about **performance**: the overhead when there is no contention, and how well the lock behaves when many threads want it.

> [!warning] Mutual exclusion alone is easy
> A "solution" that never lets anyone in satisfies mutual exclusion perfectly. That is why progress and bounded waiting matter: they rule out deadlock and starvation. Deadlock gets a module of its own next.

## Early software attempts

Can we build mutual exclusion from plain loads and stores? A naive flag fails:

```c
// broken: both can see 0, both enter
while (locked) ;  // spin
locked = 1;
/* critical section */
locked = 0;
```

The check and the set are separate steps, so this has exactly the same race it was meant to prevent.

**Peterson's algorithm** (1981) solves it for two threads using only loads and stores. Each thread raises a flag saying "I want in" and then politely gives the other thread the turn:

```c
int flag[2] = {0, 0};
int turn;

void lock(int me) {
    int other = 1 - me;
    // Plain C flags are deliberately
    // unsafe.
    flag[me] = 1;
    // Yield priority if both want entry.
    turn = other;
    while (flag[other] && turn == other)
        ;  // spin
}

void unlock(int me) { flag[me] = 0; }
```

Under sequentially consistent atomic reads/writes and suitable progress assumptions, the algorithm satisfies these requirements. The plain C version is **broken as written** because it has data races and undefined behavior; hardware store buffering is an additional way a literal load/store implementation can fail. Both threads can then read the other's flag as 0 and enter together. The later memory-ordering units explain why; for now, the lesson is to use a documented lock or atomic protocol rather than copy these plain C flags.

## Key takeaways

- Mutual exclusion, progress and bounded waiting answer different correctness questions.
- Checking a plain flag and setting it later is not one atomic action.
- Peterson’s algorithm needs a valid atomic model and progress assumptions; the plain C sketch is deliberately broken.

## Further reading

- [OSTEP: Concurrency, an introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [ThreadSanitizer documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
