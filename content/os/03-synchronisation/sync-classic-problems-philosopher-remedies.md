---
id: sync-classic-problems-philosopher-remedies
title: Break the resource cycle
level: intermediate
minutes: 3
summary: Compare resource ordering, an admission limit and an arbitrator without assuming starvation freedom.
sourceLesson: sync-classic-problems
---

Five philosophers share five chopsticks in a ring, and each needs its own chopstick and the next one clockwise. Several remedies prevent the cycle; their fairness properties need separate reasoning.

1. **Break the symmetry (resource ordering).** Number the chopsticks and always pick up the lower-numbered one first. Philosopher 4 needs chopsticks 4 and 0, so picks up 0 first. Now a full cycle of waiting is impossible. This is the most common real-world fix: a global lock order.
2. **Limit the diners.** A semaphore initialised to 4 lets at most four philosophers try to eat at once. By the pigeonhole principle, at least one of them can get both chopsticks (worked through below).
3. **A waiter (arbitrator).** A single mutex or monitor hands out both chopsticks at once, or neither. Simple, but it serialises chopstick allocation through one point.
4. **Chandy–Misra.** A distributed protocol marks chopsticks "dirty" or "clean" and transfers them under specified request and ownership rules. Its starvation-freedom argument also needs the protocol’s acyclic initial precedence and progress/message-delivery assumptions.

Why limiting the diners works: suppose the worst case, where every philosopher at the table holds exactly one chopstick and waits for another. Then:

```formula
F − d ≥ 1   when d ≤ 4
5 − 4 = 1
where
F: the number of chopsticks on the table: 5
d: the number of philosophers allowed to try to eat at once; the semaphore keeps it at 4 or fewer
≥: greater than or equal to
≤: less than or equal to
In words: if at most four diners each hold one chopstick, at least one of the five chopsticks is still free.
```

To see who eats, follow the chain of waiting. A diner holding one chopstick waits for the chopstick on their other side. If a neighbour holds that chopstick, the neighbour is waiting for the chopstick on *their* other side, and so on round the table in one direction. With at most four diners the chain cannot reach all the way round, so it ends at a chopstick nobody holds, and the diner at the end of the chain picks it up and eats. With all five at the table, the same sum gives 5 − 5 = 0 free chopsticks, and the circular wait is possible again.

Avoiding deadlock is not the same as avoiding **starvation**. With some solutions, two fast neighbours can alternate eating so that the philosopher between them almost never gets both chopsticks. A monitor-based solution where a hungry philosopher eats only when neither neighbour is eating is deadlock-free but can still starve someone unless you add ordering or ageing.

The real-world version: a bank transfer that locks account A then account B, running concurrently with a transfer from B to A. Lock ordering by account ID fixes it.

## Key takeaways

- A global resource order removes circular wait.
- Admitting at most four diners breaks this five-resource cycle under the stated acquisition pattern.
- Deadlock freedom alone does not promise that each hungry participant will eventually be served.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
