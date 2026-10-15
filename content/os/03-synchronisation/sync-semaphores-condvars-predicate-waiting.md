---
id: sync-semaphores-condvars-predicate-waiting
title: Wait on a protected predicate
level: intermediate
minutes: 4
summary: Combine a condition variable, shared state, mutex and while loop to avoid missed work.
sourceLesson: sync-semaphores-condvars
---

A condition variable supports richer questions than a permit count, such as whether a queue contains work. Correctness comes from a predicate and mutex protocol, rather than from the notification alone.

## Condition variables

A **condition variable** (CV) is a queue of threads waiting for some condition on shared state to become true. It has no counter and no memory. Use it with the mutex that protects the shared predicate; the APIs shown here require that mutex during wait.

The operations (POSIX names):

- `pthread_cond_wait(&cv, &m)`: the caller must hold `m`. It **atomically** releases `m` and puts the thread to sleep. When woken, it **re-acquires `m`** before returning.
- `pthread_cond_signal(&cv)`: wake at least one waiting thread, if any.
- `pthread_cond_broadcast(&cv)`: wake all waiting threads.

If nobody is waiting, `signal` does nothing. It is not remembered.

The canonical pattern, waiting for a child thread to finish:

```c
int done = 0;
pthread_mutex_t m =
    PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t c =
    PTHREAD_COND_INITIALIZER;

void thr_exit(void) {
    pthread_mutex_lock(&m);
    // Persist completion for a late waiter.
    done = 1;
    pthread_cond_signal(&c);
    pthread_mutex_unlock(&m);
}

void thr_join(void) {
    pthread_mutex_lock(&m);
    // Recheck after reacquiring the mutex.
    while (done == 0)
        pthread_cond_wait(&c, &m);
    pthread_mutex_unlock(&m);
}
```

Three parts are essential, and each one fixes a real bug.

### 1. The state variable

Without `done`, if the child signals before the parent waits, the signal is lost and the parent sleeps forever. The CV is just a waiting room; the *truth* lives in shared state (`done`, a queue length, a counter).

### 2. The mutex

Suppose the parent checks `done == 0` without the lock. Between that check and the call to `wait`, the child can set `done = 1` and signal. The parent then sleeps, having missed the only wakeup. This is a **lost wakeup**. Holding the mutex across the check, and having `wait` release it atomically as it sleeps, closes that window. (It is the same reason `FUTEX_WAIT` checks the value inside the kernel.)

### 3. The while loop

Always re-check the condition after waking:

```c
while (!condition)        // not "if"
    pthread_cond_wait(&cv, &m);
```

There are two reasons.

**Mesa semantics.** When thread A signals, the woken thread B does not run immediately. It merely becomes runnable and must re-acquire the mutex. In the meantime another thread C can grab the mutex and change the state. By the time B runs, the condition may be false again. A signal is only a **hint** that the state has changed.

**Spurious wakeups.** POSIX explicitly allows `pthread_cond_wait` to return even though nobody signalled. Allowing this makes CVs easier to implement efficiently, particularly on multiprocessors and when signals interrupt the wait.

> [!example] The `if` bug, traced
> One item slot, two consumers C1 and C2, one producer P. C1 waits (queue empty). P adds an item and signals; C1 becomes runnable but has not run yet. C2 arrives, takes the mutex, sees an item and consumes it. Now C1 runs, returns from `wait`, and (with `if`) assumes there is an item. It pops from an empty queue. With `while`, C1 re-checks, sees it is empty and waits again.

The alternative, **Hoare semantics**, hands the mutex directly to the woken thread so the condition is guaranteed to hold. This gives a stronger handoff contract. POSIX, Java and Python instead require callers to tolerate delayed reacquisition and recheck their predicates; the performance trade-off depends on implementation.

## Key takeaways

- The predicate is the remembered truth; a condition-variable notification is not remembered.
- Wait atomically releases the mutex and begins waiting, then reacquires before returning.
- A while loop handles both delayed reacquisition and spurious wakeups.

## Further reading

- [OSTEP: Condition variables](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [POSIX condition wait](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_wait.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Java Object monitor methods](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)
