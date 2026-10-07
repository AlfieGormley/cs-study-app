---
id: sepr-profiling
title: Profiling and performance work
level: intermediate
minutes: 13
summary: How to make code faster without guessing - set a target, benchmark honestly, use Amdahl's law, read cProfile output and flame graphs, tell CPU time from waiting, and go after the wins that actually matter.
---

A useful rule for performance work is: **measure before you change anything**. Intuition can misidentify where time goes. For example: The loop you were sure was slow takes 2% of the runtime; the real cost is a database call hidden inside a helper.

This lesson covers a disciplined workflow: define the goal, measure, find the bottleneck, change one thing, and measure again.

## When to optimise

Donald Knuth's famous line, from a 1974 paper, is usually quoted only in part:

> We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%.

The point is not "never optimise". It is: do not contort code for speed before you know it matters, and when it does matter, measure which parts matter and work there. The quoted percentages are rhetorical guidance, not measured proportions for every program.

Start with a **concrete target** tied to users or cost:

- **Latency**: "p99 of `/search` under 300 ms" (the 99th percentile, roughly 1% of observations lie above it, depending on ties and the percentile convention).
- **Throughput**: "the nightly import finishes within its 2-hour window".
- **Resources**: "fit in a 512 MB container", "halve the CPU bill".

Without a target you cannot tell when to stop, and performance work has no natural end.

> [!tip] Use percentiles, not averages
> A mean of 80 ms can hide a p99 of 2 seconds. Users making more requests have more opportunities to encounter slow requests, though request types and latency dependence also matter.

## Amdahl's law: where the ceiling is

If part of a program takes fraction *p* of the runtime, and you make that part *s* times faster, the overall speedup for fixed work, assuming the remaining runtime is unchanged, is:

```
speedup = 1 / ((1 - p) + p / s)
```

Suppose a function takes 30% of runtime and you make it 10 times faster:

```
1 / (0.7 + 0.3 / 10)
= 1 / (0.7 + 0.03)
= 1 / 0.73
≈ 1.37x
```

Even making it infinitely fast only gives 1 / 0.7 ≈ 1.43×. The 70% you did not touch caps the gain. The lesson: work on the biggest slice first, and a profiler tells you which slice that is.

## Step 1: benchmark honestly

A **benchmark** measures how long something takes, so you can compare before and after. Easy to do, easy to do badly.

For small snippets, Python's `timeit` runs code many times and handles timer details:

```python
import timeit

setup = "s = set(range(100_000))"
runs = timeit.repeat("-1 in s",
                     setup=setup,
                     number=100_000,
                     repeat=5)
print(min(runs))
```

The `timeit` docs recommend looking at the minimum of the repeats: higher values are usually caused by other processes interfering, not by your code.

Common benchmarking mistakes:

- **Unrealistic data.** An algorithm that is fine with 100 rows can be quadratic at 100,000. Use production-sized inputs.
- **Mismatched warm-up.** Warm up for steady-state measurements; measure cold starts separately if that is the target. The first run can pay for cold caches, lazy imports, connection setup and JIT compilation (in PyPy, the JVM or V8).
- **Noise.** Laptops throttle, browsers steal CPU. Repeat runs and compare distributions, not single numbers.
- **Measuring the wrong thing.** A micro-benchmark of string concatenation tells you nothing if the request spends 90% of its time waiting for Postgres.

## Step 2: profile to find the bottleneck

A **profiler** tells you where time goes. There are two main kinds.

| Kind | How it works | Example |
|---|---|---|
| Deterministic | Hooks every call and return | `cProfile` |
| Sampling | Records stacks N times/sec | `py-spy`, `perf` |

**Deterministic** profilers count observed call events in the profiled execution scope, with overhead that can disproportionately affect tiny functions. **Sampling** profilers periodically capture stacks; some interrupt execution while tools such as py-spy read another process externally. Sampling is approximate and often lower overhead, but production use requires suitable permissions and validation of workload impact. `py-spy` can attach to a running Python process by PID without restarting it.

### Reading cProfile

```
python -m cProfile -s cumtime app.py
```

Illustrative output, with some columns trimmed:

```
ncalls  tottime  cumtime  function
     1    0.002    9.810  main
  5000    0.150    9.420  load_order
  5000    9.100    9.100  db.query
200000    0.310    0.310  fmt_price
```

- **ncalls**: how many times it was called.
- **tottime**: time spent in the function itself, *excluding* functions it called.
- **cumtime**: time *including* everything it called.

Read it like this: `main` takes 9.8 s cumulatively but almost none itself. Nearly all of it is under `load_order`, and within that `db.query` has a tottime of 9.1 s from 5,000 calls. Repeated per-order queries suggest an **N+1 query** pattern if an initial query fetched the orders. Investigate batching or joining and measure the resulting database work; the profile alone does not guarantee the saving. `fmt_price` is called 200,000 times but costs only 0.3 s; optimising it cannot remove more than its measured contribution under these assumptions.

### Reading a flame graph

A **flame graph** (Brendan Gregg's visualisation) shows sampled stacks:

```
[       fmt       ][   db.query    ]
[        load_order                ]
[             main                 ]
```

- Each box is a function; the box above it is something it called.
- **Width** is the share of samples that included that function: for a CPU-time graph, wider estimates more CPU time. Other flame graphs can encode off-CPU time or allocation volume.
- The x-axis is *not* time. Boxes are sorted (often alphabetically) so identical stacks merge.
- Look for wide plateaus near the top: in a CPU-sampled graph with complete stack unwinding, these indicate self CPU time rather than just callees.

## CPU time versus waiting

A request can be slow while the CPU is idle. It may be waiting for a database, a network call, a lock or the disk. This is **off-CPU** time, and a CPU-only profiler will not show it, because a sleeping thread is not on the CPU to be sampled.

Compare **wall-clock time** (what the user experiences) with **CPU time** (what the process actually computed). If a request takes 800 ms of wall time and 20 ms of CPU time, optimising Python code cannot help much; look at what it waits for, including time runnable but waiting for CPU scheduling. A low CPU time for one request does not show that the whole machine is idle. Distributed tracing, database slow-query logs and wall-clock profiling modes are the right tools there.

For whole machines, Gregg's **USE method** is a quick checklist: for each resource (CPU, memory, disk, network), check **Utilisation**, **Saturation** (queued work) and **Errors**.

## Step 3: the wins that matter

Candidate improvements to evaluate against measurements:

1. **Do less work.** Remove repeated computation, unneeded fields, duplicate calls.
2. **Better algorithms and data structures.** O(n²) to O(n log n) beats any micro-optimisation once n is large.
3. **Batch I/O.** One query for 5,000 rows instead of 5,000 queries. Batch API calls, buffer writes.
4. **Cache** results that are expensive and reused, with a plan for invalidation.
5. **Concurrency** for I/O-bound work (asyncio, threads): overlap the waits.
6. **Move hot loops** to optimised code: NumPy vectorisation, a C extension, or a compiled language.
7. **Micro-optimisations** (local variable lookups, avoiding attribute access) last, and only in a proven hot loop.

A very common example of point 2:

```python
def common(a, b):
    # 'x in b' scans the list: O(m)
    return [x for x in a if x in b]

def common_fast(a, b):
    bs = set(b)  # O(m) once
    # 'x in bs' is O(1) on average
    return [x for x in a if x in bs]
```

With 10,000 items in each list, `common` does up to 100 million comparisons; `common_fast` does about 20,000 operations. This is an asymptotic comparison, not a measured timing guarantee. It assumes stable, hashable values and effectively constant-time equality/hashing; the set uses O(m) additional memory. Unhashable values or unusual equality semantics can invalidate this replacement. No universal seconds-to-milliseconds result is included because it cannot be reliably established without a specified workload and benchmark.

### Memory

Memory problems show up as growing RSS, swapping, or the container being OOM-killed. Python's `tracemalloc` takes snapshots of allocations; comparing two snapshots shows which lines allocated the memory that grew:

```python
import tracemalloc
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
retained = [bytearray(1024)
            for _ in range(100)]
snap2 = tracemalloc.take_snapshot()
diff = snap2.compare_to(snap1, "lineno")
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
- **Load tests that hide latency.** A load generator that waits for each response before sending the next one sends fewer requests exactly when the system slows down, so it under-reports bad latency. This is **coordinated omission**; for an independently arriving production workload, tools like wrk2 schedule a target arrival rate and measure latency from intended send times. Constant rate alone is insufficient if delayed sends are omitted from latency. A closed-loop model can be appropriate when the real workload is closed-loop.

## Key takeaways
- Set a concrete target (p99 latency, throughput, memory) and measure before changing anything.
- Amdahl's law caps the gain from speeding up one part; profile to find the biggest slice.
- Deterministic profilers count observed calls with overhead; sampling profilers estimate stack prevalence and require production overhead/permission checks.
- In cProfile, tottime is self time and cumtime includes callees; in CPU flame graphs, width estimates CPU time and the x-axis is not chronological.
- Slow but idle usually means waiting on I/O or locks. Algorithms, batching and caching beat micro-optimisation.

## Further reading
- [The Python Profilers — Python docs](https://docs.python.org/3/library/profile.html)
- [timeit — Python docs](https://docs.python.org/3/library/timeit.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
- [py-spy — sampling profiler for Python (GitHub)](https://github.com/benfred/py-spy)
- [Flame Graphs — Brendan Gregg](https://www.brendangregg.com/flamegraphs.html)
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Amdahl's law — Wikipedia](https://en.wikipedia.org/wiki/Amdahl%27s_law)
