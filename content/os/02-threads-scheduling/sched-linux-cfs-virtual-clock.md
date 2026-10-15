---
id: sched-linux-cfs-virtual-clock
title: CFS: compare weighted virtual clocks
level: advanced
minutes: 3
sourceLesson: sched-linux
summary: Classic CFS selects the task with the smallest virtual runtime.
---

## CFS: an ideal CPU, simulated

CFS’s design starts from an imaginary ideal multi-tasking CPU. For equal-weight runnable tasks sharing one CPU, each receives an equal fraction of its service:

```formula
s = 1 / n
s = 1 / 4 = 0.25
where
s: each task’s ideal CPU share, a dimensionless fraction
n: the number of equal-weight runnable tasks, four in the example
In words: four equally weighted competitors would each receive a quarter of one CPU.
```

Different weights produce unequal shares, covered in the next unit. Real hardware can run only one task per CPU at a time, so CFS tracks how far each task has fallen behind that ideal.

The tool is **virtual runtime** (`vruntime`), in nanoseconds. Every task has a **scheduling weight** (set by its nice value, below); a normal nice 0 task has weight 1024. When a task runs, its vruntime is advanced by the real time it ran, scaled by how its weight compares with 1024:

```formula
v_new = v_old + (1024t_run) / w
v_new = 50 ms + 4 ms × 1024 / 1024
v_new = 54 ms
where
v_new: the task's vruntime after it has run, in nanoseconds (ns) inside the kernel; milliseconds (ms) in these examples
v_old: the task's vruntime before it ran, same units
t_run: the real CPU time the task just ran for, same units
w: the task's weight; 1024 for nice 0, larger for more important tasks and smaller for less important ones
ns: nanoseconds, billionths of a second
ms: milliseconds, thousandths of a second
In words: a nice 0 task's virtual clock runs at real speed; a heavier task's runs slower and a lighter task's faster, so lighter tasks look as if they have had more CPU than they really have.
```

In the example, a nice 0 task with vruntime 50 ms runs for 4 ms and ends up at 54 ms. The formula is the whole of CFS's fairness: it holds for tasks in the fair class competing on one run queue.

The rule for picking is then trivial: **run the task with the smallest vruntime**, the one that has had least.

To find it fast, CFS keeps runnable tasks in a **red-black tree** ordered by vruntime, caching the leftmost node. Here n is the number of tasks represented in the tree. Picking is O(1); inserting a task after it runs or wakes is O(log n), time that grows with the logarithm of *n*: roughly one more step each time the number of runnable tasks doubles.

```
          [B 40]
         /      \
     [A 25]    [D 70]
     /
 [C 10] <- leftmost: runs next
```

As C runs, its vruntime rises. The current task is normally kept outside the queued-task tree, then reinserted at its new ordering position when descheduled. Classic CFS compares its service with queued competitors and applies slice/granularity and wake-up checks to decide when to reschedule; the picture shows key ordering rather than a node continuously moving through the tree.

## Key takeaways
- Classic CFS selects the task with the smallest virtual runtime.
- Virtual runtime grows faster for lighter tasks and slower for heavier tasks.
- A cached leftmost tree node makes selection constant-time; maintaining the ordered tree costs logarithmic time.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
