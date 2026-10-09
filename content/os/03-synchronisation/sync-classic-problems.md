---
id: sync-classic-problems
title: Classic synchronisation problems
level: intermediate
minutes: 15
summary: The bounded buffer, readers–writers, dining philosophers and sleeping barber problems, solved with semaphores and condition variables, and the real systems each one models.
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
    in = (in + 1) % N;
    sem_post(&mutex);
    sem_post(&full);   // one more item
}

int consumer(void) {
    sem_wait(&full);   // an item
    sem_wait(&mutex);
    int x = buf[out];
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
i: a slot index the code has just used, from 0 to N − 1 (the variable in or out)
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

For example, with N = 5 and two items in the buffer, `full` is 2 and `empty` is 3.

That invariant holds only when no operation holds an outstanding permit. During in-flight operations, reserved permits are not yet reflected in the opposite semaphore; that interval can be arbitrarily long if a thread is delayed. These C sketches assume successful initialization/calls; production code must handle EINTR and other semaphore errors.

> [!warning] Order of the waits matters
> Exchange the first two lines of the producer so it takes `mutex` before `empty`. When the buffer is full, the producer holds the mutex and sleeps on `empty`. The consumer that would free a slot blocks on `mutex`. Neither can proceed: a **deadlock**. Always wait for the resource, then take the lock. (The next module covers deadlock in depth.)

### With condition variables

```c
void put(int x) {
    lock(&m);
    while (count == N)
        pthread_cond_wait(&not_full, &m);
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
    q.put(None)           # sentinel

def consumer():
    while (line := q.get()) is not None:
        handle(line)
```

The bound matters. An **unbounded** queue between a fast producer and a slow consumer grows until memory runs out. A bounded one applies **back-pressure**: the producer is forced to slow to the consumer's pace.

## 2. Readers–writers

Many threads read a shared structure; a few write it. Readers do not interfere with each other, so any number may read at once. A writer needs exclusive access: no other writers and no readers.

Real examples: a routing table, a configuration object, an in-memory cache, a database page.

### Readers-preference solution

```c
int readers = 0;
sem_t mutex;    // 1: protects readers
sem_t rw;       // 1: held by writer or
                //    by the reader group

void read_lock(void) {
    sem_wait(&mutex);
    if (++readers == 1)
        sem_wait(&rw);  // first reader
    sem_post(&mutex);
}

void read_unlock(void) {
    sem_wait(&mutex);
    if (--readers == 0)
        sem_post(&rw);  // last reader
    sem_post(&mutex);
}

void write_lock(void)   { sem_wait(&rw); }
void write_unlock(void) { sem_post(&rw); }
```

The first reader in locks writers out on behalf of the whole group; the last reader out lets them back in.

The flaw is **writer starvation**. If readers keep arriving so that `readers` never drops to 0, a waiting writer never gets `rw`. For a cache read thousands of times per second, the update might be delayed indefinitely.

### Fixing starvation

- **Writers-preference**: once a writer is waiting, new readers block. This flips the problem: a steady stream of writers starves readers.
- **Fair (turnstile)**: add a turnstile with an explicit fair policy for letting readers and writers in. Plain POSIX/Python semaphore APIs do not by themselves promise FIFO wake order. A waiting writer holds the turnstile, so readers arriving after it queue behind it.

Real read-write locks expose this choice. glibc's `pthread_rwlock_t` prefers readers by default (its nonrecursive writer-preference mode requires promising that read locks will not be acquired recursively; the similarly named recursive writer-preference setting is ignored by glibc); Java's `ReentrantReadWriteLock` offers a fair mode. Lesson 6 discusses when a read-write lock actually helps.

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

1. **Break the symmetry (resource ordering).** Number the chopsticks and always pick up the lower-numbered one first. Philosopher 4 needs chopsticks 4 and 0, so picks up 0 first. Now a full cycle of waiting is impossible. This is the most common real-world fix: a global lock order.
2. **Limit the diners.** A semaphore initialised to 4 lets at most four philosophers try to eat at once. By the pigeonhole principle, at least one of them can get both chopsticks (worked through below).
3. **A waiter (arbitrator).** A single mutex or monitor hands out both chopsticks at once, or neither. Simple, but it serialises chopstick allocation through one point.
4. **Chandy–Misra.** Chopsticks are "dirty" or "clean" and are passed between neighbours on request, giving a distributed, starvation-free solution.

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

## 4. The sleeping barber

A barbershop has one barber, one barber's chair and a fixed number of waiting chairs (3 in the code below).

- If there are no customers, the barber sleeps.
- A customer arriving at a sleeping barber wakes him.
- A customer arriving while the barber is busy sits in a free waiting chair, or leaves if none are free.

It models any server with a bounded waiting queue that sheds load when full: a thread pool with a fixed-size queue that rejects work, or a call centre with a maximum hold queue. The difficulty is avoiding races between the barber checking for customers and customers checking whether the barber is asleep.

```python
from threading import Semaphore, Lock

N = 3
free_seats = N
seats = Lock()     # guards free_seats
customer_ready = Semaphore(0)
barber_ready = Semaphore(0)
customer_seated = Semaphore(0)
haircut_done = Semaphore(0)
customer_left = Semaphore(0)

def barber():
    global free_seats
    while True:
        customer_ready.acquire()  # sleep
        with seats:
            free_seats += 1  # one leaves
        barber_ready.release()  # call
        customer_seated.acquire()
        cut_hair()
        haircut_done.release()
        customer_left.acquire()

def customer():
    global free_seats
    with seats:
        if free_seats == 0:
            return           # shop full
        free_seats -= 1
        customer_ready.release()
    barber_ready.acquire()   # wait turn
    customer_seated.release()
    haircut_done.acquire()   # wait finish
    customer_left.release()
```

How it works:

- `customer_ready` counts customers waiting. The barber sleeps on it when it is 0, which is the "sleeping" part.
- `barber_ready` calls one customer. The seated, done and left handshakes coordinate chair arrival, haircut completion and departure before the next customer is called. These snippets assume no cancellation or failure during the handshake.
- `free_seats` is protected by `seats`, so two customers cannot both take the last chair.

Because semaphores remember posts, it does not matter whether a customer arrives just before or just after the barber goes to sleep. That is the race that breaks naive solutions using flags.

This version does not guarantee customers are served in arrival order, since whichever waiting customer's `acquire` returns first gets the chair. Adding a FIFO queue of per-customer semaphores fixes that.

## Comparing them

| Problem | Pattern | Real system |
|---|---|---|
| Bounded buffer | queue + back-pressure | pipes, Kafka |
| Readers–writers | shared vs exclusive | rwlocks, caches |
| Philosophers | many resources | lock ordering |
| Sleeping barber | bounded wait, shed | thread pools |

## Key takeaways
- Bounded buffer: start `empty` at the buffer's capacity, `full` at 0 and `mutex` at 1. Wait on the counting semaphore before the mutex, or you can deadlock. In Python use `queue.Queue(maxsize)`.
- Readers–writers: the simple solution lets readers starve writers; writer-preference or a fair turnstile trades that off.
- Dining philosophers: the symmetric solution can deadlock. Resource ordering, limiting diners or an arbitrator prevent it, but avoiding deadlock is not the same as avoiding starvation.
- Sleeping barber: semaphores that remember posts remove the race between "barber goes to sleep" and "customer arrives".
- Each puzzle maps to a real pattern: pipeline queues, shared/exclusive locks, multi-resource locking and load shedding.

## Further reading
- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/wp/semaphores/)
- [OSTEP: Semaphores (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Producer–consumer problem — Wikipedia](https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem)
- [Readers–writers problem — Wikipedia](https://en.wikipedia.org/wiki/Readers%E2%80%93writers_problem)
- [Dining philosophers problem — Wikipedia](https://en.wikipedia.org/wiki/Dining_philosophers_problem)
- [Sleeping barber problem — Wikipedia](https://en.wikipedia.org/wiki/Sleeping_barber_problem)
- [queue — Python documentation](https://docs.python.org/3/library/queue.html)
