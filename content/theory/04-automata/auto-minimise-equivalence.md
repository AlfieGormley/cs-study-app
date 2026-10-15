---
id: auto-minimise-equivalence
title: Equivalent states and distinguishing suffixes
level: advanced
minutes: 4
sourceLesson: auto-minimisation
summary: Equivalent states agree on every possible continuation, including empty input.
---

The subset construction and hand design both tend to produce DFAs with redundant states: two states that look different but behave identically on every possible future input. Merging them gives a smaller machine that accepts exactly the same language.

Do it until nothing more can be merged and you reach the **minimal DFA**. A remarkable fact: for each regular language over a fixed alphabet, the minimal complete DFA is unique up to renaming states. That makes it a canonical form for regular languages. Two regexes describe the same language exactly when their minimal complete DFAs agree up to a renaming that preserves the start state, transitions and accepting status, which turns "are these equivalent?" into a mechanical check.

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

For example, in the following refinement unit’s worked example, A and D both move to B on `a`, but on `b` they move to A (rejecting) and E (accepting). The empty string distinguishes A from E, so `b` distinguishes A from D.

Equivalent states can be merged. Unreachable states can simply be deleted. A DFA with no unreachable states and no equivalent pairs is a minimal DFA.

## Key takeaways
- Equivalent states agree on every possible continuation, including empty input.
- A suffix distinguishing successors also distinguishes their predecessors when its input symbol is prepended.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
