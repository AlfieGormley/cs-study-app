---
id: sync-locks-mutex-and-interrupts
title: Mutexes and local interrupt masking
level: intermediate
minutes: 3
summary: Use a mutex for a shared update and understand the limits of masking local interrupts.
sourceLesson: sync-locks
---

A **lock** (or **mutex**, for mutual exclusion) turns a critical section into something only one thread can run at a time. You call `lock()` before touching shared data and `unlock()` afterwards. If another thread holds the lock, you wait.

```c
pthread_mutex_t m =
    PTHREAD_MUTEX_INITIALIZER;

void *work(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        // Protect the full shared update.
        pthread_mutex_lock(&m);
        // The shared update stays under the
        // lock.
        counter++;
        pthread_mutex_unlock(&m);
    }
    return NULL;
}
```

```python
import threading
lock = threading.Lock()

def work():
    global counter
    for _ in range(1_000_000):
        # Release even if the body raises.
        with lock:  # acquire, release
            # The same lock protects every
            # update.
            counter += 1
```

Python's `with` releases the lock even if the body raises, which is the main reason to prefer it over calling `acquire()` and `release()` by hand.

The interesting question is how `lock()` itself avoids the race it is meant to prevent.

## Option 1: turn off interrupts

On a single CPU, disabling maskable interrupts can protect a short kernel section against relevant interrupt handlers, provided it cannot block, yield or otherwise schedule and the kernel's preemption rules are respected. It does not exclude every context, such as non-maskable interrupts.

This is genuinely used inside kernels for very short sections, but it fails as a general lock:

- It is a privileged operation; user programs cannot do it (and you would not trust them to).
- It does nothing on a **multiprocessor**: other cores keep running.
- Interrupt handling is delayed. Many interrupt sources remain pending, but excessive latency or finite device buffering can still lose events or data.

> [!note] Ownership
> A mutex has an owner: only the thread that locked it should unlock it. Unlocking a mutex you do not hold is undefined for a default pthread mutex (error-checking mutexes report it). Python's `threading.Lock` has no owner and can be released by any thread; `threading.RLock` has an owner and can be re-acquired by the same thread (re-entrant).

## Key takeaways

- Hold a lock across the entire shared invariant, and release it on every exit path.
- Disabling local maskable interrupts does not stop other CPUs or all execution contexts.
- Python Lock is non-recursive and has no owner; RLock tracks ownership and nesting.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
