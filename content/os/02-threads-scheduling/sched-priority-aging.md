---
id: sched-priority-aging
title: Strict priorities and aging
level: intermediate
minutes: 3
sourceLesson: sched-priority-mlfq
summary: Strict priority can starve lower-priority work; Linux nice values instead express fair weights.
---

FCFS, SJF and round robin treat all jobs as equals. Real systems don't: an audio thread that misses a 5 ms deadline produces a click, while a backup job can wait. **Priority scheduling** lets the system express that. It also introduces two classic failure modes, **starvation** and **priority inversion**, and the multilevel feedback queue adapts scheduling to observed behaviour. Priority inheritance addresses lock-related priority inversion separately.
## Priority scheduling

In a strict-priority model, the scheduler chooses the highest-priority ready thread. Linux nice values instead set relative fair-scheduling weights; they are not strict priorities. Threads of equal priority usually share the CPU round robin. With preemption, a higher-priority thread that becomes ready takes the CPU immediately.

Conventions vary, so always check which way the numbers run:

| System | Range | Higher priority is |
|---|---|---|
| Linux nice | −20 to 19 | Lower number |
| Linux real-time | 1 to 99 | Higher number |
| Windows | 0 to 31 | Higher number |

There are **static priorities** (set once by the user or administrator) and **dynamic priorities** (adjusted by the OS based on behaviour). SJF is in fact a priority scheduler whose priority is the predicted burst length.
## Starvation and aging

Strict priority has an obvious hole: if high-priority work keeps arriving, low-priority work **never runs**. That is **starvation**.

> [!note] Content gap: unverified historical anecdote
> A commonly repeated story about a job waiting for years on an early time-sharing system has been omitted because this audit could not establish a reliable primary record. The starvation mechanism does not depend on that story.

The standard cure is **aging**: increase a thread's priority the longer it waits, so that eventually it beats the steady stream of newcomers.
## How long does aging take?

Suppose priority numbers run from 0 (highest) to 127 (lowest), and a waiting thread improves by one level every second. A thread at 127 competes with a constant load at priority 20. The wait is the number of levels it must climb times the time each level takes:

```formula
t_age = (p_start − p_load)t_step
t_age = (127 − 20) × 1 s = 107 s
where
t_age: how long the thread waits before it reaches the same priority as the competing work, in seconds (s)
p_start: the waiting thread's starting priority number, 127 here (the lowest priority)
p_load: the priority number of the steady competing load, 20 here
t_step: how long the thread must wait to improve by one level, 1 s here
s: seconds
In words: count the levels the thread has to climb, then multiply by how long each level takes.
```

So it reaches equal priority after 107 seconds. Actual first service also depends on tie-breaking and queue length, and a chosen policy may reset the priority after the thread has run.

## Key takeaways
- Strict priority can starve lower-priority work; Linux nice values instead express fair weights.
- Check whether a larger numeric priority means more or less importance.
- Aging can raise waiting work to a competing priority; first service still depends on ties and queued work.

## Further reading
- [Scheduling: The Multi-Level Feedback Queue — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf)
- [Glenn Reeves: what happened on Pathfinder — firsthand correction in RISKS](https://catless.ncl.ac.uk/Risks/19.54.html)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority inheritance — Wikipedia](https://en.wikipedia.org/wiki/Priority_inheritance)
- [RT-mutex subsystem with PI support — Linux kernel docs](https://docs.kernel.org/locking/rt-mutex.html)
- [Multilevel feedback queue — Wikipedia](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
