---
id: sync-classic-problems-reader-writer-policy
title: Readers–writers and starvation
level: intermediate
minutes: 4
summary: Trace first-reader and last-reader coordination and choose a fairness policy.
sourceLesson: sync-classic-problems
---

Concurrent readers are safe only when they do not change the protected structure. A writer must exclude both other writers and all current readers.

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
    // First reader excludes all writers.
    if (++readers == 1)
        sem_wait(&rw);  // first reader
    sem_post(&mutex);
}

void read_unlock(void) {
    sem_wait(&mutex);
    // Only the last departing reader
    // releases.
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

Real read-write locks expose this choice. glibc's `pthread_rwlock_t` prefers readers by default (its nonrecursive writer-preference mode requires promising that read locks will not be acquired recursively; the similarly named recursive writer-preference setting is ignored by glibc); Java's `ReentrantReadWriteLock` offers a fair mode. The later read-write-lock unit discusses when reader parallelism actually helps.

## Concurrency and immutable alternatives

A high read rate is not a guarantee of starvation, but the amount of overlapping read work helps explain why reader preference deserves scrutiny. For a stable stream, Little’s law relates mean arrival rate and mean residence time to mean work in flight:

```formula
L = λW
L = (5000 / s)(0.002 s) = 10
where
L: mean reads holding the read lock, a count with no physical unit
λ: mean arrival rate of reads, here five thousand per second
W: mean lock-holding duration per read, here two milliseconds
s: second, the unit of time
In words: this example averages ten concurrent readers; it does not determine how often the reader group becomes empty.
```

A writer-preference or explicitly fair admission policy can limit new readers bypassing a waiting writer, under its scheduling and progress assumptions. Another option is immutable replacement: construct a new configuration privately, publish its pointer with a valid ordering protocol, and let readers retain the old unchanged object. Publication can then avoid waiting for every existing reader, but old storage must remain alive until a reclamation protocol proves no reader can use it. Atomic pointer replacement alone does not supply those ordering and lifetime guarantees.

## Key takeaways

- The first reader acquires exclusion on behalf of a group; the last releases it.
- Reader preference can starve a writer, and writer preference can reverse that problem.
- A fair admission protocol must supply its own fairness assumptions; a semaphore alone does not promise FIFO order.

## Further reading

- [The Little Book of Semaphores — Allen B. Downey](https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [Python queue](https://docs.python.org/3/library/queue.html)
- [glibc read-write lock preference](https://man7.org/linux/man-pages/man3/pthread_rwlockattr_setkind_np.3.html)
- [Little: A proof for the queuing formula (1961)](https://fisherp.scripts.mit.edu/wordpress/wp-content/uploads/2015/11/ContentServer.pdf)
