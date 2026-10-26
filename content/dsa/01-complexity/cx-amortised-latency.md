---
id: cx-amortised-latency
sourceLesson: cx-amortised-analysis
title: Amortisation beyond arrays and latency
level: advanced
minutes: 2
summary: Apply sequence reasoning to counters and queues while recognising latency spikes.
---

A good sequence bound does not guarantee a short delay for each operation. Here n counts operations or stored items, as each example states.

## Follow each piece of work across its lifetime

A binary counter starting at zero flips its lowest bit on every increment, the next about half as often and later bits progressively less often. Across n increments, the total number of flips is linear in n even though a single carry can flip many bits.

A queue can use an `inbox` stack and an `outbox` stack. Enqueue pushes to the inbox. Dequeue pops the outbox; only when it is empty does it transfer the inbox by repeated pop-and-push operations. The reversal restores first-in-first-out order.

Each item enters the inbox once, transfers at most once and leaves the outbox once. Starting empty, total stack operations are proportional to total queue operations, assuming each stack operation is constant cost. One dequeue can still pay for a large transfer.

## Throughput and deadlines are different requirements

A dynamic-array append may relocate all existing elements. An amortised constant bound permits that delay. A system with a strict per-operation deadline must inspect allocation, relocation and other slow paths rather than relying on the average sequence charge.

Possible approaches include reserving enough capacity before the hot path, filling a pre-sized container by index, using fixed-size chunks, or spreading migration work across updates. Each has costs: extra memory, more complicated lookup rules or allocation at chunk boundaries. None alone promises a fixed wall-clock deadline.

In Python, `[None] * n` creates a list with n actual elements. Fill those slots by index; appending instead adds after them. It is not an empty list with reserved capacity.

The proof also assumes updates progress through states. Reusing an old version of a persistent data structure can repeat expensive work without rebuilding credit. Such structures need an analysis of sharing and deferred work, not an automatic reuse of an imperative proof.

## Key takeaways
- Count how often each item or bit can incur work over a sequence.
- Amortised cost bounds total work, not tail latency.
- Preallocation or incremental work needs its own capacity and latency assumptions.

## Further reading
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
- [Python sequence operations](https://docs.python.org/3.14/library/stdtypes.html)
