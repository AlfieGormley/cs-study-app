---
id: sync-race-conditions-lost-updates
title: How shared increments lose updates
level: basic
minutes: 3
summary: Trace the load, add and store behind a shared counter update.
sourceLesson: sync-race-conditions
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
        // This shared update is not atomic.
        counter++;
    return NULL;
}

int main(void) {
    pthread_t a, b;
    pthread_create(&a, NULL, work, NULL);
    pthread_create(&b, NULL, work, NULL);
    // Join before observing the final
    // value.
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    // Deliberate data race: output is not a
    // correctness guarantee, even if
    // expected.
    printf("%d\n", counter);
}
```

This deliberately broken C program has a data race and undefined behavior, so no output is guaranteed at any optimization level. A lost-update trace below illustrates a simplified machine model, not all behavior permitted for this C program.

> [!note] Content gap
> No reproducible record supports the original exact sample counts, so they are omitted. A run that prints 2,000,000 does not establish correctness.

## Why counter++ is not one step

`counter++` looks like a single operation. A simplified x86-style expansion separates three actions:

```text
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

## Key takeaways

- A plain C increment shared without synchronisation has undefined behaviour; no observed output makes it correct.
- A load/add/store trace explains one lost-update symptom, rather than bounding C behaviour.
- Neither one source line nor one ordinary x86 instruction proves cross-core atomicity.

## Further reading

- [OSTEP: Concurrency, an introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [ThreadSanitizer documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
