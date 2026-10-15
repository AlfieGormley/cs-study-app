---
id: fp-transient-builds
title: Transient builds and Python copying
level: advanced
minutes: 3
sourceLesson: fp-persistent-data
summary: Controlled local mutation can accelerate bulk construction.
---

Controlled local mutation can accelerate bulk construction. This unit develops that mechanism using the earlier units as prerequisites.

## Bulk builds and transients

Building a 100,000-element vector by 100,000 persistent appends creates 100,000 intermediate versions that nobody will ever look at. Libraries offer a controlled escape hatch:

- **Clojure transients**: `(persistent! (reduce conj! (transient []) xs))` uses an isolated transient, then returns a persistent value in O(1). Always capture the returned transient from each update and stop using it after persistent!.
- **Immutable.js** `withMutations`: batch updates on a temporary mutable copy.
- **Immer** (JavaScript): write ordinary mutating code against a draft; it produces a new immutable object that shares every untouched part with the original.

All three control mutation through a specific API contract. Follow that contract: retain returned transient values, avoid concurrent transient use, stop after `persistent!`, and never let a temporary draft escape. Ordinary aliases do not establish those guarantees.

## Python's options

In CPython, appending to a nonempty tuple with t + (x,) copies its references in O(n), where n is the tuple's length, while the elements themselves remain shared. This preserves the old tuple and is persistent in the semantic sense, but lacks an efficient tree-based update path. For real persistent collections, use a library such as `pyrsistent` (`pvector`, `pmap`, `pset`), or accept copying when the data is small.

## Key takeaways
- Controlled local mutation can accelerate bulk construction.
- Tuple concatenation preserves versions but copies references linearly.

## Further reading
- [Clojure Transients](https://clojure.org/reference/transients)
- [Immutable](https://immutable-js.com/docs/v5/Map/)
- [Immer](https://immerjs.github.io/immer/produce/)
- [Cpython Tuple](https://raw.githubusercontent.com/python/cpython/main/Objects/tupleobject.c)
- [Pyrsistent](https://raw.githubusercontent.com/tobgu/pyrsistent/master/README.rst)
