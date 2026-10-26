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

A nondeterministic log-space machine guesses the path one vertex at a time, storing only the current vertex and a step counter, and gives up after n steps (n being the number of vertices). If a path exists, removing cycles gives one shorter than the vertex count. Vertex names and the counter need only logarithmically many bits; the machine checks each proposed edge by reading the input.

So PATH is in NL. It is also **NL-complete** under log-space reductions.

For **undirected** graphs, Reingold (2005) proved reachability is in deterministic L, a celebrated and difficult result. Whether L equals NL (equivalently, whether directed PATH is in L) is open.

## Key takeaways

- A nondeterministic machine guesses a path using a vertex and a counter.
- Directed reachability is NL-complete under log-space reductions.
- Undirected reachability is in deterministic L; L versus NL remains open.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
