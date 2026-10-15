---
id: gc-reference-count-costs
title: "The costs of keeping counts"
level: intermediate
minutes: 4
sourceLesson: gc-refcounting
summary: "Count traffic, metadata, synchronisation and cascading release can each cost time or space"
---

Reference counts replace a whole-heap tracing decision with ownership bookkeeping along execution paths. That work can be cheap in one setting and expensive in another; measure the actual implementation and sharing pattern.

## What it costs

Reference counting is not free. Creating or releasing a strong ownership reference can require count traffic. Borrowed references, moves, immortal objects and optimization can avoid updates.

- **Count updates everywhere.** Passing, storing or returning strong references can touch counts, depending on borrowing conventions and optimization. In CPython this is a measurable share of interpreter time.
- **Atomic operations under threads.** Concurrent strong-count updates require synchronization, often atomic operations whose cost depends on hardware, contention and memory ordering. C++ `shared_ptr` and Rust `Arc` pay this; Rust's `Rc` does not, and the compiler refuses to let an `Rc` cross threads. CPython's GIL let it use plain increments; the free-threaded build (PEP 703) uses **biased reference counting**, where the owning thread updates a fast local count and other threads use an atomic shared one.
- **Space.** Counts and related metadata use storage; their size varies by implementation (in `shared_ptr`, usually a separate control block).
- **Cascading frees.** In the simple eager model, dropping the last owner of an exclusively owned acyclic 10-million-node tree can require releasing all 10 million nodes before returning. Shared owners, cycles or deferred destruction change that work; eager counting alone gives no short-pause bound.
- **Copy-on-write damage.** Some operations acquiring references write counts, which can dirty shared pages after fork. The cycle collector also changes bookkeeping. gc.freeze() (Python 3.7) avoids collector traversal of frozen objects; it does not suppress their ordinary reference-count updates.

> [!tip] Avoiding count traffic
> C++ code passes `const std::shared_ptr<T>&`, or a plain `T&`, when the callee does not need to keep the object. Swift's optimiser removes retain/release pairs it can prove redundant. Rust makes clones of `Rc` explicit with `Rc::clone(&x)` so you can see each one.

## Choosing the ownership handle

Use Rc when shared ownership stays within a thread; Arc synchronises its ownership counts for use across threads when the contained type satisfies the required thread-safety traits. Arc does not by itself synchronise accesses to the contained data. In C++, separate shared_ptr handles sharing a control block can be updated concurrently; simultaneous unsynchronised writes to the same handle are a different issue.

After fork, reference-count writes and collector bookkeeping can dirty otherwise shared private pages. The resulting copies depend on the pages actually touched, not simply on the number of workers. CPython's freeze operation avoids later cycle-collector bookkeeping on frozen objects; ordinary counting writes can still occur. Keeping a dataset semantically read-only does not guarantee that its runtime metadata is never written.

## Key takeaways
- Count traffic, metadata, synchronisation and cascading release can each cost time or space.
- Borrowing, moving and compiler optimisation can avoid some reference-count updates.
- Rc and Arc express different thread-sharing contracts; neither a logical read-only dataset nor gc.freeze promises zero copy-on-write page copying.

## Further reading
- [Reference counting — Wikipedia](https://en.wikipedia.org/wiki/Reference_counting)
- [Python gc module documentation](https://docs.python.org/3/library/gc.html)
- [Python weakref module documentation](https://docs.python.org/3/library/weakref.html)
- [Automatic Reference Counting — The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/automaticreferencecounting/)
- [Rc and reference cycles — The Rust Book](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html)
- [PEP 683: Immortal objects](https://peps.python.org/pep-0683/)
- [Primary verification source 2](https://docs.python.org/3/c-api/refcounting.html)
- [Primary verification source 3](https://peps.python.org/pep-0703/)
- [Primary verification source 4](https://raw.githubusercontent.com/swiftlang/swift-book/main/TSPL.docc/LanguageGuide/AutomaticReferenceCounting.md)
- [Primary verification source 5](https://doc.rust-lang.org/std/sync/struct.Arc.html)
