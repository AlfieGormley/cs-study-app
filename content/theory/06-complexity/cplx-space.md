---
id: cplx-space
title: Space complexity and PSPACE
level: advanced
minutes: 15
summary: Measuring memory instead of time, the classes L, NL and PSPACE, Savitch's theorem, NL = coNL, TQBF and games as PSPACE-complete problems, and which separations are proven.
---

Time is not the only resource. A route planner on an embedded device, a streaming algorithm watching a network link, or a game engine searching ahead are all limited by **memory**. Space complexity asks how much working memory a problem needs.

Space behaves differently from time for one reason: **space can be reused, time cannot.** That single fact drives every result in this lesson.

## Measuring space

We use a Turing machine with a **read-only input tape** and a separate **work tape**, and count only the work-tape cells used. That makes sublinear space meaningful: a machine can read an n-bit input while storing only a few counters.

- **SPACE(s(n))**: problems decidable by a deterministic machine using O(s(n)) work cells.
- **NSPACE(s(n))**: the same with a nondeterministic machine.

Key classes:

| Class | Space bound | Example |
|---|---|---|
| L | O(log n) | Undirected reachability |
| NL | O(log n), nondet. | Directed reachability |
| PSPACE | poly(n) | TQBF, generalised games |
| EXPSPACE | 2^poly(n) | Regex equivalence with squaring |

Why log n? It is just enough to hold a constant number of pointers into the input or counters up to n. An L algorithm is roughly "a program with a fixed number of integer variables, each at most n".

## Time versus space

Two simple facts relate the resources:

1. **TIME(t) ⊆ SPACE(t).** In t steps a machine can touch at most t cells.
2. **SPACE(s) ⊆ TIME(2^O(s))** for s ≥ log n. A machine using s cells has at most about n · s · |Γ|^s · |Q| distinct **configurations** (head positions, tape contents, state), which is 2^O(s). A halting computation never repeats a configuration, so it finishes within that many steps.

So L ⊆ P and PSPACE ⊆ EXPTIME. Combining with what we know of nondeterminism:

```
L ⊆ NL ⊆ P ⊆ NP ⊆ PSPACE
  ⊆ EXPTIME ⊆ EXPSPACE
```

NP ⊆ PSPACE because a polynomial-space machine can try every certificate one after another, **reusing** the same space for each.

## Directed reachability and NL

**PATH**: given a directed graph and vertices s, t, is there a path from s to t?

A nondeterministic log-space machine guesses the path one vertex at a time, storing only the current vertex and a step counter (both O(log n) bits), and gives up after n steps. So PATH ∈ NL. It is also **NL-complete** under log-space reductions.

For **undirected** graphs, Reingold (2005) proved reachability is in deterministic L, a celebrated and difficult result. Whether L = NL (equivalently, whether directed PATH is in L) is open.

## Savitch's theorem

Does nondeterminism help for space as much as it seems to for time? Much less, it turns out.

**Savitch's theorem (1970)**: NSPACE(s) ⊆ SPACE(s²) for s ≥ log n.

The idea: a path from u to v of length at most t exists iff there's a midpoint w with a path u → w of length ≤ t/2 and w → v of length ≤ t/2. Try every w, recursing on both halves, and **reuse** the space between the two calls.

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

- Recursion depth: t halves each level, so about log₂ n levels.
- Each stack frame holds u, v, w and t: O(log n) bits.
- Total: O(log n) × O(log n) = **O(log² n)** space.

The price is time: the recursion explores roughly n^O(log n) branches. Savitch trades time for space. I compared this function with breadth-first search on 300 random graphs for every (u, v, t); they always agreed.

For a nondeterministic machine using space s, apply the same recursion to its **configuration graph** (2^O(s) nodes): depth O(s), frames of O(s) bits, so O(s²) space.

> [!note] Consequence: PSPACE = NPSPACE
> The square of a polynomial is a polynomial, so nondeterminism adds nothing to polynomial space. Compare time, where P vs NP is open.

## NL = coNL

**Immerman–Szelepcsényi theorem (proved independently, 1987–88)**: NSPACE(s) = coNSPACE(s) for s ≥ log n. In particular **NL = coNL**: a nondeterministic log-space machine can certify that t is *unreachable* from s.

The proof is "inductive counting": nondeterministically compute the exact number of vertices reachable in ≤ i steps, for i = 1, 2, ..., n, using each count to verify the next. Knowing exactly how many vertices are reachable lets the machine confirm t isn't among them.

The analogous question for time, NP vs coNP, is open and believed to go the other way.

## PSPACE-completeness: TQBF

A **quantified Boolean formula** puts quantifiers in front of a formula:

∀x ∃y ∀z ((x ∨ y) ∧ (¬y ∨ z))

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

The recursion depth is the number of variables n. A careful implementation keeps one shared assignment array and O(1) data per frame, so it uses O(n) space beyond the formula. (This Python version copies the tuple at each level, which costs O(n²): still polynomial.) Time is O(2ⁿ · |φ|): the two recursive calls run one after the other in the same space.

Trace the last one: if x is false, (x ∨ y) forces y true, and then (¬y ∨ z) requires z true for **all** z, which fails at z = false. So the ∀x fails.

Hardness, in outline: for a machine using space p(n), the formula "configuration c1 reaches c2 in ≤ 2^k steps" is written as: there exists a midpoint m such that, for all pairs (c3, c4) in {(c1, m), (m, c2)}, c3 reaches c4 in ≤ 2^(k−1) steps. The ∀ lets one sub-formula stand for both halves, so the formula grows linearly in k, not exponentially. This is Savitch's recursion written as a formula.

## Games are PSPACE problems

Alternating quantifiers are a two-player game: "there is a move for me such that for all your replies there is a move for me such that...". TQBF is a game in which players take turns setting variables.

So deciding whether the first player has a winning strategy is typically **PSPACE-complete** for games that end within polynomially many moves:

- **Generalised geography** (players extend a path in a directed graph, no repeats), PSPACE-complete.
- Generalised **Hex** and **Othello** on n × n boards, PSPACE-complete.

Games that can last exponentially long are typically harder: generalised **chess** (Fraenkel and Lichtenstein, 1981) and **Go** with Japanese ko rules (Robson, 1983) on n × n boards are **EXPTIME-complete**, so provably not in P.

Real-world PSPACE-complete problems include **equivalence of ordinary regular expressions** using union, concatenation and Kleene star (excluding backreferences and succinct extensions), **LTL model checking** used in hardware and protocol verification, and classical **AI planning** (STRIPS).

## What's proven, what's open

The **space hierarchy theorem** says more space solves strictly more problems: SPACE(s) ⊊ SPACE(s′) when s = o(s′) (for well-behaved s′ ≥ log n). Combined with Savitch's theorem:

- **Proven**: NL ⊊ PSPACE (NL ⊆ SPACE(log² n) ⊊ PSPACE), PSPACE ⊊ EXPSPACE, P ⊊ EXPTIME.
- **Open**: L vs NL, L vs P, NL vs P, P vs PSPACE, NP vs PSPACE, PSPACE vs EXPTIME.

It is striking that P = PSPACE has not been ruled out: nobody can prove that polynomial memory gives more power than polynomial time, though it is universally conjectured.

## Key takeaways
- Space can be reused, so it's far more powerful than time: NP ⊆ PSPACE, and SPACE(s) ⊆ TIME(2^O(s)).
- L ⊆ NL ⊆ P ⊆ NP ⊆ PSPACE ⊆ EXPTIME; proven strict: NL ⊊ PSPACE and P ⊊ EXPTIME.
- Savitch: NSPACE(s) ⊆ SPACE(s²) by midpoint recursion, so PSPACE = NPSPACE.
- Immerman–Szelepcsényi: NL = coNL, unlike the (open) time analogue NP vs coNP.
- TQBF is PSPACE-complete; polynomial-length two-player games are typically PSPACE-complete, and generalised chess and Go are EXPTIME-complete.

## Further reading
- [PSPACE — Wikipedia](https://en.wikipedia.org/wiki/PSPACE)
- [Savitch's theorem — Wikipedia](https://en.wikipedia.org/wiki/Savitch%27s_theorem)
- [True quantified Boolean formula — Wikipedia](https://en.wikipedia.org/wiki/True_quantified_Boolean_formula)
- [Immerman–Szelepcsényi theorem — Wikipedia](https://en.wikipedia.org/wiki/Immerman%E2%80%93Szelepcs%C3%A9nyi_theorem)
- [NL (complexity) — Wikipedia](https://en.wikipedia.org/wiki/NL_(complexity))
- [Generalized geography — Wikipedia](https://en.wikipedia.org/wiki/Generalized_geography)
- [Space hierarchy theorem — Wikipedia](https://en.wikipedia.org/wiki/Space_hierarchy_theorem)
