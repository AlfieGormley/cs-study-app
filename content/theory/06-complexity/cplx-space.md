---
id: cplx-space
title: Space complexity and PSPACE
level: advanced
minutes: 15
summary: Measuring memory instead of time, the classes L, NL and PSPACE, Savitch's theorem, why NL equals coNL, TQBF and games as PSPACE-complete problems, and which separations are proven.
---

Time is not the only resource. A route planner on an embedded device, a streaming algorithm watching a network link, or a game engine searching ahead are all limited by **memory**. Space complexity asks how much working memory a problem needs.

Space behaves differently from time for one reason: **space can be reused, time cannot.** That single fact drives every result in this lesson.

## Measuring space

We use a Turing machine with a **read-only input tape** and a separate **work tape**, and count only the work-tape cells used. That makes sublinear space meaningful: a machine can read an n-bit input while storing only a few counters.

- **SPACE(s(n))**: problems decidable by a deterministic machine using O(s(n)) work cells.
- **NSPACE(s(n))**: the same with a nondeterministic machine.

The key classes are defined by plugging particular space bounds into these:

```formula
L = SPACE(log n)
NL = NSPACE(log n)
PSPACE = SPACE(n^k)   for some k
EXPSPACE = SPACE(2^{n^k})   for some k
where
SPACE(s(n)): the problems a deterministic machine (no guessing) decides using at most a constant times s(n) cells of work tape
NSPACE(s(n)): the same, for a nondeterministic machine (one that may guess at each step)
s(n): the space bound: a function of the input size n, counted in work-tape cells
n: the input size, in bits
log: the logarithm, base 2: log n is the number of bits needed to write the number n
k: a fixed constant exponent, such as 1, 2 or 3
L: logarithmic space, deterministic
NL: nondeterministic logarithmic space
PSPACE: polynomial space: a problem is in PSPACE when it is in SPACE(n^k) for some fixed k
EXPSPACE: exponential space: SPACE(2 to the power n^k) for some fixed k
In words: L and NL allow only logarithmic work memory (without and with guessing); PSPACE allows memory polynomial in the input size; EXPSPACE allows exponential memory. None of them limits time.
```

| Class | Space bound | Example |
|---|---|---|
| L | logarithmic | Undirected reachability |
| NL | logarithmic, guessing | Directed reachability |
| PSPACE | polynomial | TQBF, generalised games |
| EXPSPACE | exponential | Regex equivalence with squaring |

Why logarithmic? It is just enough to hold a constant number of pointers into the input, or counters up to the input size. An L algorithm is roughly "a program with a fixed number of integer variables, each no bigger than the input length":

```formula
b = log_2(n)
b = log_2(2^33) = 33 bits   for n = 2^33
where
b: the number of bits one pointer or counter needs, in bits
n: the input size, in bits; 2^33 bits is about 8.6 × 10^9 bits, roughly 1 GB
log_2: logarithm base 2: the power you raise 2 to in order to get n
bits: binary digits, each 0 or 1
In words: a pointer to any position in a 1 GB input fits in 33 bits, so a log-space algorithm on that input might use only a few hundred bits of work memory.
```

## Time versus space

Two simple facts relate the resources:

1. **Time bounds space.** In t steps a machine can touch at most t cells.
2. **Space bounds time, exponentially.** A machine with a small work tape has only a limited number of distinct **configurations** (head positions, tape contents, state). A halting computation never repeats a configuration, so it finishes within that many steps.

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
N_conf ≤ n × s × |Γ|^s × |Q|
N_conf = 2^{O(s)}   for s ≥ log n
N_conf ≤ 1024 × 10 × 2^10 × 10 ≈ 10^8
where
N_conf: the number of distinct configurations the machine can be in
n: the input size; there are n possible input-head positions (1024 in the example)
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
In words: each class sits inside the next. Some of these inclusions must be strict (see the end of the lesson), but for most of them nobody knows which.
```

NP sits inside PSPACE because a polynomial-space machine can try every certificate one after another, **reusing** the same space for each.

## Directed reachability and NL

**PATH**: given a directed graph and vertices s, t, is there a path from s to t?

A nondeterministic log-space machine guesses the path one vertex at a time, storing only the current vertex and a step counter, and gives up after n steps (n being the number of vertices):

```formula
PATH ∈ NL
b = 2 × ⌈log_2(n)⌉
b = 2 × 20 = 40 bits   for n = 10^6
where
PATH: the directed reachability problem: is there a path from s to t?
NL: problems decidable by a nondeterministic machine in logarithmic space
∈: "is a member of"
b: the work memory used, in bits: one vertex name plus one step counter
n: the number of vertices in the graph
log_2: logarithm base 2
⌈ ⌉: ceiling: round up to the next whole number (log_2 of a million is about 19.93, which rounds up to 20)
bits: binary digits
In words: on a million-vertex graph the guessing machine needs only about 40 bits of work memory, so PATH is in NL.
```

So PATH is in NL. It is also **NL-complete** under log-space reductions.

For **undirected** graphs, Reingold (2005) proved reachability is in deterministic L, a celebrated and difficult result. Whether L equals NL (equivalently, whether directed PATH is in L) is open.

## Savitch's theorem

Does nondeterminism help for space as much as it seems to for time? Much less, it turns out.

**Savitch's theorem (1970)**:

```formula
NSPACE(s) ⊆ SPACE(s^2)   for s ≥ log n
where
NSPACE(s): problems a nondeterministic (guessing) machine decides using at most a constant times s work-tape cells
SPACE(s^2): problems a deterministic machine decides using at most a constant times s squared cells
s: the space bound, in cells
n: the input size, in bits
log: logarithm base 2
⊆: "is contained in"
≥: is at least
In words: removing guessing costs at most a squaring of the memory. A nondeterministic machine using 100 cells can be simulated deterministically in about 10,000 cells.
```

The idea is a midpoint recursion:

```formula
R(u, v, t)  iff  ∃ w with
  R(u, w, t/2)  and  R(w, v, t/2)
where
R(u, v, t): "there is a path from vertex u to vertex v of length at most t edges"
u, v: the start and end vertices
w: a candidate midpoint vertex
t: the maximum path length, in edges
∃: "there exists": at least one such w
In words: a path of at most t edges exists exactly when some middle vertex splits it into two halves of at most t/2 edges each.
```

Try every w, recursing on both halves, and **reuse** the space between the two calls.

```python
def reach(adj, u, v, t):
    # is there a path u -> v of length <= t?
    # (called with t >= 1)
    if t <= 1:
        return u == v or v in adj[u]
    h = (t + 1) // 2
    return any(reach(adj, u, w, h) and
               reach(adj, w, v, t - h)
               for w in adj)

adj = {0: [1], 1: [2], 2: [3],
       3: [], 4: [0]}
n = len(adj)
print(reach(adj, 0, 3, n))   # True
print(reach(adj, 3, 0, n))   # False
print(reach(adj, 4, 3, n))   # True: via 0
print(reach(adj, 0, 3, 2))   # False: 3 hops
```

Space analysis for a graph with n vertices:

- Recursion depth: the length bound halves each level, so there are about log₂ n levels.
- Each stack frame holds four numbers (u, v, w and the length), each at most n, so a frame is a logarithmic number of bits.
- Multiply them for the total.

```formula
d = log_2(n)
S = d × O(log n) = O(log^2 n)
d = log_2(1024) = 10   for n = 1024
S ≈ 10 × 4 × 10 = 400 bits
where
d: the recursion depth (number of stack frames alive at once)
S: the total work memory, in bits
n: the number of vertices; 1024 in the example
log_2: logarithm base 2; log_2(1024) = 10
log^2 n: (log n) squared
O(...): Big O: at most a constant times this, for large n
≈: approximately equal to
bits: binary digits
In words: 10 frames, each holding four 10-bit numbers, is about 400 bits. A breadth-first search would need a 1,024-bit visited array plus a queue.
```

The price is time. Each level tries every midpoint and makes two calls, so the number of branches multiplies at every level:

```formula
T ≤ (2 × n)^{log_2(n)} = n^{O(log n)}
T ≤ 2048^10 = 2^110 ≈ 1.3 × 10^33
where
T: the number of recursive calls, a measure of running time
n: the number of vertices; 1024 in the second line
log_2: logarithm base 2
O(log n): Big O: at most a constant times log n
≤: is at most
≈: approximately equal to
In words: about (2n) to the power log n calls, which is more than any polynomial. On 1,024 vertices that is around 10^33 calls, hopeless in practice.
```

Savitch trades time for space. I compared this function with breadth-first search on 300 random graphs for every (u, v, t); they always agreed.

For a nondeterministic machine using space s, apply the same recursion to its **configuration graph** (one vertex per configuration, an edge for each legal step):

```formula
N = 2^{O(s)}
d = log_2(N) = O(s)
S = d × O(s) = O(s^2)
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
NPSPACE ⊆ SPACE((n^k)^2)
SPACE(n^{2k}) ⊆ PSPACE
PSPACE = NPSPACE
where
NPSPACE: problems a nondeterministic machine decides in polynomial space
PSPACE: problems a deterministic machine decides in polynomial space
SPACE(f): problems a deterministic machine decides using at most a constant times f cells
n: the input size, in bits
k: the fixed exponent of the nondeterministic machine's space bound n^k
⊆: "is contained in"
In words: Savitch turns n^k nondeterministic space into n^{2k} deterministic space, still a polynomial. Since every deterministic machine is also a (non-guessing) nondeterministic one, the two classes are equal.
```

## NL equals coNL

**Immerman–Szelepcsényi theorem (proved independently, 1987–88)**:

```formula
NSPACE(s) = coNSPACE(s)   for s ≥ log n
NL = coNL
where
NSPACE(s): problems a nondeterministic machine decides using at most a constant times s work cells
coNSPACE(s): the complements of those problems (yes and no swapped)
NL: nondeterministic logarithmic space
coNL: the complements of NL problems
s: the space bound, in cells
n: the input size, in bits
log: logarithm base 2
≥: is at least
In words: for nondeterministic space of at least log n, a class equals its complement class. In particular **NL equals coNL**: a nondeterministic log-space machine can certify that t is *unreachable* from s.
```

The proof is "inductive counting": nondeterministically compute the exact number of vertices reachable within 1 step, then within 2 steps, and so on up to n steps, using each count to verify the next. Knowing exactly how many vertices are reachable lets the machine confirm t isn't among them.

The analogous question for time, NP vs coNP, is open and believed to go the other way.

## PSPACE-completeness: TQBF

A **quantified Boolean formula** puts quantifiers in front of a formula:

```formula
∀x ∃y ∀z ((x ∨ y) ∧ (¬y ∨ z))
where
x, y, z: Boolean variables, each true or false
∀: "for all": the rest must hold for both values of the variable
∃: "there exists": the rest must hold for at least one value of the variable
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
¬: NOT: ¬y is true exactly when y is false
In words: "for every x there is a y such that, for every z, (x or y) and (not y or z) both hold". This particular formula is false, as traced below.
```

**TQBF** asks whether a fully quantified formula is true. It is **PSPACE-complete** (Stockmeyer and Meyer, 1973). SAT is the special case where every quantifier is ∃.

The obvious recursive evaluator runs in polynomial space and exponential time:

```python
def tqbf(quants, phi, a=()):
    # quants: string of 'E'/'A', one per var
    if len(a) == len(quants):
        return phi(a)
    q = quants[len(a)]
    r = tqbf(quants, phi, a + (False,))
    if q == 'E' and r:
        return True
    if q == 'A' and not r:
        return False
    return tqbf(quants, phi, a + (True,))

f = lambda a: a[0] != a[1]
print(tqbf('AE', f))  # True:  ∀x ∃y x≠y
print(tqbf('EA', f))  # False: ∃y ∀x x≠y

g = lambda a: ((a[0] or a[1]) and
               (not a[1] or a[2]))
print(tqbf('AEA', g))  # False
```

The recursion depth is the number of variables. A careful implementation keeps one shared assignment array and a constant amount of data per frame:

```formula
S = O(n)
T = O(2^n × |φ|)
T ≈ 2^30 × |φ| ≈ 10^9 × |φ|   for n = 30
where
S: the work space beyond the formula itself
T: the running time, in steps
n: the number of variables (and so the recursion depth)
φ: phi, the quantifier-free part of the formula; |φ| is its length, the cost of evaluating it once
O(...): Big O: at most a constant times this
≈: approximately equal to
In words: linear space but exponential time, because the two recursive calls run one after the other and reuse the same space. With 30 variables that is about a billion evaluations of φ, held in only 30 frames.
```

(This Python version copies the tuple at each level, which costs space quadratic in n: still polynomial.)

Trace the last one: if x is false, (x ∨ y) forces y true, and then (¬y ∨ z) requires z true for **all** z, which fails at z = false. So the ∀x fails.

Hardness, in outline: for a machine using space p(n), write a formula saying "configuration c1 reaches configuration c2 within 2 to the power k steps", defined recursively using a midpoint:

```formula
R(c1, c2, k) = ∃m ∀c3 ∀c4
  [((c3, c4) = (c1, m) ∨
    (c3, c4) = (m, c2))
   → R(c3, c4, k − 1)]
|R(k)| = |R(k − 1)| + O(p(n))
|R(k)| = O(k × p(n)) = O(p(n)^2)
where
R(c1, c2, k): the formula "configuration c1 reaches configuration c2 in at most 2^k steps"
c1, c2: the start and end configurations, each written as about p(n) Boolean variables
m: the midpoint configuration
c3, c4: a pair of configurations that ranges over the two halves (c1, m) and (m, c2)
k: the recursion level; k = O(p(n)), because the machine has at most 2^{O(p(n))} configurations
p(n): the machine's polynomial space bound on an n-bit input
|R(k)|: the length of the formula at level k
∃: "there exists"; ∀: "for all"
∨: OR; →: implies ("if the left side holds, the right side must too")
O(...): Big O: at most a constant times this
In words: one copy of the level-(k − 1) formula serves both halves, because ∀ makes it check whichever pair is plugged in. Each level adds only about p(n) symbols, so the whole formula is polynomial size.
```

The naive version would write the sub-formula twice per level and double in size each time, giving exponentially many copies. This is Savitch's recursion written as a formula.

## Games are PSPACE problems

Alternating quantifiers are a two-player game: "there is a move for me such that for all your replies there is a move for me such that...". TQBF is a game in which players take turns setting variables.

So deciding whether the first player has a winning strategy is typically **PSPACE-complete** for games that end within polynomially many moves:

- **Generalised geography** (players extend a path in a directed graph, no repeats), PSPACE-complete.
- **Generalised Hex** and generalised **Othello** on n × n boards, PSPACE-complete.

Games that can last exponentially long are typically harder: generalised **chess** (Fraenkel and Lichtenstein, 1981) and **Go** with Japanese ko rules (Robson, 1983) on n × n boards are **EXPTIME-complete**, so provably not in P.

Real-world PSPACE-complete problems include **equivalence of ordinary regular expressions** using union, concatenation and Kleene star (excluding backreferences and succinct extensions), **LTL model checking** used in hardware and protocol verification, and classical **AI planning** (STRIPS).

## What's proven, what's open

The **space hierarchy theorem** says more space solves strictly more problems:

```formula
SPACE(s) ⊊ SPACE(s′)   when s = o(s′)
SPACE(n) ⊊ SPACE(n^2)
where
SPACE(s): problems a deterministic machine decides using at most a constant times s work cells
s, s′: two space bounds (s′ is read "s prime"); s′ must be well-behaved and at least log n
n: the input size, in bits
o(s′): little o: grows strictly more slowly than s′, so s / s′ shrinks towards 0 as n grows
⊊: "is strictly contained in": every problem on the left is on the right, and some problem on the right is not on the left
In words: give a machine asymptotically more memory and it can decide problems it could not before. For example, quadratic space decides strictly more than linear space.
```

Combined with Savitch's theorem, this proves some separations:

```formula
NL ⊆ SPACE(log^2 n) ⊊ PSPACE
PSPACE ⊊ EXPSPACE
P ⊊ EXPTIME
where
NL: nondeterministic logarithmic space
SPACE(log^2 n): deterministic space of at most a constant times (log n) squared
PSPACE: polynomial space
EXPSPACE: exponential space
P: polynomial time
EXPTIME: exponential time
n: the input size, in bits
log: logarithm base 2
⊆: "is contained in"
⊊: "is strictly contained in": contained, and not equal
In words: NL is strictly smaller than PSPACE, PSPACE strictly smaller than EXPSPACE, and P strictly smaller than EXPTIME (the last from the time hierarchy theorem).
```

- **Proven**: the three strict separations above.
- **Open**: L vs NL, L vs P, NL vs P, P vs PSPACE, NP vs PSPACE, PSPACE vs EXPTIME.

It is striking that P equalling PSPACE has not been ruled out: nobody can prove that polynomial memory gives more power than polynomial time, though it is universally conjectured.

## Key takeaways
- Space can be reused, so it's far more powerful than time: NP is inside PSPACE, and s cells of space need at most about 2 to the power s steps.
- The chain L, NL, P, NP, PSPACE, EXPTIME has each class inside the next; proven strict: NL is smaller than PSPACE and P is smaller than EXPTIME.
- Savitch: nondeterministic space s can be simulated in deterministic space s squared by midpoint recursion, so PSPACE equals NPSPACE.
- Immerman–Szelepcsényi: NL equals coNL, unlike the (open) time analogue NP vs coNP.
- TQBF is PSPACE-complete; polynomial-length two-player games are typically PSPACE-complete, and generalised chess and Go are EXPTIME-complete.

## Further reading
- [PSPACE — Wikipedia](https://en.wikipedia.org/wiki/PSPACE)
- [Savitch's theorem — Wikipedia](https://en.wikipedia.org/wiki/Savitch%27s_theorem)
- [True quantified Boolean formula — Wikipedia](https://en.wikipedia.org/wiki/True_quantified_Boolean_formula)
- [Immerman–Szelepcsényi theorem — Wikipedia](https://en.wikipedia.org/wiki/Immerman%E2%80%93Szelepcs%C3%A9nyi_theorem)
- [NL (complexity) — Wikipedia](https://en.wikipedia.org/wiki/NL_(complexity))
- [Generalized geography — Wikipedia](https://en.wikipedia.org/wiki/Generalized_geography)
- [Space hierarchy theorem — Wikipedia](https://en.wikipedia.org/wiki/Space_hierarchy_theorem)
