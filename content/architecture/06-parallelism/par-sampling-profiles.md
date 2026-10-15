---
id: par-sampling-profiles
title: Sampling events, call stacks and flame graphs
level: advanced
minutes: 3
sourceLesson: par-measuring
summary: Record the selected sampling event and unwinding conditions.
---

### Finding hot spots with `perf record`

Counting aggregates events; **sampling profiling** associates selected events with locations in the program. For example:

```
$ perf record -g ./app
$ perf report
```

Choose and record the event and sampling settings. Samples taken from cycles are weighted toward cycles, not necessarily wall time, and the default event can depend on availability. Call-stack quality requires suitable unwinding support, symbols and build configuration. Overhead and statistical precision depend on frequency, event support and workload; sample locations may suffer **sampling skid**, landing a few instructions after the one that caused the event.

Brendan Gregg’s **flame graphs** show aggregated stack samples. Rectangle width represents inclusive sample weight; stack depth is vertical and horizontal ordering is **not a timeline**. The selected event determines what that weight means. A supported Linux build of Python 3.12 or later can expose Python names to `perf` with `python -X perf`; check its build and profiling prerequisites.

## Reading a profile as evidence

Suppose a cycles-based profile gives a parsing stack 60% of the sample weight and an allocation stack 25%. That motivates inspecting those paths, but does not prove that removing the parser would cut wall time by exactly 60%. The event is cycles, samples have statistical uncertainty, and blocked time may be absent from an on-CPU profile.

Keep a release-like build with usable symbols and a supported stack-unwinding method. Record the exact command, input and sampling event. Repeat long enough to avoid interpreting a handful of samples as a stable ranking. Missing stacks or unresolved addresses are evidence-quality problems to fix before making detailed claims about callers.

After a change, compare completed work and total time as well as the shape of the graph. A function can become a larger percentage because another function became faster. Its absolute cost may have fallen. Similarly, a wide library frame may include substantial time in callees; inclusive width is different from time spent only in that function's own instructions.

## Key takeaways
- Record the selected sampling event and unwinding conditions.
- Flame-graph width is inclusive sample weight; horizontal placement is not chronology.

## Further reading
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
