---
id: auto-nfa-paths
title: Nondeterministic paths and acceptance
level: intermediate
minutes: 5
sourceLesson: auto-nfa
summary: An NFA accepts when at least one path consumes the complete input and accepts.
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

## Key takeaways
- An NFA accepts when at least one path consumes the complete input and accepts.
- Merge paths at the same state and input position when simulating.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
