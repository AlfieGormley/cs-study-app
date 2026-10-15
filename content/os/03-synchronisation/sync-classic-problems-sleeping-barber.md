---
id: sync-classic-problems-sleeping-barber
title: Coordinate a bounded waiting room
level: intermediate
minutes: 3
summary: Follow permit handshakes for a sleeping worker, waiting clients and rejected arrivals.
sourceLesson: sync-classic-problems
---

A bounded server can reject work instead of blocking the producer. The sleeping-barber model combines that admission decision with a worker that sleeps while no work is available.

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
        # Wait until the called client sits.
        customer_seated.acquire()
        cut_hair()
        haircut_done.release()
        # Finish departure before the next
        # call.
        customer_left.acquire()

def customer():
    global free_seats
    with seats:
        if free_seats == 0:
            return           # shop full
        # Reserve a waiting chair under the
        # lock.
        free_seats -= 1
        customer_ready.release()
    barber_ready.acquire()   # wait turn
    customer_seated.release()
    # Do not leave before this cut
    # completes.
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

- The seats lock protects the waiting-chair count; semaphores coordinate arrival and service phases.
- The protocol assumes no cancellation or failure partway through its handshakes.
- It sheds arrivals when the waiting room is full and does not promise arrival-order service.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
