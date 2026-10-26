---
id: cplx-savitch-resources
title: "Squaring space to remove nondeterminism"
level: advanced
minutes: 4
summary: "Logarithmic recursion depth times logarithmic frame size gives squared-logarithmic space."
sourceLesson: cplx-space
---

Continue the length-bounded reachability recursion: try a midpoint, check both halves in sequence, and retain only the current stack. The graph is read-only input; the analysis below counts additional abstract workspace rather than Python object sizes.

Space analysis for a graph with n vertices:

- Recursion depth: the length bound halves each level, so there are about log₂ n levels.
- Each stack frame holds four numbers (u, v, w and the length), each at most n, so a frame is a logarithmic number of bits.
- Multiply them for the total.

```formula essential
d = ⌈log_2(n)⌉
S = d O(log n) = O(log^2 n)
where
d: the number of halvings before the base case; including its frame adds one
S: the total work memory, in bits
n: the number of vertices
log_2: logarithm base 2
log^2 n: (log n) squared
⌈ ⌉: ceiling, rounding up to a whole number
O(...): Big O: at most a constant times this, for large n
≈: approximately equal to
bits: binary digits
In words: logarithmically many live recursion frames, each holding logarithmically many bits, give squared-logarithmic working space. The full search tree is never stored.
```

The price is time. Each level tries every midpoint and makes two calls, so the number of branches multiplies at every level:

```formula reference
T = O((2n)^{⌈log_2(n)⌉})
T = n^{O(log n)}
where
T: an upper-bound analysis of recursive-call work
⌈ ⌉: ceiling, rounding up to a whole number
O(...): Big O, an upper bound up to fixed factors for sufficiently large n
n: the number of vertices
log_2: logarithm base 2
O(log n): Big O: at most a constant times log n
≤: is at most
≈: approximately equal to
In words: trying every midpoint at each recursive level yields a quasi-polynomial time upper bound. This space-saving simulation does not establish a polynomial-time bound; particular graphs can terminate much sooner.
```

Savitch trades time for space. The midpoint equivalence proves the general reachability statement; keeping only the current recursion stack gives the space saving.

For a nondeterministic machine using space s, apply the same recursion to its **configuration graph** (one vertex per configuration, an edge for each legal step):

```formula essential
N = 2^{O(s)}
d = log_2(N) = O(s)
S = d O(s) = O(s^2)
where
N: the number of vertices (configurations) of the configuration graph
s: the machine's space bound, in cells
d: the recursion depth
S: the total work memory of the deterministic simulation
log_2: logarithm base 2
O(s): Big O: at most a constant times s
In words: there are about 2 to the power s configurations, so the recursion is about s levels deep, each frame storing a few configurations of about s cells: s squared space in total.
```

> [!note] Consequence: PSPACE equals NPSPACE
> The square of a polynomial is a polynomial, so nondeterminism adds nothing to polynomial space. Compare time, where P vs NP is open.

## Key takeaways

- Logarithmic recursion depth times logarithmic frame size gives squared-logarithmic space.
- Time can be quasi-polynomial while work memory stays tiny.
- Applying the recursion to configurations proves PSPACE equals NPSPACE.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
