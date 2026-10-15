---
id: cplx-reachability-nl
title: "Directed reachability and logarithmic space"
level: advanced
minutes: 3
summary: "A nondeterministic machine guesses a path using a vertex and a counter."
sourceLesson: cplx-space
---

## Directed reachability and NL

**PATH**: given a directed graph and vertices s, t, is there a path from s to t?

A nondeterministic log-space machine guesses the path one vertex at a time, storing only the current vertex and a step counter, and gives up after n steps (n being the number of vertices):

```formula
PATH ∈ NL
b = 2⌈log_2(n + 1)⌉ + O(log n)
b_core = 2 × 20 = 40 bits
  for n = 10^6
where
PATH: the directed reachability problem: is there a path from s to t?
NL: problems decidable by a nondeterministic machine in logarithmic space
∈: "is a member of"
b: the asymptotic working memory in bits, including input scanning and bookkeeping
b_core: an illustrative count of the vertex-name and step-counter bits
O(log n): Big O of log n, additional logarithmic storage; the total remains logarithmic
log: logarithm base two
n: the number of vertices in the graph
log_2: logarithm base 2
⌈ ⌉: ceiling: round up to the next whole number (log_2 of a million is about 19.93, which rounds up to 20)
bits: binary digits
In words: on a million-vertex graph the guessing machine uses about forty bits for those two core counters, plus logarithmic bookkeeping, so PATH is in NL.
```

So PATH is in NL. It is also **NL-complete** under log-space reductions.

For **undirected** graphs, Reingold (2005) proved reachability is in deterministic L, a celebrated and difficult result. Whether L equals NL (equivalently, whether directed PATH is in L) is open.

## Key takeaways

- A nondeterministic machine guesses a path using a vertex and a counter.
- Directed reachability is NL-complete under log-space reductions.
- Undirected reachability is in deterministic L; L versus NL remains open.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
