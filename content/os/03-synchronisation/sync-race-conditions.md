---
id: sync-race-conditions
title: Race conditions and critical sections
level: basic
minutes: 11
summary: Why counter++ is not atomic, how interleavings lose updates, the difference between a data race and a race condition, and what any solution to the critical-section problem must guarantee.
---

Threads in the same process share memory. That is what makes them fast to communicate, and it is also what makes them dangerous. When two threads touch the same data and at least one of them writes, the result can depend on exactly how the scheduler happened to interleave their instructions.

A bug whose outcome depends on timing is called a **race condition**. Races are notorious because they are non-deterministic: the program passes a thousand test runs, then corrupts data in production on a busy Tuesday.

## The simplest broken program

Two threads each add one to a shared counter a million times. You would expect 2,000,000.

```c
#include <pthread.h>
#include <stdio.h>

static int counter = 0;

void *work(void *arg) {
    for (int i = 0; i < 1000000; i++)
        counter++;
    return NULL;
}

int main(void) {
    pthread_t a, b;
    pthread_create(&a, NULL, work, NULL);
    pthread_create(&b, NULL, work, NULL);
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    printf("%d\n", counter);
}
```

This deliberately broken C program has a data race and undefined behavior, so no output is guaranteed at any optimization level. A lost-update trace below illustrates a simplified machine model, not all behavior permitted for this C program.

> [!note] Content gap
> No reproducible record supports the original exact sample counts, so they are omitted. A run that prints 2,000,000 does not establish correctness.

## Why counter++ is not one step

`counter++` looks like a single operation, but the CPU does three things:

```
mov  eax, [counter]   ; 1. load
add  eax, 1           ; 2. add in a register
mov  [counter], eax   ; 3. store
```

Each thread has its own registers. A thread can be interrupted, or simply run in parallel on another core, between any two of those instructions.

Even when the compiler emits a single `inc [counter]` instruction, it is still a read-modify-write that is not atomic across cores unless it carries the `lock` prefix. "One line of C" or "one instruction" is never a proof of atomicity.

## Tracing a lost update

Start with `counter = 5`. Each thread has a private register (`rA`, `rB`).

```
step  Thread A      Thread B    counter
1     rA = 5                    5
2                   rB = 5      5
3     rA = 6                    5
4     store 6                   6
5                   rB = 6      6
6                   store 6     6
```

Two increments ran; the counter went up by one. Thread B's store overwrote Thread A's, because B's value was computed from a stale read. This is a **lost update**.

Not every interleaving is bad. If A finishes all three steps before B starts its load, the answer is 7. The bug only appears when the windows overlap, which is why it is intermittent.

> [!example] How bad can it get?
> In a simplified sequentially consistent load/add/store model, two threads each increment N times (N at least 2). The final value can range from 2 to 2N. This is an interleaving exercise, not a guarantee for the data-racing C program, whose behaviour is undefined. The value 2 needs a pathological schedule: A loads 0 and stalls; B runs N-1 increments; A stores 1; B loads 1 and stalls; A runs its remaining N-1 increments; B stores 2. Unlikely, but the scheduler is allowed to do it.

## The same bug in Python

The global interpreter lock (GIL) serialises Python execution in a conventional CPython build, but it is not a language-level guarantee that every bytecode is atomic: operations can invoke user code or release the GIL. `counter += 1` also spans several bytecodes:

```
LOAD_GLOBAL   counter
LOAD_SMALL_INT 1
BINARY_OP     13 (+=)
STORE_GLOBAL  counter
```

(That listing is from CPython 3.14; names vary slightly between versions.) A thread switch between the load and the store loses an update exactly as in C.

```python
import threading

counter = 0

def work():
    global counter
    for _ in range(1_000_000):
        counter += 1

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
```

On modern CPython with a GIL this often prints the right answer, because the interpreter only considers switching threads at certain points. That is luck, not correctness. Free-threaded builds and changes that introduce additional switching points can expose lost updates; neither failure nor a particular count is guaranteed.

## Data races versus race conditions

These two terms are often used interchangeably, but they mean different things.

A **data race** is a precise, language-level definition. In C and C++ it is two accesses to the same memory location, from different threads, where the accesses conflict (for example, at least one writes), at least one is non-atomic, and neither happens before the other (no lock, no other synchronisation). In C and C++ a data race is **undefined behaviour**: the compiler may assume it never happens.

A **race condition** is a broader, semantic bug: the program's correctness depends on the relative timing of events.

| | Data race | No data race |
|---|---|---|
| Race condition | `counter++` unlocked | check-then-act |
| No race condition | rare, still UB in C | correct code |

The interesting cell is "race condition without a data race". Every individual access can be protected and the program can still be wrong:

```python
# each call takes the lock internally
if account.balance() >= 100:
    account.withdraw(100)
```

Two threads can both see a balance of 150, both pass the check, and both withdraw. Each method is thread-safe; the *combination* is not. This pattern is called **check-then-act** (or time-of-check to time-of-use, TOCTOU), and it is also a classic security bug with files: checking permissions on a path, then opening it after an attacker has swapped it for a symlink.

The fix is to make the check and the action a single atomic unit: hold one lock across both, or offer an operation like `withdraw_if_at_least(100)`.

## Critical sections

A **critical section** is a piece of code that accesses shared state and must not be executed by more than one thread at a time. In the counter example, the load-add-store is the critical section.

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
2. **Progress.** If no thread is in the critical section and some want to enter, one of them must be allowed in, and the decision cannot be postponed forever. Only threads trying to enter take part in deciding.
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
    flag[me] = 1;
    turn = other;
    while (flag[other] && turn == other)
        ;  // spin
}

void unlock(int me) { flag[me] = 0; }
```

Under sequentially consistent atomic reads/writes and suitable progress assumptions, the algorithm satisfies these requirements. The plain C version is **broken as written** because it has data races and undefined behavior; hardware store buffering is an additional way a literal load/store implementation can fail. Both threads can then read the other's flag as 0 and enter together. Lesson 5 explains why; for now, the moral is that real locks are built on **atomic hardware instructions**, which is the subject of the next lesson.

## Where races hide in real systems

- **Lazy initialisation**: two threads both see `cache is None` and both build it, or worse, one sees a half-built object.
- **Statistics counters** shared by worker threads.
- **Collections**: appending to a C++ `std::vector` or a Java `HashMap` from several threads can corrupt the structure itself, not just lose a value.
- **Files and databases**: two processes read-modify-write the same row or file. The same lost-update anomaly appears in databases, where it is handled by transactions and isolation levels.

Tools help find them. ThreadSanitizer (`-fsanitize=thread` in GCC and Clang) detects data races at run time; Helgrind (Valgrind) does similar. Neither finds check-then-act bugs where every access is locked.

## Key takeaways
- A race condition is any bug whose result depends on timing; a data race is the specific case of unsynchronised conflicting accesses, which is undefined behaviour in C and C++.
- `counter++` is load, add, store. Interleaving those steps loses updates, and even a single `inc` instruction is not atomic across cores without `lock`.
- Do not infer atomicity from bytecode boundaries or the GIL; protect compound shared updates explicitly.
- Making each operation thread-safe does not make a sequence of them safe; check-then-act needs one atomic unit.
- A critical-section solution needs mutual exclusion, progress and bounded waiting. Peterson's teaching algorithm needs a valid atomic memory model, such as sequentially consistent C atomics; fences alone do not legalize racing plain C accesses.

## Further reading
- [OSTEP: Concurrency, an introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [Race condition — Wikipedia](https://en.wikipedia.org/wiki/Race_condition)
- [Critical section — Wikipedia](https://en.wikipedia.org/wiki/Critical_section)
- [Peterson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Peterson%27s_algorithm)
- [dis: disassembler for Python bytecode](https://docs.python.org/3/library/dis.html)
