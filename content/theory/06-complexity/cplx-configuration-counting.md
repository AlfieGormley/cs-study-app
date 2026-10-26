---
id: cplx-configuration-counting
title: "How space bounds time"
level: advanced
minutes: 4
summary: "Time bounds space because each step touches limited memory."
sourceLesson: cplx-space
---

## Time versus space

Two simple facts relate the resources:

1. **Time bounds space.** In t steps a machine can touch at most t cells.
2. **Space bounds time, exponentially.** A machine with a small work tape has only a limited number of distinct **machine configurations** (head positions, tape contents, state). A halting deterministic computation never repeats a configuration, so it finishes within that many steps.

```formula essential
TIME(t) ⊆ SPACE(t)
SPACE(s) ⊆ TIME(2^{O(s)})   for s ≥ log n
where
TIME(t): the problems a deterministic machine decides in at most a constant times t steps
SPACE(s): the problems a deterministic machine decides using at most a constant times s work-tape cells
t: a time bound, in steps
s: a space bound, in work-tape cells
n: the input size, in bits
log: logarithm base 2
O(s): Big O: at most a constant times s, for large inputs
2^{O(s)}: 2 raised to a power that is at most a constant times s
⊆: "is contained in": every problem in the left class is also in the right class
≥: is at least
In words: a time bound also bounds the work cells a machine can visit. A halting deterministic computation with at least logarithmic workspace takes at most exponentially many steps in that space bound, up to constants in the exponent.
```

The second fact comes from counting configurations:

```formula reference
N_conf ≤ (n + 2)s|Γ|^s|Q|
N_conf = 2^{O(s)}   for s ≥ log n
where
N_conf: the number of distinct configurations the machine can be in
n: the input size; the read-only input has n symbols plus two end-marker positions
s: the positive number of available work-tape cells, also bounding work-head positions
Γ: gamma, the fixed work-tape alphabet; |Γ| is its number of symbols
|Γ|^s: the number of possible work-tape contents: |Γ| choices for each of s cells
Q: the fixed set of control states; |Q| is its size
log: logarithm base 2; s ≥ log n means the tape has at least enough cells to hold one pointer into the input
O(s): Big O: at most a constant times s
≤: is at most
In words: multiply the choices for both head positions, work-tape contents and control state. For a fixed machine with at least logarithmic workspace, the result is at most exponential in that workspace bound.
```

With these, logarithmic space fits in polynomial time and polynomial space fits in exponential time. Directed reachability also puts NL inside P; deterministic polynomial time is inside NP, and NP is inside PSPACE. These containments do not establish which neighbouring classes differ.

NP sits inside PSPACE because a polynomial-space machine can try every certificate one after another, **reusing** the same space for each.

> [!analogy] Real-world analogy: Reusing a whiteboard
> Work through a stack of tasks on one whiteboard, erasing each task before beginning the next.
>
> **How it maps:** Certificate enumeration reuses the same workspace for each check. More checks increase total time, while only one check's storage is needed at once.
>
> **Where it stops:** The machine must also store its current certificate and enumeration counter. Reuse saves simultaneous storage; it does not make the exponentially many checks fast.

## Key takeaways

- Time bounds space because each step touches limited memory.
- A halting deterministic computation cannot repeat a configuration.
- Counting configurations gives exponential-time simulations of bounded space.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
