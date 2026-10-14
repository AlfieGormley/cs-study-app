---
id: cx-amortised-latency
sourceLesson: cx-amortised-analysis
title: Amortisation beyond arrays and latency
level: advanced
minutes: 3
summary: Apply sequence reasoning to counters and queues while recognising latency spikes.
---

Here n counts operations or stored items, as stated in each example. Separate total work from the latency of one operation.

## More examples

- **Binary counter.** Incrementing a binary counter can flip many bits (`0111 -> 1000`), but over the sequence the lowest bit flips each time, the next about half as often, and the next about a quarter as often:

```formula
flips ≤ n + n/2 + n/4 + … < 2n
where
flips: the total number of bit flips over n increments
n: the number of increments, starting from 0
…: "and so on", halving each time
≤: less than or equal to
In words: bit j flips once every 2^j increments, and those halving counts add up to less than 2n, so each increment costs fewer than 2 flips on average.
```

So increment is O(1) amortised: a constant per operation, however large n is.
- **Queue from two stacks.** Push onto an `inbox` stack. To dequeue, pop from `outbox`; if it's empty, first move everything from `inbox` to `outbox`. A single dequeue can cost O(n), where n is the number of elements waiting, but each element is moved at most once, so every operation is O(1) amortised.
- **Hash table resizing** works just like the dynamic array: double the table when the load factor gets high, rehashing every key.
- Later modules meet more advanced cases: splay trees and union-find both have amortised bounds that worst-case analysis can't show.

## Pitfalls in production

**Amortised O(1) is not "every operation is fast".** A Python list of 100 million pointers occupies about 800 MB; the append that triggers a resize may have to copy most of that, and the call pauses until it finishes. Amortisation bounds aggregate work, but allocation and copying still affect measured throughput. For latency-sensitive systems (trading, games, audio, real-time control), one slow append can blow a deadline.

Ways to avoid spikes:

- **Preallocate** when you know the size: `reserve()` in C++, `with_capacity()` in Rust, `[None] * n` in Python.
- **Incremental resizing.** Redis's hash tables rehash gradually: they keep the old and new tables side by side and move a few buckets on each operation (and in a background timer), so no single command pays for the whole rehash.

**Amortisation can break if expensive states can be replayed.** The proofs assume each expensive operation is preceded by many cheap ones that build up credit. If a data structure is shared and old versions can be reused (some persistent or functional structures), an adversary can trigger the expensive operation on the same "full" version repeatedly. Okasaki's work on purely functional data structures handles this with lazy evaluation.

## Key takeaways
- Counters and two-stack queues reuse the same sequence-cost reasoning.
- A good amortised bound does not guarantee a fast individual operation.
- Preallocation and incremental resizing can help workloads with tight latency requirements.

## Further reading
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
- [CPython listobject.c (list growth policy)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
