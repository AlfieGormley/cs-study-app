---
id: sepr-performance-profilers
title: Read profiles and separate CPU from waiting
level: intermediate
minutes: 4
summary: Interpret call timings and sampled stacks, then choose tools for off-CPU delays.
sourceLesson: sepr-profiling
---

Once a representative benchmark exposes the expensive execution path, profile that workload. The question is where time goes, including time when the request is not computing.

## Step 2: profile to find the bottleneck
A **profiler** tells you where time goes. There are two main kinds.

| Kind | How it works | Example |
|---|---|---|
| Deterministic | Hooks calls and returns in scope | `cProfile` |
| Sampling | Records stacks at a fixed rate | `py-spy`, `perf` |

**Deterministic** profilers count observed call events in the profiled execution scope, with overhead that can disproportionately affect tiny functions. **Sampling** profilers periodically capture stacks; some interrupt execution while tools such as py-spy read another process externally. Sampling is approximate and often lower overhead, but production use requires suitable permissions and validation of workload impact. `py-spy` can attach to a running Python process by PID without restarting it.

### Reading cProfile

This command is a template: `app.py` must exist and the resulting profile depends on that program, its inputs and the runtime.

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

A **flame graph** (Brendan Gregg's visualisation) aggregates stacks. This schematic demonstrates the parent/callee layout; its widths are not drawn to match the cProfile numbers above:

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

For whole machines, Gregg's **USE method** is a quick checklist: for each resource (CPU, memory, disk, network), check **Utilisation**, **Resource saturation** (queued work) and **Errors**.

## Key takeaways
- cProfile self time excludes callees; cumulative time includes them.
- A CPU flame graph aggregates samples and stack relationships rather than showing a timeline.
- Low per-request CPU time can indicate I/O, locks or scheduler delay; validate attachment permissions and profiler overhead.

## Further reading
- [The Python Profilers — Python 3.14 docs](https://docs.python.org/3.14/library/profile.html)
- [py-spy](https://github.com/benfred/py-spy)
- [Flame Graphs — Brendan Gregg](https://www.brendangregg.com/flamegraphs.html)
- [Off-CPU Analysis — Brendan Gregg](https://www.brendangregg.com/offcpuanalysis.html)
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
