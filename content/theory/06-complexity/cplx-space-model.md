---
id: cplx-space-model
title: "Measuring working memory"
level: advanced
minutes: 4
summary: "Read-only input is excluded from the working-space count."
sourceLesson: cplx-space
---

Time is not the only resource. A route planner on an embedded device, a streaming algorithm watching a network link, or a game engine searching ahead are all limited by **memory**. Space complexity asks how much working memory a problem needs.

Space behaves differently from time for one reason: **space can be reused, time cannot.** That single fact drives every result in this lesson.

## Measuring space

We use a Turing machine with a **read-only input tape** and a separate **work tape**, and count only the work-tape cells used. That makes sublinear space meaningful: a machine can read an n-bit input while storing only a few counters.

- **SPACE(s(n))**: problems decidable by a deterministic machine using O(s(n)) work cells.
- **NSPACE(s(n))**: the same with a nondeterministic machine.

The key classes are defined by plugging particular space bounds into these:

```formula reference
L = SPACE(log n)
NL = NSPACE(log n)
PSPACE = SPACE(n^k)   for some k
EXPSPACE = SPACE(2^{n^k})   for some k
where
SPACE(s(n)): the problems a deterministic machine (no guessing) decides using at most a constant times s(n) cells of work tape
NSPACE(s(n)): the same, for a nondeterministic machine (one that may guess at each step)
s(n): the space bound: a function of the input size n, counted in work-tape cells
n: the input size, in bits
log: the logarithm, base 2; encoding a position among n positions takes about this many bits, with integer rounding
k: a fixed constant exponent, such as 1, 2 or 3
L: logarithmic space, deterministic
NL: nondeterministic logarithmic space
PSPACE: polynomial space: a problem is in PSPACE when it is in SPACE(n^k) for some fixed k
EXPSPACE: exponential space: SPACE(2 to the power n^k) for some fixed k
In words: L and NL allow only logarithmic work memory (without and with guessing); PSPACE allows memory polynomial in the input size; EXPSPACE allows exponential memory. Their definitions constrain working space rather than imposing an explicit time bound. Deciders must still halt, and configuration counting gives an implicit deterministic time bound.
```

| Class | Space bound | Example |
|---|---|---|
| L | logarithmic | Undirected reachability |
| NL | logarithmic, guessing | Directed reachability |
| PSPACE | polynomial | TQBF, generalised games |
| EXPSPACE | exponential | Regex equivalence with squaring |

Why logarithmic? It is just enough to hold a constant number of pointers into the input, or counters up to the input size. Think of a log-space algorithm as keeping a fixed number of input positions and small counters while rereading the input as needed. Doubling the input length adds only about one bit per position counter.

## Key takeaways

- Read-only input is excluded from the working-space count.
- Logarithmic work memory can store a fixed number of input positions.
- Space classes distinguish deterministic from nondeterministic computation.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
