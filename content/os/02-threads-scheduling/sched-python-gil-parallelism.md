---
id: sched-python-gil-parallelism
title: Python’s GIL, races and parallel alternatives
level: basic
minutes: 4
sourceLesson: sched-thread-apis
summary: GIL-enabled CPython executes bytecode in one thread at a time per interpreter.
---

## Python's GIL

A GIL-enabled CPython interpreter has a **Global Interpreter Lock**: a single lock that a thread must hold to execute Python bytecode. Python threads are real OS threads (1:1), but only one at a time runs Python code.
## Why it exists

CPython manages memory with **reference counts** on every object. Incrementing and decrementing those counts from several threads at once would need a lock or atomic operation on every object access. One big lock was simpler and made single-threaded code fast.
## What it means for CPU-bound code

```python
import threading, time

def spin(n):
    while n:
        n -= 1


# Equal work; actual durations may vary.
N = 20_000_000
t0 = time.perf_counter()
spin(N); spin(N)
dt = time.perf_counter() - t0
print(f"serial:  {dt:.2f}s")

t0 = time.perf_counter()
ts = [threading.Thread(target=spin,
                       args=(N,))
      for _ in range(2)]
for t in ts: t.start()

# Join before reading results or duration.
for t in ts: t.join()
dt = time.perf_counter() - t0
print(f"threads: {dt:.2f}s")
```

On a standard build the two lines print roughly the same time. The threads take turns holding the GIL (a waiting thread asks the holder to drop it after the **switch interval**, 5 ms by default, see `sys.getswitchinterval()`), so there is no parallel speed-up.
## What it does not hurt

The GIL is **released** during blocking I/O (`socket.recv`, file reads, `time.sleep`) and by many C extensions during long computations (NumPy array operations, `hashlib` on large inputs, `zlib`). So threads work well for I/O-bound Python, as in the pool example above, and for code that spends its time in GIL-releasing libraries.
## What it does not prevent: races

A common myth is that the GIL makes Python code thread-safe. It only guarantees that the interpreter's own internals stay consistent. Thread-switch points depend on the CPython version, and bytecodes may invoke user code or extensions. Do not assume a shared **read-modify-write** sequence is atomic:

```python
import threading

counter = 0

def bump(x):
    return x + 1

def work():
    global counter
    for _ in range(1_000_000):
        # Shared read, compute, then write.
        counter = bump(counter)

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()

# Join before reading results or duration.
for t in ts: t.join()

# One observed count cannot prove safety.
print(counter)
```

This is a race demonstration, not a reproducible output guarantee. Depending on build, scheduling and implementation, it may lose updates or print the expected count; a passing run does not establish correctness. One possible interleaving is that a thread reads counter, switches before completing the call and store, and later writes back a stale value. Exact switch opportunities depend on the interpreter version; loss is possible, not guaranteed by a particular source line.

A plain `counter += 1` in the loop often *happens* to give the right answer on recent CPython versions, because of where the interpreter checks for thread switches. That is an implementation detail, not a guarantee, and it is not a safe shared-counter protocol on free-threaded builds. Protect shared state with a `threading.Lock` (the next module covers locks properly).

Some simple built-in operations have useful implementation-level locking or atomicity, but callbacks, custom key methods and free-threaded builds complicate the rules. Use documented guarantees and explicit synchronisation for shared invariants; check-then-insert is not automatically atomic.
## Getting real parallelism in Python

- **Processes**: `multiprocessing` or `ProcessPoolExecutor`. Each process has its own interpreter and GIL. The cost is pickling data between processes.
- **C extensions** that release the GIL (NumPy and friends).
- **Free-threaded CPython** ([PEP 703](https://peps.python.org/pep-0703/)): a build with no GIL, experimental in 3.13 and officially supported (but not the default) from 3.14. It's installed as a separate interpreter, e.g. `python3.14t`. Single-threaded code runs somewhat slower, and C extensions must be marked compatible or the GIL is turned back on.
- **Subinterpreters**: Python 3.14 added `concurrent.interpreters` and `InterpreterPoolExecutor`, where each interpreter has its own GIL.

> [!note] Content gap: runtime measurements
> No reproducible record supports exact thread-creation timing, a particular racy counter output, false-sharing slowdown or ideal pool speed-up. Examples show mechanisms; timing and capacity must be measured for the chosen runtime and workload.

## Key takeaways
- GIL-enabled CPython executes bytecode in one thread at a time per interpreter.
- Blocking I/O and compatible native extensions can release the GIL; multi-step shared invariants still need synchronisation.
- Processes, GIL-releasing native work, free-threaded builds and isolated interpreters offer different routes to parallel computation.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
- [Thread safety — NumPy documentation](https://numpy.org/doc/stable/reference/thread_safety.html)
