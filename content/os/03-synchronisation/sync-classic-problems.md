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

Producers create items and put them in a buffer of fixed size N; consumers take them out. A producer must wait when the buffer is full, a consumer when it is empty, and the buffer itself must not be corrupted by concurrent access.

This is every queue between pipeline stages: a web server's accept queue, a logging thread, Kafka consumers, the pipe in `cat log | grep error`.

### With semaphores

Three semaphores:

- `empty = N`: free slots (producers wait on it)
- `full = 0`: filled slots (consumers wait on it)
- `mutex = 1`: protects the buffer indices

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

When no operation holds an outstanding permit, empty + full = N. During in-flight operations, reserved permits are not yet reflected in the opposite semaphore; that interval can be arbitrarily long if a thread is delayed. These C sketches assume successful initialization/calls; production code must handle EINTR and other semaphore errors.

> [!warning] Order of the waits matters
> Swap the first two lines of the producer so it takes `mutex` before `empty`. When the buffer is full, the producer holds the mutex and sleeps on `empty`. The consumer that would free a slot blocks on `mutex`. Neither can proceed: a **deadlock**. Always wait for the resource, then take the lock. (The next module covers deadlock in depth.)

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
- **Fair (turnstile)**: add a turnstile with an explicit fair admission policy for readers and writers. Plain POSIX/Python semaphore APIs do not by themselves promise FIFO wake order. A waiting writer holds the turnstile, so readers arriving after it queue behind it.

Real read-write locks expose this choice. glibc's `pthread_rwlock_t` prefers readers by default (its nonrecursive writer-preference mode requires promising that read locks will not be acquired recursively; the similarly named recursive writer-preference setting is ignored by glibc); Java's `ReentrantReadWriteLock` offers a fair mode. Lesson 6 discusses when a read-write lock actually helps.

## 3. Dining philosophers

Five philosophers sit at a round table with one fork between each pair (five forks). To eat, a philosopher needs **both** the left and right forks. They alternate between thinking and eating. The problem is due to Dijkstra (1965), with the dining story popularised by Tony Hoare.

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

If all five pick up their left fork at the same moment, each waits forever for a right fork held by a neighbour. That circular wait is deadlock; here we only look at the standard ways out.

1. **Break the symmetry (resource ordering).** Number the forks and always pick up the lower-numbered one first. Philosopher 4 needs forks 4 and 0, so picks up 0 first. Now a full cycle of waiting is impossible. This is the most common real-world fix: a global lock order.
2. **Limit the diners.** A semaphore initialised to 4 lets at most four philosophers try to eat at once. By the pigeonhole principle, at least one of them can get both forks.
3. **A waiter (arbitrator).** A single mutex or monitor hands out both forks at once, or neither. Simple, but it serialises fork allocation through one point.
4. **Chandy–Misra.** Forks are "dirty" or "clean" and are passed between neighbours on request, giving a distributed, starvation-free solution.

Avoiding deadlock is not the same as avoiding **starvation**. With some solutions, two fast neighbours can alternate eating so that the philosopher between them almost never gets both forks. A monitor-based solution where a hungry philosopher eats only when neither neighbour is eating is deadlock-free but can still starve someone unless you add ordering or ageing.

The real-world version: a bank transfer that locks account A then account B, running concurrently with a transfer from B to A. Lock ordering by account ID fixes it.

## 4. The sleeping barber

A barbershop has one barber, one barber's chair and N waiting chairs.

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
- Bounded buffer: `empty = N`, `full = 0`, `mutex = 1`. Wait on the counting semaphore before the mutex, or you can deadlock. In Python use `queue.Queue(maxsize)`.
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
