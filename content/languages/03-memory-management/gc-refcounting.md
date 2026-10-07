---
id: gc-refcounting
title: Reference counting and cycles
level: intermediate
minutes: 12
summary: Freeing an object the moment its last reference disappears, how CPython, Swift, C++ and Rust do it, what it costs, why cycles defeat it, and the weak references and cycle collectors that fix them.
---

The simplest automatic answer to "when can this object be freed?" is: **when nobody refers to it any more**. Keep a counter in every object of how many references point at it. When the counter drops to zero, free the object.

That is **reference counting**. It runs inside CPython, Swift and Objective-C (as ARC), PHP, Perl, C++'s `std::shared_ptr` and Rust's `Rc` and `Arc`. It is easy to understand, it frees memory promptly, and it has one famous blind spot: **cycles**.

## The mechanism

In the basic model each managed allocation has a strong-reference count (possibly in a separate control block). The runtime (or the compiler) adjusts it whenever a reference is created or destroyed:

- A reference is **created** (assignment, passing an argument, putting it in a list): increment.
- A reference is **destroyed** (a variable is reassigned or goes out of scope, an item is removed): decrement.
- The count reaches **zero**: free the object, and decrement everything **it** refers to.

```
 a = Obj()        Obj  rc=1  <- a
 b = a            Obj  rc=2  <- a, b
 del a            Obj  rc=1  <- b
 b = None         Obj  rc=0  -> freed
```

That last rule makes freeing **recursive**. When the head of a linked list dies, its count of zero decrements the second node to zero, and so on down the list.

## Watching it in CPython

In ordinary GIL-enabled CPython, object headers include reference-count metadata. This simple non-resurrecting example illustrates prompt finalization; free-threaded/deferred counting, cycles and finalizers can alter timing:

```python
class Noisy:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print("freed", self.name)

a = Noisy("a")
b = a
del a
print("after del a")
del b
print("after del b")
```

Output:

```
after del a
freed a
after del b
```

`del a` only drops the count from 2 to 1, because `b` still refers to the object. `del b` drops it to 0, so the object is freed immediately, before the next line runs.

> [!note] Immortal objects
> Since Python 3.12, objects such as `None`, `True` and small integers are **immortal** (PEP 683): reference-count operations treat them specially and ordinary decrements do not deallocate them. The large reported count is not a reliable count of live references or a stable universal constant.

## Why people like it

1. **Promptness.** Acyclic, non-resurrecting objects can be reclaimed promptly when their last strong owner releases them; allocator retention can still keep process memory high.
2. **Deterministic destruction.** Simple eager counting has predictable release points. For files use with/open, RAII or explicit close; temporary-object destruction is not a portable resource-management guarantee, and cycles or deferred counting can delay it.
3. **Incremental by nature.** The work is spread across the program, with no separate collector to pause everything (mostly; see below).
4. **Locality.** It only touches the objects being changed, not the whole heap.

## What it costs

Reference counting is not free. Creating or releasing a strong ownership reference can require count traffic. Borrowed references, moves, immortal objects and optimization can avoid updates.

- **Count updates everywhere.** Passing, storing or returning strong references can touch counts, depending on borrowing conventions and optimization. In CPython this is a measurable share of interpreter time.
- **Atomic operations under threads.** Concurrent strong-count updates require synchronization, often atomic operations whose cost depends on hardware, contention and memory ordering. C++ `shared_ptr` and Rust `Arc` pay this; Rust's `Rc` does not, and the compiler refuses to let an `Rc` cross threads. CPython's GIL let it use plain increments; the free-threaded build (PEP 703) uses **biased reference counting**, where the owning thread updates a fast local count and other threads use an atomic shared one.
- **Space.** Counts and related metadata use storage; their size varies by implementation (in `shared_ptr`, usually a separate control block).
- **Cascading frees.** Dropping the last reference to a 10-million-node tree frees 10 million objects right then. That is a pause, just one you caused yourself.
- **Copy-on-write damage.** Some operations acquiring references write counts, which can dirty shared pages after fork. The cycle collector also changes bookkeeping. gc.freeze() (Python 3.7) avoids collector traversal of frozen objects; it does not suppress their ordinary reference-count updates.

> [!tip] Avoiding count traffic
> C++ code passes `const std::shared_ptr<T>&`, or a plain `T&`, when the callee does not need to keep the object. Swift's optimiser removes retain/release pairs it can prove redundant. Rust makes clones of `Rc` explicit with `Rc::clone(&x)` so you can see each one.

## The cycle problem

Two objects that refer to each other each hold a count of at least 1, forever, even when nothing else can reach them.

```
 before:  x --> [A rc=2] --> [B rc=2] <-- y
                   ^------------'

 after del x, y:
          [A rc=1] --> [B rc=1]
             ^------------'
          unreachable, never freed
```

Cycles are everywhere in real programs: a parent node and its children with `parent` pointers, a doubly linked list, an object that registers itself as a callback, an exception that holds a traceback that holds the frame that holds the exception.

Pure counting cannot reclaim an unreachable strong-reference cycle that remains intact. Weak edges, explicit link removal or a design that forbids strong cycles can avoid that situation. There are two fixes: make some references not count (weak references), or add a separate collector that finds cycles.

## Fix 1: weak references

A **weak reference** points at an object without contributing to its count. When the object is freed, the weak reference becomes empty instead of dangling.

The rule of thumb: **owners hold strong references, back-pointers are weak.** A parent owns its children; a child's pointer to its parent is weak.

| Language | Strong | Weak |
|---|---|---|
| Python | normal ref | `weakref.ref` |
| Swift | default strong | weak (nil on release); unowned has a different lifetime contract |
| C++ | `shared_ptr` | `weak_ptr` |
| Rust | `Rc` / `Arc` | `Weak` |

```python
import weakref

class Node:
    def __init__(self, parent=None):
        self.children = []
        self._parent = (weakref.ref(parent)
                        if parent else None)

    @property
    def parent(self):
        ref = self._parent
        return ref() if ref else None
```

Calling the weak reference returns the object, or `None` if it has been freed. C++'s `weak_ptr::lock()` and Rust's `Weak::upgrade()` work the same way: they give you a temporary strong reference or nothing.

Swift adds `unowned`, a reference that does not keep its target strongly alive. You promise its target remains alive whenever it is accessed. Ordinary checked `unowned` traps on access after deallocation; `unowned(unsafe)` omits that protection. Swift closures are the classic cycle: a view controller stores a closure that captures `self` strongly. The fix is a capture list, `{ [weak self] in ... }`.

Weak references only help where you can see the cycle coming. Ordinary Swift/Objective-C ARC and C++ `shared_ptr` have no general tracing cycle collector. Explicitly clearing links can also break a cycle; a retained cycle otherwise leaks. Xcode provides a memory graph debugger to investigate such ownership.

## Fix 2: a cycle collector

CPython takes the belt-and-braces route: reference counting for the common case, plus a **cycle collector** in the `gc` module for the rest.

It only needs to consider **container** objects (lists, dicts, class instances), because ordinary built-in int and str instances do not contain references participating in cycles; subclasses and extension types can have different layouts. The algorithm is neat:

1. For each container being examined, copy its reference count into a scratch field.
2. For every reference *between* those containers, subtract one from the target's scratch count.
3. Anything left with a scratch count above zero is referenced from **outside** the group, so it is alive. Everything reachable from it is alive too.
4. Whatever remains is referenced only from inside the group: unreachable cycles. Free it.

```python
import gc
gc.disable()  # explicit collect still works

class Node:
    def __init__(self, name):
        self.name, self.other = name, None
    def __del__(self):
        print("freed", self.name)

x, y = Node("x"), Node("y")
x.other, y.other = y, x
del x, y
print("after del")
gc.collect()
print("collected")
gc.enable()
```

Output (the two "freed" lines may come in either order):

```
after del
freed x
freed y
collected
```

After `del x, y`, each node still has a count of 1 from the other, so nothing is freed. `gc.collect()` subtracts the internal references, finds both at zero, and frees them. Since Python 3.4 (PEP 442), objects with `__del__` in a cycle are collected normally. Before that, they were parked uncollectable in `gc.garbage`.

The collector is **generational**: new containers are examined often, survivors less often, because most objects die young (lesson 4). Scheduling depends on version/build: net allocation counts matter, and free-threaded CPython also considers process-memory growth. The thresholds are tunable with `gc.set_threshold()`.

> [!warning] Disabling the cycle collector
> gc.disable() disables automatic cyclic collection. Reference counting still operates and explicit gc.collect() still works; unreachable intact strong cycles can accumulate until explicitly collected or broken. Some services do this deliberately for predictable latency and then must avoid creating cycles.

## Where reference counting sits

| | Ref counting | Tracing GC |
|---|---|---|
| When freed | last strong release in the basic acyclic model | during collection |
| Cycles | need extra help | free |
| Cost paid on | strong-reference updates and cascading release | collection and barriers |
| Destructors | deterministic | not timed |

Many systems blend the two. CPython is reference counting plus a tracing cycle collector. Research collectors use **deferred** reference counting, which skips count updates for stack variables and reconciles them periodically, to get most of the promptness with much less overhead.

## Key takeaways
- Reference counting frees an object the moment its count reaches zero, and frees its children recursively.
- Eager counting often gives prompt destruction, but cycles, resurrection and deferred counting are exceptions; use explicit resource-management constructs for files and locks.
- The costs include strong-reference count traffic, synchronization for shared counts and possible long cascading releases; optimized or borrowed references can avoid updates.
- Cycles are never freed by counting alone. Fix them with weak back-pointers (`weakref`, `weak`, `weak_ptr`, `Weak`) or a cycle collector.
- CPython combines counting with a generational cycle collector that finds groups referenced only from inside themselves.

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
