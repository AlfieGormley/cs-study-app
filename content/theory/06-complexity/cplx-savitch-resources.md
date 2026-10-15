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

```formula
d = ⌈log_2(n)⌉
S = d O(log n) = O(log^2 n)
d = log_2(1024) = 10   for n = 1024
S ≈ 10 × 4 × 10 = 400 bits
where
d: the number of halvings before the base case; including its frame adds one
S: the total work memory, in bits
n: the number of vertices; 1024 in the example
log_2: logarithm base 2; log_2(1024) = 10
log^2 n: (log n) squared
⌈ ⌉: ceiling, rounding up to a whole number
O(...): Big O: at most a constant times this, for large n
≈: approximately equal to
bits: binary digits
In words: about ten recursive levels, each holding roughly forty bits, gives a four-hundred-bit scale; the base-case frame and the length-bound endpoint add small overhead. A breadth-first search would need a 1,024-bit visited array plus a queue.
```

The price is time. Each level tries every midpoint and makes two calls, so the number of branches multiplies at every level:

```formula
T = O((2n)^{⌈log_2(n)⌉})
T = n^{O(log n)}
T_scale = 2048^{10} = 2^{110}
T_scale ≈ 1.3 × 10^{33}
where
T: an upper-bound analysis of recursive-call work
T_scale: the growth expression evaluated at 1024 vertices; not a measured or guaranteed number of calls
⌈ ⌉: ceiling, rounding up to a whole number
O(...): Big O, an upper bound up to fixed factors for sufficiently large n
n: the number of vertices; 1024 in the second line
log_2: logarithm base 2
O(log n): Big O: at most a constant times log n
≤: is at most
≈: approximately equal to
In words: the displayed upper-bound growth function exceeds every fixed polynomial. On 1,024 vertices that is an upper-bound growth scale around ten to the thirty-third power. Short-circuiting can do much less work on a particular graph; the bound is not a lower bound or a measured call count.
```

Savitch trades time for space. A seeded finite audit compares the function with a length-bounded breadth-first search on 300 random directed graphs for all endpoint pairs and positive bounds up to the vertex count. The recurrence, rather than the test sample, proves the general reachability statement.

For a nondeterministic machine using space s, apply the same recursion to its **configuration graph** (one vertex per configuration, an edge for each legal step):

```formula
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

```formula
NSPACE(n^k) ⊆ SPACE((n^k)^2)
SPACE(n^{2k}) ⊆ PSPACE
PSPACE = NPSPACE
where
NPSPACE: the union of nondeterministic polynomial-space bounds
NSPACE(n^k): one particular nondeterministic space bound, for a fixed k
PSPACE: problems a deterministic machine decides in polynomial space
SPACE(f): problems a deterministic machine decides using at most a constant times f cells
n: the input size, in bits
k: the fixed exponent of the nondeterministic machine's space bound n^k
⊆: "is contained in"
In words: Savitch turns n^k nondeterministic space into n^{2k} deterministic space, still a polynomial. Since every deterministic machine is also a (non-guessing) nondeterministic one, the two classes are equal.
```

## Key takeaways

- Logarithmic recursion depth times logarithmic frame size gives squared-logarithmic space.
- Time can be quasi-polynomial while work memory stays tiny.
- Applying the recursion to configurations proves PSPACE equals NPSPACE.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
