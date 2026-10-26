---
id: cx-measuring-algorithms
sourceLesson: cx-in-practice
title: Measuring and choosing an algorithm
level: advanced
minutes: 2
summary: Use doubling ratios and realistic constraints to choose a suitable implementation.
---

Measurement tests whether the model explains the actual implementation. Use realistic inputs, repeat runs and inspect the operations dominating elapsed time.

## Doubling is a diagnostic experiment

Measure at several successively doubled input sizes while holding the task and environment comparable. A roughly doubled time suggests linear behaviour; quadrupled time suggests quadratic behaviour; eightfold time suggests cubic behaviour. Linear-times-log growth is slightly above doubling over sufficiently large sizes.

These are clues over the measured range, not proofs of asymptotic bounds. Startup work, cache transitions, allocation and noise can distort ratios. A backtracking or exponential algorithm need not follow a stable power-law ratio at all.

Python's `timeit` repeats small benchmarks and documents common measurement pitfalls. Decide whether setup and garbage collection belong in the measured workload. Minimum repeated time can help estimate uncontended execution; service latency needs its own distribution, including slow requests. A profiler identifies where time is spent but also adds overhead.

## Connect the observation to the code

```python
def drain(items):
    out = []
    while items:
        out.append(items.pop(0))
    return out
```

One visible loop does not make this linear. Each front removal shifts the remaining list references, so the total work is quadratic in original item count. A consistent fourfold doubling ratio supports that diagnosis. A deque can remove from the front without shifting every remaining element. Copying once and clearing the original may also satisfy the required behaviour; check mutation and aliasing requirements.

## Choose for the scarce resource

To keep the best hundred scores from a stream too large to store, maintain a min-heap of at most a hundred retained scores. Its smallest retained score is the replacement threshold. Read every record once and replace only when necessary. Storage depends on the requested result count, not stream length.

A conventional in-memory quickselect requires the items available for partitioning, and sorting all records does more ordering than the request needs. Match the approach to output, memory and streaming requirements, then benchmark it.

## Key takeaways
- Doubling ratios suggest where to investigate.
- Confirm the mechanism behind an observed slowdown.
- Choose and measure against actual input, output, memory and latency constraints.

## Further reading
- [Python timeit](https://docs.python.org/3.14/library/timeit.html)
- [Python heap selection](https://docs.python.org/3.14/library/heapq.html)
- [Python deque](https://docs.python.org/3.14/library/collections.html)
