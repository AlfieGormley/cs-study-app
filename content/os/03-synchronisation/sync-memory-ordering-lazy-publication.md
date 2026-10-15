---
id: sync-memory-ordering-lazy-publication
title: Make lazy initialisation safe
level: advanced
minutes: 3
summary: Repair double-checked locking and use documented initialisation mechanisms.
sourceLesson: sync-memory-ordering
---

Lazy initialisation must guarantee both that construction is coordinated and that a reader sees a fully initialised object. Checking a pointer twice does not itself provide either ordering guarantee.

## The double-checked locking bug

Lazy initialisation of a shared singleton is a classic. To avoid locking an already-initialized fast path, programmers wrote:

```c
Singleton *instance = NULL;   // plain

Singleton *get(void) {
    if (instance == NULL) {          // 1
        lock(&m);
        if (instance == NULL)        // 2
            instance = make();       // 3
        unlock(&m);
    }
    return instance;
}
```

The idea: check without the lock (fast path); if it looks uninitialised, take the lock and check again.

It is broken: the unlocked plain pointer read races with publication in C. One illustrative failure is incomplete publication. Line 3 performs two kinds of write: the writes inside `make()` that fill in the object's fields, and the write of the pointer into `instance`. Nothing stops the pointer store becoming visible to another thread **before** the field stores (the compiler can reorder them, and so can a weakly ordered CPU). A second thread then passes check 1, sees a non-null pointer, skips the lock entirely, and reads uninitialised fields.

The famous "Double-Checked Locking is Broken" declaration, signed by Bill Pugh and a group of Java and concurrency researchers, documented why the ordinary fast path was unsound under the old Java memory model. Prefer a documented initialisation protocol; the following choices supply the required construction and visibility guarantees:

- **C11**: make `instance` an `_Atomic(Singleton *)`, load it with `memory_order_acquire`, store it with `memory_order_release`.
- **Java 5+**: declare the field `volatile` (JSR-133 gave volatile acquire/release semantics).
- **C++11**: just use a function-local `static`; its initialisation is guaranteed thread-safe ("magic statics").
- **POSIX**: `pthread_once`.
- **Python**: initialise at module import, or use a lock; `functools.cache` alone does not promise the function runs only once under concurrency.

```c
_Atomic(Singleton *) instance;

Singleton *get(void) {
    Singleton *p = atomic_load_explicit(
        &instance, memory_order_acquire);
    if (p == NULL) {
        lock(&m);
        p = atomic_load_explicit(&instance,
            memory_order_relaxed);
        if (p == NULL) {
            // Construct before publication.
            p = make();
            atomic_store_explicit(&instance,
                p, memory_order_release);
        }
        unlock(&m);
    }
    return p;
}
```

The inner load can be relaxed because the mutex already orders it after any previous initialiser’s unlock. Assume initialisation before thread creation, a successful make(), and an object that remains alive and unchanged for these readers; failure and shutdown need their own policy.

## What this means for Python

Python has no `memory_order`. A conventional CPython GIL serialises Python execution while held, but this implementation mechanism does not specify a complete language-level ordering contract for arbitrary compound operations. Free-threaded CPython currently uses internal locking for many built-ins, but that is not a blanket language-level atomicity contract. In both cases use documented threading and queue protocols for shared invariants. Python does not specify the complete C11 memory model described above.

## Key takeaways

- An unlocked plain singleton pointer races with publication in C.
- The repaired example uses acquire/release publication and a mutex around construction.
- Prefer language/library initialisation protocols, and do not infer an entire memory model from the Python GIL.

## Further reading

- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Linux memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)
- [The Double-Checked Locking declaration](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [Java memory model specification](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [The Go memory model](https://go.dev/ref/mem)
