---
id: sync-race-conditions-interleaving-bounds
title: Bounds in a load/store model
level: basic
minutes: 2
summary: Construct the smallest and largest counter values in a precisely stated interleaving model.
sourceLesson: sync-race-conditions
---

A simplified model lets us reason about schedules without pretending that undefined C behaviour has a finite outcome set. Each increment loads the shared counter, adds one privately, then stores the private value.

### How bad can it get?

Take a simplified, sequentially consistent model: every load and store happens whole, one at a time, in some interleaved order. Two threads start with the counter at 0 and each run the same number of load/add/store increments, at least two each. The range of possible final values is:

```formula
2 ≤ V_final ≤ 2N   for N ≥ 2
where
V_final: the value of the shared counter once both threads have finished, starting from 0
N: the number of increments each thread performs, each one a separate load, add and store
≤: less than or equal to
≥: greater than or equal to
In words: with two threads the result can be anything from 2 (almost every update lost) up to 2N (no update lost).
```

For example, if each thread performs one million increments, this model permits final values from 2 to 2,000,000. This is a modelled result, not a bound on the broken C program.

The top value needs no overlapping read/modify/write windows. The bottom value, 2, needs a pathological schedule:

1. A loads 0 and stalls.
2. B runs all but one of its increments.
3. A stores 1, wiping out all of B's work.
4. B loads 1 and stalls.
5. A runs all of its remaining increments.
6. B stores 2, wiping out all of A's work.

Unlikely, but the scheduler is allowed to do it. The bound needs at least two increments per thread: with just one each, the final value can be 1 (both load 0, both store 1).

This is an interleaving exercise, not a guarantee for a data-racing C program, whose behaviour is undefined.

## Key takeaways

- The model assumes indivisible loads/stores and preserved per-thread order; it is not data-racing C.
- For at least two increments per thread, a delayed stale store can leave only two counted increments.
- One increment per thread has different possible results: one or two.

## Further reading

- [OSTEP: Concurrency, an introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [ThreadSanitizer documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
