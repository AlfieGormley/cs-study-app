---
id: fp-snapshot-sharing
title: Snapshots, identity and thread sharing
level: advanced
minutes: 3
sourceLesson: fp-persistent-data
summary: A snapshot root is cheap but retains all reachable shared memory.
---

A snapshot root is cheap but retains all reachable shared memory. This unit develops that mechanism using the earlier units as prerequisites.

## Why bother: what sharing buys you

## Cheap snapshots and undo

Retaining an old root is a cheap snapshot, but keeps its reachable nodes alive. An editor's undo stack is just a list of previous document values. A game can keep the last 60 game states for rewind with memory proportional to what changed.

## O(1) change detection

For deeply immutable values, two references to the same object refer to unchanged contents. Mutable objects can change while retaining identity. React and Redux depend on this: `React.memo` compares each prop with `Object.is`, and Redux's `useSelector` compares results by reference, whose default change detection assumes immutable updates. It can also re-render for other reasons, and custom equality functions change the selection comparison. Many persistent APIs reuse identity for no-op updates, but that behavior is API-dependent; different references need not mean different contents.

## Safe sharing across threads

Deeply immutable data can avoid locks for its contents after safe publication and while its lifetime is guaranteed; mutable elements or reference-management protocols still need care. A Clojure atom holds a persistent value: a writer builds a new version and swaps a single pointer with compare-and-set, while readers keep using whatever version they grabbed.

## Where it gets hard

## Constant factors

A persistent vector lookup is several dependent pointer loads; an array lookup is one. Each update allocates fresh nodes, which means garbage collection pressure. For a tight numeric loop, a flat mutable array can avoid those indirections and allocations. Measure the actual implementation and workload before claiming a speed ratio. Persistent collections win when you actually need old versions or sharing, not by default.

## Key takeaways
- A snapshot root is cheap but retains all reachable shared memory.
- Identity comparisons require immutable updates and safe publication.

## Further reading
- [Okasaki: Purely Functional Data Structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
- [React Memo](https://react.dev/reference/react/memo)
- [Redux Selector](https://react-redux.js.org/api/hooks)
- [Java Memory](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Clojure Atoms](https://clojure.org/reference/atoms)
