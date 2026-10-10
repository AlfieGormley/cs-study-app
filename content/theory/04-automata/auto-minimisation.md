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

Two states are **equivalent states** if every possible future input gives the same verdict from both. They are **distinguishable states** if some input string (a **distinguishing suffix**) takes one to an accepting state and the other to a non-accepting state.

```formula
p ≡ q   iff   ∀ z ∈ Σ* :
  δ̂(p, z) ∈ F   ⟺   δ̂(q, z) ∈ F
where
p, q: two states of the same DFA
≡: is equivalent to
∀: for all
z: any input string, thought of as "the rest of the input"
Σ*: every finite string over the alphabet Σ, including the empty string ε
∈: is an element of
δ̂: "delta hat": δ̂(p, z) is the state reached by starting at p and reading all of z
F: the set of accepting states
⟺: holds exactly when: either both sides are true or both are false
In words: ("iff" means "if and only if".) Two states are equivalent when, for every possible remaining input, both accept or both reject. If even one string gets different verdicts, that string distinguishes them.
```

Two observations drive every algorithm:

1. An accepting and a non-accepting state are distinguished by the empty string: you are already there, and one accepts.
2. If two states move, on some symbol, to a pair of states already known to be distinguishable, then the two states are distinguishable too: by that symbol followed by the old distinguishing string.

```formula
δ̂(p, c · z) = δ̂(δ(p, c), z)
where
p: a state
c: one input symbol
z: a string that already distinguishes δ(p, c) from the other state's successor
·: concatenation: c followed by z
δ: the transition function: δ(p, c) is the state p moves to on c
δ̂: the extended transition function: the state reached after reading a whole string
In words: reading c then z from p is the same as first stepping on c and then reading z. So a distinguishing string for the successors, with c put in front, distinguishes the original pair.
```

For example, in the worked example below, A and D both move to B on `a`, but on `b` they move to A (rejecting) and E (accepting). The empty string distinguishes A from E, so `b` distinguishes A from D.

Equivalent states can be merged. Unreachable states can simply be deleted. A DFA with no unreachable states and no equivalent pairs is a minimal DFA.

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

Round 2. Recheck with the new blocks. B goes to D on a and C on b; D goes to B on a and E on b. Both land in ({B, D}, {C, E}), so they still agree. C and E both go to {B, D} on a and {A} on b. Nothing splits, so we have a **stable partition**.

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

Each state's **refinement signature** is its current block plus the blocks it moves to. States with equal signatures stay together. When a round creates no new blocks, stop. On the example (with F removed) it returns `{A: 0, B: 1, C: 2, D: 1, E: 2}`: three blocks, B with D and C with E.

The DFA must be complete (every transition defined), so add a dead state first if needed. Remove unreachable states before calling this function. It returns state-to-block IDs; constructing the quotient transitions, start and accepting states is a separate step.

## The table-filling algorithm

The textbook alternative (Hopcroft and Ullman) works on pairs. Draw a triangle with one cell per pair of states.

1. Mark every pair where one is accepting and the other is not.
2. Repeat: mark a pair if, on some symbol, its two successors form a pair that is already marked (the rule below).
3. When a full pass marks nothing, every unmarked pair is equivalent.

```formula
(p, q) ∈ D   if   ∃ c ∈ Σ :
  (δ(p, c), δ(q, c)) ∈ D
where
D: the set of marked pairs: pairs already known to be distinguishable
p, q: the two states of the pair being checked
∃: there exists: at least one
c: an input symbol
Σ: the input alphabet
∈: is an element of
δ: the transition function: δ(p, c) is the state p moves to on c
( , ): an unordered pair of states, one cell of the triangle
In words: a pair becomes distinguishable as soon as some single symbol sends it to a pair that is already known to be distinguishable.
```

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

The running times below are written in Big O notation, in terms of two sizes of the DFA:

```formula
T_Moore = O(k × n²)
T_Hopcroft = O(k × n × log_2(n))
where
T_Moore: the worst-case running time of Moore's partition refinement
T_Hopcroft: the worst-case running time of Hopcroft's algorithm
O( ): Big O: an upper bound on growth that ignores constant factors
n: the number of states in the DFA
k: the size of the alphabet (the number of different input symbols)
n²: n squared, n × n
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1, so log_2(1024) = 10
In words: Moore's algorithm can take time proportional to the alphabet size times the square of the state count; Hopcroft's replaces one factor of n with the much smaller log of n.
```

For a 1,000-state DFA over 2 symbols, k × n² is 2,000,000, while k × n × log₂ n is about 2 × 1,000 × 10 = 20,000: a hundredfold difference before constant factors.

| Algorithm | Worst case | Notes |
|---|---|---|
| Table filling | O(k n²) with a dependency worklist | repeated full passes can be slower |
| Moore | O(k n²) | rounds of refinement |
| Hopcroft (1971) | O(k n log n) | split by smaller half |
| Brzozowski | exponential | det(rev(det(rev(A)))) |

**Hopcroft's algorithm** is the standard choice for large automata. Its worklist rule matters: if a split block is already pending, replace it with both pieces; otherwise schedule only the smaller piece. Smaller-piece scheduling and reverse transition lists let each of the k × n transitions be charged O(log n) times: a state can only be in a scheduled "smaller half" about log₂ n times, because each time the piece containing it at least halves.

**Brzozowski's algorithm** is strange and elegant: reverse the automaton, determinise, reverse again, determinise again.

```formula
A_min = det(rev(det(rev(A))))
where
A: the input automaton (a DFA or an NFA)
rev: reversal: flip every arrow, make the accepting states the start states and the start state the accepting state. The result recognises every string of the language written backwards
det: determinisation by the subset construction, keeping only reachable sets
A_min: the result, a minimal DFA for the same language as A
In words: reverse, determinise, reverse, determinise, reading the functions from the inside out; the result is always the minimal DFA.
```

The result is always the minimal DFA. Its worst case is exponential because each determinisation can blow up, but it can be fast in practice and works directly on NFAs.

## The Myhill–Nerode theorem

Minimisation rests on a theorem that describes the minimal DFA without mentioning any machine at all.

For a language, call two strings **L-equivalent** if no suffix tells them apart:

```formula
x ≡_L y   iff   ∀ z ∈ Σ* :
  x · z ∈ L   ⟺   y · z ∈ L
where
x, y: two strings, thought of as "inputs read so far"
L: the language
≡_L: is L-equivalent to
∀: for all
z: any possible continuation (suffix)
Σ*: every finite string over the alphabet, including the empty string
·: concatenation: x followed by z
∈: is an element of
⟺: holds exactly when: both sides true, or both false
In words: ("iff" means "if and only if".) Two prefixes are L-equivalent when every possible ending puts both in L or both outside L. The strings sharing one verdict-pattern form an equivalence class.
```

For "strings ending in ab", `a` and `bba` are L-equivalent (both just saw a), while `a` and `b` are not: appending `b` gives `ab` in L and `bb` outside it.

> [!note] Myhill–Nerode (1958)
> L is regular if and only if L-equivalence has finitely many classes. When it does, the number of classes equals the number of states in the minimal DFA.

The intuition: a DFA state is exactly "everything about the past that matters for the future". Strings that reach the same state of the minimal DFA are L-equivalent, and each class is one state.

### A second way to prove non-regularity

Myhill–Nerode is an exact test, unlike the pumping lemma for regular languages. To show L is not regular, find infinitely many strings that are pairwise distinguishable.

Take the language of n a's followed by n b's. The strings a, aa, aaa, ... are pairwise distinguishable:

```formula
L = { a^n b^n : n ≥ 0 }
a^i · b^i ∈ L
a^j · b^i ∉ L   for i ≠ j
where
L: the language
a, b: the two symbols
a^n: n copies of a in a row; b^n likewise
n: any whole number 0 or more
i, j: two different counts of a's, both at least 1
·: concatenation: one string straight after another
∈, ∉: is, and is not, an element of
≠: is not equal to
≥: is greater than or equal to
In words: the suffix of i b's completes i a's into a string of L but fails for any other number of a's, so every count of a's is in its own class.
```

For example, `aa` and `aaa` are separated by `bb`: `aabb` is in L and `aaabb` is not. Infinitely many classes, so not regular. No case analysis about splits, no choice of how many copies to pump.

### Lower bounds on DFA size

It also gives tight lower bounds. In lesson 2, "the n-th symbol from the end is 1" needed 2ⁿ states, that is n copies of 2 multiplied together, where n is the position being checked. That was a Myhill–Nerode argument: the 2ⁿ strings of length n are pairwise distinguishable. For n = 3 that is 8 strings, `000` to `111`, and 8 states.

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
- Partition refinement starts from {accepting, non-accepting} and splits blocks until none splits; table filling marks distinguishable pairs.
- For a DFA with n states over k symbols, Hopcroft's algorithm runs in O(k n log n); Brzozowski's double reversal is elegant but exponential in the worst case.
- The minimal complete DFA over a fixed alphabet is unique up to renaming, so it is a canonical form for checking regex or automaton equivalence.
- Myhill–Nerode: L is regular exactly when it has finitely many equivalence classes, and that number is the minimal DFA size.
- Infinitely many pairwise distinguishable strings prove a language is not regular.

## Further reading
- [DFA minimization — Wikipedia](https://en.wikipedia.org/wiki/DFA_minimization)
- [Myhill–Nerode theorem — Wikipedia](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem)
- [Hopcroft, An n log n algorithm for minimizing states in a finite automaton (1971, PDF)](http://i.stanford.edu/pub/cstr/reports/cs/tr/71/190/CS-TR-71-190.pdf)
- [Induction of regular languages (Angluin's L*) — Wikipedia](https://en.wikipedia.org/wiki/Induction_of_regular_languages)
