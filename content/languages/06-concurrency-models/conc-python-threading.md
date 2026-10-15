---
id: conc-python-threading
title: The GIL, free threading and coordination costs
level: basic
minutes: 3
sourceLesson: conc-threads-shared-memory
summary: The GIL limits bytecode parallelism in a GIL-enabled interpreter, not every native operation.
---

Threads still require the shared-state discipline established earlier. This unit separates CPython interpreter configuration from the language-independent problems of coordination and resource use.

## Python and the GIL

CPython has historically had a **Global Interpreter Lock**: only one thread executes Python bytecode at a time. Consequences:

- **CPU-bound** Python threads do not run in parallel. Threads do not provide multicore bytecode parallelism in one GIL-bound interpreter; total timing depends on overhead and workload. Use `multiprocessing` or a native library that releases the GIL (NumPy does for many operations).
- **I/O-bound** threads work well, because the GIL is released while a thread waits on a socket or file.
- A bytecode can invoke user code or release the GIL, so bytecode boundaries are not a universal atomicity contract. The lost update above still happens.

PEP 703 added an optional **free-threaded** build (`python3.13t`), experimental in 3.13 and officially supported (though not the default) from 3.14. Without a GIL, threads run Python in parallel, and code that leaned on the GIL by accident is exposed.

## Where shared-memory threads hurt

- **Composability.** Two correct lock-using modules can deadlock when combined, if they take locks in different orders.
- **Invisible contracts.** In many APIs the lock discipline is a convention; type systems, annotations and wrappers can make parts of that discipline explicit.
- **Testing.** Races are timing-dependent. A test can pass a million times and fail in production under load. Tools help: Go's `-race` flag, Clang's ThreadSanitizer, Java's jcstress harness.
- **Cost per thread.** OS threads consume stack reservations and scheduler resources. No universal stack-size range, switch time or maximum count is supplied because these depend on platform, configuration and workload. That pressure drives the lighter models in the next lessons.

The rest of this module is, in a sense, a tour of escape routes. Single-thread event loops reduce simultaneous shared-memory access; async tasks can also run on multithreaded runtimes. Channels and actors encourage message passing but may still transmit shared references. Rust keeps shared memory but makes the compiler check it.

## Key takeaways
- The GIL limits bytecode parallelism in a GIL-enabled interpreter, not every native operation.
- Free-threaded builds still require explicit coordination of shared invariants.

## Further reading
- [Chapter 17: Threads and Locks — Java Language Specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [The Go Memory Model](https://go.dev/ref/mem)
- [Memory model — cppreference](https://en.cppreference.com/w/cpp/language/memory_model)
- [Acquire and Release Semantics — Preshing on Programming](https://preshing.com/20120913/acquire-and-release-semantics/)
- [threading — Python docs](https://docs.python.org/3/library/threading.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [Primary verification source 1](https://eel.is/c++draft/intro.races)
- [Primary verification source 2](https://eel.is/c++draft/atomics.order)
