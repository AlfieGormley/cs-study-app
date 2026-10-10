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

An NFA is described by the same five ingredients as a DFA (states, alphabet, transition function, start state, accepting states). Only the transition function changes: instead of naming one next state, it names a whole set of possible next states, and it may also move without reading anything.

```formula
DFA:  δ : Q × Σ → Q
NFA:  δ : Q × (Σ ∪ {ε}) → P(Q)
δ(1, a) = ∅
where
DFA, NFA: labels saying which kind of machine each line describes
δ: Greek delta: the transition function
Q: the finite set of automaton states
Σ: capital Greek sigma: the input alphabet
×: the Cartesian product: the set of all (state, symbol) pairs
∪: union: the set of everything in either set
{ε}: the set containing just ε, the empty string. Allowing it as a "symbol" means a move can be made without reading input
→: maps to: δ takes a pair from the left-hand set and returns one element of the right-hand set
P(Q): the power set of Q: the set of all subsets of Q, from the empty set up to Q itself. A machine with 3 states has 2³ = 8 subsets
a: an input symbol (from the example below)
1: state 1 of the example below
∅: the empty set, a set with no elements: here, no move at all
In words: a DFA's transition function returns exactly one state; an NFA's returns a set of states, which may hold several states, one, or none, and an NFA may also have moves labelled ε that read no input.
```

So from a state on a symbol, an NFA can have:

- **several** next states (a choice),
- **no** next state (that path dies),
- **ε-transitions**, moves taken without reading any input.

An NFA **accepts** a string if **at least one** path through the machine consumes the whole string and ends in an accepting state. Paths that die or end elsewhere do not matter.

## Example: strings ending in ab

Over the alphabet {a, b}:

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

In this table, a set in curly braces lists the possible next states, and ∅ (the empty set) means there is no move: that path dies.

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

The **ε-closure** of a set of states is that set plus everything reachable from it using only ε-arrows (zero or more of them). When simulating, you take the closure at the start and after every symbol.

```formula
E(S) = { r : q ⇒_ε r for some q ∈ S }
S ⊆ E(S)
where
E(S): the ε-closure of S, written ε-closure(S) in the prose and code
S: a set of NFA states
q: a state in S
r: a stand-in for any state of the NFA
ε: Greek epsilon: the empty string; an ε-arrow is a move that reads no input
⇒_ε: "can reach using only ε-arrows": following zero or more ε-arrows leads from the left state to the right one
∈: is an element of
{ r : … }: the set of all states r that make the condition after the colon true
⊆: is a subset of: every state of S is in its own closure, because following zero ε-arrows is allowed
In words: the ε-closure of a set of states is every state you can reach from it without reading any input, including the states you started in.
```

Example: accept strings of a's whose length is divisible by 2 **or** by 3.

```formula
L = { a^k : k mod 2 = 0 or k mod 3 = 0 }
where
L: the language being recognised
a: the only input symbol
a^k: k copies of a in a row, for example a^3 = aaa; a^0 is the empty string
k: the length of the string, a whole number 0, 1, 2, …
mod: the remainder after whole-number division, so 9 mod 2 = 1
{ … : … }: the set of all strings of that form that make the condition after the colon true
In words: accept a run of a's when its length is even, or a multiple of 3, or both.
```

```
      ε           a
 (s) ---> ((p0)) <---> (p1)
  |
  |   ε          a        a
  +-----> ((r0)) ---> (r1) ---> (r2)
             ^                   |
             +-------- a --------+
```

The start state s has ε-arrows to a 2-cycle and a 3-cycle.

```formula
E({s}) = {s, p0, r0}
where
E: the ε-closure: every state reachable without reading input
s: the start state
p0, r0: the accepting "count is 0 so far" states of the 2-cycle and the 3-cycle
{ }: the set of the states listed inside
In words: before reading anything, the machine is already in s, p0 and r0 at once. Two of those accept, so the empty string is accepted.
```

After one a the set is {p1, r1}: reject. After two, {p0, r2}: accept. The accepted lengths are 0, 2, 3, 4, 6, 8, 9, 10, 12, and so on.

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

Here ε is the empty string `""`. Each step looks at every current state and every arrow out of it at most once, and there is one closure for the start plus one step per input symbol. That gives this cost:

```formula
T = O((n + 1) × (m + e))
T = O((n + 1) × m)   when e = O(m)
where
T: the running time of run_nfa, counted in basic steps
O( ): Big O: an upper bound on growth that ignores constant factors
n: the length of the input string, in symbols
m: the number of NFA states
e: the number of transitions (arrows) in the NFA
In words: the work is at most the input length plus one, times the size of the machine. When each state has a bounded number of arrows out of it, the number of arrows is proportional to the number of states, and the bound simplifies to input length times states.
```

It needs O(m) working memory for the current set, excluding the stored automaton. A Thompson-style NFA (lesson 3) has at most two arrows out of each state, so the second line applies. For example, a 200-state NFA scanning a 1,000,000-symbol input does at most about 200 × 1,000,001 ≈ 2 × 10⁸ state visits, times a constant. That bound is exactly what makes linear-time regex engines possible: Thompson's algorithm tracks reachable states; modern RE2 and Go regexp use related automaton techniques alongside other optimizations.

## The subset construction

The simulation above already is a DFA in disguise. Its "state" at each moment is a set of NFA states, and there are only finitely many such sets. So build a DFA whose states are those sets. The rules, in symbols:

```formula
S₀ = E({q₀})
T = E( ⋃_{q ∈ S} δ(q, c) )
S ∈ F_D   if   S ∩ F ≠ ∅
|Q_D| ≤ 2^m
where
S₀: the start state of the new DFA
E: the ε-closure: a set of states plus everything reachable from it by ε-arrows alone
q₀: the start state of the NFA
S: one DFA state, which is a set of NFA states
q: one NFA state inside S
c: one input symbol
δ: the NFA's transition function: δ(q, c) is the set of states q can move to on c
⋃_{q ∈ S}: big union: gather the results for every q in S into a single set
∈: is an element of
T: the DFA state reached from S on symbol c
F: the NFA's accepting states
∩: intersection: the states in both sets
≠: is not equal to
∅: the empty set
F_D: the DFA's set of accepting states
Q_D: the DFA's set of states
| |: vertical bars around a set mean its cardinality: the number of elements
≤: is less than or equal to
m: the number of NFA states
2^m: 2 to the power m: how many subsets a set of m states has
In words: start from the closure of the NFA's start state; from any set, on any symbol, move every member and take the closure of the result; a set accepts if it contains at least one NFA accepting state. Since each DFA state is a subset of the m NFA states, there can be at most 2^m of them.
```

As a procedure:

1. Make the closure of the NFA's start state the DFA start state.
2. For each unprocessed DFA state and each symbol, compute the next set with the rule above. Add it if it is new.
3. Mark a DFA state accepting if it contains any NFA accepting state.
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

For "length divisible by 2 or 3", the reachable subsets are {s, p0, r0}, {p1, r1}, {p0, r2}, {p1, r0}, {p0, r1}, {p1, r2} and {p0, r0}. That is 7 DFA states: the start, then six sets that track the length's remainder after dividing by 2 and its remainder after dividing by 3, together. The start and {p0, r0} turn out to be equivalent, so the minimal DFA has 6 states: one per remainder of the length after dividing by 6.

## The exponential blow-up

Back to "the n-th symbol from the end is 1", where n is a fixed whole number such as 3. The NFA has one looping start state, one state for the guess on 1, then one state for each of the n − 1 "any symbol" steps that must follow. The subset construction produces:

| n | NFA states | DFA states |
|---|---|---|
| 1 | 2 | 2 |
| 2 | 3 | 4 |
| 3 | 4 | 8 |
| 4 | 5 | 16 |
| 6 | 7 | 64 |

The pattern in the table, in symbols:

```formula
m = n + 1
d = 2^n = 2^{m − 1}
where
n: which position from the end must be 1 (n = 3 means third from the end)
m: the number of NFA states
d: the number of states in the minimal DFA
2^n: 2 to the power n: the number of different bit strings of length n
In words: the NFA grows by one state each time n goes up by one, but the DFA doubles. For n = 6 the NFA has 7 states and the DFA has 2^6 = 64.
```

These DFAs are already minimal DFAs; you cannot do better. The reason is that the DFA must remember the last n symbols. Take two different strings u and v of length n. They differ at some position, say u has 1 and v has 0 at position i, counting from the left. Append i − 1 more symbols: now that position is n-th from the end, so one string is accepted and the other is not. So all 2ⁿ strings of length n need different states.

For example, with n set to 3, take u as `110` and v as `100`. They differ at position 2, so append one symbol, say `0`: `1100` has 1 third from the end (accept) and `1000` has 0 there (reject).

> [!warning] Worst case is real
> The general subset bound is exponential in the number of NFA states, and this family comes close to it. Full determinisation can be manageable for a given workload, but engines that build full DFAs ahead of time must guard against patterns like `(a|b)*a(a|b){20}`, which needs over a million states.

The general bound against this family:

```formula
d ≤ 2^m
d_L = 2^{m − 1}
2^{21} = 2,097,152
where
d: the number of states of the DFA built from the NFA
d_L: the minimal DFA size for the language "n-th symbol from the end is 1", whose NFA has m states
m: the number of NFA states
2^m: 2 to the power m: the number of subsets of m states, the most the subset construction can ever produce
≤: is less than or equal to
In words: an m-state NFA never needs more than 2^m DFA states. The n-th-from-the-end family needs exactly half that, 2^(m − 1): exponential, but not the full bound. The pattern (a|b)*a(a|b){20} asks for "21st from the end is a", so its minimal DFA has 2^21, about 2.1 million, states.
```

## Why both models matter

- **NFAs are easy to build.** Union, concatenation and star are almost trivial with ε-arrows. That is why the regex-to-automaton construction (next lesson) produces an NFA.
- **DFAs are fast to run.** One table lookup per symbol, no sets.
- **Practical engines mix the two.** RE2 and Rust's `regex` do a **lazy** subset construction: they build DFA states on demand during matching and cache them. If the cache gets too big, they flush it or fall back to NFA simulation. You get DFA speed on typical inputs without paying the exponential cost up front.

In this comparison, m is the number of NFA states and e is the number of transitions (arrows).

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
- Simulate it by tracking the set of possible states, with ε-closure after each step. For an input of length n and an NFA with m states and e transitions, that takes O((n + 1)·(m + e)) time including initialization, or O((n + 1)·m) for bounded out-degree.
- The subset construction turns any NFA into a DFA whose states are sets of NFA states; build only reachable sets.
- NFAs and DFAs recognise exactly the same languages (Rabin–Scott), but the DFA can be exponentially larger: "n-th from last is 1" needs an NFA with n + 1 states but a DFA with 2ⁿ states (2 multiplied by itself n times).
- Practical engines can build DFA states lazily and bound cache memory, falling back when necessary; this trades some matching speed for control of memory growth.

## Further reading
- [Nondeterministic finite automaton — Wikipedia](https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton)
- [Powerset construction — Wikipedia](https://en.wikipedia.org/wiki/Powerset_construction)
- [Rabin and Scott, Finite Automata and Their Decision Problems (1959, PDF)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
- [Regular Expression Matching: the Virtual Machine Approach — Russ Cox](https://swtch.com/~rsc/regexp/regexp2.html)
