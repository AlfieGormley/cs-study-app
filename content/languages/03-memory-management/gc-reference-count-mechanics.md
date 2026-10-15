---
id: gc-reference-count-mechanics
title: "Strong counts and prompt release"
level: intermediate
minutes: 5
sourceLesson: gc-refcounting
summary: "The basic eager-counting model tracks strong owners and reclaims an acyclic, non-resurrecting value when its last owner releases it"
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

That last rule can create a **cascading release**. In an exclusively owned acyclic linked list, releasing the head can make each successor lose its last owner. Implementations can use worklists or other techniques rather than literal native-stack recursion.

In the trace above, each `rc=` value is the object's reference count. Each update is a single addition or subtraction:

```formula
rc' = rc + 1
rc' = rc − 1
where
rc: the object's reference count before the change: how many strong references currently point at it
rc': the count after the change; the first line applies when a reference is created, the second when one is destroyed
In words: creating a reference adds one, destroying one subtracts one, and the object is freed at the moment the count reaches 0.
```

Following the trace: `Obj()` starts at 1, `b = a` makes it 1 + 1 = 2, `del a` makes it 2 − 1 = 1, and `b = None` makes it 1 − 1 = 0, so the object is freed. The model assumes every reference is counted; weak references (below) deliberately are not.

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
# b still holds this object alive.
del a
print("after del a")
# Last owner leaves in this CPython example.
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
> Since Python 3.12, objects such as `None`, `True` and small integers are **immortal objects** (PEP 683): reference-count operations treat them specially and ordinary decrements do not deallocate them. The large reported count is not a reliable count of live references or a stable universal constant.

## Why people like it

1. **Promptness.** Acyclic, non-resurrecting objects can be reclaimed promptly when their last strong owner releases them; allocator retention can still keep process memory high.
2. **Deterministic destruction.** Simple eager counting has predictable release points. For files use with/open, RAII or explicit close; temporary-object destruction is not a portable resource-management guarantee, and cycles or deferred counting can delay it.
3. **Incremental by nature.** The work is spread across the program, without requiring a separate whole-heap collection in the basic acyclic model; cascading release can still take substantial time.
4. **Locality.** Basic count updates touch ownership metadata for the affected values rather than scanning an entire heap; releasing a final owner can touch further objects.

## Key takeaways
- The basic eager-counting model tracks strong owners and reclaims an acyclic, non-resurrecting value when its last owner releases it.
- Deleting one Python name does not destroy an object retained by another name.
- Cycles, deferred counting, immortal objects and finalizers qualify any claim of universally immediate destruction.

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
