---
id: sched-linux
title: Linux scheduling - CFS, EEVDF and real-time classes
level: advanced
minutes: 15
summary: How Linux actually picks the next thread - scheduling classes, CFS's virtual runtime and weights, nice values, the EEVDF scheduler that replaced CFS in 6.6, and the SCHED_FIFO, SCHED_RR and SCHED_DEADLINE real-time policies.
---

The previous lesson's MLFQ guesses which jobs are interactive and rewards them. Linux took a different route in 2007: stop guessing, and divide the CPU **fairly**, in proportion to a weight. That idea, the Completely Fair Scheduler (CFS), ran almost every Linux machine for 16 years. In 2023 its core was replaced by **EEVDF**, which keeps the fairness and adds an explicit notion of latency.

Real-time work sits above all of this, in strict-priority classes that the fair scheduler never overrides.

## A short history

| Kernel | Scheduler |
|---|---|
| 2.4 | O(n): scan every task |
| 2.6.0 (2003) | O(1): priority arrays plus interactivity heuristics |
| 2.6.23 (2007) | CFS |
| 6.6 (2023) | EEVDF replaces CFS's pick logic |
| 6.12 (2024) | sched_ext: schedulers in BPF |

The O(1) scheduler was fast but relied on heuristics to guess which tasks were interactive, much like MLFQ. Those heuristics could be fooled, and desktop latency suffered under load. Con Kolivas's fairness-based RSDL patches showed a simpler approach worked, and Ingo Molnar wrote CFS in response.

## Scheduling classes

The kernel doesn't have one scheduler; it has a stack of **scheduling classes**, checked in strict order. Ordinary selection considers higher classes first, subject to bandwidth limits. A deadline-class fair server can also dispatch fair work to prevent starvation.

```
stop      (kernel internal, per CPU)
deadline  SCHED_DEADLINE
rt        SCHED_FIFO, SCHED_RR (1-99)
fair      SCHED_NORMAL, SCHED_BATCH,
          SCHED_IDLE
ext       sched_ext (BPF, if loaded)
idle      the idle task
```

Ignoring throttling and fair-server service, an eligible `SCHED_FIFO` thread outranks normal threads regardless of nice. Ordinary applications usually use `SCHED_NORMAL` (`SCHED_OTHER` in the userspace API). A loaded sched_ext scheduler can take over normal, batch and idle-policy tasks; in partial mode it handles only `SCHED_EXT` tasks.

## CFS: an ideal CPU, simulated

CFS's design starts from an imaginary "ideal multi-tasking CPU" that runs all *n* runnable tasks simultaneously, each at 1/*n* speed. Real hardware can run only one task per CPU at a time, so CFS tracks how far each task has fallen behind that ideal.

The tool is **virtual runtime** (`vruntime`), in nanoseconds. When a task runs for a real time *Δ*, its vruntime grows by:

```
vruntime += delta * 1024 / weight
```

The rule for picking is then trivial: **run the task with the smallest vruntime**, the one that has had least.

To find it fast, CFS keeps runnable tasks in a **red-black tree** ordered by vruntime, caching the leftmost node. Picking is O(1); inserting a task after it runs or wakes is O(log *n*).

```
          [B 40]
         /      \
     [A 25]    [D 70]
     /
 [C 10] <- leftmost: runs next
```

As C runs, its vruntime rises and it moves right; eventually another task becomes leftmost and preempts it. A small granularity stops tasks swapping every microsecond and thrashing the cache.

### Weights and nice

Nice values map to weights through a fixed table. Nice 0 is 1024, and each step is a factor of about **1.25**:

| Nice | Weight |
|---|---|
| −20 | 88761 |
| −5 | 3121 |
| 0 | 1024 |
| 1 | 820 |
| 5 | 335 |
| 19 | 15 |

For two otherwise equal competitors in one fair group, moving one from nice 0 to nice 1 changes the split from 50/50 to about 55.5/44.5. The share change depends on the competitors. A higher weight makes vruntime grow *more slowly*, so the task stays leftmost for longer and gets more real CPU.

> [!example] Who gets what?
> Three CPU-bound tasks in the same fair group share one CPU: A and B at nice 0, C at nice 5. Total weight = 1024 + 1024 + 335 = 2383.
> - A: 1024 / 2383 ≈ 43%
> - B: ≈ 43%
> - C: 335 / 2383 ≈ 14%
>
> Check with vruntime: after 10 ms of real time each, A and B gain 10 ms of vruntime, but C gains 10 × 1024 / 335 ≈ 30.6 ms. C becomes "rightmost" three times as fast, so it runs about a third as often.

Note what nice is *not*: it's not a strict priority. A nice 19 task alongside a nice 0 task still gets 15 / 1039, about 1.4%. That proportional share assumes competition within the same fair group, available CPU bandwidth and no overriding higher-class work.

### Sleepers and new tasks

A task that sleeps for a minute would wake with a tiny vruntime and monopolise the CPU while it "caught up". CFS prevents this with `min_vruntime`, a monotonic floor tracking the smallest vruntime in the queue. A waking task's vruntime is raised to roughly `min_vruntime` minus a small bonus (half a latency period), so interactive tasks get a modest head start, not a minute's worth. New tasks start near `min_vruntime` too.

### Latency and slices

CFS had no fixed quantum. It aimed to run every runnable task once within a **target latency** (6 ms by default, scaled by 1 + log2 of the CPU count, capped at 8 CPUs), with a minimum slice of 0.75 ms (also scaled) so that hundreds of tasks wouldn't each get microseconds.

That worked, but latency was a side effect of fairness. There was no way to say "this task wants short, frequent slices", so CFS grew wake-up heuristics to keep desktops snappy, and these were hard to reason about.

## EEVDF: fairness plus deadlines

**Earliest Eligible Virtual Deadline First** comes from a 1995 paper by Ion Stoica and Hussein Abdel-Wahab. Peter Zijlstra's implementation became the fair-class scheduler in Linux 6.6. Weights, nice and the red-black tree stay; the *picking rule* changes.

Two ideas:

1. **Lag.** Compare the service a task should have received on the ideal CPU with what it actually got. Positive lag means it is owed CPU; negative means it has had more than its share. In practice the kernel computes the weighted average vruntime *V* of the queue, and a task is **eligible** if its vruntime ≤ *V* (lag ≥ 0).
2. **Virtual deadline.** Each task requests a slice *r* (by default the base slice). Its deadline is its vruntime plus that slice scaled by weight:

```
deadline = vruntime + r * 1024 / weight
```

The rule: **among eligible tasks, run the one with the earliest virtual deadline.**

Eligibility keeps it fair: nobody who is ahead of their share gets picked. Deadlines add latency control: a task asking for a **shorter slice** gets an earlier deadline, so it runs sooner, though in smaller pieces. Over time it gets the same total share.

> [!example] Short slice, same weight
> A and B are both nice 0 with vruntime 0. A uses a 3 ms slice; B asks for 1 ms.
> - Both are eligible (vruntime 0 = *V*).
> - Deadlines: A = 0 + 3 = 3, B = 0 + 1 = 1.
> - B runs first, for 1 ms. Its vruntime becomes 1 and its next deadline 2.
>
> B now waits for A to catch up before it is eligible again, so neither gets more than its half. B simply gets its half in smaller, more frequent pieces.

In the checked Linux 6.12 source the unscaled base slice is 0.75 ms; the default logarithmic scaling gives 3 ms at eight or more CPUs. Tunables and later kernels can differ. Since Linux 6.12 a normal task can request its own slice, between 0.1 ms and 100 ms, through the `sched_runtime` field of `sched_setattr()`.

Lag also needs care for sleepers. A task that sleeps with negative lag shouldn't erase its debt by sleeping briefly. Current kernels keep such a task on the queue in a "deferred dequeue" state so its lag decays, rather than simply resetting it.

> [!note] Is CFS gone?
> The name lingers: the fair class still lives in `kernel/sched/fair.c`, and many docs and tools still say CFS. Weights, nice, vruntime, group scheduling and CFS bandwidth control all carried over. What changed is how the next task is chosen and how preemption is decided.

## Fairness between whom?

Linux schedules **threads**, not processes. Within one fair group, equal-weight runnable threads compete individually: sixteen such threads collectively receive sixteen shares against one for a single-threaded competitor, when CPU capacity is contested. Two mechanisms rebalance this:

- **Group scheduling**: with cgroups, the fair scheduler first divides CPU between groups (by `cpu.weight` in cgroup v2, default 100), then between tasks within a group. systemd puts each service and user session in its own cgroup.
- **Autogroup** (since 2.6.38): on kernels with it enabled, each terminal session gets its own group, so a `make -j32` in one terminal doesn't swamp your desktop.

One surprise follows: under group scheduling, a thread's nice value only matters **relative to other threads in the same group**. `renice` on a process in one session does nothing against a process in another.

## Real-time classes

For audio, industrial control and low-latency trading, fairness is the wrong goal. The `rt` class gives **strict priorities** from 1 to 99 (higher wins):

- **SCHED_FIFO**: runs until it blocks, yields or is preempted by a higher RT priority. No time slice at all.
- **SCHED_RR**: the same, but threads at *equal* priority rotate with a time slice (100 ms by default, `sched_rr_timeslice_ms`).

```python
import os

# Needs CAP_SYS_NICE or
# sufficient RLIMIT_RTPRIO
os.sched_setscheduler(
    0, os.SCHED_FIFO, os.sched_param(50))
print(os.sched_getscheduler(0)
      == os.SCHED_FIFO)  # True
```

From the shell: `chrt -f 50 ./audio-engine`, and `chrt -p <pid>` to inspect.

> [!warning] A runaway FIFO thread
> A `SCHED_FIFO` thread stuck in a busy loop never yields, so nothing below it runs on that CPU: not your shell, not `kill`. Linux guards against this. RT throttling commonly limits RT work to 950 ms per 1 s (`sched_rt_runtime_us` / `sched_rt_period_us`). Linux 6.12 also introduced a deadline-class fair server that can supply CPU to fair tasks. These are distinct mechanisms; behaviour depends on kernel version, configuration and tunables.

### SCHED_DEADLINE

Since Linux 3.14, the top policy is **SCHED_DEADLINE**. Instead of a priority, a task declares three numbers:

- **runtime**: CPU time needed per period;
- **deadline**: by when, relative to the period start;
- **period**: how often it repeats.

```
chrt -d --sched-runtime  5000000 \
        --sched-deadline 10000000 \
        --sched-period  16666666 0 ./render
```

That says "5 ms of CPU every 16.7 ms frame, finished within 10 ms". The kernel schedules deadline tasks by **Earliest Deadline First**, and uses the Constant Bandwidth Server to stop any task exceeding its runtime. It also performs **admission control**: if the new task's utilisation (runtime / period) would push the total over the permitted limit, `sched_setattr()` fails with `EBUSY`. Admission checks reserve bandwidth; acceptance alone is not a universal proof that application deadlines will be met. Worst-case execution time, blocking, deadline versus period, CPU topology and scheduling assumptions still matter. The kernel documentation distinguishes schedulability tests from the simpler utilization admission test.

### The other fair policies

- **SCHED_BATCH**: fair share, but treated as CPU-bound and preempts others less; good for batch jobs that want cache-friendly long runs.
- **SCHED_IDLE**: extremely low-weight background work in the fair class. It is not the per-CPU idle task and does not promise zero service whenever normal work is runnable.

## Seeing it on a real system

```
$ ps -eLo pid,tid,cls,rtprio,ni,comm
  PID   TID CLS RTPRIO  NI COMMAND
  612   612  TS      -   0 sshd
  880   901  FF     50   - audio-engine
 1200  1200  TS      -  19 backup
```

`TS` is the fair class, `FF` is FIFO, `RR` is round robin, `DLN` is deadline. In `top`, real-time tasks show `rt` in the PR column.

`/proc/<pid>/sched` shows a task's vruntime, slice and switch counts, and `perf sched` records scheduling latency. Scheduler tunables moved from `/proc/sys/kernel` to `/sys/kernel/debug/sched/` in 5.13, a signal that they're for debugging, not routine tuning.

## Pitfalls

- **Expecting nice to be a priority.** It's a weight. Nice 19 gets a small fair share; `SCHED_IDLE` gives background work an even smaller weight, not a strict idle-only guarantee.
- **Renicing across groups.** With autogroup or cgroups, nice only competes within the group. Use `cpu.weight` between groups.
- **Making things real-time "to be safe".** An RT thread that spins starves everything below it, including kernel threads that it may depend on. Use RT for short, bounded work.
- **RT with ordinary locks.** RT threads sharing locks with normal threads invite priority inversion; use `PTHREAD_PRIO_INHERIT` mutexes.

## Key takeaways
- Linux stacks scheduling classes: deadline, then real-time, then fair, then idle. Bandwidth controls and deadline-class fair-server service qualify this ordering.
- CFS gives each task CPU in proportion to its weight by always running the task with the smallest vruntime; vruntime grows more slowly for heavier tasks.
- Nice maps to weights that differ by about 1.25× per step (CPU shares depend on competing weights); it's proportional sharing, not strict priority.
- EEVDF (6.6+) keeps the weights but picks the eligible task (lag ≥ 0) with the earliest virtual deadline, so shorter requested slices mean lower latency without a bigger share.
- SCHED_FIFO and SCHED_RR give strict priorities 1–99; SCHED_DEADLINE reserves runtime using deadline/period parameters and admission control; application deadline guarantees require additional schedulability assumptions. All are powerful enough to starve the system, which is why limits exist.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
