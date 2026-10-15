---
id: conc-python-awaits
title: Sequential waits and concurrent Python tasks
level: basic
minutes: 3
sourceLesson: conc-async-await
summary: Calling a Python coroutine function does not run its body.
---

On one responsive asyncio loop, ordinary tasks share a thread cooperatively. The examples below use CPython’s default task factory; eager task creation can change when a coroutine starts.

## Python asyncio

An `async def` function is a **coroutine function**. Calling it does *not* run it; it returns a coroutine object that runs when awaited or scheduled.

```python
# Measure elapsed waits, not CPU work.
import asyncio, time

async def fetch(name, delay):
    await asyncio.sleep(delay)  # fake I/O
    return name

async def main():
    t = time.perf_counter()
    a = await fetch("a", 1)
    b = await fetch("b", 1)
    print(time.perf_counter() - t)  # ~2.0

    t = time.perf_counter()
    r = await asyncio.gather(
        fetch("a", 1), fetch("b", 1),
        fetch("c", 1))
    print(r)  # ['a', 'b', 'c']
    print(time.perf_counter() - t)  # ~1.0

asyncio.run(main())
```

The first half takes two seconds: `await` means "pause *this* coroutine until the result is ready", so the second fetch does not start until the first finishes. `async` does not make code concurrent on its own; you have to start several things before awaiting them. `asyncio.gather` (or `asyncio.create_task`, or a `TaskGroup`, covered in the later task-scope unit) does that.

The two timings follow a simple rule. Awaiting one after another adds the waits up; starting them all first lets the waits overlap, so the total is roughly the longest single wait:

```formula
T_seq = d_1 + d_2 + … + d_n
T_conc ≈ max(d_1, d_2, …, d_n)
T_seq = 1 s + 1 s = 2 s
T_conc ≈ max(1 s, 1 s, 1 s) = 1 s
where
T_seq: the total time when each await finishes before the next one starts, in seconds (s)
T_conc: the total time when all the operations are started first and then awaited together, in seconds (s)
d_1, d_2, d_n: how long the first, second and last operation spends waiting, in seconds (s); here each fetch waits 1 s, with two fetches in the sequential half of the example and three in the `gather` half
n: how many operations there are
…: and so on, for every operation in between
max: the largest of the values listed
≈: approximately equal to; a little scheduling overhead is added on top
s: seconds
In words: sequential awaits cost the sum of the waits, while overlapped awaits cost about the longest single wait.
```

So ten 1-second fetches take about 10 seconds awaited one by one, and about 1 second with `gather`. The rule only holds while the waits are genuinely idle time (network, timers, disk). It breaks down when a task does CPU work or blocks the thread, when the far end limits how many requests it serves at once, or when a connection pool caps how many can run.

Tasks can interleave at suspension points:

```python
# Start these waits before joining.
async def worker(name, n):
    for i in range(n):
        print(name, i)
        await asyncio.sleep(0)  # yield

async def main():
    await asyncio.gather(
        worker("A", 2), worker("B", 2))
# default factory: A 0, B 0, A 1, B 1
```

`asyncio.sleep(0)` is the idiom for "let others run". Without any `await` inside the loop, A would print both lines before B started.

## Bound the number of in-flight operations

Starting everything at once is not a capacity policy. Creating 20,000 fetches can exhaust file descriptors, a connection pool, memory or the remote service’s limits. An `asyncio.Semaphore(100)` around each active fetch admits at most 100 operations into that protected portion at a time. It still permits 20,000 waiting task objects if they were all created up front; a bounded worker queue also limits that retained task backlog. Choose the bound from service capacity and measure it rather than treating 100 as a universal recommendation.

## Key takeaways
- Calling a Python coroutine function does not run its body.
- Starting operations together overlaps idle waits; capacity limits still bound concurrency.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html)
- [Primary source: html.spec.whatwg.org](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [Primary source: nodejs.org](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
