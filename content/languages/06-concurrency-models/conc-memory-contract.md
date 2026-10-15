---
id: conc-memory-contract
title: Happens-before and language memory models
level: basic
minutes: 3
sourceLesson: conc-threads-shared-memory
summary: Happens-before is a language-level ordering contract, not elapsed time.
---

The preceding Java example showed why shared writes need an ordering contract. This unit compares that contract across languages rather than assuming hardware interleavings explain every program.

## Memory models: the contract

Compilers reorder instructions and CPUs execute them out of order, because that is how they get fast. A language's **memory model** is the contract that says which reorderings your program can observe. The central idea is **happens-before**:

- Everything a thread does before **releasing** a lock happens-before everything another thread does after **acquiring** that same lock.
- A Java volatile write synchronizes with subsequent reads in synchronization order. A C++ release-store synchronizes with an acquire-load that reads from it (or the qualifying release sequence).
- Starting a thread happens-before its first action; a thread's last action happens-before `join()` returns.

Happens-before constrains which writes a read may observe; intervening writes matter. In C++, conflicting accesses form a data race when they are potentially concurrent, unordered, and at least one is non-atomic.

Java and Go provide a data-race-free sequential-consistency guarantee. For C++, race freedom alone is insufficient when weaker atomics are used: a race-free program restricted to mutexes and sequentially consistent atomics supports the simple interleaving model, while relaxed atomics can permit non-SC outcomes. What happens when you *do* race differs sharply:

| Language | Data race means |
|---|---|
| C, C++ | Undefined behaviour |
| Java | Defined but weird: stale or reordered values |
| Go | Mostly like Java; races on multi-word values can corrupt memory |
| Rust (safe) | Type/ownership rules prevent data races, assuming sound unsafe dependencies |
| CPython with GIL | Python operations still need synchronization; native extensions have their own obligations |

"Undefined behaviour" in C++ really means anything: the optimiser may assume races never happen and transform your code in surprising ways. Java chose to keep even racy programs memory-safe, because the JVM must never let you forge a pointer. Even so, Java allows a non-volatile `long` or `double` write to be split into two 32-bit halves (a torn 64-bit value), so another thread can see half of each value.

## Key takeaways
- Happens-before is a language-level ordering contract, not elapsed time.
- Race consequences differ by language; weaker C++ atomics need more than race freedom.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/threading.html)
- [Primary source: docs.oracle.com](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Primary source: go.dev](https://go.dev/ref/mem)
- [Primary source: eel.is](https://eel.is/c++draft/intro.races)
