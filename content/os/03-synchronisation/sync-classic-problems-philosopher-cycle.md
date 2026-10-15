---
id: sync-classic-problems-philosopher-cycle
title: How dining philosophers deadlock
level: intermediate
minutes: 2
summary: Trace circular waiting when each participant holds one resource and needs another.
sourceLesson: sync-classic-problems
---

The dining-philosophers puzzle isolates multi-resource acquisition. The same circular wait can occur when two bank transfers lock their source and destination accounts in opposite orders.

## 3. Dining philosophers

Five philosophers sit at a round table with one chopstick between each pair (five chopsticks). To eat, a philosopher needs **both** the left and right chopsticks. They alternate between thinking and eating. The problem is due to Dijkstra (1965), with the dining story popularised by Tony Hoare.

```
        P0
    f0      f1
  P4          P1
   f4        f2
    P3  f3  P2
```

The naive solution:

```c
void philosopher(int i) {
    while (1) {
        think();
        // Deliberately symmetric: can
        // deadlock.
        sem_wait(&fork[i]);         // left
        sem_wait(&fork[(i+1) % 5]); // right
        eat();
        sem_post(&fork[(i + 1) % 5]);
        sem_post(&fork[i]);
    }
}
```

Each philosopher's left chopstick has the philosopher's own number, and the right chopstick is the next one round the table. The `% 5` in the code is what makes the numbering wrap round:

```formula
f_left = i
f_right = (i + 1) mod 5
f_right = (4 + 1) mod 5 = 0
where
i: the philosopher's number, from 0 to 4
f_left: the number of that philosopher's left chopstick
f_right: the number of that philosopher's right chopstick
mod: modulo: the remainder after dividing, written % in C; it makes the numbering wrap from 4 back to 0
In words: philosopher 4's right chopstick is chopstick 0, so philosopher 4 needs chopsticks 4 and 0.
```

In the code, each chopstick is one semaphore in an array, indexed by the chopstick's number.

If all five pick up their left chopstick at the same moment, each waits forever for a right chopstick held by a neighbour. That circular wait is deadlock; here we only look at the standard ways out.

## Key takeaways

- Each philosopher needs two neighbouring chopsticks and holds the first while waiting for the second.
- Symmetric left-then-right acquisition can make a complete cycle.
- Resource numbers and the drawing must describe the same neighbouring pairs.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
