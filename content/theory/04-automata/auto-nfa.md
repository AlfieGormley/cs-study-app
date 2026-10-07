---
id: auto-nfa
title: NFAs and the subset construction
level: intermediate
minutes: 14
summary: Nondeterministic automata that can be in many states at once, ε-moves, and the subset construction that turns any NFA into an equivalent DFA, sometimes at exponential cost.
---

Try to build a DFA for "binary strings whose third symbol from the end is 1". It is awkward. As you read, you do not know which symbol will turn out to be third from the end, so the machine has to remember the last three symbols at all times. That needs 8 states.

Now imagine a machine allowed to **guess**. It reads along, and at some 1 it guesses "this is the one", then checks that exactly two more symbols follow. If any guess works out, the string is accepted. That machine needs 4 states and is obvious to design.

That is a **nondeterministic finite automaton** (NFA). The surprise, proved by Rabin and Scott in 1959, is that guessing adds no power: every NFA has an equivalent DFA. What it can add is **conciseness**, sometimes exponentially so.

## The definition

An NFA is a 5-tuple (Q, Σ, δ, q₀, F), like a DFA, except for the transition function:

```
DFA:  δ : Q × Σ       → Q
NFA:  δ : Q × (Σ ∪ {ε}) → P(Q)
```

P(Q) is the set of all subsets of Q. So from a state on a symbol, an NFA can have:

- **several** next states (a choice),
- **no** next state (that path dies),
- **ε-transitions**, moves taken without reading any input.

An NFA **accepts** a string if **at least one** path through the machine consumes the whole string and ends in an accepting state. Paths that die or end elsewhere do not matter.

## Example: strings ending in ab

Over Σ = {a, b}:

```
   a,b
   +-+
   v |
--> (0) --a--> (1) --b--> ((2))
```

| State | on a | on b |
|---|---|---|
| → 0 | {0, 1} | {0} |
| 1 | ∅ | {2} |
| 2 (accept) | ∅ | ∅ |

State 0 loops on everything, waiting. On an a it can also guess "this a starts the final ab" and move to 1. From 1, a b reaches 2. If more input follows, the path from 2 dies, which is fine; another path stayed in 0.

## Two ways to think about nondeterminism

1. **Guessing.** The machine magically picks the right move every time. If any sequence of choices leads to acceptance, it accepts. This is the view that makes NFAs easy to design.
2. **Parallel copies.** At each choice the machine clones itself. All clones run in lockstep. Accept if any clone ends in F. This is the view that tells you how to **run** an NFA.

For efficient simulation, merge all copies at the same state and input position: keep the set of possible states, rather than one clone per path.

Trace `baab` through the NFA above:

```
start      {0}
read b ->  {0}
read a ->  {0, 1}
read a ->  {0, 1}
read b ->  {0, 2}   contains 2: accept
```

## ε-transitions and ε-closure

An ε-transition lets the machine change state for free. They make it easy to glue machines together: "do this OR that" becomes a start state with ε-arrows into two sub-machines.

The **ε-closure** of a set of states S is S plus everything reachable from S using only ε-arrows. When simulating, you take the closure at the start and after every symbol.

Example: accept aᵏ where k is divisible by 2 **or** by 3.

```
      ε           a
 (s) ---> ((p0)) <---> (p1)
  |
  |   ε          a        a
  +-----> ((r0)) ---> (r1) ---> (r2)
             ^                   |
             +-------- a --------+
```

The start state s has ε-arrows to a 2-cycle and a 3-cycle. ε-closure({s}) = {s, p0, r0}, which contains accepting states, so ε is accepted. After one a the set is {p1, r1}: reject. After two, {p0, r2}: accept. The accepted lengths are 0, 2, 3, 4, 6, 8, 9, 10, 12, and so on.

## Simulating an NFA in Python

```python
def close(delta, S):
    S = set(S)
    todo = list(S)
    while todo:
        q = todo.pop()
        for r in delta.get((q, ""), ()):
            if r not in S:
                S.add(r)
                todo.append(r)
    return S

def run_nfa(delta, start, accept, w):
    S = close(delta, {start})
    for c in w:
        T = set()
        for q in S:
            T |= delta.get((q, c), set())
        S = close(delta, T)
    return bool(S & accept)
```

Here ε is the empty string `""`. With m states and e transitions, each step takes O(m + e), giving O((n + 1) · (m + e)) time including the initial closure and O(m) working memory, excluding the stored automaton. For a Thompson-style NFA, bounded out-degree gives e = O(m), hence **O((n + 1) · m)** time. That bound is exactly what makes linear-time regex engines possible: Thompson's algorithm tracks reachable states; modern RE2 and Go regexp use related automaton techniques alongside other optimizations.

## The subset construction

The simulation above already is a DFA in disguise. Its "state" at each moment is a set of NFA states, and there are finitely many such sets (at most 2ᵐ). So build a DFA whose states are those sets:

1. The DFA start state is ε-closure({q₀}).
2. For each unprocessed DFA state S and each symbol c, compute T = ε-closure(⋃ δ(q, c) for q ∈ S). Add T if it is new.
3. A DFA state S is accepting if S contains any NFA accepting state.
4. Stop when no new sets appear. Only build sets you can actually reach.

This is also called the **powerset construction**.

### Worked example: ending in ab

Start with {0}.

| DFA state | on a | on b | Accept? |
|---|---|---|---|
| → {0} | {0, 1} | {0} | no |
| {0, 1} | {0, 1} | {0, 2} | no |
| {0, 2} | {0, 1} | {0} | yes |

Only 3 of the 2³ = 8 possible subsets are reachable. Rename them and you have an ordinary DFA:

| DFA state | Meaning | on a | on b |
|---|---|---|---|
| → A = {0} | no progress | B | A |
| B = {0, 1} | just saw a | B | C |
| C = {0, 2} (accept) | just saw ab | B | A |

### Worked example: the ε-NFA

For "length divisible by 2 or 3", the reachable subsets are {s, p0, r0}, {p1, r1}, {p0, r2}, {p1, r0}, {p0, r1}, {p1, r2} and {p0, r0}. That is 7 DFA states: the start, then six sets that track (k mod 2, k mod 3) together. The start and {p0, r0} turn out to be equivalent, so the minimal DFA has 6 states (one per value of k mod 6).

## The exponential blow-up

Back to "the n-th symbol from the end is 1". The NFA has n + 1 states: a looping start, a guess on 1, then n − 1 steps of "any symbol". The subset construction produces:

| n | NFA states | DFA states |
|---|---|---|
| 1 | 2 | 2 |
| 2 | 3 | 4 |
| 3 | 4 | 8 |
| 4 | 5 | 16 |
| 6 | 7 | 64 |

These DFAs are already minimal; you cannot do better. The reason is that the DFA must remember the last n symbols. Take two different strings u and v of length n. They differ at some position, say u has 1 and v has 0 at position i. Append i − 1 more symbols: now that position is n-th from the end, so one string is accepted and the other is not. So all 2ⁿ strings of length n need different states.

> [!warning] Worst case is real
> The general subset bound is 2ᵐ states for an m-state NFA. This particular family has m = n + 1 NFA states and 2ⁿ = 2^(m−1) minimal DFA states: exponential, but not exactly 2ᵐ. Full determinisation can be manageable for a given workload, but engines that build full DFAs ahead of time must guard against patterns like `(a|b)*a(a|b){20}`, which needs over a million states.

## Why both models matter

- **NFAs are easy to build.** Union, concatenation and star are almost trivial with ε-arrows. That is why the regex-to-automaton construction (next lesson) produces an NFA.
- **DFAs are fast to run.** One table lookup per symbol, no sets.
- **Practical engines mix the two.** RE2 and Rust's `regex` do a **lazy** subset construction: they build DFA states on demand during matching and cache them. If the cache gets too big, they flush it or fall back to NFA simulation. You get DFA speed on typical inputs without paying the 2ᵐ cost up front.

| | NFA simulation | Full DFA |
|---|---|---|
| Build cost | O(m) for a Thompson-style NFA | potentially exponential, including transition computation |
| Time per symbol | O(m) for bounded out-degree | O(1) with a precomputed transition table |
| Memory | O(m + e), including transitions | O(2ᵐ) states; transition storage also depends on alphabet size |

## Pitfalls

- **Forgetting ε-closure.** Take the closure of the start state and after every step. Missing it makes ε-arrows invisible, and strings are wrongly rejected.
- **Complementing an NFA by swapping F.** This does not work. An NFA accepts if *some* path accepts, so after swapping, a string with one accepting and one rejecting path is accepted by both machines. Determinise first, then swap.
- **Treating nondeterminism as randomness.** An NFA does not flip coins. It accepts if an accepting path *exists*. It is an existence statement, like the "certificate" view of NP you will meet later.

## Key takeaways
- An NFA can have several, zero or ε moves; it accepts if any path ends in an accepting state.
- Simulate it by tracking the set of possible states, with ε-closure after each step: O((n + 1)·(m + e)) time including initialization, or O((n + 1)·m) for bounded out-degree.
- The subset construction turns any NFA into a DFA whose states are sets of NFA states; build only reachable sets.
- NFAs and DFAs recognise exactly the same languages (Rabin–Scott), but the DFA can be exponentially larger: "n-th from last is 1" needs 2ⁿ DFA states.
- Practical engines can build DFA states lazily and bound cache memory, falling back when necessary; this trades some matching speed for control of memory growth.

## Further reading
- [Nondeterministic finite automaton — Wikipedia](https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton)
- [Powerset construction — Wikipedia](https://en.wikipedia.org/wiki/Powerset_construction)
- [Rabin and Scott, Finite Automata and Their Decision Problems (1959, PDF)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
- [Regular Expression Matching: the Virtual Machine Approach — Russ Cox](https://swtch.com/~rsc/regexp/regexp2.html)
