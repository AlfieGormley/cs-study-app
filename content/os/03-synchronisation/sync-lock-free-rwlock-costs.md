---
id: sync-lock-free-rwlock-costs
title: When read-write locks help
level: advanced
minutes: 2
summary: Compare concurrent read work with shared reader-metadata overhead.
sourceLesson: sync-lock-free
---

Read-mostly is a useful workload description, rather than a sufficient proof that a read-write lock will be faster. The length of each protected read and the lock implementation also matter.

## Read-write locks

Many shared structures are read far more often than written: routing tables, configuration, caches, DNS zones. A **read-write lock** lets any number of readers in at once and gives writers exclusive access.

```c
pthread_rwlock_t rw =
    PTHREAD_RWLOCK_INITIALIZER;

int lookup(int key) {
    pthread_rwlock_rdlock(&rw);
    // Read only while sharing the read
    // lock.
    int v = table_get(key);
    pthread_rwlock_unlock(&rw);
    return v;
}

void update(int key, int v) {
    pthread_rwlock_wrlock(&rw);
    // Exclude both other writers and
    // readers.
    table_put(key, v);
    pthread_rwlock_unlock(&rw);
}
```

It seems like an obvious win, but it often disappoints:

- **Readers still write.** Many implementations update shared reader metadata on entry and exit. With 32 cores doing short lookups, that one cache line bounces between cores just as a mutex's would. For read sections that are short enough, this overhead can outweigh reader parallelism; there is no universal duration threshold.
- **Starvation.** As in the readers–writers problem, a reader-preferring lock (glibc's default) can starve writers; a writer-preferring one can starve readers.
- **Upgrade deadlock.** Two readers that each try to upgrade to a write lock wait for each other to stop reading. Most libraries do not support upgrading for this reason.

Longer read sections and rare writes can make reader parallelism worthwhile, but the crossover must be measured on the actual implementation and hardware. For short, very hot reads you want readers that write nothing shared at all.

## Key takeaways

- Read-write locks allow parallel readers but can still contend on shared metadata.
- Preference policies and attempted upgrades can introduce starvation or deadlock.
- Choose a documented library protocol and measure the actual workload before replacing a mutex.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
