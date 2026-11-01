---
id: sepr-performance-benchmarks
title: Benchmark the workload users run
level: intermediate
minutes: 4
summary: Compare repeated measurements and recognise load tests that omit queued requests.
sourceLesson: sepr-profiling
---

The target from the previous lesson decides what to measure. A benchmark is only useful if its data, what it times and the way requests arrive all resemble that target.

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

The printed number depends on the machine and Python version (about half a millisecond on one recent laptop running Python 3.14). Note that it is the total for 100,000 lookups, not the time per lookup.

The `timeit` docs recommend looking at the minimum of the repeats: higher values are usually caused by other processes interfering, not by your code.

Common benchmarking mistakes:

- **Unrealistic data.** An algorithm that is fine with 100 rows can be quadratic at 100,000. Use production-sized inputs.
- **Mismatched warm-up.** Warm up for steady-state measurements; measure cold starts separately if that is the target. The first run can pay for cold caches, lazy imports, connection setup and JIT compilation (in PyPy, the JVM or V8).
- **Noise.** Laptops slow their CPUs when hot (thermal throttling), browsers steal CPU. Repeat runs and compare distributions, not single numbers.
- **Measuring the wrong thing.** A micro-benchmark of string concatenation tells you nothing if the request spends 90% of its time waiting for Postgres.

## Match the arrival model

A common load-testing trap hides exactly the slow periods you care about. A load generator that waits for each response before sending the next one sends fewer requests when the system slows down, so a stall produces only a handful of slow samples and the percentiles look far better than users experience. This is **coordinated omission**: the tool unintentionally coordinates with the system it is testing and omits the requests that would have queued up.

If real users arrive independently of how fast the server is (most public web traffic), use a tool such as wrk2 that sends requests on a fixed schedule and measures each request's latency from when it *should* have been sent. A constant rate is not enough on its own: if the tool quietly delays sends during a stall and times them from the actual send, the omission is still there. If the real workload is itself closed-loop (a fixed pool of workers that each wait for a reply), a closed-loop test can be the right model.

> [!analogy] Real-world analogy: timing a doctor's waiting room
> To measure waiting times at a surgery, you send in one volunteer, wait until they come out, then send the next. When the doctor disappears for a two-hour emergency, your one volunteer waits two hours and you record one bad wait. Real patients keep arriving during those two hours, so dozens of people would have waited, many of them for a long time.
>
> **How it maps:** The volunteer is a closed-loop load generator thread, the emergency is a server stall and the real arriving patients are independent user requests. Timing each patient from their appointment slot, not from when you finally sent them in, is measuring from the intended send time.
>
> **Where it stops:** Some real systems really are closed-loop: a fixed set of batch workers does wait for each reply before sending more, and for them the one-at-a-time measurement is the honest one.

## Key takeaways
- Use representative data, repeated measurements and comparable machines and load.
- Warm steady-state tests consistently; measure cold starts separately when they matter.
- For independently arriving traffic, account for latency from intended arrival times.

## Further reading
- [timeit — Python docs](https://docs.python.org/3/library/timeit.html)
- [wrk2 arrival-time latency accounting](https://github.com/giltene/wrk2)
