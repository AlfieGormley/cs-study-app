---
id: conc-thread-sharing
title: What threads share
level: basic
minutes: 3
sourceLesson: conc-threads-shared-memory
summary: Each thread has its own execution stack; ordinary process memory may be shared.
---

Many languages offer shared-memory concurrency: several **threads** running inside one process, all able to read and write the same variables. Java, C, C++, C#, Python, Go and Rust all offer it. It is the model the hardware most directly supports, though synchronization and contention affect performance. Shared mutable state also creates opportunities for concurrency bugs.

This lesson looks at threads from the *language's* point of view: what your code is allowed to assume when two threads touch the same memory. (How the kernel schedules threads and implements locks is covered in the Operating Systems subject.)

## The intuition

Picture two cooks sharing one kitchen and one notepad of orders. Each can read and scribble on the notepad whenever they like. That is efficient: nobody has to copy orders around. But if both glance at "pancakes: 3", both add one, and both write "4", one order has vanished.

Threads are the cooks and the heap is the notepad. Shared access avoids some copying, but cache coherence and synchronization have costs.

## Starting threads

For example, Python exposes threads and joining through threading:

```python
# Join before observing final results.
import threading

def work(n):
    print("working on", n)

t = threading.Thread(target=work, args=(1,))
t.start()   # runs concurrently from here
t.join()    # wait for it to finish
```

Java has `new Thread(r).start()`, C++ has `std::thread`, Rust has `std::thread::spawn`. Each thread has its own execution stack, while process memory can be shared. Local variables can also become shared through references in languages that permit it; storage on a stack does not itself enforce isolation.

## Key takeaways
- Each thread has its own execution stack, while ordinary process memory can be shared.
- Escaped references can share local storage; being on a stack does not itself enforce isolation.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/threading.html)
- [Primary source: docs.oracle.com](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Primary source: go.dev](https://go.dev/ref/mem)
- [Primary source: eel.is](https://eel.is/c++draft/intro.races)
