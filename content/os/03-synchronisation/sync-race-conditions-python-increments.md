---
id: sync-race-conditions-python-increments
title: Python increments and the GIL
level: basic
minutes: 2
summary: Distinguish a successful Python test run from a documented atomicity guarantee.
sourceLesson: sync-race-conditions
---

Python also shares mutable objects between threads. A conventional CPython GIL can mask a race in a particular workload, so the reason for correctness must come from the synchronisation protocol.

## The same bug in Python

The global interpreter lock (GIL) serialises Python execution in a conventional CPython build, but it is not a language-level guarantee that every bytecode is atomic: operations can invoke user code or release the GIL. `counter += 1` also spans several bytecodes:

```text
LOAD_GLOBAL   counter
LOAD_SMALL_INT 1
BINARY_OP     13 (+=)
STORE_GLOBAL  counter
```

That illustrative listing uses CPython 3.14 instruction names; names and switching points vary between versions. If execution can interleave a load and a later store, an update can be lost. The existence of several bytecodes does not itself prove that a particular CPython build switches between them.

```python
import threading

counter = 0

def work():
    global counter
    for _ in range(1_000_000):
        # Compound update needs a shared
        # lock.
        counter += 1

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
# Observe after all workers have joined.
# This unsynchronised count is not promised.
print(counter)
```

On modern CPython with a GIL this often prints the right answer, because the interpreter only considers switching threads at certain points. That is luck, not correctness. Free-threaded builds and changes that introduce additional switching points can expose lost updates; neither failure nor a particular count is guaranteed.

## Key takeaways

- A GIL is an interpreter mechanism, not a portable contract for compound operations.
- An exact output or a failure is not promised for the unsynchronised counter example.
- Use a documented lock around the complete shared update.

## Further reading

- [Python 3.14 disassembler](https://docs.python.org/3.14/library/dis.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
