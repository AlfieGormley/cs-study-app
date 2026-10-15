---
id: sync-semaphores-condvars-remembered-signals
title: Semaphores remember completion
level: intermediate
minutes: 2
summary: Coordinate a child and parent without losing a signal sent before the wait.
sourceLesson: sync-semaphores-condvars
---

A completion signal must survive a scheduling gap: the worker may finish before the parent reaches its wait. A semaphore records that completion in its permit count.

### As an ordering tool

Initialised to 0, a `wait` blocks until some other thread `signal`s. This makes "B must happen after A" trivial:

```c
sem_t done;  // sem_init(&done, 0, 0)
             // before creating the child

void *child(void *arg) {
    // Finish the work before posting.
    do_work();
    sem_post(&done);   // 0 -> 1
    return NULL;
}

// parent
pthread_create(&t, NULL, child, NULL);
sem_wait(&done);       // blocks until post
```

Assuming initialization and calls succeed, it works whichever thread runs first. POSIX sem_wait can fail with EINTR; real code must retry that case and handle other errors rather than enter a protected section without a permit. The snippets omit this error handling. If the child posts before the parent waits, the counter is 1 and the parent thread's wait returns immediately. The semaphore *remembers* the signal. That memory is the key difference from a condition variable.

### Semaphore versus mutex

A binary semaphore looks like a mutex, but:

- A semaphore has **no owner**. Any thread can `post`, which is what makes the ordering pattern work, but also means nobody catches a stray release.
- A POSIX mutex has an owner, enabling ownership-based error checks and optional recursive or **priority inheritance** protocols. A counting semaphore supplies no single designated owner to boost; do not infer mutex-style priority inheritance from it. Python’s primitive Lock is a documented ownership exception, as discussed earlier.

Use a mutex for mutual exclusion and a semaphore for counting or signalling.

## Key takeaways

- An initial count of zero makes a semaphore suitable for a completion event.
- A post before a wait leaves a permit, so the ordering works in either execution order.
- A semaphore has no owner; POSIX wait errors must be handled before assuming a permit was acquired.

## Further reading

- [OSTEP: Condition variables](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [POSIX condition wait](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_wait.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Java Object monitor methods](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)
