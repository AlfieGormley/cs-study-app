---
id: sync-classic-problems-queue-back-pressure
title: Bounded queues apply back-pressure
level: intermediate
minutes: 2
summary: Use condition-variable predicates and a library queue to stop producers outrunning consumers.
sourceLesson: sync-classic-problems
---

A bounded buffer can also be expressed with a mutex, a count and condition variables. The queue’s capacity limits accumulated work, while the consumer’s service rate still limits sustained throughput.

### With condition variables

```c
void put(int x) {
    lock(&m);
    while (count == N)
        pthread_cond_wait(&not_full, &m);
    // Only run after the not-full
    // predicate.
    buf[in] = x; in = (in + 1) % N;
    count++;
    pthread_cond_signal(&not_empty);
    unlock(&m);
}
```

`get` is the mirror image: wait while `count == 0`, take an item, signal `not_full`. Two CVs ensure producers only wake consumers and vice versa.

In Python you would almost never write this yourself. `queue.Queue(maxsize=N)` is exactly a bounded buffer built from one lock and condition variables, and `put` and `get` block appropriately:

```python
import queue, threading

q = queue.Queue(maxsize=100)

def producer():
    for line in open("access.log"):
        q.put(line)       # blocks if full
    # One sentinel ends this one consumer.
    q.put(None)           # sentinel

def consumer():
    while (line := q.get()) is not None:
        # Process each line before the
        # sentinel.
        handle(line)
```

The bound matters. An **unbounded queue** between a fast producer and a slow consumer grows until memory runs out. A bounded one applies **back-pressure**: the producer is forced to slow to the consumer's pace.

## Key takeaways

- Use separate not-full and not-empty predicates, both protected by the buffer mutex.
- queue.Queue provides a bounded blocking queue without reimplementing the protocol.
- A bounded queue eventually blocks a faster producer; an unbounded queue can grow without limit.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
