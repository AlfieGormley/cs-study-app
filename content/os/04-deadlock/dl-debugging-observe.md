---
id: dl-debugging-observe
title: Observing a persistent wait
level: advanced
minutes: 2
sourceLesson: dl-debugging
summary: Collect multiple dumps and measure application progress instead of inferring deadlock from CPU alone.
---

Many concurrency deadlocks depend on timing; others, such as recursive acquisition of a non-reentrant lock, happen deterministically. The faulty lock order can sit in the code for months until the one interleaving that triggers it happens, possibly under production load. Debugging them comes in two halves:

- **After the fact**: a process has hung. Find which threads are stuck, on which locks, held by whom.
- **Before the fact**: tools that spot a lock-order cycle the first time both code paths run, even if they never actually collide.

The second half is far cheaper. This lesson covers both, then the design rules that make the tools rarely fire.

## Step 1: is it really a deadlock?

When a service stops responding, check CPU first (the deadlock fundamentals lessons's table):

| Observation | Suspect |
|---|---|
| ~0% CPU, stacks never change | Deadlock or lost wake-up |
| High CPU, stacks repeat or change | Livelock, busy loop, or spinning deadlock |
| Some requests finish, some don't | Starvation, or a partial deadlock |
| Blocked in I/O, not locks | Slow dependency or an I/O dependency cycle |

Then take **two or three thread dumps a few seconds apart**. Repeated stacks are evidence of a persistent wait, not proof of deadlock; a legitimate long wait can look the same. Changing stacks can indicate useful progress or livelock. Confirm dependencies and application progress.

## Key takeaways
- Collect multiple dumps and measure application progress instead of inferring deadlock from CPU alone.
- A stable wait can be legitimate; reconstruct dependencies to confirm a cycle.
- Order-checking tools can find potential cycles before conflicting paths overlap.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [Linux: runtime locking correctness validator](https://docs.kernel.org/locking/lockdep-design.html)
