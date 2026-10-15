---
id: sched-linux-group-fairness-tools
title: Fairness between groups and scheduler inspection
level: advanced
minutes: 3
sourceLesson: sched-linux
summary: Thread-level nice acts within a scheduling group; group weights control competition between groups.
---

## Fairness between whom?

Linux schedules **threads**, not processes. Within one fair group, equal-weight runnable threads compete individually: sixteen such threads collectively receive sixteen shares against one for a single-threaded competitor, when CPU capacity is contested. Two mechanisms rebalance this:

- **Group scheduling**: with cgroups, the fair scheduler first divides CPU between groups (by `cpu.weight` in cgroup v2, default 100), then between tasks within a group. systemd commonly organises services and user sessions into cgroups; the actual hierarchy and enabled controllers determine the competing groups.
- **Autogroup** (since 2.6.38): on kernels with it enabled, each terminal session gets its own group, so a `make -j32` in one terminal doesn't swamp your desktop.

One surprise follows: under group scheduling, a thread's nice value only matters **relative to other threads in the same group**. When two autogroups compete and a task is alone in its group, renicing that task changes no relative competitor inside that group. Different cgroup layouts or other tasks within the groups can change the outcome.
## The other fair policies

- **SCHED_BATCH**: fair share, but treated as CPU-bound and preempts others less; good for batch jobs that want cache-friendly long runs.
- **SCHED_IDLE**: extremely low-weight background work in the fair class. It is not the per-CPU idle task and does not promise zero service whenever normal work is runnable.
## Seeing it on a real system

The following ps listing is illustrative; policies, identifiers and commands on your host will differ.

```
$ ps -eLo pid,tid,cls,rtprio,ni,comm
  PID   TID CLS RTPRIO  NI COMMAND
  612   612  TS      -   0 sshd
  880   901  FF     50   - audio-engine
 1200  1200  TS      -  19 backup
```

`TS` is the fair class, `FF` is FIFO, `RR` is round robin, `DLN` is deadline. In `top`, the PR column shows 20 plus the nice value for normal tasks; real-time tasks show negative numbers (minus 1 minus their real-time priority), and `rt` for real-time priority 99.

`/proc/<pid>/sched` shows a task's vruntime, slice and switch counts, and `perf sched` records scheduling latency. Several fair-scheduler debugging tunables moved from /proc/sys/kernel to /sys/kernel/debug/sched/ in Linux 5.13. Other settings, including RT bandwidth and RR timeslice controls, remain sysctls; availability also depends on configuration and privileges.
## Pitfalls

- **Expecting nice to be a priority.** It's a weight. Nice 19 gets a small fair share; `SCHED_IDLE` gives background work an even smaller weight, not a strict idle-only guarantee.
- **Renicing across groups.** With autogroup or cgroups, nice only competes within the group. Use `cpu.weight` between groups.
- **Making things real-time "to be safe".** An RT thread that spins starves everything below it, including kernel threads that it may depend on. Use RT for short, bounded work.
- **RT with ordinary locks.** RT threads sharing locks with normal threads invite priority inversion; use `PTHREAD_PRIO_INHERIT` mutexes.

## Key takeaways
- Thread-level nice acts within a scheduling group; group weights control competition between groups.
- SCHED_IDLE remains a low-weight fair policy, separate from the per-CPU idle task.
- Inspect per-thread policies and queue behaviour before changing tunables or selecting real-time policies.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
- [CPU-controller hierarchy — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
