---
id: sync-classic-problems-semaphore-buffer
title: A bounded buffer with semaphores
level: intermediate
minutes: 4
summary: Coordinate free slots, filled slots and protected circular-buffer updates.
sourceLesson: sync-classic-problems
---

A handful of synchronisation puzzles have been studied since the 1960s and 70s. They survive because each one isolates a pattern you meet constantly in real systems: a queue between stages, a cache that is read far more than written, threads that need several resources at once, a server with a waiting room.

Work through them once with semaphores and condition variables and you will recognise them everywhere.

## 1. Producer–consumer (bounded buffer)

Producers create items and put them in a buffer with a fixed number of slots; consumers take them out. A producer must wait when the buffer is full, a consumer when it is empty, and the buffer itself must never be corrupted by concurrent access.

This is every queue between pipeline stages: a web server's accept queue, a logging thread, Kafka consumers, the pipe in `cat log | grep error`.

### With semaphores

Three semaphores, named after what they count, with these starting values:

```formula
empty = N
full = 0
mutex = 1
where
empty: the semaphore counting free slots; producers wait on it before writing
full: the semaphore counting filled slots, meaning items ready to take; consumers wait on it before reading
mutex: a semaphore used as a lock (a binary semaphore) that protects the buffer and its two indices
N: the buffer's capacity, the number of slots it holds, for example 5
In words: at the start every slot is free, no slot holds an item, and the lock is available.
```

```c
void producer(int x) {
    sem_wait(&empty);  // a free slot
    sem_wait(&mutex);
    buf[in] = x;
    // Wrap the write slot around the ring.
    in = (in + 1) % N;
    sem_post(&mutex);
    sem_post(&full);   // one more item
}

int consumer(void) {
    sem_wait(&full);   // an item
    sem_wait(&mutex);
    int x = buf[out];
    // Reserve the next slot for a later
    // read.
    out = (out + 1) % N;
    sem_post(&mutex);
    sem_post(&empty);  // one more slot
    return x;
}
```

The buffer is used as a circular buffer. The indices `in` (next slot to write) and `out` (next slot to read) move forward one slot at a time and wrap from the last slot back to the first, which is what `% N` does in C:

```formula
i_next = (i + 1) mod N
i_next = (4 + 1) mod 5 = 0
where
i: a slot index the code has just used, starting at zero and ending one below the capacity (the code variable in or out)
i_next: the slot index it moves on to
mod: modulo: the remainder after dividing by N, written % in C
N: the number of slots in the buffer; 5 in the example line
In words: step to the next slot, and after the last slot return to slot 0, like a clock face.
```

The two counting semaphores always add up to the capacity when nobody is part-way through an operation:

```formula
empty + full = N
where
empty: the current value of the free-slot semaphore
full: the current value of the filled-slot semaphore
N: the buffer's capacity in slots
In words: every slot is either free or full, so the two counts together equal the number of slots.
```

For example, with five slots and two stored items, at a quiescent point `full` is 2 and `empty` is 3.

That invariant holds only when no operation holds an outstanding permit. During in-flight operations, reserved permits are not yet reflected in the opposite semaphore; that interval can be arbitrarily long if a thread is delayed. These C sketches assume successful initialization/calls; production code must handle EINTR and other semaphore errors.

> [!warning] Order of the waits matters
> Exchange the first two lines of the producer so it takes `mutex` before `empty`. When the buffer is full, the producer holds the mutex and sleeps on `empty`. The consumer that would free a slot blocks on `mutex`. Neither can proceed: a **deadlock**. Always wait for the resource, then take the lock. (The next module covers deadlock in depth.)

## Key takeaways

- The slot semaphores and the buffer mutex protect different invariants.
- Acquire a resource permit before the mutex, so a sleeping producer does not block the consumer that could free space.
- The free-plus-full invariant describes quiescent points without outstanding reservations.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
