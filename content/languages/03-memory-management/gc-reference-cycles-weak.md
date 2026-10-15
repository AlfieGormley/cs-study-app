---
id: gc-reference-cycles-weak
title: "Cycles and weak ownership edges"
level: intermediate
minutes: 4
sourceLesson: gc-refcounting
summary: "An intact unreachable strong cycle keeps its own counts above zero under pure reference counting"
---

A strong-reference count records incoming owners, not reachability from the running program. A group can therefore own itself after every outside reference disappears.

## The cycle problem

In the diagram, A and B name the two objects, x and y are outside references, and rc labels each object's strong-reference count. It is a toy ownership graph with no additional references.

Two objects that refer to each other each hold a count of at least 1, forever, even when nothing else can reach them.

```
 before:  x --> [A rc=2] --> [B rc=2] <-- y
                   ^------------'

 after del x, y:
          [A rc=1] --> [B rc=1]
             ^------------'
          unreachable, never freed
```

Cycles are everywhere in real programs: a parent node and its children with `parent` pointers, a doubly linked list, an object that adds itself as a callback, an exception that holds a traceback that holds the frame that holds the exception.

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
        # Back-pointer does not own the
        # parent.
        self._parent = (weakref.ref(parent)
                        if parent else None)

    @property
    def parent(self):
        ref = self._parent
        # A collected target resolves to
        # None.
        return ref() if ref else None
```

Calling the weak reference returns the object, or `None` if it has been freed. C++'s `weak_ptr::lock()` and Rust's `Weak::upgrade()` work the same way: they give you a temporary strong reference or nothing.

Swift adds `unowned`, a reference that does not keep its target strongly alive. You promise its target remains alive whenever it is accessed. Ordinary checked `unowned` traps on access after deallocation; `unowned(unsafe)` omits that protection. Swift closures are the classic cycle: a view controller stores a closure that captures `self` strongly. The fix is a capture list, `{ [weak self] in ... }`.

Weak references only help where you can see the cycle coming. Ordinary Swift/Objective-C ARC and C++ `shared_ptr` have no general tracing cycle collector. Explicitly clearing links can also break a cycle; a retained cycle otherwise leaks. Xcode provides a memory graph debugger to investigate such ownership.

## Key takeaways
- An intact unreachable strong cycle keeps its own counts above zero under pure reference counting.
- Choose weak back-pointers where the domain's ownership relation permits them; acquiring a weak target can fail.
- Swift checked unowned references carry a lifetime obligation and trap after target deallocation; they are not interchangeable with optional weak references.

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
