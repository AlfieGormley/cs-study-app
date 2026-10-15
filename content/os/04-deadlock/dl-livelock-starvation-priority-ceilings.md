---
id: dl-livelock-starvation-priority-ceilings
title: Priority ceilings and ownerless waits
level: intermediate
minutes: 2
sourceLesson: dl-livelock-starvation
summary: Immediate ceiling boosting and the original ceiling protocol have different admission rules.
---

### Priority ceiling

Each mutex is given a **ceiling**: the priority of the highest-priority thread that ever uses it. With the **immediate priority ceiling** variant (`PTHREAD_PRIO_PROTECT` in POSIX), a holder immediately runs at the higher of its own priority and the highest ceiling of its held protected mutexes, so lower-priority unrelated tasks cannot preempt it in the usual single-CPU fixed-priority model. Equal-priority scheduling and multiprocessor behavior need separate analysis.

The original priority ceiling protocol (Sha, Rajkumar and Lehoczky, 1990) goes further: a thread may lock a mutex only if its priority is higher than the ceilings of all mutexes currently locked by other threads. Under the protocol's single-processor fixed-priority model, correctly assigned ceilings, bounded critical sections and resource-use assumptions, that rule **prevents deadlock** and limits a job's lower-priority blocking to at most one critical section. The cost is that every ceiling must be worked out in advance, which suits static real-time systems more than general-purpose servers.

### When inheritance can't help

Let H denote a high-priority waiting thread and L a low-priority producer. Inheritance needs to know *who* to boost, so conventional mutex PI needs an identifiable **owner**. Other systems can propagate priority through explicitly tracked server or resource dependencies; ownership need not literally be a POSIX mutex. A semaphore, condition variable, queue or pipe has no owner. If H waits on a semaphore that L will eventually post, the kernel has no idea that L is the one to boost.

Choose a dependency protocol that exposes ownership where blocking is unavoidable; hard real-time audio code should generally avoid blocking on lower-priority work altogether. Apple's platforms, for example, donate priority to the owner of a `pthread_mutex` or `os_unfair_lock` but can't do so for a `DispatchSemaphore`.

## Key takeaways
- Immediate ceiling boosting and the original ceiling protocol have different admission rules.
- Original ceiling bounds require its classical scheduling and resource-use assumptions.
- Ownerless semaphore waits do not identify a producer for conventional mutex priority inheritance.

## Further reading
- [POSIX: mutex priority protocols](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_mutexattr_getprotocol.html)
- [Sha, Rajkumar and Lehoczky: priority inheritance protocols](https://www.math.unipd.it/~tullio/RTS/2009/SRL-1990.pdf)
- [Linux: priority inheritance and boost chains](https://docs.kernel.org/locking/rt-mutex-design.html)
