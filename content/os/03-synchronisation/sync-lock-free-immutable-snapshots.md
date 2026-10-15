---
id: sync-lock-free-immutable-snapshots
title: Publish immutable snapshots in Python
level: advanced
minutes: 3
summary: Use a brief lock for publication and keep previously returned versions unchanged.
sourceLesson: sync-lock-free
---

The useful RCU idea here is an unchanged published version. A managed runtime helps preserve object lifetime, while a documented lock supplies the publication protocol in this Python example.

### The same idea in Python

Managed runtimes help keep referenced objects alive, but do not supply publication ordering or application immutability automatically. This example uses a brief shared lock to obtain or publish a snapshot, then allows use of that immutable snapshot outside the lock.

```python
import threading

_config = {"timeout": 10}  # never mutated
_write_lock = threading.Lock()

def get_config():
    with _write_lock:
        return _config  # immutable snapshot

def set_timeout(t):
    global _config
    with _write_lock:      # publish lock
        # Shallow copy: nested values must
        # also
        # remain immutable to readers.
        new = dict(_config)
        new["timeout"] = t
        _config = new      # publish
```

Readers briefly take the publication lock, then retain a reference to an unchanged dictionary. Reclamation timing is runtime-dependent. Callers must never mutate the returned dictionary or mutable objects reachable from it. Java’s `CopyOnWriteArrayList` similarly provides snapshot iteration using replacement arrays for mutative operations; frequent copying can make it unsuitable for write-heavy workloads.

The rule that makes this safe: **never mutate a published object**. `_config["timeout"] = 30` could break the guarantee that a published dictionary never changes; do not equate Python multi-step-operation races with the precise C data-race definition.

> [!note] Content gap
> No hardware-specific lock, cache-transfer or RCU timing benchmark is available. The Treiber stack example deliberately omits safe reclamation, and the seqlock/RCU fragments are protocol illustrations, not complete production implementations.

## Choosing a tool

| Situation | Reach for |
|---|---|
| Shared counter | atomic fetch-add |
| Small, hot, plain data | seqlock |
| Read-mostly linked data | RCU or copy-on-write updates |
| Long reads, some writes | read-write lock |
| Queue between threads | library queue |
| Anything else | a mutex |

> [!warning] Lock-free is not automatically faster
> Under heavy contention on one word, CAS loops fail and retry repeatedly, and the cache line still bounces between cores. A well-implemented mutex that puts waiters to sleep can beat a naive lock-free structure. Lock-free code is also very hard to get right and test. Use proven libraries (`java.util.concurrent`, Rust's `crossbeam`, Folly, Boost.Lockfree, `liburcu`) and benchmark before replacing a lock.

## Key takeaways

- Build a private replacement and publish it under the shared lock.
- A retained reference keeps an old dictionary alive, but the application must also keep it unchanged.
- This lock-assisted snapshot example is not a lock-free Python RCU implementation.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
