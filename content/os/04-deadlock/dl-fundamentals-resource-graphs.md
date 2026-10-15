---
id: dl-fundamentals-resource-graphs
title: Reading resource-allocation graphs
level: basic
minutes: 2
sourceLesson: dl-fundamentals
summary: Request edges point from a process to a resource; assignment edges point back to a holder.
---

## Resource-allocation graphs

A **resource-allocation graph** (RAG) makes the conditions visible. It has two kinds of node and two kinds of edge:

- Circles are threads (or processes): `T1`, `T2`.
- Boxes are resources: `[A]`, `[B]`. Dots inside a box show how many instances it has.
- A **request edge** `T → R` means T is waiting for R.
- An **assignment edge** `R → T` means R is held by T.

The transfer deadlock looks like this:

```
     holds           wants
 [A] -----> (T1) -----> [B]
  ^                      |
  |  wants        holds  |
  +------ (T2) <---------+
```

Follow the arrows: A → T1 → B → T2 → A. A cycle.

### When a cycle isn't a deadlock

Suppose resource R has **two** instances (two identical database connections, say) and resource S has one:

```
 R has 2 instances: held by T1 and T4
 S has 1 instance:  held by T2

 T1 wants S   (T1 -> S -> T2)
 T2 wants R   (T2 -> R -> T1, or -> T4)
```

There is a cycle T1 → S → T2 → R → T1. But T4 also holds an instance of R and is not waiting for anything. When T4 finishes and releases its instance, T2 gets it, finishes, releases S, and T1 proceeds. The cycle dissolves.

So the rules are:

- **No cycle**: no deadlock, guaranteed.
- **Cycle, single-instance resources**: deadlock, guaranteed.
- **Cycle, multi-instance resources**: deadlock *possible*; you need a more careful check (the detection algorithm in the detection and recovery lessons).

## Key takeaways
- Request edges point from a process to a resource; assignment edges point back to a holder.
- A cycle proves deadlock for exclusive single-instance resources.
- With interchangeable multiple instances, a holder outside the cycle may release a unit and unblock it.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
