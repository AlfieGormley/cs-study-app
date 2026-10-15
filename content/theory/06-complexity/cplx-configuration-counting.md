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
2. **Space bounds time, exponentially.** A machine with a small work tape has only a limited number of distinct **machine configurations** (head positions, tape contents, state). A halting computation never repeats a configuration, so it finishes within that many steps.

```formula
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
In words: whatever can be done in t steps can be done in t cells; and a machine limited to s cells (with s at least log n) must finish within about 2 to the power s steps, or it would repeat itself and loop forever.
```

The second fact comes from counting configurations:

```formula
N_conf ≤ (n + 2)s|Γ|^s|Q|
N_conf = 2^{O(s)}   for s ≥ log n
N_conf ≤ 1026 × 10 × 2^{10} × 10
N_conf ≈ 1.05 × 10^8
where
N_conf: the number of distinct configurations the machine can be in
n: the input size; the read-only input has n symbols plus two end-marker positions (n is 1024 in the example)
s: the number of work-tape cells used; there are s work-head positions (10 in the example)
Γ: gamma, the work-tape alphabet (the symbols a cell can hold); |Γ| is how many there are (2 in the example)
|Γ|^s: the number of possible work-tape contents: |Γ| choices for each of s cells
Q: the set of the machine's control states; |Q| is how many there are (10 in the example)
log: logarithm base 2; s ≥ log n means the tape has at least enough cells to hold one pointer into the input
O(s): Big O: at most a constant times s
≤: is at most
≈: approximately equal to
In words: multiply the choices for the input head, the work head, the tape contents and the state. When s ≥ log n the input-head factor n is at most 2^s, so the whole product is 2 to the power of a constant times s.
```

With these, logarithmic space fits in polynomial time and polynomial space fits in exponential time. Combining with what we know of nondeterminism gives one chain of classes:

```formula
L ⊆ NL ⊆ P ⊆ NP ⊆ PSPACE
  ⊆ EXPTIME ⊆ EXPSPACE
where
L: problems decidable by a deterministic machine in logarithmic space
NL: the same with a nondeterministic (guessing) machine
P: problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: problems whose yes-answers have a short certificate checkable in polynomial time
PSPACE: problems decidable in polynomial space, however long it takes
EXPTIME: problems decidable in exponential time, at most about 2 to the power n^k steps
EXPSPACE: problems decidable in exponential space
n: the input size, in bits
k: a fixed constant exponent
⊆: "is contained in": every problem in the left class is also in the right class (they may be equal)
In words: each class sits inside the next. Some of these inclusions must be strict (see the games and hierarchy unit), but for most of them nobody knows which.
```

NP sits inside PSPACE because a polynomial-space machine can try every certificate one after another, **reusing** the same space for each.

## Key takeaways

- Time bounds space because each step touches limited memory.
- A halting deterministic computation cannot repeat a configuration.
- Counting configurations gives exponential-time simulations of bounded space.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
