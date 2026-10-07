---
id: auto-minimisation
title: DFA minimisation and Myhill–Nerode
level: advanced
minutes: 15
summary: Which states of a DFA are really the same, the partition-refinement and table-filling algorithms that merge them, the Myhill–Nerode theorem behind them, and what minimal DFAs are used for.
---

The subset construction and hand design both tend to produce DFAs with redundant states: two states that look different but behave identically on every possible future input. Merging them gives a smaller machine that accepts exactly the same language.

Do it until nothing more can be merged and you reach the **minimal DFA**. A remarkable fact: for each regular language over a fixed alphabet, the minimal complete DFA is unique up to renaming states. That makes it a canonical form. Two regexes describe the same language exactly when their minimal complete DFAs agree up to a renaming that preserves the start state, transitions and accepting status, which turns "are these equivalent?" into a mechanical check.

## When are two states the same?

Two states p and q are **equivalent** if, for every string z, starting from p and reading z ends in an accepting state exactly when starting from q does.

They are **distinguishable** if some string z (a **distinguishing suffix**) takes one to an accepting state and the other to a non-accepting state.

Two observations drive every algorithm:

1. An accepting and a non-accepting state are distinguished by ε.
2. If p and q go, on some symbol c, to states that are already known to be distinguishable by z, then p and q are distinguishable by cz.

Equivalent states can be merged. Unreachable states can simply be deleted. A DFA with no unreachable states and no equivalent pairs is minimal.

## Worked example

This DFA accepts strings over {a, b} that end in ab, but it was built carelessly:

| State | on a | on b |
|---|---|---|
| → A | B | A |
| B | D | C |
| C (accept) | D | A |
| D | B | E |
| E (accept) | B | A |
| F | C | F |

### Step 1: remove unreachable states

Search from A: A reaches B; B reaches D and C; D reaches E. Nothing reaches F, so delete it. Five states remain.

### Step 2: partition refinement (Moore's algorithm)

Start from the coarsest guess, two blocks: accepting and non-accepting. Then repeatedly split any block whose members disagree about which block they go to on some symbol.

Round 0:

```
N = {A, B, D}    Acc = {C, E}
```

Round 1. For each state, note which block each transition lands in:

```
     on a   on b
A    N      N
B    N      Acc
D    N      Acc
C    N      N
E    N      N
```

A disagrees with B and D (its b goes to N, theirs to Acc), so split N into {A} and {B, D}. C and E agree, so they stay together.

```
{A}   {B, D}   {C, E}
```

Round 2. Recheck with the new blocks. B goes to D on a and C on b; D goes to B on a and E on b. Both land in ({B, D}, {C, E}), so they still agree. C and E both go to {B, D} on a and {A} on b. Nothing splits, so the partition is **stable**.

The minimal DFA has 3 states:

| Block | Meaning | on a | on b |
|---|---|---|---|
| → {A} | no progress | {B,D} | {A} |
| {B,D} | just saw a | {B,D} | {C,E} |
| {C,E} (accept) | just saw ab | {B,D} | {A} |

That is the same machine the subset construction gave in lesson 2, as uniqueness promises.

### The same thing in Python

```python
def minimise(states, alpha, delta, accept):
    states = tuple(states)
    alpha = tuple(alpha)
    # start: split accepting / non-accepting
    part = {q: q in accept for q in states}
    while True:
        sig = {q: (part[q],) + tuple(
                   part[delta[(q, c)]]
                   for c in alpha)
               for q in states}
        ids = {}
        new = {q: ids.setdefault(sig[q],
                                 len(ids))
               for q in states}
        old = len(set(part.values()))
        if len(ids) == old:
            return new   # stable: no split
        part = new
```

Each state's **signature** is its current block plus the blocks it moves to. States with equal signatures stay together. When a round creates no new blocks, stop. On the example (with F removed) it returns `{A: 0, B: 1, C: 2, D: 1, E: 2}`: three blocks, B with D and C with E.

The DFA must be complete (every transition defined), so add a dead state first if needed. Remove unreachable states before calling this function. It returns state-to-block IDs; constructing the quotient transitions, start and accepting states is a separate step.

## The table-filling algorithm

The textbook alternative (Hopcroft and Ullman) works on pairs. Draw a triangle with one cell per pair of states.

1. Mark every pair where one is accepting and the other is not.
2. Repeat: mark (p, q) if for some symbol c, the pair (δ(p, c), δ(q, c)) is already marked.
3. When a full pass marks nothing, every unmarked pair is equivalent.

For our five states:

```
    A    B    C    D
B   x1
C   x0   x0
D   x1   =    x0
E   x0   x0   =    x0
```

`x0` means marked in step 1 (different acceptance). `x1` means marked in the first pass: for (A, B), reading b gives (A, C), which is already marked. The two unmarked cells are (B, D) and (C, E), the same merges as before.

Table filling is easy to do by hand but takes O(n²) space for n states. It also tells you why each pair differs, which helps when debugging.

## How fast?

| Algorithm | Worst case | Notes |
|---|---|---|
| Table filling | O(k n²) with a dependency worklist | repeated full passes can be slower |
| Moore | O(k n²) | rounds of refinement |
| Hopcroft (1971) | O(k n log n) | split by smaller half |
| Brzozowski | exponential | det(rev(det(rev(A)))) |

Here n is the number of states and k the alphabet size.

**Hopcroft's algorithm** is the standard choice for large automata. Its worklist rule matters: if a split block is already pending, replace it with both pieces; otherwise schedule only the smaller piece. Smaller-piece scheduling and reverse transition lists let each of the k·n transitions be charged O(log n) times.

**Brzozowski's algorithm** is strange and elegant: reverse the automaton, determinise, reverse again, determinise again. The result is always minimal. Its worst case is exponential because each determinisation can blow up, but it can be fast in practice and works directly on NFAs.

## The Myhill–Nerode theorem

Minimisation rests on a theorem that describes the minimal DFA without mentioning any machine at all.

For a language L, call two strings x and y **L-equivalent** if no suffix tells them apart: for every z, xz ∈ L exactly when yz ∈ L.

> [!note] Myhill–Nerode (1958)
> L is regular if and only if L-equivalence has finitely many classes. When it does, the number of classes equals the number of states in the minimal DFA.

The intuition: a DFA state is exactly "everything about the past that matters for the future". Strings that reach the same state of the minimal DFA are L-equivalent, and each class is one state.

### A second way to prove non-regularity

Myhill–Nerode is an exact test, unlike the pumping lemma. To show L is not regular, find infinitely many strings that are pairwise distinguishable.

For L = { aⁿbⁿ }: the strings a, aa, aaa, ... are pairwise distinguishable. For i ≠ j, the suffix bⁱ puts aⁱbⁱ in L and aʲbⁱ outside it. Infinitely many classes, so not regular. No case analysis about splits, no choice of i.

### Lower bounds on DFA size

It also gives tight lower bounds. In lesson 2, "the n-th symbol from the end is 1" needed 2ⁿ states. That was a Myhill–Nerode argument: the 2ⁿ strings of length n are pairwise distinguishable.

## What minimal DFAs are used for

- **Equivalence checking.** To check `a(ba)*` against `(ab)*a`, build both minimal DFAs and compare. Both describe alternating strings that start and end with a, so they come out identical. In practice tools skip full minimisation and search the product automaton for a reachable pair (p, q) where exactly one accepts; the path to it is a counterexample. For a*b* versus (ab)*, a and b are both shortest counterexamples; alphabet traversal order determines which is returned.
- **Lexer generators.** Generators that emit a DFA as code or tables, such as re2c, minimise it first, which directly shrinks the generated scanner.
- **Hardware.** Fewer logical states may reduce storage or logic, but encoding and synthesis matter. The same binary bit count can cover several state counts, and next-state logic can become more complex.
- **Model checking and verification.** Verification tools minimise automata to shrink the state spaces they have to explore and store.
- **Learning automata.** Angluin's L* algorithm learns a minimal DFA using membership queries and equivalence queries that return counterexamples when a hypothesis is wrong. It is used to infer models of black-box network protocols and software.

## Pitfalls

- **Minimising an NFA is hard.** Uniqueness and these fast algorithms apply to DFAs. The decision problem of whether an equivalent NFA with at most a given number of states exists is PSPACE-complete, even when the input is a DFA. Minimum NFAs need not be unique.
- **Forgetting the dead state.** If your DFA is partial, add the dead state before refining, otherwise states that "fall off" on different symbols may be wrongly merged.
- **Forgetting unreachable states.** They do not change the language, but they inflate the count. Partition refinement on its own will not delete them.
- **Merging on one step.** Two states with identical rows and the same accepting status are equivalent, but states with different rows can still be equivalent (B and D above have different rows). Refinement has to run to a fixed point.

## Key takeaways
- Two states are equivalent if no suffix distinguishes them; merge equivalent states and delete unreachable ones.
- Partition refinement starts from {accepting, non-accepting} and splits blocks until stable; table filling marks distinguishable pairs.
- Hopcroft's algorithm runs in O(k n log n); Brzozowski's double reversal is elegant but exponential in the worst case.
- The minimal complete DFA over a fixed alphabet is unique up to renaming, so it is a canonical form for checking regex or automaton equivalence.
- Myhill–Nerode: L is regular exactly when it has finitely many equivalence classes, and that number is the minimal DFA size.
- Infinitely many pairwise distinguishable strings prove a language is not regular.

## Further reading
- [DFA minimization — Wikipedia](https://en.wikipedia.org/wiki/DFA_minimization)
- [Myhill–Nerode theorem — Wikipedia](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem)
- [Hopcroft, An n log n algorithm for minimizing states in a finite automaton (1971, PDF)](http://i.stanford.edu/pub/cstr/reports/cs/tr/71/190/CS-TR-71-190.pdf)
- [Induction of regular languages (Angluin's L*) — Wikipedia](https://en.wikipedia.org/wiki/Induction_of_regular_languages)
