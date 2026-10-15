---
id: sepr-performance-memory
title: Trace retained memory and protect gains
level: intermediate
minutes: 3
summary: Compare allocation snapshots, distinguish Python allocations from process memory and guard against regressions.
sourceLesson: sepr-profiling
---

Performance includes memory as well as latency. A growing resident footprint needs allocation evidence and a workload with a clear observation window.

## Compare allocations

Memory problems show up as growing RSS, memory swapping, or the container being OOM-killed. Python's `tracemalloc` takes snapshots of allocations; comparing two snapshots shows which lines allocated the memory that grew:

```python
import tracemalloc
# Trace before taking the baseline.
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
# Retain 100 buffers across both snapshots.
retained = [bytearray(1024)
            for _ in range(100)]
snap2 = tracemalloc.take_snapshot()
diff = snap2.compare_to(snap1, "lineno")
# Show up to five allocation differences.
# Paths, sizes and counts depend on Python.
for stat in diff[:5]:
    print(stat)
```

Typical culprits are unbounded caches, lists that grow for the lifetime of a process, and objects retained by callbacks or other references. Python normally collects unreachable reference cycles; cycles alone do not establish a leak. tracemalloc covers traced Python allocations, not every native allocation or all RSS.

## Step 4: verify and protect
After a change, re-run the **same benchmark**, on the same machine and data. Keep the change only if it moved the target metric meaningfully. Then protect the gain: a performance test in CI with a generous threshold, or production dashboards that alert on regressions. Speed lost a little at a time in later commits is common and hard to notice.

## Pitfalls
- **Optimising without a profile.** The most common mistake, and the most wasted effort.
- **Trusting micro-benchmarks** for macro decisions. Measure the real workload too.
- **Ignoring the tail.** Improving the median while p99 gets worse can make the product feel slower.
- **Sacrificing clarity for tiny gains.** Unreadable code has its own cost. Comment any non-obvious optimisation with the measurement that justified it.

## Key takeaways
- Compare snapshots to identify growing traced allocations and inspect who still retains the objects.
- Python allocation tracking does not cover every native allocation or all resident process memory.
- Re-run the same benchmark after a change and protect a meaningful gain with appropriate monitoring.

## Further reading
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
- [gc — Python docs](https://docs.python.org/3/library/gc.html)
