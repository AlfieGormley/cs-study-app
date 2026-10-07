---
id: sched-priority-mlfq
title: Priorities, MLFQ and starvation
level: intermediate
minutes: 13
summary: Priority scheduling and its failure modes, the multilevel feedback queue that learns which jobs are interactive, aging, and priority inversion from Mars Pathfinder to priority inheritance.
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

Priorities can be **static** (set once by the user or administrator) or **dynamic** (adjusted by the OS based on behaviour). SJF is in fact a priority scheduler whose priority is the predicted burst length.

## Starvation and aging

Strict priority has an obvious hole: if high-priority work keeps arriving, low-priority work **never runs**. That is **starvation**.

> [!note] Content gap: unverified historical anecdote
> A commonly repeated story about a job waiting for years on an early time-sharing system has been omitted because this audit could not establish a reliable primary record. The starvation mechanism does not depend on that story.

The standard cure is **aging**: increase a thread's priority the longer it waits, so that eventually it beats the steady stream of newcomers.

> [!example] How long does aging take?
> Priorities run from 0 (highest) to 127. A waiting thread improves by 1 every second. A thread at 127 competing with a constant load at priority 20 must climb 107 levels, so it reaches equal priority after 107 seconds. Actual first service also depends on tie-breaking and queue length; a chosen policy may reset priority after service.

## The multilevel feedback queue (MLFQ)

The deeper problem is that the OS doesn't know which jobs are short or interactive. SJF needs that knowledge; round robin ignores it. The **multilevel feedback queue**, first described by Corbató's CTSS in 1962 (part of the work that earned him the Turing Award), *learns* it by watching how jobs behave.

MLFQ keeps several ready queues, one per priority level. The textbook rules (as in OSTEP) are:

1. If priority(A) > priority(B), A runs.
2. If priority(A) = priority(B), they share the CPU round robin.
3. A new job enters at the **highest** priority.
4. Once a job uses up its **time allotment** at a level, however many times it gave up the CPU along the way, it moves down one level.
5. After some period S, move **every** job back to the top queue (the **priority boost**).

Lower queues usually get **longer quanta**: short slices at the top for responsiveness, long slices at the bottom where CPU-bound jobs live and switching overhead matters more.

```
Q2 (high)  q=10ms  [new jobs, interactive]
Q1         q=20ms  [demoted once]
Q0 (low)   q=40ms  [CPU-bound, RR]
```

### Why it approximates SJF

Rule 3 assumes every new job might be short. If it is, it finishes (or blocks) while still at the top, getting SJF-like treatment. If it isn't, Rule 4 pushes it down level by level until it sits with the other long jobs. The scheduler has learned the job is CPU-bound without being told.

### A worked trace

Three levels as above, with an allotment of one quantum per level. A CPU-bound job A arrives at 0. An interactive job B arrives at 50 and repeatedly runs for 2 ms, then waits 8 ms for I/O.

```
t (ms)  0   10        30   50 52   60 62
Q2      [A ]               [B]     [B]
Q1          [A     ]
Q0                  [A   ]    [A  ]   [A
```

1. 0–10: A uses its full 10 ms at Q2 and is demoted.
2. 10–30: A uses 20 ms at Q1 and is demoted to Q0.
3. 30–50: A runs at Q0.
4. 50: B arrives at Q2 and preempts A immediately (Rule 1).
5. B runs 2 ms and blocks; A carries on until B's I/O completes at 60, when B preempts it again.

In the idealised zero-overhead trace, B runs immediately when ready; no measured wake-up latency is implied. A uses all the leftover time. That's the behaviour we want from a desktop.

### Rule 4 and gaming the scheduler

Early MLFQ designs had a gentler rule: *a job that gives up the CPU before its quantum expires keeps its priority*. That rewards interactive jobs, but it can be **gamed**. A job that runs for 9.9 ms of a 10 ms quantum, then issues a trivial I/O, stays at the top forever and gets nearly all the CPU.

Rule 4 closes the hole with better **accounting**: the scheduler tracks *total* CPU used at a level, not per burst. In the trace above, B uses 2 ms per burst, so after five bursts it has used its 10 ms allotment and drops to Q1. That is the cost of being game-proof: even a genuinely interactive job slowly sinks. Rule 5 lifts it back.

### Rule 5: the priority boost

Without boosts, two things go wrong:

- **Starvation**: many interactive jobs at the top can use all the CPU, and jobs in Q0 never run.
- **Changing behaviour**: a job that was CPU-bound (say, a program loading data) and then becomes interactive is stuck at the bottom.

Boosting everything to the top every S ms fixes both. S is one of Ousterhout's "voodoo constants": too long and long jobs starve; too short and interactive jobs lose their advantage. Real systems tune it, or replace the boost with aging or decay of usage history.

### MLFQ in real systems

The cited historical Solaris documentation describes 60 time-sharing priorities and default quanta from 40 ms at priority 59 to 200 ms at priority 0; these are version/configuration-specific values. Windows uses 32 priority levels with dynamic boosts for threads that finish waiting on I/O or own the foreground window. FreeBSD's ULE scheduler computes an "interactivity score" from sleep and run times. Linux took a different path: since 2.6.23 (2007) its normal scheduler has been built on fairness rather than feedback queues, as the next lesson explains.

## Priority inversion

Priorities interact badly with locks. Take three threads on one CPU, sharing a mutex `m`:

- **H**: high priority, needs `m` briefly;
- **M**: medium priority, CPU-heavy, never touches `m`;
- **L**: low priority, takes `m` now and then.

```
L: lock(m) ...........   ...unlock
H:      wakes, lock(m) -> BLOCKED
M:           wakes, runs, runs, runs
           <---- H waits for M ---->
```

1. L takes `m`.
2. H wakes, preempts L and tries to lock `m`. It blocks.
3. M wakes. It outranks L, so it preempts L.
4. L can't run, so it can't release `m`, so H can't run.

H is now waiting for M, a lower-priority thread that has nothing to do with `m`. The priorities have been **inverted**. Worse, the delay isn't bounded by L's short critical section; it lasts as long as M (and any other medium-priority work) keeps running. This is **unbounded priority inversion**.

### Mars Pathfinder, 1997

Glenn Reeves, who led Pathfinder's software team, describes a priority inversion involving a semaphore inside VxWorks `select`/pipe handling. The low-priority ASI/MET task held the resource; intermediate work delayed it while the higher-priority `bc_dist` task waited. A deadline check by `bc_sched` triggered a reset.

Engineers reproduced the failure with tracing, enabled priority inheritance through a configuration change, tested the wider effects and deployed it using their validated spacecraft patch mechanism. Reeves explicitly says they **did not use the VxWorks shell** for the update. He also says the pre-landing occurrence was investigated and remained unresolved, rather than being dismissed as a hardware glitch.

This firsthand correction matters: retain the inversion lesson without repeating the inaccurate interpreter-fix and ignored-warning story.

### Priority inheritance

The fix is **priority inheritance**: while a thread holds a lock that a higher-priority thread is waiting for, it temporarily runs at the waiter's priority.

1. H blocks on `m`, held by L. L is boosted to H's priority.
2. M wakes but can't preempt L, which now outranks it.
3. L finishes its critical section and releases `m`, dropping back to low priority.
4. H takes `m` and runs.

In this isolated three-thread example, H waits for L's remaining critical section plus scheduling overhead. General bounds must include nesting, higher-priority interference and any blocking by the holder. Inheritance must be **transitive**: if L is itself blocked on a lock held by another thread, that thread is boosted too.

An alternative is an **immediate priority ceiling** protocol: each mutex gets a ceiling equal to the highest priority of any thread that may lock it, and whoever holds it runs at the ceiling straight away. It needs the ceiling worked out in advance, but avoids repeated priority changes.

POSIX exposes both as mutex attributes:

```c
pthread_mutexattr_t a;
pthread_mutexattr_init(&a);
pthread_mutexattr_setprotocol(
    &a, PTHREAD_PRIO_INHERIT);
/* or PTHREAD_PRIO_PROTECT for ceiling */
pthread_mutex_init(&m, &a);
```

On Linux, `PTHREAD_PRIO_INHERIT` mutexes are built on PI futexes and the kernel's `rt_mutex`, which handles chains of boosts. The PREEMPT_RT real-time kernel goes further and converts most kernel spinlocks into priority-inheriting sleeping locks for the same reason.

Priority inversion matters most for real-time threads with strict priorities. Ordinary Linux threads under the fair scheduler suffer milder versions: a low-weight thread holding a lock still runs, just slowly. The next module covers locks in depth.

## Key takeaways
- Priority scheduling runs the most important ready thread first; equal priorities share round robin. Check which way the numbers run.
- Strict priorities starve low-priority work; aging raises a thread's priority the longer it waits.
- MLFQ learns behaviour: new jobs start high, jobs that use their allotment sink, and periodic boosts prevent starvation and let jobs change character.
- Track total CPU used at a level (not per burst) so that jobs can't game the scheduler by yielding just before the quantum ends.
- Priority inversion lets a medium-priority thread delay a high-priority one indefinitely. Priority inheritance mitigates inversion under stated scheduling/locking assumptions; Pathfinder's fix enabled it for the relevant semaphore mechanism.

## Further reading
- [Scheduling: The Multi-Level Feedback Queue — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf)
- [Glenn Reeves: what happened on Pathfinder — firsthand correction in RISKS](https://catless.ncl.ac.uk/Risks/19.54.html)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority inheritance — Wikipedia](https://en.wikipedia.org/wiki/Priority_inheritance)
- [RT-mutex subsystem with PI support — Linux kernel docs](https://docs.kernel.org/locking/rt-mutex.html)
- [Multilevel feedback queue — Wikipedia](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
