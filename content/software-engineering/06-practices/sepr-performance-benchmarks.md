---
id: sepr-performance-benchmarks
title: Benchmark the workload users run
level: intermediate
minutes: 3
summary: Compare repeated measurements and recognise load tests that omit queued requests.
sourceLesson: sepr-profiling
---

The target from the preceding unit determines what to measure. A benchmark is useful only if its data, timing boundary and arrival model represent that target.

## Step 1: benchmark honestly
A **benchmark** measures how long something takes, so you can compare before and after. Easy to do, easy to do badly.

For small snippets, Python's `timeit` runs code many times and handles timer details:

```python
import timeit

setup = "s = set(range(100_000))"
# Time only the lookup, not set creation.
runs = timeit.repeat("-1 in s",
                     setup=setup,
                     number=100_000,
                     repeat=5)
# Fastest total seconds for 100,000 tests.
print(min(runs))
```

The printed number is runtime-dependent; there is no fixed expected duration. It is a total for 100,000 lookups, not seconds per lookup.

The `timeit` docs recommend looking at the minimum of the repeats: higher values are usually caused by other processes interfering, not by your code.

Common benchmarking mistakes:

- **Unrealistic data.** An algorithm that is fine with 100 rows can be quadratic at 100,000. Use production-sized inputs.
- **Mismatched warm-up.** Warm up for steady-state measurements; measure cold starts separately if that is the target. The first run can pay for cold caches, lazy imports, connection setup and JIT compilation (in PyPy, the JVM or V8).
- **Noise.** Laptops slow their CPUs when hot (thermal throttling), browsers steal CPU. Repeat runs and compare distributions, not single numbers.
- **Measuring the wrong thing.** A micro-benchmark of string concatenation tells you nothing if the request spends 90% of its time waiting for Postgres.

## Match the arrival model

- **Load tests that omit queued waits.** A load generator that waits for each response before sending the next one sends fewer requests exactly when the system slows down, so it under-reports bad latency. This is **coordinated omission**; for an independently arriving production workload, tools like wrk2 schedule a target arrival rate and measure latency from intended send times. Constant rate alone is insufficient if delayed sends are omitted from latency. A closed-loop model can be appropriate when the real workload is closed-loop.

## Key takeaways
- Use representative data, repeated measurements and comparable machines and load.
- Warm steady-state tests consistently; measure cold starts separately when they matter.
- For independently arriving traffic, account for latency from intended arrival times.

## Further reading
- [timeit — Python docs](https://docs.python.org/3/library/timeit.html)
- [wrk2 arrival-time latency accounting](https://github.com/giltene/wrk2)
