---
id: sched-linux-history-classes
title: Linux scheduler history and class ordering
level: advanced
minutes: 3
sourceLesson: sched-linux
summary: Classic scheduler names describe different selection policies across kernel versions.
---

The earlier MLFQ units describe a policy that guesses which jobs are interactive and rewards them. Linux took a different route in 2007: stop guessing, and divide the CPU **fairly**, in proportion to a weight. That idea, the Completely Fair Scheduler (CFS), entered mainline in Linux 2.6.23. Linux 6.6, released in 2023, changed fair-class selection to **EEVDF**, which keeps weighted fairness and adds an explicit notion of latency. Deployed distributions can retain older kernels or backport changes.

Real-time work sits above all of this, in strict-priority classes that the fair scheduler never overrides.
## A short history

The O(...) labels are Big O notation, where n is the number of runnable tasks: O(n) means picking the next task took time proportional to n, and O(1) means it took the same time however many tasks there were.

| Kernel | Scheduler |
|---|---|
| 2.4 | O(n): scan runnable tasks |
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

## Key takeaways
- Classic scheduler names describe different selection policies across kernel versions.
- Real-time and deadline classes normally outrank fair work, subject to bandwidth controls and fair-server service.
- sched_ext can replace normal scheduling according to its configured mode.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
